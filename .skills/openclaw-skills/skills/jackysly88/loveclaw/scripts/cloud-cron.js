/**
 * LoveClaw - 云端版定时任务
 * 匹配逻辑在本地（skill）计算，FC 只负责存取数据
 */

const path = require('path');
process.chdir(path.join(process.env.HOME || '/root', '.openclaw', 'workspace'));

const cloudData = require('./cloud-data');
const bazi = require('./bazi');

const MATCH_THRESHOLD = 70; // 双向匹配阈值

/**
 * 从独立的年月日时字段构造 bazi 对象
 * 兼容数据库中 bazi 字段为空的情况
 */
function buildBaziObject(profile) {
  // 如果 bazi 字段已存在且有效，直接返回
  if (profile.bazi && typeof profile.bazi === 'object' && profile.bazi.yearGan) {
    return profile.bazi;
  }
  // 否则从独立字段构造
  return {
    yearGan: profile.baziYearGan || profile.baziYear?.replace(profile.baziYearZhi || '', '') || '',
    yearZhi: profile.baziYearZhi || profile.baziYear?.slice(-1) || '',
    monthGan: profile.baziMonthGan || profile.baziMonth?.replace(profile.baziMonthZhi || '', '') || '',
    monthZhi: profile.baziMonthZhi || profile.baziMonth?.slice(-1) || '',
    dayGan: profile.baziDayGan || profile.baziDay?.replace(profile.baziDayZhi || '', '') || '',
    dayZhi: profile.baziDayZhi || profile.baziDay?.slice(-1) || '',
    hourGan: profile.baziHourGan || profile.baziHour?.replace(profile.baziHourZhi || '', '') || '',
    hourZhi: profile.baziHourZhi || profile.baziHour?.slice(-1) || '',
  };
}

/**
 * 检查用户是否有有效的八字数据
 */
function hasValidBazi(profile) {
  const b = buildBaziObject(profile);
  return b.yearGan && b.yearZhi && b.monthGan && b.monthZhi && b.dayGan && b.dayZhi && b.hourGan && b.hourZhi;
}

/**
 * 计算双向匹配分数（使用 match.js 的算法）
 */
function calculateMutualScore(baziA, baziB) {
  if (!baziA || !baziB) return { scoreAToB: 0, scoreBToA: 0, isMutual: false, mutualScore: 0 };
  const scoreAToB = bazi.calculateMatchScore(baziA, baziB);
  const scoreBToA = bazi.calculateMatchScore(baziB, baziA);
  const isMutual = scoreAToB >= MATCH_THRESHOLD && scoreBToA >= MATCH_THRESHOLD;
  const mutualScore = Math.min(scoreAToB, scoreBToA);
  return { scoreAToB, scoreBToA, isMutual, mutualScore };
}

/**
 * 执行每日匹配（基于 TableStore，云端计算）
 */
async function runDailyMatching() {
  console.log('[匹配任务] 开始执行...');

  const profiles = await cloudData.getAllProfiles();
  console.log(`[匹配任务] 当前用户数: ${profiles.length}`);

  const today = new Date(Date.now() + 8 * 3600 * 1000).toISOString().split('T')[0];
  const matchedSet = new Set();
  const results = [];

  for (const profile of profiles) {
    // 跳过已匹配的用户
    if (matchedSet.has(profile.userId)) continue;
    // 跳过今日已匹配的用户
    if (profile.todayMatchDone === '1' && profile.todayMatchDate === today) {
      matchedSet.add(profile.userId);
      continue;
    }
    // 跳过缺少关键信息的用户
    if (!hasValidBazi(profile) || !profile.city || !profile.gender || !profile.preferredGender) continue;

    // 查找最佳同城双向匹配
    const cands = profiles.filter(p => {
      if (matchedSet.has(p.userId)) return false;
      if (p.userId === profile.userId) return false;
      if (!hasValidBazi(p) || !p.city) return false;
      // 同城
      if (p.city !== profile.city) return false;
      // 双向喜欢
      if (p.gender !== profile.preferredGender) return false;
      if (p.preferredGender !== profile.gender) return false;
      return true;
    });

    if (!cands.length) continue;

    // 计算每个候选的匹配分数（从独立字段构造 bazi 对象）
    const profileBazi = buildBaziObject(profile);
    const scored = cands.map(c => {
      const score = calculateMutualScore(profileBazi, buildBaziObject(c));
      return { candidate: c, ...score };
    }).filter(s => s.isMutual);

    if (!scored.length) continue;

    // 取分数最高者
    scored.sort((a, b) => b.mutualScore - a.mutualScore);
    const best = scored[0];

    console.log(`[匹配任务] ${profile.name} ↔ ${best.candidate.name} (${best.mutualScore}分, ${profile.city})`);

    // 构建历史记录
    const uHist = Array.isArray(profile.matchedWithHistory) ? profile.matchedWithHistory : [];
    uHist.push({ userId: best.candidate.userId, date: today });
    const pHist = Array.isArray(best.candidate.matchedWithHistory) ? best.candidate.matchedWithHistory : [];
    pHist.push({ userId: profile.userId, date: today });

    // 保存双方匹配结果
    const [uSave, pSave] = await Promise.all([
      cloudData.saveMatch(profile.userId, best.candidate.userId, uHist),
      cloudData.saveMatch(best.candidate.userId, profile.userId, pHist),
    ]);

    if (uSave.success && pSave.success) {
      console.log(`[匹配任务] ✅ ${profile.name} 和 ${best.candidate.name} 匹配成功（${best.mutualScore}分）`);
      results.push({ user: profile.name, partner: best.candidate.name, score: best.mutualScore });
    } else {
      console.error(`[匹配任务] ❌ 保存失败: ${profile.userId}->${best.candidate.userId}`, uSave.error, pSave.error);
    }

    matchedSet.add(profile.userId);
    matchedSet.add(best.candidate.userId);
  }

  console.log(`[匹配任务] 完成，共 ${results.length} 对匹配`);
  return results;
}

/**
 * 发送通知 - 通过飞书 API 直接发送
 */
const FEISHU_APP_ID = 'cli_a919f24117389bc0';
const FEISHU_APP_SECRET = 'l64HJwZvSq8FzGggmfe14g8hdWjJBW3Q';
let feishuAccessToken = null;

async function getFeishuAccessToken() {
  if (feishuAccessToken) return feishuAccessToken;
  const resp = await fetch('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ app_id: FEISHU_APP_ID, app_secret: FEISHU_APP_SECRET }),
  });
  const data = await resp.json();
  if (data.code !== 0) throw new Error('Failed to get Feishu access token: ' + data.msg);
  feishuAccessToken = data.tenant_access_token;
  return feishuAccessToken;
}

async function notifyUser(channel, target, textOrOptions) {
  try {
    if (!channel || !target) return;
    
    const text = typeof textOrOptions === 'string' ? textOrOptions : textOrOptions.message || '';
    const mediaUrl = typeof textOrOptions === 'object' ? textOrOptions.media : null;
    
    switch (channel) {
      case 'feishu':
        await notifyFeishu(target, text, mediaUrl);
        break;
      case 'telegram':
        await notifyTelegram(target, text, mediaUrl);
        break;
      case 'whatsapp':
        await notifyWhatsApp(target, text, mediaUrl);
        break;
      default:
        console.log('[通知跳过] 不支持的 channel:', channel);
    }
  } catch(e) {
    console.error('[通知失败]', e.message);
  }
}

async function notifyFeishu(target, text, mediaUrl) {
  const token = await getFeishuAccessToken();
  if (mediaUrl) {
    // 发送图片消息
    const resp = await fetch('https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token,
      },
      body: JSON.stringify({
        receive_id: target,
        msg_type: 'image',
        content: JSON.stringify({ image_key: mediaUrl }),
      }),
    });
    const data = await resp.json();
    if (data.code !== 0 && data.code !== '0') {
      console.error('[飞书图片发送失败]', data.msg);
    }
    // 再发文字
    if (text) {
      await sendFeishuText(token, target, text);
    }
  } else {
    await sendFeishuText(token, target, text);
  }
}

async function sendFeishuText(token, target, text) {
  const resp = await fetch('https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token,
    },
    body: JSON.stringify({
      receive_id: target,
      msg_type: 'text',
      content: JSON.stringify({ text }),
    }),
  });
  const data = await resp.json();
  if (data.code !== 0 && data.code !== '0') {
    console.error('[飞书通知失败]', data.msg);
  }
}

async function notifyTelegram(target, text, mediaUrl) {
  const botToken = process.env.TELEGRAM_BOT_TOKEN;
  if (!botToken) {
    console.log('[Telegram通知跳过] 未配置 TELEGRAM_BOT_TOKEN');
    return;
  }
  
  if (mediaUrl) {
    // 发送图片
    await fetch(`https://api.telegram.org/bot${botToken}/sendPhoto`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: target,
        photo: mediaUrl,
        caption: text,
      }),
    });
  } else {
    await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: target,
        text: text,
      }),
    });
  }
}

async function notifyWhatsApp(target, text, mediaUrl) {
  const phoneId = process.env.WHATSAPP_PHONE_ID;
  const accessToken = process.env.WHATSAPP_ACCESS_TOKEN;
  if (!phoneId || !accessToken) {
    console.log('[WhatsApp通知跳过] 未配置 WHATSAPP_PHONE_ID 或 WHATSAPP_ACCESS_TOKEN');
    return;
  }
  
  const payload = {
    messaging_product: 'whatsapp',
    to: target,
    type: mediaUrl ? 'image' : 'text',
  };
  
  if (mediaUrl) {
    payload.image = { link: mediaUrl };
    if (text) payload.caption = text;
  } else {
    payload.text = { body: text };
  }
  
  await fetch(`https://graph.facebook.com/v18.0/${phoneId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
    },
    body: JSON.stringify(payload),
  });
}

/**
 * 生成晚8点报告
 */
async function runEveningReports() {
  console.log('[报告任务] 开始生成...');

  try {
    // 获取所有用户档案，检查 notifyEnabled 状态
    const allProfiles = await cloudData.getAllProfiles();
    const notifyEnabledUsers = new Set(
      allProfiles.filter(p => p.notifyEnabled === '1' || p.notifyEnabled === true)
        .map(p => p.userId || p.phone)
    );
    console.log(`[报告任务] 开启推送的用户数: ${notifyEnabledUsers.size}`);

    const data = await cloudData.apiRequest('/api/report');
    const matchedUsers = (data.matches || []).filter(m => !m.reported && notifyEnabledUsers.has(m.userId));
    const noMatchUsers = (data.noMatchUsers || []).filter(u => notifyEnabledUsers.has(u.userId));

    // 发送匹配成功报告
    for (const m of matchedUsers) {
      const target = m.notificationTarget || m.userId;
      if (!m.channel || !target) {
        console.log('[报告任务] 跳过（无通知目标）:', m.userId);
        continue;
      }

      // 先发送照片（如果有）
      if (m.partnerPhotoOssUrl) {
        await notifyUser(m.channel, target, { media: m.partnerPhotoOssUrl, message: '' });
        await new Promise(r => setTimeout(r, 500)); // 稍等一下让消息顺序正确
      }

      // 构建报告文本
      const report = `🌟 今日缘分报告\n\n` +
        `已为你找到缘分匹配！\n\n` +
        `📍 城市：${m.city || '未知'}\n` +
        `💕 对方姓名：${m.partnerName || '未知'}\n` +
        `📱 对方手机：${m.partnerPhone || '未知'}\n\n` +
        `快去联系ta吧！祝你们有美好的缘分 🍀`;

      await notifyUser(m.channel, target, report);
      console.log(`[报告任务] 已发送给 ${m.name}(${m.userId}) -> ${m.partnerName}`);
    }

    // 发送未匹配提示（仅发送给开启推送的用户）
    for (const u of noMatchUsers) {
      const target = u.notificationTarget || u.userId;
      if (!u.channel || !target) {
        console.log('[报告任务] 跳过（无通知目标）:', u.userId);
        continue;
      }

      const noMatchReport = `🌟 今日缘分报告\n\n` +
        `爱情龙虾今日未匹配成功～\n\n` +
        `🍀 命运的齿轮持续转动，期待明日月老的光临！\n\n` +
        `💡 用户无需重复报名即可享受每日自动匹配`;

      await notifyUser(u.channel, target, noMatchReport);
      console.log(`[报告任务] 未匹配提示已发送给 ${u.name}(${u.userId})`);
    }

    if (matchedUsers.length === 0 && noMatchUsers.length === 0) {
      console.log('[报告任务] 今日无需要推送的用户');
    } else {
      console.log(`[报告任务] 已发送 ${matchedUsers.length} 份匹配报告，${noMatchUsers.length} 份未匹配提示`);
    }
  } catch(e) {
    console.error('[报告任务] 失败:', e.message);
  }
}

// ========================
// CLI 入口
// ========================
const [, , command] = process.argv;

if (command === 'match') {
  runDailyMatching().then(() => process.exit(0)).catch(e => {
    console.error('[匹配任务异常]', e);
    process.exit(1);
  });
} else if (command === 'report') {
  runEveningReports().then(() => process.exit(0)).catch(e => {
    console.error('[报告任务异常]', e);
    process.exit(1);
  });
} else {
  console.log('用法: node cloud-cron.js [match|report]');
  process.exit(1);
}
