#!/usr/bin/env node

/**
 * Readdy Website Builder CLI
 *
 * 轻量级脚本，用于通过 Readdy.ai 平台创建和管理网站。
 * 用法: node readdy.mjs <command> [options]
 *
 * 配置:
 *   node readdy.mjs config --token <token>          保存认证 token
 *   配置文件位置: ~/.readdy/config.json
 */

import path from 'path';
import fs from 'fs';
import os from 'os';
import { createInterface } from 'readline';

// ─── 配置文件 ────────────────────────────────────────────────────────────────

const CONFIG_DIR = path.join(os.homedir(), '.readdy');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');

function loadConfig() {
  try {
    return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  } catch {
    return {};
  }
}

function saveConfig(config) {
  if (!fs.existsSync(CONFIG_DIR)) fs.mkdirSync(CONFIG_DIR, { recursive: true });
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2) + '\n', 'utf8');
}

const config = loadConfig();
const API_HOST = config.apiHost || 'https://gbh.readdy.ai';
const TOKEN = config.token;
const DEFAULT_FRAMEWORK = 'react_v2';
const DEFAULT_DEVICE = 'web';
const DEFAULT_CATEGORY = 2;

// ─── helpers ────────────────────────────────────────────────────────────────

function die(msg, code = 1) {
  console.error(`[ERROR] ${msg}`);
  process.exit(code);
}

function info(msg) {
  console.log(`[INFO] ${msg}`);
}

function warn(msg) {
  console.warn(`[WARN] ${msg}`);
}

async function api(method, path, body, projectId) {
  if (!TOKEN) die('未配置认证 token。请运行: node readdy.mjs config --token <your-token>');

  const url = `${API_HOST}${path}`;
  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${TOKEN}`,
  };
  if (projectId) headers['X-Project-ID'] = projectId;

  const opts = { method, headers };
  if (body && method !== 'GET') opts.body = JSON.stringify(body);

  let finalUrl = url;
  if (method === 'GET' && body) {
    const qs = new URLSearchParams(
      Object.entries(body).filter(([, v]) => v !== undefined).map(([k, v]) => [k, String(v)])
    ).toString();
    if (qs) finalUrl = `${url}?${qs}`;
  }
  try {
    const res = await fetch(finalUrl, opts);
    const data = await res.json().catch(() => null);

    if (!res.ok) {
      const errMsg = data?.meta?.message || data?.meta?.detail || res.statusText;
      const errCode = data?.code || res.status;
      handleError(errCode, errMsg);
      return null;
    }

    if (data?.code && data.code !== 'OK') {
      handleError(data.code, data?.meta?.message || data?.meta?.detail || 'Unknown error');
      return null;
    }

    return data;
  } catch (err) {
    if (err?.cause?.code === 'ENOTFOUND' || err?.cause?.code === 'ECONNREFUSED') {
      die('网络连接失败，请检查网络或关闭 VPN 后重试。');
    }
    die(`请求失败: ${err.message}`);
  }
}

/** SSE 流式请求 — 用于 /api/project/generate */
async function apiSSE(path, body, projectId) {
  if (!TOKEN) die('未配置认证 token。请运行: node readdy.mjs config --token <your-token>');

  const url = `${API_HOST}${path}`;
  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${TOKEN}`,
  };
  if (projectId) headers['X-Project-ID'] = projectId;

  let res;
  try {
    res = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });
  } catch (err) {
    warn(`SSE 连接失败: ${err.message}`);
    return null;
  }

  // 如果返回 JSON 而非 SSE，说明出错了
  if (res.headers.get('Content-Type')?.includes('application/json')) {
    const json = await res.json().catch(() => null);
    if (json?.code && json.code !== 'OK') {
      handleError(json.code, json?.meta?.message || json?.meta?.detail || 'Generate failed');
      return null;
    }
    return json;
  }

  if (!res.ok) {
    handleError(res.status, res.statusText);
    return null;
  }

  // 解析 SSE 流 — 对齐前端 SSEReaderHandle + Reader 状态机行为
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let currentEvent = '';

  // 元数据 (从 response 事件提取)
  let versionId = null;
  let showId = null;
  let revertShowId = null;
  let sessionId = null;
  let sessionStatus = null;
  let language = null;
  let requestId = null;
  let errorInfo = null;

  // eventData 收集 — 与前端 Reader.getEventDataItem() 输出格式一致
  const eventData = [];

  // thinking 状态
  let thinkingStart = null;

  // data 累积 (前端 DataReader: 累积 text 直到遇到 action 标签或事件切换)
  let accumulatedText = '';

  // tool 状态 (前端 ToolReader: 同名 tool 后续 data 累积到同一 entry)
  let currentToolEntry = null;
  let currentToolName = '';

  const ACTION_START = '<action';
  const ACTION_END = '</action>';

  /** 从文本中拆分 <action>...</action> 标签，对齐前端 DataReader + ActionReader */
  function splitAndPushTextWithAction(text) {
    const actionIdx = text.indexOf(ACTION_START);
    if (actionIdx === -1) {
      if (text) eventData.push({ event: 'data', data: { text } });
      return;
    }
    const cleanText = text.slice(0, actionIdx);
    if (cleanText) eventData.push({ event: 'data', data: { text: cleanText } });

    const remaining = text.slice(actionIdx);
    const endIdx = remaining.indexOf(ACTION_END);
    if (endIdx === -1) {
      if (remaining) eventData.push({ event: 'data', data: { text: remaining } });
      return;
    }
    const actionBlock = remaining.slice(0, endIdx + ACTION_END.length);
    const nameMatch = actionBlock.match(/<action[^>]*\bname=["']([^"']+)["']/);
    const actionName = nameMatch ? nameMatch[1] : '';
    let actionDataStr = '';
    if (actionName === 'nextStep') {
      const steps = [];
      const stepRe = /<step>([\s\S]*?)<\/step>/g;
      let m, n = 1;
      while ((m = stepRe.exec(actionBlock)) !== null) steps.push({ step: n++, data: m[1].trim() });
      actionDataStr = JSON.stringify({ steps });
    }
    eventData.push({ event: 'action', data: { action: actionName, status: 'ready', data: actionDataStr } });

    const afterAction = remaining.slice(endIdx + ACTION_END.length);
    if (afterAction.trim()) splitAndPushTextWithAction(afterAction);
  }

  /** flush 当前 reader 状态 */
  function flushCurrent() {
    if (accumulatedText && currentEvent === 'data') {
      splitAndPushTextWithAction(accumulatedText);
      accumulatedText = '';
    }
    if (thinkingStart !== null && currentEvent === 'thinking') {
      eventData.push({ event: 'thinking', data: { duration: Date.now() - thinkingStart, isThinking: false } });
      thinkingStart = null;
    }
    if (currentToolEntry && currentEvent === 'tool') {
      eventData.push(currentToolEntry);
      currentToolEntry = null;
      currentToolName = '';
    }
  }

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('event:')) {
          const newEvent = line.slice(6).trim();
          // 事件类型切换时 flush
          if (newEvent !== currentEvent) {
            flushCurrent();
          }
          currentEvent = newEvent;
          if (currentEvent === 'thinking') thinkingStart = Date.now();
        } else if (line.startsWith('data:')) {
          const data = line.slice(5);

          // ── 按事件类型分发 ──
          if (currentEvent === 'thinking') {
            process.stdout.write(data);
          } else if (currentEvent === 'data') {
            process.stdout.write(data);
            accumulatedText += data;
            // 对齐前端 DataReader：实时检测 <action 标签并拆分
            if (accumulatedText.indexOf(ACTION_START) !== -1 && accumulatedText.indexOf(ACTION_END) !== -1) {
              splitAndPushTextWithAction(accumulatedText);
              accumulatedText = '';
            }
          } else if (currentEvent === 'tool') {
            try {
              const toolObj = JSON.parse(data);
              const name = toolObj.name || toolObj.tool;
              if (name && name !== currentToolName) {
                // 新 tool — flush 旧的，开始新 entry
                if (currentToolEntry) eventData.push(currentToolEntry);
                currentToolName = name;
                process.stdout.write('\n');
                info(`  [tool] ${name}`);
                const toolData = { name };
                if (toolObj.files) toolData.files = toolObj.files;
                if (toolObj.toolData) toolData.toolData = toolObj.toolData;
                currentToolEntry = { event: 'tool', data: toolData };
              } else if (currentToolEntry) {
                // 同名 tool 后续 data — 累积 files/toolData
                if (toolObj.files) currentToolEntry.data.files = toolObj.files;
                if (toolObj.toolData) currentToolEntry.data.toolData = { ...(currentToolEntry.data.toolData || {}), ...toolObj.toolData };
              }
            } catch {}
          } else if (currentEvent === 'action') {
            // 独立 action SSE 事件
            try {
              const actionObj = JSON.parse(data);
              eventData.push({ event: 'action', data: { action: actionObj.action || '', status: actionObj.status || 'ready', data: actionObj.data || '' } });
            } catch {
              // 非 JSON — 可能是原始 action 标签文本
              const nameMatch = data.match(/<action[^>]*\bname=["']([^"']+)["']/);
              if (nameMatch) {
                eventData.push({ event: 'action', data: { action: nameMatch[1], status: 'ready', data: '' } });
              }
            }
          }

          // response 事件 — 提取元数据 (对齐前端 ResponseReader)
          if (currentEvent === 'response' || currentEvent === 'finish') {
            try {
              const r = JSON.parse(data);
              // error
              if (r.error) {
                errorInfo = { type: 'normal', code: r.error.err_code || 'UnknownError', status: r.error.status || 0, message: r.error.err_code || '' };
              }
              if (r.project_version_id) versionId = r.project_version_id;
              if (r.show_id) showId = r.show_id;
              if (r.revert_show_id) revertShowId = r.revert_show_id;
              if (r.session_id) sessionId = r.session_id;
              if (r.session_status) sessionStatus = r.session_status;
              if (r.language) language = r.language;
              if (r.request_id) requestId = r.request_id;
            } catch {}
          }
        }
      }
    }
  } catch (err) {
    warn(`SSE 流读取中断: ${err.message}`);
  }
  // flush 剩余状态
  flushCurrent();
  if (accumulatedText) {
    splitAndPushTextWithAction(accumulatedText);
    accumulatedText = '';
  }
  if (thinkingStart !== null) {
    eventData.push({ event: 'thinking', data: { duration: Date.now() - thinkingStart, isThinking: false } });
  }
  process.stdout.write('\n');

  return { eventData, versionId, showId, revertShowId, sessionId, sessionStatus, language, requestId, errorInfo };
}

// ─── error handling ─────────────────────────────────────────────────────────

function handleError(code, message) {
  const errorMap = {
    401: '认证失败，token 已过期或无效，请运行: node readdy.mjs config --token <new-token>',
    403: '权限不足，当前角色无法执行此操作。',
    AccessDenied: '权限不足，当前角色无法执行此操作。',
    ProjectNotFound: '项目不存在或已被删除。',
    ProjectMax: '项目数量已达上限，请升级订阅或删除旧项目。',
    ApiKeyInvalid: 'API Key 格式无效或已失效。',
    ImageTooLarge: '图片大小不能超过 3.5MB。',
    SubscriptionInGracePeriod: '订阅处于宽限期，请更新支付信息。',
    RequestTimeout: '请求超时，请稍后重试。',
    InvalidParameter: `参数错误: ${message}`,
    PromptTooLong: '请求内容过长，请简化后重试。',
    InternalError: '服务器内部错误，请稍后重试。',
    PreviewError: `预览错误: ${message}`,
  };
  const msg = errorMap[code] || `[${code}] ${message || '未知错误，请检查网络或联系支持。'}`;
  console.error(`[ERROR] ${msg}`);
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

/** 从 stdin 读取一行用户输入 */
function readUserInput(prompt) {
  return new Promise((resolve) => {
    process.stdout.write(prompt);
    const rl = createInterface({ input: process.stdin, output: process.stdout });
    rl.once('line', (line) => {
      rl.close();
      resolve(line.trim());
    });
    rl.once('close', () => resolve(''));
  });
}

// ─── build + session 续传 ────────────────────────────────────────────────────

/**
 * 构建项目并轮询检查状态
 * @returns {{ buildOk: boolean, buildError: string }}
 */
async function buildAndCheck(projectId, versionId) {
  info('  正在构建项目...');
  const buildRes = await api('POST', '/api/project/build', { projectId, versionId }, projectId);
  if (!buildRes) warn('构建请求失败');

  info('  正在检查构建状态...');
  let buildOk = false;
  let buildError = '';
  for (let i = 0; i < 30; i++) {
    await sleep(2000);
    const checkRes = await api('POST', '/api/project/build_check', { projectId, versionId }, projectId);
    if (checkRes?.code === 'OK' && checkRes.data?.previewUrl) {
      buildOk = true;
      info(`  构建成功! 预览: ${checkRes.data.previewUrl}`);
      break;
    }
    if (checkRes?.data?.compileError) {
      buildError = checkRes.data.compileError;
      warn(`  构建错误: ${buildError.slice(0, 200)}`);
      break;
    }
  }
  if (!buildOk && !buildError) warn('构建未在超时时间内完成');
  return { buildOk, buildError };
}

/**
 * 执行 generate → build/ask_user → session 续传循环
 * 对齐前端 GeneratePageSession 的完整 SessionStatus 处理:
 *   - waiting_build: 执行 build 后自动续传
 *   - waiting_input: 提示用户输入后续传 (CLI 场景下从 stdin 读取)
 *   - completed: 会话正常结束
 *   - failed: 会话失败
 * @returns {{ allEventData, versionId, finalRequestId, finalSessionId, finalSessionStatus, finalShowId, language, hasBuilt }}
 */
async function generateWithSessionLoop(projectId, generateParams) {
  let allEventData = [];
  let versionId = null;
  let finalRequestId = '';
  let finalSessionId = '';
  let finalSessionStatus = '';
  let finalShowId = 0;
  let lang = '';
  let hasBuilt = false;
  let currentParams = { ...generateParams };
  let round = 0;
  const MAX_ROUNDS = 10;

  while (round < MAX_ROUNDS) {
    round++;
    info(`  Generate 第 ${round} 轮...`);

    const sseResult = await apiSSE('/api/project/generate', currentParams, projectId);
    if (!sseResult) {
      warn('SSE 生成失败');
      break;
    }

    allEventData = [...allEventData, ...sseResult.eventData];
    if (sseResult.versionId) versionId = sseResult.versionId;
    if (sseResult.showId) finalShowId = sseResult.showId;
    if (sseResult.requestId) finalRequestId = sseResult.requestId;
    if (sseResult.sessionId) finalSessionId = sseResult.sessionId;
    if (sseResult.sessionStatus) finalSessionStatus = sseResult.sessionStatus;
    if (sseResult.language) lang = sseResult.language;

    info(`  versionId: ${versionId || '(无)'}, sessionStatus: ${finalSessionStatus || '(无)'}`);

    if (sseResult.errorInfo) {
      warn(`  生成返回错误: [${sseResult.errorInfo.code}] ${sseResult.errorInfo.message}`);
      break;
    }

    // ── 根据 sessionStatus 决定下一步 ──

    if (finalSessionStatus === 'failed') {
      warn('  Session 失败，终止生成');
      break;
    }

    if (finalSessionStatus === 'completed' || !finalSessionId) {
      // 会话正常结束或无 sessionId — 退出循环
      break;
    }

    if (finalSessionStatus === 'waiting_build' && versionId) {
      // waiting_build — 执行 build 后继续
      info('  Session 需要 build 后续传...');
      const { buildOk, buildError } = await buildAndCheck(projectId, versionId);
      hasBuilt = true;

      currentParams = {
        ...generateParams,
        sessionId: finalSessionId,
        buildResult: { success: buildOk, error: buildError || '' },
        language: lang,
      };
      continue;
    }

    if (finalSessionStatus === 'waiting_input') {
      // waiting_input — CLI 场景下从 stdin 读取用户输入
      info('  Session 等待用户输入 (ask_user)...');
      const userInput = await readUserInput('请输入回复内容 (输入后按回车): ');
      if (!userInput) {
        warn('  用户未输入内容，终止生成');
        break;
      }

      currentParams = {
        ...generateParams,
        query: userInput,
        sessionId: finalSessionId,
        language: lang,
      };
      continue;
    }

    // 未知状态或无需续传 — 退出
    break;
  }

  if (round >= MAX_ROUNDS) warn('Session 续传轮次达到上限');

  return { allEventData, versionId, finalRequestId, finalSessionId, finalSessionStatus, finalShowId, language: lang, hasBuilt };
}

// ─── message helpers ─────────────────────────────────────────────────────────

/** 创建用户消息 (role=1) */
async function createUserMsg(projectId, query, imageUrl) {
  const contentItems = [];
  if (imageUrl) contentItems.push({ type: 1, data: { url: imageUrl } });
  contentItems.push({ type: 0, data: { text: query } });
  const content = JSON.stringify({ content: contentItems, status: 0, type: 0 });
  const res = await api('POST', '/api/project/msg', { projectId, role: 1, content }, projectId);
  return res?.data?.id || null;
}

/** 创建 AI 占位消息 (role=0, recordStatus=2) */
async function createAiMsg(projectId, fromMsgId, recordReference = 0) {
  const content = JSON.stringify({
    content: [{ type: 3, data: { recordStatus: 2, showId: 0, eventData: [{ event: 'analyzing', data: {} }], requestId: '' } }],
    status: 0,
    type: 1,
    recordReference,
    fromMsgId
  });
  const res = await api('POST', '/api/project/msg', { projectId, role: 0, content }, projectId);
  return res?.data?.id || null;
}

/** 更新 AI 消息为完成状态 — 对齐前端 GenerateResponseHandler.message 结构 */
async function updateAiMsg(projectId, msgId, { versionId = 0, showId = 0, requestId = '', fromMsgId = 0, recordReference = 0, eventData = [], sessionId = '', sessionStatus = '', revertShowId } = {}) {
  const msgData = { projectVersionId: versionId, recordStatus: 0, showId, eventData, requestId };
  if (sessionId) msgData.sessionId = sessionId;
  if (sessionStatus) msgData.sessionStatus = sessionStatus;
  const msgContent = {
    content: [{ type: 3, data: msgData }],
    status: 0,
    type: 1,
    recordReference,
    fromMsgId
  };
  if (revertShowId) msgContent.revertShowId = revertShowId;
  const content = JSON.stringify(msgContent);
  await api('PUT', '/api/project/msg', { projectId, msgId, role: 0, content }, projectId);
}

// ─── commands ───────────────────────────────────────────────────────────────

/** 1. 项目列表 */
async function listProjects(pageNum = 1, pageSize = 50) {
  info('正在获取项目列表...');
  const res = await api('POST', '/api/page_gen/project/list', {
    page: { pageNum: Number(pageNum), pageSize: Number(pageSize) },
  });
  if (!res) return;

  const { projects, page } = res.data;
  console.log(`\n共 ${page.total} 个项目 (第 ${page.pageNum} 页, 每页 ${page.pageSize}):\n`);
  console.log('ID'.padEnd(28) + 'Name'.padEnd(30) + 'Framework'.padEnd(12) + 'Published'.padEnd(10) + 'Device'.padEnd(10) + 'Role');
  console.log('-'.repeat(100));
  for (const p of projects) {
    console.log(
      (p.id || '').padEnd(28) +
      (p.name || '(unnamed)').padEnd(30) +
      (p.framework || '-').padEnd(12) +
      (p.isPublish ? 'Yes' : 'No').padEnd(10) +
      (p.device || '-').padEnd(10) +
      (p.role || '-')
    );
  }
  return projects;
}

/** 2. 获取项目信息 */
async function getProjectInfo(projectId) {
  if (!projectId) die('--id (projectId) 是必须的');

  info(`正在获取项目 ${projectId} 信息...`);
  const res = await api('GET', '/api/page_gen/project', { projectId }, projectId);
  if (!res) return null;

  console.log('\n项目信息:');
  console.log(JSON.stringify(res.data, null, 2));
  return res.data;
}

/** 3. 获取项目历史消息 */
async function getProjectMessages(projectId, pageNum = 1, pageSize = 50) {
  if (!projectId) die('--id (projectId) 是必须的');

  info('正在获取项目历史消息...');
  const res = await api('POST', '/api/project/msg_list', {
    projectId,
    page: { pageNum: Number(pageNum), pageSize: Number(pageSize) },
  }, projectId);
  if (!res) return null;

  const { projectMsgs, page } = res.data;
  console.log(`\n共 ${page.total} 条消息 (第 ${page.pageNum} 页):\n`);
  for (const msg of projectMsgs) {
    const role = msg.role === 1 ? 'USER' : 'AI';
    const time = new Date(msg.createdAt * 1000).toLocaleString();
    const content = msg.content.length > 100 ? msg.content.slice(0, 100) + '...' : msg.content;
    console.log(`[${role}] (id:${msg.id}) ${time}\n  ${content}\n`);
  }
  return projectMsgs;
}

/** 4. 项目新建 — 完整流程 (对齐 HAR 抓包 + 前端源码) */
async function createProject(opts) {
  const { query, device, framework, lib, category } = opts;
  if (!query) die('--query 是必须的 (项目描述/需求)');

  const deviceType = device || DEFAULT_DEVICE;
  const fw = framework || DEFAULT_FRAMEWORK;

  // ═══════════════════════════════════════════════════════════════════════════
  // Step 1/8: gen_section (生成页面模块) + suggest_title (生成项目名称) 并行
  // ═══════════════════════════════════════════════════════════════════════════
  info('Step 1/8: 正在并行生成页面模块和项目名称...');
  const [sectionRes, titleRes] = await Promise.all([
    api('POST', '/api/project/gen_section', { query }),
    api('POST', '/api/page_gen/suggest/page_title', { query }),
  ]);

  // 解析 gen_section 结果
  let sections = [], pages = [], logoPrompt = '';
  if (sectionRes?.data) {
    sections = sectionRes.data.sections || [];
    pages = sectionRes.data.pages || [];
    logoPrompt = sectionRes.data.logo || '';
    const items = pages.length > 0 ? pages : sections;
    info(`  获取到 ${items.length} 个${pages.length > 0 ? '页面' : '模块'}`);
    items.forEach((item, i) => console.log(`    ${i + 1}. ${item}`));
  } else {
    warn('[Step 1] gen_section 失败，后续生成可能缺少页面结构');
  }

  // 解析 suggest_title 结果
  let projectName = 'New Project';
  if (titleRes?.data?.title) {
    projectName = titleRes.data.title;
    info(`  项目名称: ${projectName}`);
  } else {
    warn('[Step 1] suggest_title 失败，使用默认名称: New Project');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Step 2/8: gen_logo (依赖 gen_section 返回的 logoPrompt)
  // ═══════════════════════════════════════════════════════════════════════════
  let logoUrl = '';
  if (logoPrompt) {
    info('Step 2/8: 正在生成 Logo...');
    const logoRes = await api('POST', '/api/project/gen_logo', { query: logoPrompt });
    if (logoRes?.data?.imageUrl) {
      logoUrl = logoRes.data.imageUrl;
      info(`  Logo 已生成: ${logoUrl}`);
    } else {
      warn('[Step 2] Logo 生成失败，将跳过 Logo');
    }
  } else {
    info('Step 2/8: 跳过 (gen_section 未返回 logo prompt)');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Step 3/8: 创建项目 (POST /api/page_gen/project)
  // ═══════════════════════════════════════════════════════════════════════════
  info('Step 3/8: 正在创建项目...');
  const createParams = {
    name: projectName,
    framework: fw,
    lib: lib || '',
    category: category !== undefined ? Number(category) : DEFAULT_CATEGORY,
    device: deviceType,
  };
  const createRes = await api('POST', '/api/page_gen/project', createParams);
  if (!createRes?.data?.id) die('[Step 3] 项目创建失败，无法继续');
  const projectId = createRes.data.id;
  info(`  项目已创建: ${projectId}`);

  // ═══════════════════════════════════════════════════════════════════════════
  // Step 4/8: 保存 Logo 到项目 (PUT /api/page_gen/project)
  // ═══════════════════════════════════════════════════════════════════════════
  if (logoUrl) {
    info('Step 4/8: 正在保存 Logo...');
    const logoSaveRes = await api('PUT', '/api/page_gen/project', { projectId, logo: logoUrl }, projectId);
    if (!logoSaveRes) warn('[Step 4] Logo 保存失败，项目将没有 Logo');
  } else {
    info('Step 4/8: 跳过 (无 Logo)');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Step 5/8: 创建消息记录 + 发起 generate (并行，对齐前端行为)
  //
  // 前端时序: 用户消息、AI占位消息、generate 三个请求几乎同时发出
  // - 用户消息: POST /api/project/msg (role=1)
  // - AI占位消息: POST /api/project/msg (role=0, recordStatus=2)
  // - generate: POST /api/project/generate (SSE)
  // ═══════════════════════════════════════════════════════════════════════════
  info('Step 5/8: 正在创建消息记录并生成项目内容...');

  // 构建 pageSection — HAR 显示使用全部 sections
  const pageSection = pages.length > 0
    ? pages.map(p => `<webpage>${p}</webpage>`).join('')
    : sections.map(s => `<section>${s}</section>`).join('');

  // 构建 generate 参数 — 严格对齐 HAR 中第一次 generate 请求
  const generateParams = {
    projectID: projectId,
    parentVersionID: 0,
    query,
    route: '/',
    browser: { language: 'zh-CN', timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Shanghai' },
    parentShowID: 0,
    apiVersion: 'v2',
    language: '',                        // 首次为空字符串，续传时由 generateWithSessionLoop 填充
    role: '',
    elementCode: '',
    xpath: '',
    ...(pageSection && { pageSection }),
    ...(logoUrl && { logoUrl }),
  };

  // 并行发起: 用户消息 + AI消息 + generate
  // 不等待消息创建完成就开始 generate，与前端行为一致
  const userMsgPromise = createUserMsg(projectId, query);
  const aiMsgPromise = (async () => {
    // AI 消息需要 fromMsgId，但不阻塞 generate
    const userMsgId = await userMsgPromise;
    return createAiMsg(projectId, userMsgId);
  })();
  const generatePromise = generateWithSessionLoop(projectId, generateParams);

  // 等待所有完成
  const [userMsgId, aiMsgId, result] = await Promise.all([
    userMsgPromise,
    aiMsgPromise,
    generatePromise,
  ]);

  if (!userMsgId) warn('[Step 5] 用户消息创建失败，消息记录不完整');
  if (!aiMsgId) warn('[Step 5] AI 消息创建失败，消息记录不完整');

  const versionId = result.versionId;

  if (!versionId) {
    warn('[Step 5] generate 未返回 versionId，无法构建');
    if (aiMsgId) {
      await updateAiMsg(projectId, aiMsgId, { fromMsgId: userMsgId, eventData: result.allEventData });
    }
    console.log(`\n项目创建完成 (无版本生成)! ID: ${projectId}`);
    return { projectId };
  }

  info(`  versionId: ${versionId}`);

  // ═══════════════════════════════════════════════════════════════════════════
  // Step 6/8: 最终构建 (如果续传循环中没有 build 过)
  //
  // 前端 handleCompleted():
  //   hasBuiltSuccessfully → 跳过
  //   有 versionId 但未 build → 执行兜底 build
  // ═══════════════════════════════════════════════════════════════════════════
  if (!result.hasBuilt) {
    info('Step 6/8: 正在执行最终构建...');
    const { buildOk, buildError } = await buildAndCheck(projectId, versionId);
    if (!buildOk) {
      warn(`[Step 6] 构建失败${buildError ? ': ' + buildError.slice(0, 200) : ''}`);
    }
  } else {
    info('Step 6/8: 跳过 (已在续传中构建)');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Step 7/8: 设置 showId (POST /api/project/set_show_id)
  //
  // 前端重试策略: timerRetryFetch([0, 2000, 2000, 2000, 2000])
  // 第一次可能返回 showID=0，需要重试
  // ═══════════════════════════════════════════════════════════════════════════
  info('Step 7/8: 正在设置 showId...');
  let finalShowId = result.finalShowId || 0;
  if (!finalShowId || finalShowId <= 0) {
    // 对齐前端 timerRetryFetch([0, 2000, 2000, 2000, 2000])：按业务值重试
    const delays = [0, 2000, 2000, 2000, 2000];
    for (let i = 0; i < delays.length; i++) {
      if (delays[i]) await sleep(delays[i]);
      const res = await api('POST', '/api/project/set_show_id',
        { projectId, versionID: versionId }, projectId);
      finalShowId = res?.data?.showID || 0;
      if (finalShowId > 0) {
        info(`  showId: ${finalShowId}`);
        break;
      }
      if (i < delays.length - 1) info(`  showId 仍为 0，重试中 (${i + 1}/${delays.length})...`);
    }
    if (!finalShowId || finalShowId <= 0) {
      warn('[Step 7] set_show_id 多次重试后仍返回 showId=0');
    }
  } else {
    info(`  showId: ${finalShowId} (从 SSE response 获取)`);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Step 8/8: 更新 AI 消息为完成状态 (PUT /api/project/msg)
  //
  // recordStatus: 2 → 0, showId: 最终值, eventData: 完整事件流
  // ═══════════════════════════════════════════════════════════════════════════
  info('Step 8/8: 正在更新消息为完成状态...');
  if (aiMsgId) {
    await updateAiMsg(projectId, aiMsgId, {
      versionId,
      showId: finalShowId,
      fromMsgId: userMsgId,
      eventData: result.allEventData,
      requestId: result.finalRequestId,
      sessionId: result.finalSessionId,
      sessionStatus: result.finalSessionStatus,
    });
    info('  消息已更新');
  } else {
    warn('[Step 8] 无 AI 消息 ID，跳过消息更新');
  }

  console.log(`\n项目创建完成! ID: ${projectId}, versionId: ${versionId}, showId: ${finalShowId}`);
  return { projectId, versionId, showId: finalShowId };
}

/** 5. 项目修改 — 完整流程 (通过 AI 重新生成) */
async function modifyProject(opts) {
  const { id, query } = opts;
  if (!id) die('--id (projectId) 是必须的');
  if (!query) die('--query 是必须的 (修改需求描述)');

  // Step 1: 获取项目信息
  info('Step 1/6: 正在获取项目信息...');
  const projectRes = await api('GET', '/api/page_gen/project', { projectId: id }, id);
  if (!projectRes) die('[Step 1] 获取项目信息失败');
  const project = projectRes.data;
  info(`  项目: ${project?.name || id}`);

  // Step 2: 获取历史消息
  info('Step 2/6: 正在获取历史消息...');
  const msgRes = await api('POST', '/api/project/msg_list', {
    projectId: id,
    isTemplate: false,
    page: { pageNum: 1, pageSize: 100 },
  }, id);
  const messages = msgRes?.data?.projectMsgs || [];
  info(`  获取到 ${messages.length} 条历史消息`);

  // 从历史消息中提取 parentVersionID、parentShowID、parentSessionId，构建 history JSON
  let parentVersionID = 0;
  let parentShowID = 0;
  let parentSessionId = '';
  const historyEntries = [];

  for (const msg of messages) {
    try {
      const content = JSON.parse(msg.content);
      if (msg.role === 0 && Array.isArray(content.content)) {
        // AI 消息: 提取 projectVersionId、showId、sessionId
        for (const item of content.content) {
          if (item.data?.projectVersionId && item.data.projectVersionId > parentVersionID) {
            parentVersionID = item.data.projectVersionId;
          }
          if (item.data?.versionId && item.data.versionId > parentVersionID) {
            parentVersionID = item.data.versionId;
          }
          if (item.data?.showId && item.data.showId > parentShowID) {
            parentShowID = item.data.showId;
          }
          if (item.data?.sessionId) {
            parentSessionId = item.data.sessionId;
          }
        }
      }
      // 构建 history JSON: 用户消息 + 对应 AI 事件
      if (msg.role === 1 && Array.isArray(content.content)) {
        const text = content.content.filter(c => c.type === 0).map(c => c.data?.text || '').join('');
        if (text) historyEntries.push({ user: text, events: [] });
      }
      if (msg.role === 0 && Array.isArray(content.content) && historyEntries.length > 0) {
        const lastEntry = historyEntries[historyEntries.length - 1];
        for (const item of content.content) {
          if (item.data?.eventData && Array.isArray(item.data.eventData)) {
            for (const ev of item.data.eventData) {
              if (ev.event === 'tool') {
                const toolName = ev.data?.name || '';
                const files = ev.data?.files || [];
                const toolData = ev.data?.toolData ? JSON.stringify(ev.data.toolData) : '';
                lastEntry.events.push({ type: 'tool_info', tool: toolName, info: toolData || files.join(',') });
              } else if (ev.event === 'data') {
                const text = ev.data?.text || '';
                if (text) lastEntry.events.push({ type: 'text', content: text });
              }
            }
          }
        }
      }
    } catch {}
  }
  info(`  parentVersionID: ${parentVersionID}, parentShowID: ${parentShowID}, parentSessionId: ${parentSessionId || '(无)'}`);

  // 构建 history JSON 字符串
  const historyJSON = historyEntries.length > 0 ? JSON.stringify(historyEntries) : '';

  // ═══════════════════════════════════════════════════════════════════════════
  // Step 3/6: 创建消息记录 + 发起 generate (并行，对齐前端行为)
  //
  // 前端时序: 用户消息、AI占位消息、generate 三个请求几乎同时发出
  // - 用户消息: POST /api/project/msg (role=1)
  // - AI占位消息: POST /api/project/msg (role=0, recordStatus=2)
  // - generate: POST /api/project/generate (SSE)
  // ═══════════════════════════════════════════════════════════════════════════
  info('Step 3/6: 正在创建消息记录并生成修改内容...');

  const generateParams = {
    parentVersionID,
    projectID: id,
    query,
    route: '/',
    parentShowID,
    browser: { language: 'zh-CN', timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Shanghai' },
    apiVersion: 'v2',
    currentDevice: project?.device || DEFAULT_DEVICE,
    console: [],
    network: [],
    language: '',                        // 首次为空字符串，续传时由 generateWithSessionLoop 填充
    role: project?.role || '',           // 从项目信息获取用户角色
    embedCode: '',
    ...(parentSessionId && { parentSessionId }),
    ...(historyJSON && { history: historyJSON }),
  };

  // 并行发起: 用户消息 + AI消息 + generate (对齐前端 executeSend 行为)
  const userMsgPromise = createUserMsg(id, query);
  const aiMsgPromise = (async () => {
    const userMsgId = await userMsgPromise;
    return createAiMsg(id, userMsgId, parentVersionID);
  })();
  const generatePromise = generateWithSessionLoop(id, generateParams);

  const [userMsgId, aiMsgId, result] = await Promise.all([
    userMsgPromise,
    aiMsgPromise,
    generatePromise,
  ]);

  if (!userMsgId) warn('[Step 3] 用户消息创建失败，消息记录不完整');
  if (!aiMsgId) warn('[Step 3] AI 消息创建失败，消息记录不完整');
  const versionId = result.versionId;

  if (!versionId) {
    warn('[Step 3] generate 未返回 versionId，无法构建');
    if (aiMsgId) await updateAiMsg(id, aiMsgId, { fromMsgId: userMsgId, recordReference: parentVersionID, eventData: result.allEventData });
    console.log('\n修改完成 (无新版本生成)');
    return { projectId: id };
  }

  info(`  versionId: ${versionId}`);

  // ═══════════════════════════════════════════════════════════════════════════
  // Step 4/6: 最终构建 (如果续传循环中没有 build 过)
  // ═══════════════════════════════════════════════════════════════════════════
  if (!result.hasBuilt) {
    info('Step 4/6: 正在执行最终构建...');
    const { buildOk, buildError } = await buildAndCheck(id, versionId);
    if (!buildOk) {
      warn(`[Step 4] 构建失败${buildError ? ': ' + buildError.slice(0, 200) : ''}`);
    }
  } else {
    info('Step 4/6: 跳过 (已在续传中构建)');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Step 5/6: 设置 showId (POST /api/project/set_show_id)
  // ═══════════════════════════════════════════════════════════════════════════
  info('Step 5/6: 正在设置 showId...');
  let finalShowId = result.finalShowId || 0;
  if (!finalShowId || finalShowId <= 0) {
    const delays = [0, 2000, 2000, 2000, 2000];
    for (let i = 0; i < delays.length; i++) {
      if (delays[i]) await sleep(delays[i]);
      const res = await api('POST', '/api/project/set_show_id',
        { projectId: id, versionID: versionId }, id);
      finalShowId = res?.data?.showID || 0;
      if (finalShowId > 0) {
        info(`  showId: ${finalShowId}`);
        break;
      }
      if (i < delays.length - 1) info(`  showId 仍为 0，重试中 (${i + 1}/${delays.length})...`);
    }
    if (!finalShowId || finalShowId <= 0) {
      warn('[Step 5] set_show_id 多次重试后仍返回 showId=0');
    }
  } else {
    info(`  showId: ${finalShowId} (从 SSE response 获取)`);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Step 6/6: 更新 AI 消息为完成状态 (PUT /api/project/msg)
  // ═══════════════════════════════════════════════════════════════════════════
  info('Step 6/6: 正在更新消息为完成状态...');
  if (aiMsgId) {
    await updateAiMsg(id, aiMsgId, {
      versionId, showId: finalShowId, fromMsgId: userMsgId, recordReference: parentVersionID,
      eventData: result.allEventData, requestId: result.finalRequestId,
      sessionId: result.finalSessionId, sessionStatus: result.finalSessionStatus,
    });
    info('  消息已更新');
  } else {
    warn('[Step 6] 无 AI 消息 ID，跳过消息更新');
  }

  console.log(`\n项目修改完成! ID: ${id}, versionId: ${versionId}, showId: ${finalShowId}`);
  return { projectId: id, versionId, showId: finalShowId };
}

/** 6. 项目属性更新 (名称/描述/logo 等) */
async function updateProject(opts) {
  const { id, name, background, referBackground, businessName, introduction,
    phoneNumber, businessHour, languageStyle, email, logo, notifyEmail } = opts;
  if (!id) die('--id (projectId) 是必须的');

  const params = { projectId: id };
  const fields = { name, background, referBackground, businessName, introduction,
    phoneNumber, businessHour, languageStyle, email, logo, notifyEmail };
  let hasUpdate = false;
  for (const [k, v] of Object.entries(fields)) {
    if (v !== undefined) { params[k] = v; hasUpdate = true; }
  }
  if (!hasUpdate) die('至少需要提供一个要更新的字段 (如 --name, --background, --logo 等)');

  info(`正在更新项目 ${id}...`);
  const res = await api('PUT', '/api/page_gen/project', params, id);
  if (!res) return;

  console.log('项目属性更新成功!');
  return res;
}

/** 7. 项目删除 */
async function deleteProject(projectId) {
  if (!projectId) die('--id (projectId) 是必须的');

  info(`正在删除项目 ${projectId}...`);
  const res = await api('DELETE', '/api/page_gen/project', { projectId }, projectId);
  if (!res) return;

  console.log('项目已删除。');
  return res;
}

/** 8. 项目预览 */
async function previewProject(projectId, versionId) {
  if (!projectId) die('--id (projectId) 是必须的');

  // 如果没有指定 versionId，从历史消息中提取最新的
  if (!versionId) {
    info('正在从历史消息中提取最新 versionId...');
    const msgRes = await api('POST', '/api/project/msg_list', {
      projectId,
      isTemplate: false,
      page: { pageNum: 1, pageSize: 50 },
    }, projectId);
    const messages = msgRes?.data?.projectMsgs || [];
    for (const msg of messages) {
      if (msg.role !== 0) continue;
      try {
        const content = JSON.parse(msg.content);
        if (Array.isArray(content.content)) {
          for (const item of content.content) {
            if (item.data?.projectVersionId && item.data.projectVersionId > 0) {
              versionId = item.data.projectVersionId;
            }
          }
        }
      } catch {}
    }
    if (versionId) {
      info(`  提取到 versionId: ${versionId}`);
    } else {
      die('未找到 versionId，请通过 --versionId 指定');
    }
  }

  // 通过 share 接口获取预览链接 (对齐前端实际行为)
  info('正在获取预览链接...');
  const shareRes = await api('GET', '/api/project/share', {
    projectId,
    versionId: Number(versionId),
  }, projectId);

  if (shareRes?.data?.url) {
    console.log(`\n预览链接: ${shareRes.data.url}`);
  } else {
    warn('未获取到预览链接');
  }

  return shareRes?.data;
}

/** 9. 验证 Resend API Key */
async function validateApiKey(projectId, apiKey) {
  if (!projectId) die('--id (projectId) 是必须的');
  if (!apiKey) die('--apiKey 是必须的');

  info('正在验证 API Key...');
  const res = await api('POST', '/api/brand_email/validate_api_key', { projectId, apiKey }, projectId);
  if (!res) return;

  console.log('API Key 验证通过!');
  return res.data;
}

/** 10. 获取品牌邮件配置 */
async function getBrandEmailConfig(projectId) {
  if (!projectId) die('--id (projectId) 是必须的');

  info('正在获取品牌邮件配置...');
  const res = await api('GET', `/api/brand_email/config/${projectId}`, null, projectId);
  if (!res) return;

  console.log('\n品牌邮件配置:');
  console.log(JSON.stringify(res.data, null, 2));
  return res.data;
}

/** 11. 配置管理 */
function configCommand(opts) {
  const cfg = loadConfig();
  let changed = false;

  if (opts.token) {
    cfg.token = opts.token;
    changed = true;
    info('token 已保存');
  }
  if (opts.host) {
    cfg.apiHost = opts.host;
    changed = true;
    info(`apiHost 已保存: ${opts.host}`);
  }
  if (changed) {
    saveConfig(cfg);
    console.log(`配置已写入: ${CONFIG_FILE}`);
  } else {
    console.log(`配置文件: ${CONFIG_FILE}`);
    console.log(`  token:   ${cfg.token ? cfg.token.slice(0, 20) + '...' : '(未设置)'}`);
    console.log(`  apiHost: ${cfg.apiHost || '(默认) https://gbh.readdy.ai'}`);
  }
}

// ─── CLI arg parser ─────────────────────────────────────────────────────────

function parseArgs(argv) {
  const args = argv.slice(2);
  const command = args[0];
  const opts = {};
  for (let i = 1; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      const next = args[i + 1];
      if (next && !next.startsWith('--')) {
        opts[key] = next;
        i++;
      } else {
        opts[key] = true;
      }
    }
  }
  return { command, opts };
}

function printUsage() {
  console.log(`
Readdy Website Builder CLI

用法: node readdy.mjs <command> [options]

Commands:
  list    [--page <n>] [--pageSize <n>]           列出所有项目
  info    --id <projectId>                         获取项目信息
  messages --id <projectId>                        获取项目历史消息
  create  --query <描述>                           新建网站 (完整流程)
          [--device web|mobile]
          [--framework <f>] [--lib <l>]
          [--category <c>]
  modify  --id <projectId> --query <修改需求>      修改网站 (AI 重新生成)
  update  --id <projectId> [--name <n>]            更新项目属性
          [--background <b>] [--logo <url>]
          [--businessName <bn>] [--email <e>]
  delete  --id <projectId>                         删除项目
  preview --id <projectId> [--versionId <v>]       预览项目
  validate-key --id <projectId> --apiKey <key>     验证 Resend API Key
  email-config --id <projectId>                    获取品牌邮件配置
  config  [--token <token>] [--host <url>]          配置认证信息

Config:
  配置文件: ~/.readdy/config.json
  支持字段: token (认证令牌), apiHost (API 基地址)
`);
}

// ─── main ───────────────────────────────────────────────────────────────────

async function main() {
  const { command, opts } = parseArgs(process.argv);

  switch (command) {
    case 'list':
      await listProjects(opts.page, opts.pageSize);
      break;
    case 'info':
      await getProjectInfo(opts.id);
      break;
    case 'messages':
      await getProjectMessages(opts.id, opts.page, opts.pageSize);
      break;
    case 'create':
      await createProject(opts);
      break;
    case 'modify':
      await modifyProject(opts);
      break;
    case 'update':
      await updateProject(opts);
      break;
    case 'delete':
      await deleteProject(opts.id);
      break;
    case 'preview':
      await previewProject(opts.id, opts.versionId);
      break;
    case 'validate-key':
      await validateApiKey(opts.id, opts.apiKey);
      break;
    case 'email-config':
      await getBrandEmailConfig(opts.id);
      break;
    case 'config':
      configCommand(opts);
      break;
    default:
      printUsage();
      if (command) die(`未知命令: ${command}`);
      break;
  }
}

main().catch(err => {
  console.error(`[FATAL] ${err.message}`);
  process.exit(1);
});