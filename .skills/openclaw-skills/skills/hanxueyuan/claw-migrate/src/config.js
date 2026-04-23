#!/usr/bin/env node

/**
 * 配置管理模块
 * 定义文件分类和迁移策略
 */

// 文件分类定义
const FILE_CATEGORIES = {
  // 核心配置文件
  CORE_CONFIG: [
    'AGENTS.md',
    'SOUL.md',
    'IDENTITY.md',
    'USER.md',
    'TOOLS.md',
    'HEARTBEAT.md',
    'REVIEW_GUIDE.md'
  ],
  
  // 技能文件
  SKILLS: [
    'skills/**/SKILL.md',
    'skills/*/index.js',
    'skills/*/package.json'
  ],
  
  // 记忆文件
  MEMORY: [
    'MEMORY.md',
    'memory/*.md'
  ],
  
  // 学习记录
  LEARNINGS: [
    '.learnings/*.md',
    '.learnings/LEARNINGS.md',
    '.learnings/ERRORS.md',
    '.learnings/FEATURE_REQUESTS.md'
  ],
  
  // 环境配置（敏感信息）
  ENV: [
    '.env',
    '.env.example'
  ],
  
  // Channel 配置（飞书等）
  CHANNEL_CONFIG: [
    'feishu/*.json',
    'feishu/**/*.json',
    'telegram/*.json',
    'telegram/**/*.json',
    'discord/*.json',
    'discord/**/*.json',
    '*.yaml',
    '*.yml'
  ],
  
  // 模板文件
  TEMPLATES: [
    'templates/*'
  ],
  
  // 脚本文件
  SCRIPTS: [
    'scripts/*.js',
    'scripts/*.sh'
  ],
  
  // 其他配置
  OTHER_CONFIG: [
    '.gitignore',
    '.openclaw/*.json',
    'package.json'
  ]
};

// 迁移类型与文件类别的映射
const CATEGORY_TYPE_MAP = {
  config: ['CORE_CONFIG', 'ENV', 'OTHER_CONFIG', 'TEMPLATES', 'SCRIPTS', 'CHANNEL_CONFIG'],
  skills: ['SKILLS'],
  memory: ['MEMORY'],
  learnings: ['LEARNINGS'],
  channel: ['CHANNEL_CONFIG'],
  all: ['CORE_CONFIG', 'SKILLS', 'MEMORY', 'LEARNINGS', 'ENV', 'CHANNEL_CONFIG', 'TEMPLATES', 'SCRIPTS', 'OTHER_CONFIG']
};

// 合并策略配置
const MERGE_STRATEGIES = {
  // 覆盖模式：直接用远端内容替换本地
  OVERWRITE: ['CORE_CONFIG', 'TEMPLATES', 'SCRIPTS', 'OTHER_CONFIG'],
  
  // 合并模式：智能合并
  MERGE: ['MEMORY', 'LEARNINGS'],
  
  // 跳过模式：本地已有则跳过
  SKIP: ['SKILLS', 'ENV', 'CHANNEL_CONFIG'],  // Channel 配置保留本地
  
  // 字段级合并：openclaw.json 特殊处理
  FIELD_MERGE: ['openclaw.json']
};

// 机器特定文件（不迁移）
const MACHINE_SPECIFIC_FILES = [
  'feishu/dedup/*.json',      // 消息去重 ID
  'feishu/pairing/*.json',    // Feishu pairing
  'telegram/sessions/*.json', // Telegram 会话
  'discord/pairing/*.json',   // Discord pairing
  '.env',                      // 环境变量
  '*.log',                     // 日志
  'sessions/*.jsonl',          // 会话数据
  '.git/config'                // git 配置
];

// openclaw.json 字段分类
const OPENCLAW_JSON_FIELDS = {
  // 可以覆盖的字段（通用配置）
  overwrite: [
    'models',
    'skills',
    'gateway',
    'agents.defaults',
    'browser.headless',
    'browser.noSandbox'
  ],
  
  // 保留本地的字段（机器特定）
  keepLocal: [
    'browser.executablePath',
    'browser.defaultProfile',
    'channel.*.pairing',
    'channel.*.auth',
    'channel.*.sessionId'
  ]
};

// 迁移配置
const MIGRATION_CONFIG = {
  // 是否创建备份
  createBackup: true,
  
  // 备份目录
  backupDir: '.migrate-backup',
  
  // 最大备份保留数量
  maxBackups: 10,
  
  // 是否验证文件内容
  validateContent: true,
  
  // 文件编码
  encoding: 'utf8'
};

module.exports = {
  FILE_CATEGORIES,
  CATEGORY_TYPE_MAP,
  MERGE_STRATEGIES,
  MIGRATION_CONFIG,
  MACHINE_SPECIFIC_FILES,
  OPENCLAW_JSON_FIELDS
};
