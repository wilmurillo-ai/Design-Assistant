/**
 * Auto Update Checker - 按需更新检查器
 * 
 * 核心逻辑：
 * 1. 在 skill 被触发时检查更新
 * 2. 根据版本变化分级处理
 * 3. 缓存结果避免频繁请求
 * 
 * 安全说明：
 * - 只读取本地文件，不执行外部命令
 * - 使用 OpenClaw 标准 API
 * - 无网络请求（依赖 clawhub CLI 的输出）
 */

const fs = require('fs');
const path = require('path');

const CACHE_DIR = path.join(process.env.HOME, '.openclaw', 'skill-update-cache');
const LOG_PATH = path.join(process.env.HOME, '.openclaw', 'logs', 'auto-update-skill.log');
const CONFIG_PATH = path.join(process.env.HOME, '.openclaw', 'auto-update-skill.json');
const SKILL_REGISTRY_PATH = path.join(process.env.HOME, '.openclaw', 'skills', '.registry.json');

// 默认配置
const DEFAULT_CONFIG = {
  mode: 'interactive',
  cacheDuration: 24 * 60 * 60 * 1000, // 24小时
  autoUpgrade: {
    patch: true,
    minor: false,
    major: false
  },
  remindInterval: 7 * 24 * 60 * 60 * 1000, // 7天
  blacklist: [],
  quietHours: {
    start: '22:00',
    end: '08:00'
  }
};

// 日志
function log(level, message) {
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
  const line = `[${timestamp}] ${level}: ${message}`;
  
  // 控制台输出（根据级别）
  if (level === 'ERROR') console.error(line);
  else if (level === 'WARN') console.warn(line);
  else console.log(line);
  
  // 写入日志
  try {
    const logDir = path.dirname(LOG_PATH);
    if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });
    fs.appendFileSync(LOG_PATH, line + '\n');
  } catch (e) {}
}

// 加载配置
function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      const userConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
      return { ...DEFAULT_CONFIG, ...userConfig };
    }
  } catch (e) {
    log('WARN', `加载配置失败: ${e.message}`);
  }
  return DEFAULT_CONFIG;
}

// 保存配置
function saveConfig(config) {
  try {
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  } catch (e) {
    log('ERROR', `保存配置失败: ${e.message}`);
  }
}

// 解析版本
function parseVersion(version) {
  const parts = version.split('.').map(Number);
  return {
    major: parts[0] || 0,
    minor: parts[1] || 0,
    patch: parts[2] || 0,
    raw: version
  };
}

// 比较版本
function compareVersion(v1, v2) {
  const a = parseVersion(v1);
  const b = parseVersion(v2);
  
  if (a.major !== b.major) return a.major > b.major ? 1 : -1;
  if (a.minor !== b.minor) return a.minor > b.minor ? 1 : -1;
  if (a.patch !== b.patch) return a.patch > b.patch ? 1 : -1;
  return 0;
}

// 获取更新类型
function getUpdateType(current, latest) {
  const c = parseVersion(current);
  const l = parseVersion(latest);
  
  if (l.major > c.major) return 'major';
  if (l.minor > c.minor) return 'minor';
  if (l.patch > c.patch) return 'patch';
  return 'none';
}

// 获取已安装 skill 列表（从本地目录读取）
function getInstalledSkills() {
  const skills = [];
  const skillsDir = path.join(process.env.HOME, '.openclaw', 'skills');
  
  try {
    if (!fs.existsSync(skillsDir)) return skills;
    
    const entries = fs.readdirSync(skillsDir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isDirectory() && !entry.name.startsWith('.')) {
        const skillPath = path.join(skillsDir, entry.name);
        const skillMdPath = path.join(skillPath, 'SKILL.md');
        
        if (fs.existsSync(skillMdPath)) {
          // 尝试从目录中的版本文件读取版本
          const versionPath = path.join(skillPath, '.version');
          let version = '0.0.0';
          
          if (fs.existsSync(versionPath)) {
            version = fs.readFileSync(versionPath, 'utf8').trim();
          }
          
          skills.push({
            name: entry.name,
            version: version,
            path: skillPath
          });
        }
      }
    }
  } catch (e) {
    log('ERROR', `读取 skill 目录失败: ${e.message}`);
  }
  
  return skills;
}

// 获取 skill 当前版本（从本地读取）
function getCurrentVersion(skillName) {
  try {
    const versionPath = path.join(process.env.HOME, '.openclaw', 'skills', skillName, '.version');
    if (fs.existsSync(versionPath)) {
      return fs.readFileSync(versionPath, 'utf8').trim();
    }
    
    // 尝试从 SKILL.md 解析版本
    const skillMdPath = path.join(process.env.HOME, '.openclaw', 'skills', skillName, 'SKILL.md');
    if (fs.existsSync(skillMdPath)) {
      const content = fs.readFileSync(skillMdPath, 'utf8');
      const versionMatch = content.match(/version[:\s]+(\d+\.\d+\.\d+)/i);
      if (versionMatch) return versionMatch[1];
    }
  } catch (e) {
    log('ERROR', `获取 ${skillName} 当前版本失败: ${e.message}`);
  }
  return null;
}

// 获取 skill 最新版本（从缓存或提示用户查询）
function getLatestVersion(skillName) {
  // 首先检查缓存
  const cached = getCachedVersion(skillName);
  if (cached && cached.version) {
    return cached.version;
  }
  
  // 如果没有缓存，返回 null（需要外部查询 clawhub）
  return null;
}

// 缓存相关
function getCachePath(skillName) {
  if (!fs.existsSync(CACHE_DIR)) {
    fs.mkdirSync(CACHE_DIR, { recursive: true });
  }
  return path.join(CACHE_DIR, `${skillName}.json`);
}

function getCachedVersion(skillName) {
  try {
    const cachePath = getCachePath(skillName);
    if (!fs.existsSync(cachePath)) return null;
    
    const cache = JSON.parse(fs.readFileSync(cachePath, 'utf8'));
    const config = loadConfig();
    
    // 检查缓存是否过期
    if (Date.now() - cache.timestamp > config.cacheDuration) {
      return null;
    }
    
    return cache;
  } catch (e) {
    return null;
  }
}

function setCachedVersion(skillName, version, skipped = false) {
  try {
    const cachePath = getCachePath(skillName);
    const cache = {
      skillName,
      version,
      timestamp: Date.now(),
      skipped,
      skippedAt: skipped ? Date.now() : null
    };
    fs.writeFileSync(cachePath, JSON.stringify(cache, null, 2));
  } catch (e) {
    log('WARN', `缓存写入失败: ${e.message}`);
  }
}

// 检查是否在安静时段
function isQuietHours(config) {
  const now = new Date();
  const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
  
  const { start, end } = config.quietHours;
  
  if (start < end) {
    return currentTime >= start && currentTime <= end;
  } else {
    // 跨天的情况（如 22:00 - 08:00）
    return currentTime >= start || currentTime <= end;
  }
}

// 检查是否应该提醒（跳过间隔）
function shouldRemind(skillName, config) {
  try {
    const cachePath = getCachePath(skillName);
    if (!fs.existsSync(cachePath)) return true;
    
    const cache = JSON.parse(fs.readFileSync(cachePath, 'utf8'));
    
    // 如果用户跳过了，检查是否过了 remindInterval
    if (cache.skipped && cache.skippedAt) {
      return Date.now() - cache.skippedAt > config.remindInterval;
    }
    
    return true;
  } catch (e) {
    return true;
  }
}

// 备份 skill
function backupSkill(skillName, version) {
  try {
    const backupDir = path.join(process.env.HOME, '.openclaw', 'skill-backups');
    const skillPath = path.join(process.env.HOME, '.openclaw', 'skills', skillName);
    const backupPath = path.join(backupDir, `${skillName}@${version}`);
    
    if (!fs.existsSync(backupDir)) {
      fs.mkdirSync(backupDir, { recursive: true });
    }
    
    if (fs.existsSync(skillPath)) {
      // 复制 skill 目录到备份
      copyDir(skillPath, backupPath);
      log('INFO', `备份 ${skillName}@${version} 成功`);
      return true;
    }
  } catch (e) {
    log('ERROR', `备份 ${skillName} 失败: ${e.message}`);
  }
  return false;
}

// 复制目录（递归）
function copyDir(src, dest) {
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }
  
  const entries = fs.readdirSync(src, { withFileTypes: true });
  
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

// 验证 skill
function verifySkill(skillName) {
  try {
    const skillPath = path.join(process.env.HOME, '.openclaw', 'skills', skillName);
    const skillMdPath = path.join(skillPath, 'SKILL.md');
    
    if (!fs.existsSync(skillMdPath)) {
      log('WARN', `${skillName} 缺少 SKILL.md`);
      return false;
    }
    
    return true;
  } catch (e) {
    log('ERROR', `验证 ${skillName} 失败: ${e.message}`);
    return false;
  }
}

// 回滚 skill
function rollbackSkill(skillName, version) {
  try {
    const backupPath = path.join(process.env.HOME, '.openclaw', 'skill-backups', `${skillName}@${version}`);
    const skillPath = path.join(process.env.HOME, '.openclaw', 'skills', skillName);
    
    if (!fs.existsSync(backupPath)) {
      log('ERROR', `备份不存在: ${backupPath}`);
      return false;
    }
    
    // 删除当前版本，恢复备份
    if (fs.existsSync(skillPath)) {
      fs.rmSync(skillPath, { recursive: true });
    }
    copyDir(backupPath, skillPath);
    
    log('INFO', `回滚 ${skillName} 到 ${version} 成功`);
    return true;
  } catch (e) {
    log('ERROR', `回滚 ${skillName} 失败: ${e.message}`);
    return false;
  }
}

// 主检查函数（简化版，不执行外部命令）
async function checkAndPrompt(skillName, options = {}) {
  const config = loadConfig();
  const { interactive = true, quiet = false, latestVersion = null } = options;
  
  // 检查黑名单
  if (config.blacklist.includes(skillName)) {
    log('DEBUG', `${skillName} 在黑名单中，跳过检查`);
    return { shouldUpdate: false, reason: 'blacklisted' };
  }
  
  // 获取当前版本
  const currentVersion = getCurrentVersion(skillName);
  if (!currentVersion) {
    log('WARN', `无法获取 ${skillName} 当前版本`);
    return { shouldUpdate: false, reason: 'not_installed' };
  }
  
  // 使用传入的最新版本或查询缓存
  let latest = latestVersion || getLatestVersion(skillName);
  
  if (!latest) {
    // 如果没有提供最新版本，提示用户需要查询
    if (!quiet) {
      console.log(`[ℹ️] 请运行 'clawhub inspect ${skillName}' 获取最新版本信息`);
    }
    return { 
      shouldUpdate: false, 
      currentVersion, 
      reason: 'need_query_clawhub',
      message: `请运行 'clawhub inspect ${skillName}' 获取最新版本信息`
    };
  }
  
  // 比较版本
  const cmp = compareVersion(latest, currentVersion);
  if (cmp <= 0) {
    log('DEBUG', `${skillName} 已是最新版本 ${currentVersion}`);
    return { shouldUpdate: false, currentVersion, latestVersion: latest, reason: 'up_to_date' };
  }
  
  // 获取更新类型
  const updateType = getUpdateType(currentVersion, latest);
  
  // 检查是否应该提醒
  if (!shouldRemind(skillName, config)) {
    log('DEBUG', `${skillName} 跳过提醒（用户近期已拒绝）`);
    return { shouldUpdate: false, currentVersion, latestVersion: latest, updateType, reason: 'remind_delayed' };
  }
  
  // 安静时段不提醒
  if (isQuietHours(config) && interactive) {
    log('DEBUG', '当前为安静时段，跳过提醒');
    return { shouldUpdate: false, currentVersion, latestVersion: latest, updateType, reason: 'quiet_hours' };
  }
  
  // 根据更新类型处理
  const result = {
    skillName,
    currentVersion,
    latestVersion: latest,
    updateType,
    shouldUpdate: false
  };
  
  // Patch 自动升级
  if (updateType === 'patch' && config.autoUpgrade.patch) {
    if (!quiet) console.log(`[ℹ️] ${skillName} ${currentVersion} → ${latest} (patch)，建议升级`);
    result.shouldUpdate = true;
    return result;
  }
  
  // Minor 建议升级
  if (updateType === 'minor') {
    if (!quiet) {
      console.log(`\n[📦] ${skillName} 有更新: ${currentVersion} → ${latest}`);
      console.log(`     更新类型: minor（新功能，向后兼容）`);
    }
    result.shouldUpdate = true;
    return result;
  }
  
  // Major 需确认
  if (updateType === 'major') {
    if (!quiet) {
      console.log(`\n[⚠️] ${skillName} 重大版本更新: ${currentVersion} → ${latest}`);
      console.log(`     ⚠️ 此更新包含重大变更，可能影响现有功能`);
      console.log(`     建议查看更新文档后再决定\n`);
    }
    result.shouldUpdate = false;
    result.reason = 'major_needs_confirmation';
    return result;
  }
  
  return result;
}

// 导出
module.exports = {
  checkAndPrompt,
  getCurrentVersion,
  getLatestVersion,
  getUpdateType,
  compareVersion,
  parseVersion,
  backupSkill,
  rollbackSkill,
  loadConfig,
  saveConfig,
  log,
  getInstalledSkills,
  setCachedVersion,
  getCachedVersion
};
