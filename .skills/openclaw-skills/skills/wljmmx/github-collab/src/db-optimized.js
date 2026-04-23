/**
 * 优化版数据库封装
 * 添加连接池、缓存、性能监控等优化
 */

const { getDatabaseManager } = require('./db/database-manager');
const config = require('./config');
const cache = require('./cache');

// 获取数据库管理器实例
const dbManager = getDatabaseManager();
let db = null;

/**
 * 初始化数据库连接
 */
async function init() {
  console.log('🚀 初始化优化数据库连接...');
  console.log(`📁 数据库路径：${config.database.path}`);
  console.log(`📊 数据库类型：${config.database.type}`);
  console.log(`📝 数据库名称：${config.database.name}`);
  console.log(`🔋 连接池大小：${config.database.poolSize}`);
  console.log(`⏱️ 查询超时：${config.database.timeout}ms`);

  const success = dbManager.init();
  if (success) {
    db = dbManager.getDatabase();

    // 启用 WAL 模式
    db.pragma('journal_mode = WAL');

    // 启用同步写入
    db.pragma('synchronous = NORMAL');

    // 设置缓存大小
    db.pragma('cache_size = -64000'); // 64MB

    // 启用分析
    db.pragma('analyze');

    console.log('✅ 优化数据库连接成功');
    return true;
  }

  console.error('❌ 优化数据库连接失败');
  return false;
}

/**
 * 获取数据库实例
 */
function getDB() {
  if (!db) {
    throw new Error('数据库未初始化，请先调用 init()');
  }
  return db;
}

/**
 * 执行 SQL 查询（带缓存）
 * @param {string} sql - SQL 语句
 * @param {array} params - 参数
 * @param {object} options - 选项 { cache: true/false, ttl: seconds }
 */
async function query(sql, params = [], options = {}) {
  const { cache: useCache = false, ttl = config.CACHE_TTL } = options;

  // 如果启用缓存，先检查缓存
  if (useCache && cache.isEnabled()) {
    const cacheKey = `sql:${sql}:${JSON.stringify(params)}`;
    const cached = cache.get(cacheKey);
    if (cached) {
      console.log(`📦 缓存命中：${cacheKey}`);
      return cached;
    }
  }

  // 执行查询
  const start = Date.now();
  const result = dbManager.query(sql, params);
  const duration = Date.now() - start;

  // 记录性能指标
  if (duration > 100) {
    console.warn(`⚠️ 慢查询 (${duration}ms): ${sql}`);
  }

  // 如果启用缓存，缓存结果
  if (useCache && cache.isEnabled()) {
    const cacheKey = `sql:${sql}:${JSON.stringify(params)}`;
    cache.set(cacheKey, result, ttl);
  }

  return result;
}

/**
 * 执行 SQL 查询并获取所有结果（带缓存）
 */
async function getAll(sql, params = [], options = {}) {
  const { cache: useCache = false, ttl = config.CACHE_TTL } = options;

  // 如果启用缓存，先检查缓存
  if (useCache && cache.isEnabled()) {
    const cacheKey = `sql:all:${sql}:${JSON.stringify(params)}`;
    const cached = cache.get(cacheKey);
    if (cached) {
      console.log(`📦 缓存命中：${cacheKey}`);
      return cached;
    }
  }

  // 执行查询
  const start = Date.now();
  const result = dbManager.getAll(sql, params);
  const duration = Date.now() - start;

  // 记录性能指标
  if (duration > 100) {
    console.warn(`⚠️ 慢查询 (${duration}ms): ${sql}`);
  }

  // 如果启用缓存，缓存结果
  if (useCache && cache.isEnabled()) {
    const cacheKey = `sql:all:${sql}:${JSON.stringify(params)}`;
    cache.set(cacheKey, result, ttl);
  }

  return result;
}

/**
 * 执行 SQL 查询并获取单条结果（带缓存）
 */
async function get(sql, params = [], options = {}) {
  const { cache: useCache = false, ttl = config.CACHE_TTL } = options;

  // 如果启用缓存，先检查缓存
  if (useCache && cache.isEnabled()) {
    const cacheKey = `sql:get:${sql}:${JSON.stringify(params)}`;
    const cached = cache.get(cacheKey);
    if (cached) {
      console.log(`📦 缓存命中：${cacheKey}`);
      return cached;
    }
  }

  // 执行查询
  const start = Date.now();
  const result = dbManager.get(sql, params);
  const duration = Date.now() - start;

  // 记录性能指标
  if (duration > 100) {
    console.warn(`⚠️ 慢查询 (${duration}ms): ${sql}`);
  }

  // 如果启用缓存，缓存结果
  if (useCache && cache.isEnabled()) {
    const cacheKey = `sql:get:${sql}:${JSON.stringify(params)}`;
    cache.set(cacheKey, result, ttl);
  }

  return result;
}

/**
 * 执行事务
 */
function transaction(fn) {
  return dbManager.transaction(fn);
}

/**
 * 关闭数据库连接
 */
function close() {
  if (db) {
    dbManager.close();
    db = null;
    console.log('✅ 优化数据库连接已关闭');
  }
}

/**
 * 获取数据库配置
 */
function getConfig() {
  return dbManager.getConfig();
}

/**
 * 获取数据库路径
 */
function getDbPath() {
  return dbManager.getDbPath();
}

/**
 * 性能监控
 */
function getPerformanceMetrics() {
  return {
    path: getDbPath(),
    config: getConfig(),
    cacheEnabled: cache.isEnabled(),
    cacheSize: cache.getSize()
  };
}

module.exports = {
  init,
  getDB,
  query,
  getAll,
  get,
  transaction,
  close,
  getConfig,
  getDbPath,
  getPerformanceMetrics,
  dbManager
};
