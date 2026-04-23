/**
 * 睡眠障碍脑波音频助手 - 意图处理器
 * 
 * 为睡眠障碍人群提供个性化脑波音频播放服务
 * 支持用户画像匹配、定时关闭等功能
 */

const fs = require('fs');
const path = require('path');

// 睡眠障碍类型枚举
const SLEEP_TYPES = ['入睡困难', '睡眠维持', '早醒', '昼夜节律', '焦虑失眠', '浅眠多梦', '深睡不足', '通用'];

// 严重程度枚举
const SEVERITIES = ['轻度', '中度', '重度'];

// 年龄组枚举
const AGE_GROUPS = ['青年', '中年', '老年'];

// 性别枚举
const GENDERS = ['男', '女'];

// 时长选项
const DURATIONS = [15, 20, 30];
const DEFAULT_DURATION = 15;

// 本地音频库路径
const AUDIO_LIBRARY_PATH = "C:\\Users\\龚文瀚\\Desktop\\SleepAudioDB";

// 用户画像文件路径
const USER_PROFILES_PATH = path.join(__dirname, 'user-profiles.json');

// 合规声明
const COMPLIANCE_NOTICE = '温馨提示：本音频为非药物健康辅助，不替代医疗诊断与治疗。';

// 音频清单缓存
let audioManifest = null;

/**
 * 加载用户画像
 */
function loadUserProfiles() {
  try {
    if (fs.existsSync(USER_PROFILES_PATH)) {
      const data = fs.readFileSync(USER_PROFILES_PATH, 'utf-8');
      return JSON.parse(data);
    }
  } catch (e) {
    console.error('Failed to load user profiles:', e);
  }
  return {};
}

/**
 * 保存用户画像
 */
function saveUserProfiles(profiles) {
  try {
    fs.writeFileSync(USER_PROFILES_PATH, JSON.stringify(profiles, null, 2), 'utf-8');
    return true;
  } catch (e) {
    console.error('Failed to save user profiles:', e);
    return false;
  }
}

/**
 * 加载音频清单
 */
async function loadManifest() {
  if (audioManifest) return audioManifest;
  
  try {
    const manifestPath = path.join(__dirname, '..', 'audio_library', 'manifest.json');
    const data = fs.readFileSync(manifestPath, 'utf-8');
    audioManifest = JSON.parse(data);
    return audioManifest;
  } catch (e) {
    console.error('Failed to load manifest:', e);
    return null;
  }
}

/**
 * 解析用户输入的信息
 */
function parseUserInput(text) {
  const result = {
    age: null,
    gender: null,
    sleep_type: null,
    severity: null
  };
  
  const lowerText = text.toLowerCase();
  
  // 解析年龄
  if (lowerText.includes('青年') || lowerText.match(/\d+/)) {
    const ageMatch = text.match(/(\d+)\s*[岁岁]/);
    if (ageMatch) {
      const age = parseInt(ageMatch[1]);
      if (age <= 40) result.age = '青年';
      else if (age <= 65) result.age = '中年';
      else result.age = '老年';
    }
  }
  if (lowerText.includes('中年') || lowerText.includes('老了') || lowerText.includes('老年')) {
    if (lowerText.includes('中年')) result.age = '中年';
    if (lowerText.includes('老年') || lowerText.includes('老了')) result.age = '老年';
  }
  
  // 解析性别
  if (lowerText.includes('男')) result.gender = '男';
  if (lowerText.includes('女')) result.gender = '女';
  
  // 解析睡眠问题类型
  if (lowerText.includes('入睡困难') || lowerText.includes('睡不着') || lowerText.includes('失眠') || lowerText.includes('入睡')) {
    result.sleep_type = '入睡困难';
  }
  if (lowerText.includes('易醒') || lowerText.includes('容易醒') || lowerText.includes('惊醒') || lowerText.includes('夜间醒来') || lowerText.includes('夜里醒')) {
    result.sleep_type = '睡眠维持';
  }
  if (lowerText.includes('深睡不足') || lowerText.includes('深睡不够') || lowerText.includes('睡眠浅')) {
    result.sleep_type = '深睡不足';
  }
  if (lowerText.includes('焦虑失眠') || lowerText.includes('焦虑') || lowerText.includes('睡前焦虑')) {
    result.sleep_type = '焦虑失眠';
  }
  if (lowerText.includes('早醒') || lowerText.includes('凌晨醒')) {
    result.sleep_type = '早醒';
  }
  if (lowerText.includes('昼夜节律') || lowerText.includes('作息') || lowerText.includes('倒时差')) {
    result.sleep_type = '昼夜节律';
  }
  if (lowerText.includes('浅眠') || lowerText.includes('多梦') || lowerText.includes('睡眠浅')) {
    result.sleep_type = '浅眠多梦';
  }
  if (lowerText.includes('午睡') || lowerText.includes('午休')) {
    result.sleep_type = '通用';
  }
  
  // 解析严重程度
  if (lowerText.includes('轻度') || lowerText.includes('轻度')) result.severity = '轻度';
  if (lowerText.includes('中度') || lowerText.includes('中等')) result.severity = '中度';
  if (lowerText.includes('重度') || lowerText.includes('严重')) result.severity = '重度';
  
  return result;
}

/**
 * 主入口：处理意图
 */
async function handleIntent({ user_id, intent_id, slots, context, message_text }) {
  // 加载音频清单
  await loadManifest();

  switch (intent_id) {
    case 'PLAY_BRAINWAVE_AUDIO':
      return await handlePlayAudio(user_id, slots, message_text);
    case 'SET_USER_PROFILE':
      return await handleSetProfile(user_id, slots, message_text);
    case 'QUERY_USER_PROFILE':
      return handleQueryProfile(user_id);
    case 'CONTROL_AUDIO':
      return await handleControlAudio(slots);
    case 'SET_AUDIO_TIMER':
      return await handleSetTimer(slots);
    case 'SWITCH_AUDIO':
      return await handleSwitchAudio(user_id, slots);
    case 'QUERY_SKILL_HELP':
      return handleHelp();
    case 'EXIT_SKILL':
      return handleExit();
    default:
      return { reply_text: '暂不支持该操作。' + COMPLIANCE_NOTICE };
  }
}

/**
 * 处理播放脑波音频
 */
async function handlePlayAudio(user_id, slots, message_text) {
  let { sleep_type, severity, duration, age, gender } = slots || {};
  
  // 获取用户画像
  const profiles = loadUserProfiles();
  const userProfile = profiles[user_id] || {};
  
  // 如果有消息文本，尝试解析其中的信息
  if (message_text) {
    const parsed = parseUserInput(message_text);
    sleep_type = sleep_type || parsed.sleep_type;
    severity = severity || parsed.severity;
    age = age || parsed.age;
    gender = gender || parsed.gender;
  }
  
  // 如果还没有信息，提示用户设置
  if (!sleep_type || !severity) {
    // 尝试从用户画像获取
    sleep_type = sleep_type || userProfile.sleep_type;
    severity = severity || userProfile.severity;
    age = age || userProfile.age;
    gender = gender || userProfile.gender;
  }
  
  // 如果还是没有完整信息，引导用户设置
  if (!sleep_type || !SEVERITIES.includes(severity || '')) {
    return {
      reply_text: '为了给您匹配合适的音频，请告诉我：\n' +
                  '1️⃣ 您的年龄（青年/中年/老年）\n' +
                  '2️⃣ 性别（男/女）\n' +
                  '3️⃣ 睡眠问题类型（入睡困难/易醒/深睡不足）\n' +
                  '4️⃣ 严重程度（轻度/中度/重度）\n\n' +
                  '例如："45岁，男，入睡困难，中度"' + COMPLIANCE_NOTICE,
      need_confirm: true,
      awaiting_profile: true
    };
  }

  // 匹配音频资源
  const audio = await matchAudio(sleep_type, severity, duration);
  
  if (!audio) {
    return {
      reply_text: '暂时无法找到合适音频，您可以尝试调整时长或更换睡眠类型。' + COMPLIANCE_NOTICE
    };
  }

  // 根据 source 决定返回本地路径还是线上 URL
  const isOnline = audioManifest.source === 'cos';
  const audioUrl = isOnline ? audio.url : audio.file_path;
  
  // 返回播放指令
  return {
    reply_text: `正在播放「${sleep_type}」脑波音频（${severity}），请收听～ 🎧\n\n` + COMPLIANCE_NOTICE,
    audio_file: audio.file_path,
    audio_url: audioUrl,
    audio_name: audio.filename,
    play_command: isOnline ? 'stream' : 'local',
    control_cmd: 'play',
    source: audioManifest.source,
    metadata: {
      sleep_type,
      severity,
      duration: duration || DEFAULT_DURATION,
      age,
      gender
    }
  };
}

/**
 * 处理设置用户信息
 */
async function handleSetProfile(user_id, slots, message_text) {
  const profiles = loadUserProfiles();
  const existingProfile = profiles[user_id] || {};
  
  let { age, gender, sleep_type, severity } = slots || {};
  
  // 如果有消息文本，尝试解析
  if (message_text) {
    const parsed = parseUserInput(message_text);
    age = age || parsed.age;
    gender = gender || parsed.gender;
    sleep_type = sleep_type || parsed.sleep_type;
    severity = severity || parsed.severity;
  }
  
  // 如果成功提取到信息，保存
  if (age || gender || sleep_type || severity) {
    profiles[user_id] = {
      ...existingProfile,
      age: age || existingProfile.age,
      gender: gender || existingProfile.gender,
      sleep_type: sleep_type || existingProfile.sleep_type,
      severity: severity || existingProfile.severity,
      updated_at: new Date().toISOString()
    };
    saveUserProfiles(profiles);
    
    // 构建确认话术
    let reply = '好的，已为您设置：';
    const parts = [];
    if (age) parts.push(`年龄：${age}`);
    if (gender) parts.push(`性别：${gender}`);
    if (sleep_type) parts.push(`睡眠问题：${sleep_type}`);
    if (severity) parts.push(`严重程度：${severity}`);
    
    reply += parts.join('，') + '。\n\n以后您说"播放睡眠音频"，我会自动为您匹配合适的音频。';
    
    return {
      reply_text: reply + '\n\n' + COMPLIANCE_NOTICE,
      user_profile: profiles[user_id]
    };
  }
  
  // 没有提取到信息，提示用户
  return {
    reply_text: '请告诉我您的信息，例如："45岁，男，入睡困难，中度"' + COMPLIANCE_NOTICE,
    need_confirm: true
  };
}

/**
 * 处理查询用户信息
 */
function handleQueryProfile(user_id) {
  const profiles = loadUserProfiles();
  const profile = profiles[user_id];
  
  if (!profile || !profile.sleep_type) {
    return {
      reply_text: '您还未设置个人信息。请告诉我您的年龄、性别、睡眠问题类型和严重程度。' + COMPLIANCE_NOTICE
    };
  }

  const reply = `您的信息：
• 年龄：${profile.age || '未设置'}
• 性别：${profile.gender || '未设置'}
• 睡眠问题：${profile.sleep_type || '未设置'}
• 严重程度：${profile.severity || '未设置'}`;

  return {
    reply_text: reply + '\n\n' + COMPLIANCE_NOTICE
  };
}

/**
 * 处理音频控制
 */
async function handleControlAudio(slots) {
  const { action } = slots || {};
  
  let control_cmd = 'play';
  let reply_text = '';

  switch (action) {
    case 'pause':
      control_cmd = 'pause';
      reply_text = '已暂停播放。' + COMPLIANCE_NOTICE;
      break;
    case 'resume':
    case 'continue':
      control_cmd = 'resume';
      reply_text = '已继续播放。' + COMPLIANCE_NOTICE;
      break;
    case 'stop':
      control_cmd = 'stop';
      reply_text = '已停止播放。' + COMPLIANCE_NOTICE;
      break;
    default:
      return { reply_text: '暂不支持该操作。' + COMPLIANCE_NOTICE };
  }

  return { reply_text, control_cmd };
}

/**
 * 处理定时关闭
 */
async function handleSetTimer(slots) {
  const { duration } = slots || {};

  if (!duration || !DURATIONS.includes(duration)) {
    return { 
      reply_text: `好的，我将为您设置${duration || DEFAULT_DURATION}分钟后自动停止播放。` + COMPLIANCE_NOTICE,
      timer: { duration_minutes: duration || DEFAULT_DURATION, action: 'stop' }
    };
  }

  return {
    reply_text: `好的，${duration}分钟后将自动为您关闭音频。`,
    timer: { duration_minutes: duration, action: 'stop' }
  };
}

/**
 * 处理切换音频
 */
async function handleSwitchAudio(user_id, slots) {
  return await handlePlayAudio(user_id, slots, null);
}

/**
 * 处理帮助查询
 */
function handleHelp() {
  return {
    reply_text: `您可以对我说：
• 播放睡眠音频 - 开始播放脑波音频
• 设置我的信息 - 告诉我您的年龄、性别、睡眠问题等
• 查看我的信息 - 查看当前设置
• 定时X分钟关闭 - 设置播放时长
• 换一个音频 - 切换其他音频

首次使用请告诉我您的年龄、性别、睡眠问题类型和严重程度，我会为您匹配合适的音频。
${COMPLIANCE_NOTICE}`
  };
}

/**
 * 处理退出技能
 */
function handleExit() {
  return {
    reply_text: '好的，已退出睡眠脑波音频助手。如有需要随时呼唤我。',
    control_cmd: 'stop',
    exit_skill: true
  };
}

/**
 * 匹配音频资源
 */
async function matchAudio(sleep_type, severity, duration) {
  if (!audioManifest || !audioManifest.audio_files) {
    return null;
  }

  const files = audioManifest.audio_files;
  
  // 精确匹配：睡眠类型 + 严重程度
  let matched = files.filter(f => {
    return f.sleep_type === sleep_type && f.severity === severity;
  });

  // 如果没有精确匹配，尝试只匹配睡眠类型
  if (matched.length === 0) {
    matched = files.filter(f => {
      return f.sleep_type === sleep_type;
    });
  }

  // 如果还是没有，返回通用类型
  if (matched.length === 0) {
    matched = files.filter(f => {
      return f.sleep_type === '通用';
    });
  }

  return matched.length > 0 ? matched[0] : null;
}

module.exports = {
  handleIntent,
  SLEEP_TYPES,
  SEVERITIES,
  AGE_GROUPS,
  GENDERS,
  DURATIONS,
  COMPLIANCE_NOTICE,
  AUDIO_LIBRARY_PATH,
  loadUserProfiles,
  parseUserInput
};
