/**
 * 优化后的数据库查询模块
 * 包含：查询缓存、索引优化、N+1 查询优化、批量查询优化
 */

const { LRUCache } = require('./cache');

/**
 * 数据库查询优化器
 */
class QueryOptimizer {
  constructor(options = {}) {
    // 查询缓存
    this.queryCache = new LRUCache({
      maxSize: options.cacheSize || 500,
      defaultTTL: options.cacheTTL || 5 * 60 * 1000, // 默认 5 分钟
      onEvict: options.onEvict || null
    });

    // 批量查询配置
    this.batchConfig = {
      maxSize: options.batchSize || 100,
      timeout: options.batchTimeout || 100 // 毫秒
    };

    // 批量查询队列
    this.batchQueues = new Map();

    // 索引建议缓存
    this.indexSuggestions = new LRUCache({
      maxSize: 100,
      defaultTTL: 24 * 60 * 60 * 1000 // 24 小时
    });
  }

  /**
   * 生成查询缓存键
   */
  _generateCacheKey(query, params = []) {
    return JSON.stringify({ query, params });
  }

  /**
   * 缓存数据库查询结果
   * @param {string} query - SQL 查询语句
   * @param {Array} params - 查询参数
   * @param {Function} fetchFn - 数据获取函数
   * @param {number} ttl - 缓存 TTL
   * @returns {Promise<Array>} 查询结果
   */
  async cachedQuery(query, params = [], fetchFn, ttl = null) {
    const cacheKey = this._generateCacheKey(query, params);

    // 尝试从缓存获取
    const cached = this.queryCache.get(cacheKey);
    if (cached !== undefined) {
      return cached;
    }

    // 执行实际查询
    const result = await fetchFn(query, params);

    // 缓存结果
    this.queryCache.set(cacheKey, result, ttl);

    return result;
  }

  /**
   * 批量查询优化 - 解决 N+1 问题
   * 示例：获取用户及其订单
   *
   * 未优化（N+1 查询）:
   *   SELECT * FROM users
   *   FOR user IN users: SELECT * FROM orders WHERE user_id = ?
   *
   * 优化后（2 次查询）:
   *   SELECT * FROM users
   *   SELECT * FROM orders WHERE user_id IN (?, ?, ...)
   */
  async batchFetchByIds(model, ids, fetchByIdsFn, fetchByIdFn) {
    if (!ids || ids.length === 0) {
      return [];
    }

    // 去重
    const uniqueIds = [...new Set(ids)];

    // 批量获取所有数据
    const allData = await fetchByIdsFn(uniqueIds);

    // 构建映射表
    const dataMap = new Map();
    if (Array.isArray(allData)) {
      for (const item of allData) {
        dataMap.set(item.id, item);
      }
    } else if (allData && typeof allData === 'object') {
      for (const id of uniqueIds) {
        dataMap.set(id, allData[id]);
      }
    }

    // 按原始顺序返回（保留重复）
    return ids.map((id) => dataMap.get(id) || null);
  }

  /**
   * 延迟批量查询 - 自动合并相同查询
   * @param {string} key - 查询键
   * @param {Array} ids - 要查询的 ID 列表
   * @param {Function} batchFn - 批量查询函数
   * @returns {Promise<Array>} 查询结果
   */
  async delayedBatchFetch(key, ids, batchFn) {
    if (!ids || ids.length === 0) {
      return [];
    }

    // 去重
    const uniqueIds = [...new Set(ids)];

    // 创建或获取队列
    if (!this.batchQueues.has(key)) {
      this.batchQueues.set(key, {
        ids: new Set(),
        resolves: [],
        timer: null
      });
    }

    const queue = this.batchQueues.get(key);

    // 添加 ID 到队列
    for (const id of uniqueIds) {
      queue.ids.add(id);
    }

    // 创建解析函数
    const resolvePromise = new Promise((resolve) => {
      queue.resolves.push(resolve);
    });

    // 设置延迟执行
    if (!queue.timer) {
      queue.timer = setTimeout(async () => {
        const allIds = [...queue.ids];
        const results = await batchFn(allIds);

        // 构建结果映射
        const resultMap = new Map();
        if (Array.isArray(results)) {
          for (const item of results) {
            resultMap.set(item.id, item);
          }
        }

        // 调用所有解析函数
        for (const resolve of queue.resolves) {
          resolve(resultMap);
        }

        // 清理队列
        queue.ids.clear();
        queue.resolves = [];
        queue.timer = null;

        // 如果队列为空，删除
        if (queue.ids.size === 0 && queue.resolves.length === 0) {
          this.batchQueues.delete(key);
        }
      }, this.batchConfig.timeout);
    }

    return resolvePromise;
  }

  /**
   * 优化用户和订单查询（解决 N+1 问题）
   * @param {Array} userIds - 用户 ID 列表
   * @param {Function} db - 数据库实例
   * @returns {Promise<Array>} 用户及其订单列表
   */
  async fetchUsersWithOrders(userIds, db) {
    // 第 1 次查询：获取所有用户
    const users = await this.cachedQuery(
      'SELECT * FROM users WHERE id IN (' + userIds.map(() => '?').join(',') + ')',
      userIds,
      async (query, params) => {
        return db.all(query, params);
      },
      60 * 1000 // 1 分钟缓存
    );

    // 收集所有订单 ID
    const orderIds = [];
    for (const user of users) {
      if (user.order_ids) {
        orderIds.push(...user.order_ids.split(',').filter((id) => id));
      }
    }

    // 第 2 次查询：批量获取所有订单（而不是为每个用户单独查询）
    let orders = [];
    if (orderIds.length > 0) {
      orders = await this.cachedQuery(
        'SELECT * FROM orders WHERE id IN (' + orderIds.map(() => '?').join(',') + ')',
        orderIds,
        async (query, params) => {
          return db.all(query, params);
        },
        60 * 1000
      );
    }

    // 构建订单映射
    const orderMap = new Map();
    for (const order of orders) {
      if (!orderMap.has(order.user_id)) {
        orderMap.set(order.user_id, []);
      }
      orderMap.get(order.user_id).push(order);
    }

    // 组装结果
    return users.map((user) => ({
      ...user,
      orders: orderMap.get(user.id) || []
    }));
  }

  /**
   * 索引优化建议
   * 分析查询并推荐索引
   */
  suggestIndexes(queries) {
    const suggestions = [];

    for (const query of queries) {
      const lowerQuery = query.toLowerCase();
      const cacheKey = `index_suggestion_${query}`;

      // 检查缓存
      const cached = this.indexSuggestions.get(cacheKey);
      if (cached) {
        suggestions.push(cached);
        continue;
      }

      const suggestion = { query, indexes: [] };

      // 分析 WHERE 子句
      const whereMatch = lowerQuery.match(/where\s+(\w+)\s*=\s*\?/i);
      if (whereMatch) {
        suggestion.indexes.push({
          type: 'single',
          column: whereMatch[1],
          reason: 'WHERE 子句中使用等值查询'
        });
      }

      // 分析 JOIN 子句
      const joinMatches = lowerQuery.matchAll(
        /join\s+\w+\s+on\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)/gi
      );
      for (const match of joinMatches) {
        suggestion.indexes.push({
          type: 'join',
          columns: [match[2], match[4]],
          tables: [match[1], match[3]],
          reason: 'JOIN 操作需要索引'
        });
      }

      // 分析 ORDER BY
      const orderMatch = lowerQuery.match(/order\s+by\s+(\w+)/i);
      if (orderMatch) {
        suggestion.indexes.push({
          type: 'sort',
          column: orderMatch[1],
          reason: 'ORDER BY 排序操作'
        });
      }

      // 分析 GROUP BY
      const groupMatch = lowerQuery.match(/group\s+by\s+(\w+)/i);
      if (groupMatch) {
        suggestion.indexes.push({
          type: 'group',
          column: groupMatch[1],
          reason: 'GROUP BY 分组操作'
        });
      }

      this.indexSuggestions.set(cacheKey, suggestion);
      suggestions.push(suggestion);
    }

    return suggestions;
  }

  /**
   * 获取缓存统计
   */
  getCacheStats() {
    return this.queryCache.getStats();
  }

  /**
   * 清空缓存
   */
  clearCache() {
    this.queryCache.clear();
    this.indexSuggestions.clear();
  }
}

module.exports = { QueryOptimizer };
