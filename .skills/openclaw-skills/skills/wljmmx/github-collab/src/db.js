/**
 * 数据库封装 - 统一数据库访问
 * 使用配置化的数据库路径
 */

const { getDatabaseManager } = require('./db/database-manager');
const config = require('./config');

// 获取数据库管理器实例
const dbManager = getDatabaseManager();

/**
 * 初始化数据库连接
 */
function init() {
  console.log(`📁 数据库路径：${config.database.path}`);
  console.log(`📊 数据库类型：${config.database.type}`);
  console.log(`📝 数据库名称：${config.database.name}`);
  return dbManager.init();
}

/**
 * 获取数据库实例
 */
function getDB() {
  return dbManager.getDatabase();
}

/**
 * 执行 SQL 查询
 */
function query(sql, params = []) {
  return dbManager.query(sql, params);
}

/**
 * 执行 SQL 查询并获取所有结果
 */
function getAll(sql, params = []) {
  return dbManager.getAll(sql, params);
}

/**
 * 执行 SQL 查询并获取单条结果
 */
function get(sql, params = []) {
  return dbManager.get(sql, params);
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
  dbManager.close();
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
  dbManager
};
