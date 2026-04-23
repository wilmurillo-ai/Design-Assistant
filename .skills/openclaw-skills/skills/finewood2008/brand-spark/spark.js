/**
 * 火花 (Spark) - AI 品牌内容创作 Skill
 * 
 * 统一入口：覆盖图文、海报等全工作台
 * 核心能力：对话式采集 + workspace 资料感知 + 18 平台 + 全参数控制
 * 
 * 注意：Skill 行为主要由 SKILL.md 驱动（Agent 按指引执行对话和 API 调用）
 *       本文件提供 programmatic 调用能力，适用于自动化场景
 */

const fs = require('fs');
const path = require('path');

// ── 配置 ──
const configPath = path.join(__dirname, 'config.json');
let config = { apiKey: '', apiUrl: '' };
if (fs.existsSync(configPath)) {
  config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
}

// ── 平台映射 ──
const PLATFORMS = {
  // 国内
  wechat: '微信公众号', weibo: '微博', xiaohongshu: '小红书', douyin: '抖音',
  zhihu: '知乎', bilibili: 'B站', toutiao: '今日头条', baidu: '百家号', kuaishou: '快手',
  // 海外
  twitter: 'X/Twitter', linkedin: 'LinkedIn', instagram: 'Instagram', facebook: 'Facebook',
  threads: 'Threads', tiktok: 'TikTok', youtube: 'YouTube', medium: 'Medium', reddit: 'Reddit',
};

// ── 平台关键词 → ID ──
const PLATFORM_KEYWORDS = {
  '公众号': 'wechat', '微信': 'wechat', '微博': 'weibo',
  '小红书': 'xiaohongshu', '种草': 'xiaohongshu',
  '抖音': 'douyin', '口播': 'douyin',
  '知乎': 'zhihu', '专栏': 'zhihu',
  'b站': 'bilibili', '哔哩哔哩': 'bilibili',
  '头条': 'toutiao', '今日头条': 'toutiao',
  '百家号': 'baidu', '百度': 'baidu',
  '快手': 'kuaishou',
  'twitter': 'twitter', 'x': 'twitter', '推特': 'twitter',
  'linkedin': 'linkedin', '领英': 'linkedin',
  'instagram': 'instagram', 'ins': 'instagram',
  'facebook': 'facebook', '脸书': 'facebook',
  'threads': 'threads',
  'tiktok': 'tiktok',
  'youtube': 'youtube', '油管': 'youtube',
  'medium': 'medium',
  'reddit': 'reddit',
};

// ── 写作风格 ──
const WRITING_STYLES = {
  professional: '专业严谨', casual: '轻松口语', literary: '文艺抒情',
  humorous: '幽默风趣', provocative: '犀利锐评', storytelling: '故事叙事',
};

// ── 场景推断 ──
function inferParams(topic, platform) {
  const t = (topic || '').toLowerCase();
  const params = {
    writing_style: 'professional', content_depth: 'detailed',
    emotional_tone: 'positive', humanizer_enabled: true,
    humanizer_strength: 'medium', auto_image_enabled: true,
    image_style: 'commercial', image_quality: 'standard',
  };

  if (/融资|上市|合作|签约/.test(t)) {
    Object.assign(params, { writing_style: 'professional', content_depth: 'detailed', emotional_tone: 'positive', cta_style: 'soft', word_count_target: 2000 });
  } else if (/种草|安利|推荐|测评/.test(t)) {
    Object.assign(params, { writing_style: 'casual', content_depth: 'overview', emotional_tone: 'empathetic', humanizer_strength: 'high', word_count_target: 800 });
  } else if (/分析|报告|研究|趋势/.test(t)) {
    Object.assign(params, { writing_style: 'professional', content_depth: 'expert', emotional_tone: 'neutral', word_count_target: 2500 });
  } else if (/促销|限时|活动|优惠/.test(t)) {
    Object.assign(params, { writing_style: 'provocative', content_depth: 'overview', emotional_tone: 'urgent', cta_style: 'conversion', word_count_target: 1000 });
  } else if (/故事|创业|历程|品牌故事/.test(t)) {
    Object.assign(params, { writing_style: 'storytelling', content_depth: 'detailed', emotional_tone: 'inspiring', word_count_target: 1500 });
  }

  return params;
}

// ── 核心提交函数 ──
async function createSession({ topic, platform, tones, adapt_platforms, context, generation_params }) {
  if (!config.apiKey) {
    throw new Error('未配置 API Key，请在 config.json 中填入 apiKey，或访问 https://spark.babelink.ai 获取');
  }

  const body = {
    topic,
    platform: platform || 'wechat',
    tones: tones || ['professional'],
    adapt_platforms: adapt_platforms || [platform || 'wechat'],
    source: 'openclaw',
    context: context || {},
    generation_params: generation_params || inferParams(topic, platform),
  };

  const response = await fetch(config.apiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': config.apiKey,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`提交失败 (${response.status}): ${error}`);
  }

  return await response.json();
}

// ── 简易对话式运行（向后兼容） ──
async function run({ say, ask, topic, tones, platform }) {
  if (!config.apiKey) {
    await say('⚠️ 请先配置 API Key\n\n访问 https://spark.babelink.ai 注册后在个人中心生成');
    return;
  }

  if (!topic) {
    const response = await ask('📝 你想创作什么内容？（主题/灵感/链接都可以）');
    topic = response.trim();
  }

  if (!platform) {
    const response = await ask('📱 发到哪个平台？（如：公众号/小红书/Twitter，或输入"全平台"）');
    const input = response.trim().toLowerCase();
    platform = PLATFORM_KEYWORDS[input] || 'wechat';
  }

  tones = tones || ['professional'];

  await say('🔥 正在提交到火花平台...');

  const data = await createSession({ topic, platform, tones });
  const dashboardUrl = data.dashboardUrl || `https://spark.babelink.ai/article/${data.sessionId}`;
  const platformLabel = PLATFORMS[data.platform] || data.platform;

  let msg = `✅ 已提交！\n📱 平台：${platformLabel}`;
  if (data.adapt_platforms && data.adapt_platforms.length > 1) {
    const others = data.adapt_platforms.filter(p => p !== data.platform).map(p => PLATFORMS[p] || p).join('、');
    msg += `\n📤 适配：${others}`;
  }
  msg += `\n🔗 查看编辑：${dashboardUrl}`;

  await say(msg);
}

module.exports = { run, createSession, inferParams, PLATFORMS, PLATFORM_KEYWORDS };
