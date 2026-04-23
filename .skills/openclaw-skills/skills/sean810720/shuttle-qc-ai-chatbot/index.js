#!/usr/bin/env node

/**
 * Shuttle QC AI Chatbot Skill
 * 自動化操作瀏覽器與 AI 客服對話
 */

const { program } = require('commander');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

program
  .name('shuttle-qc-ai-chatbot')
  .description('Shuttle QC AI Chatbot 自動化查詢工具')
  .version('1.0.1');

// 單次查詢
program
  .command('query')
  .description('執行單次查詢')
  .argument('<text>', '查詢文字')
  .option('--url <url>', '目標網頁 URL', 'http://192.168.100.98:8888/v1')
  .option('--timeout <seconds>', '等待回應超時秒數', '30')
  .option('--output <format>', '輸出格式: json 或 text', 'json')
  .action(async (text, options) => {
    try {
      const result = await runQuery(text, options);
      outputResult(result, options.output);
    } catch (error) {
      console.error('❌ 執行失敗:', error.message);
      process.exit(1);
    }
  });

// 批次查詢
program
  .command('batch')
  .description('批次執行查詢')
  .argument('<file>', '查詢列表檔案（每行一筆）')
  .option('--url <url>', '目標網頁 URL', 'http://192.168.100.98:8888/v1')
  .option('--timeout <seconds>', '等待回應超時秒數', '30')
  .option('--output <format>', '輸出格式: json 或 text', 'json')
  .action(async (file, options) => {
    try {
      const queries = readQueries(file);
      const results = [];

      for (const query of queries) {
        console.log(`🔍 執行查詢: ${query}`);
        const result = await runQuery(query, options);
        results.push(result);

        // 批次時簡單分隔
        if (options.output === 'text') {
          console.log('\n' + '='.repeat(50) + '\n');
        }
      }

      if (options.output === 'json') {
        console.log(JSON.stringify(results, null, 2));
      }
    } catch (error) {
      console.error('❌ 批次執行失敗:', error.message);
      process.exit(1);
    }
  });

/**
 * 執行單次查詢
 */
async function runQuery(query, options) {
  const startTime = Date.now();
  let targetId = null;

  try {
    // 1. 啟動瀏覽器
    console.log('🚀 啟動瀏覽器...');
    await execPromise('openclaw browser start --profile openclaw');
    // 取得 targetId
    const statusOutput = await execPromise('openclaw browser status --profile openclaw --json');
    console.log('   [DEBUG] status stdout:', statusOutput.stdout.substring(0, 200));
    const status = JSON.parse(statusOutput.stdout);
    targetId = status.activeTab?.id || '0';

    // 2. 導航到頁面
    console.log(`📍 導航到 ${options.url}...`);
    await execPromise(`openclaw browser navigate --profile openclaw "${options.url}"`);

    // 3. 輸入查詢文字（動態查找輸入框）
    console.log(`✍️  輸入查詢: "${query}"...`);
    await typeQuery(query);

    // 4. 等待回應
    console.log('⏳ 等待 AI 回應...');
    const response = await waitForResponse(parseInt(options.timeout) * 1000);

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

    return {
      query,
      response,
      url: options.url,
      elapsed: `${elapsed}s`,
      timestamp: new Date().toISOString()
    };
  } finally {
    // 5. 關閉瀏覽器
    if (targetId) {
      console.log('🛑 關閉瀏覽器...');
      await execPromise('openclaw browser stop --profile openclaw').catch(() => {});
    }
  }
}

/**
 * 輸入查詢文字（使用 evaluate 直接操作 DOM）
 */
async function typeQuery(text) {
  // 使用 evaluate 找到 textbox 並輸入
  const script = `
    (function() {
      const placeholder = "Send a message...";
      // 尋找輸入框
      const inputs = document.querySelectorAll('input[type="text"], textarea, [contenteditable]');
      let input = null;
      for (const el of inputs) {
        if (el.placeholder && el.placeholder.includes('Send a message') ||
            el.getAttribute('aria-label')?.includes('message') ||
            el.getAttribute('data-testid')?.includes('message')) {
          input = el;
          break;
        }
      }
      // fallback: 第一個看起来像輸入框的元素
      if (!input && inputs.length > 0) input = inputs[0];
      
      if (!input) {
        return { found: false, error: 'No input found' };
      }
      
      input.focus();
      // 輸入文字
      if (input.tagName === 'INPUT' || input.tagName === 'TEXTAREA') {
        input.value = ${JSON.stringify(text)};
        input.dispatchEvent(new Event('input', { bubbles: true }));
      } else if (input.isContentEditable) {
        input.textContent = ${JSON.stringify(text)};
        input.dispatchEvent(new Event('input', { bubbles: true }));
      }
      return { found: true, tag: input.tagName };
    })()
  `;
  
  const { stdout } = await execPromise(`openclaw browser evaluate --profile openclaw --fn '${escapeSingleQuotes(script)}'`);
  console.log('   [DEBUG] evaluate result:', stdout);
  
  // 送出（Enter）
  await execPromise('openclaw browser press --profile openclaw Enter');
}

/**
 * 轉義單引號供 shell 使用
 */
function escapeSingleQuotes(str) {
  return str.replace(/'/g, "'\"'\"'");
}

/**
 * 從快照中找到輸入框的 ref
 */
function findTextboxRef(snapshot) {
  // 列出所有 role 幫助除錯
  function listRoles(nodes, depth = 0) {
    if (!nodes) return;
    const nodeList = Array.isArray(nodes) ? nodes : [nodes];
    for (const node of nodeList) {
      console.log('   '.repeat(depth) + `- role:${node.role}, ref:${node.ref}, placeholder:${node.placeholder}`);
      if (node.children) listRoles(node.children, depth + 1);
    }
  }
  console.log('📋 Snapshot roles:');
  listRoles(snapshot);

  // 遞迴搜尋尋找 textbox，placeholder 為 "Send a message..."
  function search(nodes) {
    if (!nodes) return null;
    const nodeList = Array.isArray(nodes) ? nodes : [nodes];
    for (const node of nodeList) {
      if (node.role === 'textbox' && node.placeholder && node.placeholder.includes('Send a message')) {
        return node.ref;
      }
      if (node.children) {
        const found = search(node.children);
        if (found) return found;
      }
    }
    return null;
  }
  
  const ref = search(snapshot);
  if (ref) return ref;
  
  // fallback: 嘗試找出任何 textbox
  function findAnyTextbox(nodes) {
    if (!nodes) return null;
    const nodeList = Array.isArray(nodes) ? nodes : [nodes];
    for (const node of nodeList) {
      if (node.role === 'textbox') return node.ref;
      if (node.children) {
        const found = findAnyTextbox(node.children);
        if (found) return found;
      }
    }
    return null;
  }
  
  return findAnyTextbox(snapshot);
}

/**
 * 等待 AI 回應
 */
async function waitForResponse(timeoutMs) {
  const start = Date.now();
  const checkInterval = 2000; // 每 2 秒檢查一次

  // 記錄初始頁面狀態的文字內容
  let initialText = '';
  try {
    const initialSnapshot = await getSnapshot();
    initialText = extractAllText(initialSnapshot);
  } catch (e) {
    console.log('⚠️  無法獲取初始狀態');
  }

  while (Date.now() - start < timeoutMs) {
    try {
      const snapshot = await getSnapshot();
      const currentText = extractAllText(snapshot);

      // 檢查是否有新文字出現（排除固定的 UI 文字）
      const newContent = currentText.replace(initialText, '').trim();
      if (newContent && newContent.length > 20) { // 至少 20 字才視為有效回應
        console.log(`✅ 收到回應 (${newContent.length} 字元)`);
        return newContent;
      }

      console.log(`⏳ 等待中... (${Math.round((Date.now() - start) / 1000)}s)`);
    } catch (e) {
      // 忽略錯誤，繼續等待
    }

    await sleep(checkInterval);
  }

  throw new Error(`等待回應超時（${timeoutMs / 1000}秒）`);
}

/**
 * 取得頁面 snapshot
 */
async function getSnapshot() {
  const { stdout } = await execPromise('openclaw browser snapshot --profile openclaw --json --limit 200');
  const data = JSON.parse(stdout);
  console.log('   [DEBUG] refs map:', JSON.stringify(data.refs, null, 2));
  console.log('   [DEBUG] Full snapshot tree (first 2000 chars):\n' + data.snapshot.substring(0, 2000));
  // data.snapshot 是 text tree，需要解析成結構化物件
  const tree = parseSnapshotTree(data.snapshot, data.refs);
  
  // 將 refs map 裡的 ref 分配到對應 role 的節點
  assignRefsFromMap(tree, data.refs);
  
  return tree;
}

/**
 * 從 refs map 分配 ref 給沒有 ref 的節點
 */
function assignRefsFromMap(tree, refsMap) {
  // 收集所有需要 ref 的節點 (按 role)
  const needed = {};
  function collect(nodes) {
    if (!nodes) return;
    for (const node of Array.isArray(nodes) ? nodes : [nodes]) {
      if (!node.ref && node.role) {
        if (!needed[node.role]) needed[node.role] = [];
        needed[node.role].push(node);
      }
      if (node.children) collect(node.children);
    }
  }
  collect(tree);

  // 為每個 role 分配 refs map 中對應的 ref
  for (const [role, nodesNeedingRef] of Object.entries(needed)) {
    // 找出 refsMap 中這個 role 的所有 ref (未使用)
    const availableRefs = Object.entries(refsMap)
      .filter(([ref, info]) => info.role === role)
      .map(([ref]) => ref);
    
    // 分配給需要 ref 的節點
    for (let i = 0; i < nodesNeedingRef.length && i < availableRefs.length; i++) {
      nodesNeedingRef[i].ref = availableRefs[i];
    }
  }
}

/**
 * 解析 snapshot tree 文字成物件結構
 * 輸入格式示例：
 * "- generic [active]:
 *   - generic [ref=e1] [cursor=pointer]:"
 */
function parseSnapshotTree(treeStr, refsMap) {
  const lines = treeStr.split('\n');
  const root = [];
  const stack = [{ children: root, level: -2 }]; // 虛擬根節點

  for (let line of lines) {
    if (!line.trim()) continue;

    // 計算縮排級別 (2 spaces per level)
    const indent = line.length - line.trimStart().length;
    const level = Math.floor(indent / 2);

    // 移除縮排
    let trimmed = line.trim();

    // 必須以 '-' 開頭
    if (!trimmed.startsWith('-')) continue;
    trimmed = trimmed.substring(1).trim();

    // 提取 role（第一個 token）
    const roleMatch = trimmed.match(/^(\S+)/);
    const role = roleMatch ? roleMatch[1] : 'generic';

    // 提取 ref（如果有）
    const refMatch = trimmed.match(/\[ref=([^\]]+)\]/);
    const ref = refMatch ? refMatch[1] : null;

    // 提取引號內的文字（placeholder 或 text）
    const textMatch = trimmed.match(/"([^"]*)"/);
    const placeholder = (role === 'textbox' && textMatch) ? textMatch[1] : null;
    const text = (role !== 'textbox' && textMatch) ? textMatch[1] : null;

    // 創建節點
    const node = {
      ref,
      role,
      text,
      placeholder,
      children: []
    };

    // 根據級別放入stack
    while (stack.length > 0 && stack[stack.length - 1].level >= level) {
      stack.pop();
    }
    stack[stack.length - 1].children.push(node);
    stack.push({ children: node.children, level });
  }

  return root;
}

/**
 * 從 snapshot 提取所有文字內容
 */
function extractAllText(snapshot) {
  const texts = [];
  
  function traverse(obj) {
    if (typeof obj === 'string') {
      texts.push(obj);
    } else if (Array.isArray(obj)) {
      obj.forEach(traverse);
    } else if (typeof obj === 'object' && obj !== null) {
      if (obj.text) texts.push(obj.text);
      if (obj.label) texts.push(obj.label);
      if (obj.placeholder) texts.push(obj.placeholder);
      if (obj.value) texts.push(obj.value);
      Object.values(obj).forEach(traverse);
    }
  }
  
  traverse(snapshot);
  return texts.join('\n');
}

/**
 * 讀取批次查詢檔案
 */
function readQueries(filePath) {
  const fullPath = path.resolve(filePath);
  const content = fs.readFileSync(fullPath, 'utf-8');
  return content
    .split('\n')
    .map(line => line.trim())
    .filter(line => line && !line.startsWith('#'));
}

/**
 * 輸出結果
 */
function outputResult(result, format) {
  if (format === 'json') {
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log(`🔍 查詢：${result.query}`);
    console.log(`⏱️  耗時：${result.elapsed}`);
    console.log(`📅 時間：${result.timestamp}`);
    console.log('\n📋 回應內容：');
    console.log(result.response);
  }
}

/**
 * 睡眠函數
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 轉義雙引號 for shell command
 */
function escapeQuotes(str) {
  return str.replace(/"/g, '\\"');
}

// 執行 CLI
program.parse();
