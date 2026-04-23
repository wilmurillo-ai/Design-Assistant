/**
 * 统一配置文件
 * 所有配置项都可通过环境变量或配置文件修改
 */

const path = require('path');
const fs = require('fs');

// 默认配置
const DEFAULT_CONFIG = {
  db: {
    type: 'better-sqlite3',
    path: './db/gitwork.db',
    host: 'localhost',
    port: 3306,
    user: undefined,
    password: undefined,
    database: undefined,
    pool: {
      min: 2,
      max: 10,
      acquireTimeout: 30000,
      idleTimeout: 10000
    }
  },
  log: {
    level: 'INFO',
    file: './logs/app.log'
  },
  agent: {
    heartbeatInterval: 5 * 60 * 1000, // 5 分钟
    syncInterval: 10 * 60 * 1000, // 10 分钟
    maxParallel: 3,
    autoRecovery: true
  },
  cache: {
    enabled: true,
    ttl: 300 // 5 分钟
  },
  qqbot: {
    token: '',
    appId: '',
    secret: ''
  },
  projectRoot: __dirname + '/../'
};

/**
 * 从环境变量加载配置
 */
function loadFromEnv() {
  const env = {};

  // 数据库配置
  if (
    process.env.DB_TYPE ||
    process.env.DB_PATH ||
    process.env.DB_HOST ||
    process.env.DB_PORT ||
    process.env.DB_USER ||
    process.env.DB_PASSWORD ||
    process.env.DB_NAME ||
    process.env.DB_POOL_MIN ||
    process.env.DB_POOL_MAX ||
    process.env.DB_POOL_ACQUIRE_TIMEOUT ||
    process.env.DB_POOL_IDLE_TIMEOUT
  ) {
    env.db = {};

    if (process.env.DB_TYPE) env.db.type = process.env.DB_TYPE;
    if (process.env.DB_PATH) env.db.path = process.env.DB_PATH;
    if (process.env.DB_HOST) env.db.host = process.env.DB_HOST;
    if (process.env.DB_PORT) env.db.port = parseInt(process.env.DB_PORT, 10);
    if (process.env.DB_USER) env.db.user = process.env.DB_USER;
    if (process.env.DB_PASSWORD) env.db.password = process.env.DB_PASSWORD;
    if (process.env.DB_NAME) env.db.database = process.env.DB_NAME;

    if (
      process.env.DB_POOL_MIN ||
      process.env.DB_POOL_MAX ||
      process.env.DB_POOL_ACQUIRE_TIMEOUT ||
      process.env.DB_POOL_IDLE_TIMEOUT
    ) {
      env.db.pool = {};
      if (process.env.DB_POOL_MIN) env.db.pool.min = parseInt(process.env.DB_POOL_MIN, 10);
      if (process.env.DB_POOL_MAX) env.db.pool.max = parseInt(process.env.DB_POOL_MAX, 10);
      if (process.env.DB_POOL_ACQUIRE_TIMEOUT)
        env.db.pool.acquireTimeout = parseInt(process.env.DB_POOL_ACQUIRE_TIMEOUT, 10);
      if (process.env.DB_POOL_IDLE_TIMEOUT)
        env.db.pool.idleTimeout = parseInt(process.env.DB_POOL_IDLE_TIMEOUT, 10);
    }
  }

  // 日志配置
  if (process.env.LOG_LEVEL || process.env.LOG_FILE) {
    env.log = {};
    if (process.env.LOG_LEVEL) env.log.level = process.env.LOG_LEVEL;
    if (process.env.LOG_FILE) env.log.file = process.env.LOG_FILE;
  }

  // Agent 配置
  if (process.env.HEARTBEAT_INTERVAL || process.env.SYNC_INTERVAL) {
    env.agent = {};
    if (process.env.HEARTBEAT_INTERVAL) {
      env.agent.heartbeatInterval = parseInt(process.env.HEARTBEAT_INTERVAL, 10) * 60 * 1000;
    }
    if (process.env.SYNC_INTERVAL) {
      env.agent.syncInterval = parseInt(process.env.SYNC_INTERVAL, 10) * 60 * 1000;
    }
  }

  return env;
}

/**
 * 从自定义配置文件加载配置
 */
function loadFromCustomConfig(configPath) {
  if (!configPath || typeof configPath !== 'string') {
    return {};
  }

  try {
    if (!fs.existsSync(configPath)) {
      return {};
    }

    const content = fs.readFileSync(configPath, 'utf8');
    return JSON.parse(content);
  } catch (error) {
    return {};
  }
}

/**
 * 深度合并配置对象
 */
function mergeConfigs(...configs) {
  return configs.reduce((acc, config) => {
    if (!config || typeof config !== 'object') {
      return acc;
    }

    Object.keys(config).forEach((key) => {
      const accValue = acc[key];
      const configValue = config[key];

      if (
        accValue &&
        configValue &&
        typeof accValue === 'object' &&
        typeof configValue === 'object' &&
        !Array.isArray(accValue) &&
        !Array.isArray(configValue)
      ) {
        acc[key] = mergeConfigs(accValue, configValue);
      } else {
        acc[key] = configValue;
      }
    });

    return acc;
  }, {});
}

/**
 * 深度克隆对象
 */
function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => deepClone(item));
  }

  const cloned = {};
  Object.keys(obj).forEach((key) => {
    cloned[key] = deepClone(obj[key]);
  });

  return cloned;
}

/**
 * 获取完整配置
 */
function getConfig(customConfigPath) {
  const envConfig = loadFromEnv();
  const customConfig = customConfigPath ? loadFromCustomConfig(customConfigPath) : {};

  // 合并配置：默认 < 环境变量 < 自定义配置
  return mergeConfigs(deepClone(DEFAULT_CONFIG), envConfig, customConfig);
}

// 导出配置
module.exports = {
  DEFAULT_CONFIG,
  getConfig,
  loadFromEnv,
  loadFromCustomConfig,
  mergeConfigs,
  deepClone,
  // 向后兼容
  getDatabaseConfig: () => getConfig().db,
  getDatabasePath: () => {
    const config = getConfig();
    return path.resolve(config.projectRoot, config.db.path);
  }
};
