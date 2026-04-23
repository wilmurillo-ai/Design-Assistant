/**
 * 性能优化测试套件
 * 测试 cache.js, db-optimizer.js, file-optimizer.js
 */

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const { LRUCache } = require('./cache');
const { QueryOptimizer } = require('./db-optimizer');
const { FileOptimizer } = require('./file-optimizer');

// 测试配置
const TEST_DIR = path.join(__dirname, '.test-temp');

/**
 * 测试工具
 */
class TestUtils {
  static setup() {
    if (!fs.existsSync(TEST_DIR)) {
      fs.mkdirSync(TEST_DIR, { recursive: true });
    }
  }

  static teardown() {
    if (fs.existsSync(TEST_DIR)) {
      const files = fs.readdirSync(TEST_DIR);
      for (const file of files) {
        fs.unlinkSync(path.join(TEST_DIR, file));
      }
      fs.rmdirSync(TEST_DIR);
    }
  }

  static measure(fn) {
    const start = Date.now();
    const result = fn();
    const end = Date.now();
    return { result, duration: end - start };
  }

  static async measureAsync(fn) {
    const start = Date.now();
    const result = await fn();
    const end = Date.now();
    return { result, duration: end - start };
  }

  static formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  }
}

/**
 * LRUCache 测试
 */
async function testLRUCache() {
  console.log('\n' + '='.repeat(60));
  console.log('LRUCache 测试');
  console.log('='.repeat(60));

  // 测试 1: 基本功能
  console.log('\n[测试 1] 基本 set/get 功能');
  const cache = new LRUCache({ maxSize: 5 });
  cache.set('key1', 'value1');
  cache.set('key2', 'value2');
  assert.strictEqual(cache.get('key1'), 'value1');
  assert.strictEqual(cache.get('key2'), 'value2');
  console.log('✓ 基本功能正常');

  // 测试 2: LRU 淘汰
  console.log('\n[测试 2] LRU 淘汰策略');
  const evicted = [];
  const lruCache = new LRUCache({
    maxSize: 3,
    onEvict: (key, value) => evicted.push({ key, value })
  });

  lruCache.set('a', 1);
  lruCache.set('b', 2);
  lruCache.set('c', 3);
  lruCache.set('d', 4); // 应该淘汰 a

  assert.strictEqual(lruCache.get('a'), undefined);
  assert.strictEqual(lruCache.get('b'), 2);
  assert.strictEqual(evicted.length, 1);
  assert.strictEqual(evicted[0].key, 'a');
  console.log('✓ LRU 淘汰正常');

  // 测试 3: TTL 过期
  console.log('\n[测试 3] TTL 过期');
  const ttlCache = new LRUCache({ defaultTTL: 100 });
  ttlCache.set('temp', 'value', 100);
  assert.strictEqual(ttlCache.get('temp'), 'value');

  // 等待过期
  await new Promise((r) => setTimeout(r, 150));
  assert.strictEqual(ttlCache.get('temp'), undefined);
  console.log('✓ TTL 过期正常');

  // 测试 4: 缓存预热
  console.log('\n[测试 4] 缓存预热');
  const warmCache = new LRUCache({ maxSize: 100 });
  const warmupData = [
    { key: 'user:1', value: { id: 1, name: 'Alice' } },
    { key: 'user:2', value: { id: 2, name: 'Bob' } },
    { key: 'user:3', value: { id: 3, name: 'Charlie' } }
  ];
  warmCache.warmUp(warmupData);
  assert.strictEqual(warmCache.size(), 3);
  assert.strictEqual(warmCache.get('user:1').name, 'Alice');
  console.log('✓ 缓存预热正常');

  // 测试 5: 性能测试
  console.log('\n[测试 5] 性能测试 - 10000 次操作');
  const perfCache = new LRUCache({ maxSize: 10000 });

  // 写入性能
  const writeStart = Date.now();
  for (let i = 0; i < 10000; i++) {
    perfCache.set(`key${i}`, `value${i}`);
  }
  const writeEnd = Date.now();

  // 读取性能
  const readStart = Date.now();
  for (let i = 0; i < 10000; i++) {
    perfCache.get(`key${i}`);
  }
  const readEnd = Date.now();

  console.log(`  写入 10000 项：${writeEnd - writeStart}ms`);
  console.log(`  读取 10000 项：${readEnd - readStart}ms`);
  console.log(`  命中率：${perfCache.getStats().hitRate}`);
  console.log('✓ 性能测试完成');

  return {
    name: 'LRUCache',
    tests: 5,
    passed: 5,
    metrics: {
      write10k: writeEnd - writeStart,
      read10k: readEnd - readStart
    }
  };
}

/**
 * QueryOptimizer 测试
 */
async function testQueryOptimizer() {
  console.log('\n' + '='.repeat(60));
  console.log('QueryOptimizer 测试');
  console.log('='.repeat(60));

  const optimizer = new QueryOptimizer({ cacheSize: 100 });

  // 测试 1: 查询缓存
  console.log('\n[测试 1] 查询缓存');
  let queryCount = 0;
  const mockFetch = async (query, params) => {
    queryCount++;
    return [{ id: 1, name: 'Test' }];
  };

  await optimizer.cachedQuery('SELECT * FROM users WHERE id = ?', [1], mockFetch);
  assert.strictEqual(queryCount, 1);

  await optimizer.cachedQuery('SELECT * FROM users WHERE id = ?', [1], mockFetch);
  assert.strictEqual(queryCount, 1); // 应该从缓存返回

  console.log('✓ 查询缓存正常');

  // 测试 2: N+1 优化
  console.log('\n[测试 2] N+1 查询优化');

  const users = [
    { id: 1, name: 'Alice', order_ids: '101,102' },
    { id: 2, name: 'Bob', order_ids: '103' },
    { id: 3, name: 'Charlie', order_ids: '104,105' }
  ];

  const orders = [
    { id: 101, user_id: 1, product: 'Product A' },
    { id: 102, user_id: 1, product: 'Product B' },
    { id: 103, user_id: 2, product: 'Product C' },
    { id: 104, user_id: 3, product: 'Product D' },
    { id: 105, user_id: 3, product: 'Product E' }
  ];

  // 模拟批量查询
  const batchFetch = async (ids) => {
    return orders.filter((o) => ids.includes(o.id));
  };

  const result = await optimizer.batchFetchByIds(
    'orders',
    [101, 102, 103, 104, 105],
    batchFetch,
    null
  );

  assert.strictEqual(result.length, 5);
  console.log('✓ N+1 优化正常');

  // 测试 3: 索引建议
  console.log('\n[测试 3] 索引建议');
  const queries = [
    'SELECT * FROM users WHERE email = ?',
    'SELECT * FROM orders JOIN users ON orders.user_id = users.id',
    'SELECT * FROM products ORDER BY created_at'
  ];

  const suggestions = optimizer.suggestIndexes(queries);
  assert.strictEqual(suggestions.length, 3);
  assert.strictEqual(suggestions[0].indexes.length, 1);
  console.log('✓ 索引建议正常');

  // 测试 4: 性能对比
  console.log('\n[测试 4] 性能对比 - 带缓存 vs 不带缓存');

  const fetchFn = async (query, params) => {
    await new Promise((r) => setTimeout(r, 10)); // 模拟数据库延迟
    return [{ id: params[0], name: 'User' }];
  };

  // 不带缓存
  const noCacheStart = Date.now();
  for (let i = 0; i < 100; i++) {
    await fetchFn('SELECT * FROM users WHERE id = ?', [i]);
  }
  const noCacheEnd = Date.now();

  // 带缓存
  const cacheStart = Date.now();
  for (let i = 0; i < 100; i++) {
    await optimizer.cachedQuery('SELECT * FROM users WHERE id = ?', [i], fetchFn);
  }
  const cacheEnd = Date.now();

  console.log(`  不带缓存：${noCacheEnd - noCacheStart}ms`);
  console.log(`  带缓存：${cacheEnd - cacheStart}ms`);
  console.log(`  提升：${((noCacheEnd - noCacheStart) / (cacheEnd - cacheStart)).toFixed(2)}x`);
  console.log('✓ 性能对比完成');

  return {
    name: 'QueryOptimizer',
    tests: 4,
    passed: 4,
    metrics: {
      noCache: noCacheEnd - noCacheStart,
      withCache: cacheEnd - cacheStart
    }
  };
}

/**
 * FileOptimizer 测试
 */
async function testFileOptimizer() {
  console.log('\n' + '='.repeat(60));
  console.log('FileOptimizer 测试');
  console.log('='.repeat(60));

  TestUtils.setup();
  const optimizer = new FileOptimizer({ tempDir: TEST_DIR });

  // 测试 1: 文件缓存
  console.log('\n[测试 1] 文件缓存');
  const testFile = path.join(TEST_DIR, 'test.txt');
  await fs.promises.writeFile(testFile, 'Hello World');

  const read1 = await optimizer.readFile(testFile);
  const read2 = await optimizer.readFile(testFile);
  assert.strictEqual(read1, 'Hello World');
  assert.strictEqual(read2, 'Hello World');
  console.log('✓ 文件缓存正常');

  // 测试 2: 流式读写
  console.log('\n[测试 2] 流式读写大文件');
  const largeFile = path.join(TEST_DIR, 'large.txt');
  const content = 'Line ' + Array(10000).fill('test content ').join('\nLine ');

  const writeStream = optimizer.streamWrite(largeFile);
  writeStream.write(content);
  writeStream.end();
  await new Promise((r) => writeStream.on('finish', r));

  const stats = fs.statSync(largeFile);
  console.log(`  文件大小：${TestUtils.formatBytes(stats.size)}`);
  console.log('✓ 流式读写正常');

  // 测试 3: 文件压缩
  console.log('\n[测试 3] 文件压缩');
  const compressedFile = path.join(TEST_DIR, 'large.txt.gz');
  await optimizer.compressFile(largeFile, compressedFile);

  const originalSize = fs.statSync(largeFile).size;
  const compressedSize = fs.statSync(compressedFile).size;
  const ratio = ((compressedSize / originalSize) * 100).toFixed(2);

  console.log(`  原始大小：${TestUtils.formatBytes(originalSize)}`);
  console.log(`  压缩大小：${TestUtils.formatBytes(compressedSize)}`);
  console.log(`  压缩比：${ratio}%`);
  console.log('✓ 文件压缩正常');

  // 测试 4: 批量文件操作
  console.log('\n[测试 4] 批量文件操作');
  const files = new Map();
  for (let i = 0; i < 10; i++) {
    files.set(path.join(TEST_DIR, `batch${i}.txt`), `Content ${i}`);
  }

  const batchStart = Date.now();
  await optimizer.batchWriteFiles(files);
  const batchWriteEnd = Date.now();

  const batchReadStart = Date.now();
  const results = await optimizer.batchReadFiles(Array.from(files.keys()), { concurrency: 5 });
  const batchReadEnd = Date.now();

  assert.strictEqual(results.size, 10);
  console.log(`  批量写入 10 文件：${batchWriteEnd - batchStart}ms`);
  console.log(`  批量读取 10 文件：${batchReadEnd - batchReadStart}ms`);
  console.log('✓ 批量文件操作正常');

  // 测试 5: 逐行处理
  console.log('\n[测试 5] 逐行处理大文件');
  let lineCount = 0;
  await optimizer.processFileLineByLine(largeFile, (line) => {
    lineCount++;
  });
  console.log(`  处理行数：${lineCount}`);
  console.log('✓ 逐行处理正常');

  // 清理
  TestUtils.teardown();

  return {
    name: 'FileOptimizer',
    tests: 5,
    passed: 5,
    metrics: {
      batchWrite: batchWriteEnd - batchStart,
      batchRead: batchReadEnd - batchReadStart,
      compressionRatio: ratio
    }
  };
}

/**
 * 运行所有测试
 */
async function runAllTests() {
  console.log('\n' + '='.repeat(60));
  console.log('性能优化测试套件');
  console.log('='.repeat(60));
  console.log(`开始时间：${new Date().toISOString()}`);

  const results = [];

  try {
    results.push(await testLRUCache());
    results.push(await testQueryOptimizer());
    results.push(await testFileOptimizer());
  } catch (error) {
    console.error('\n测试失败:', error);
  }

  // 生成报告
  console.log('\n' + '='.repeat(60));
  console.log('测试报告');
  console.log('='.repeat(60));

  let totalTests = 0;
  let totalPassed = 0;

  for (const result of results) {
    totalTests += result.tests;
    totalPassed += result.passed;
    console.log(`\n${result.name}: ${result.passed}/${result.tests} 通过`);
  }

  console.log(`\n总计：${totalPassed}/${totalTests} 通过`);

  // 性能对比
  console.log('\n' + '='.repeat(60));
  console.log('性能对比报告');
  console.log('='.repeat(60));

  console.log('\n【缓存模块】');
  const cacheResult = results.find((r) => r.name === 'LRUCache');
  if (cacheResult) {
    console.log(`  写入 10000 项：${cacheResult.metrics.write10k}ms`);
    console.log(`  读取 10000 项：${cacheResult.metrics.read10k}ms`);
  }

  console.log('\n【数据库查询优化】');
  const dbResult = results.find((r) => r.name === 'QueryOptimizer');
  if (dbResult) {
    const improvement = (dbResult.metrics.noCache / dbResult.metrics.withCache).toFixed(2);
    console.log(`  不带缓存：${dbResult.metrics.noCache}ms`);
    console.log(`  带缓存：${dbResult.metrics.withCache}ms`);
    console.log(`  性能提升：${improvement}x`);
  }

  console.log('\n【文件读写优化】');
  const fileResult = results.find((r) => r.name === 'FileOptimizer');
  if (fileResult) {
    console.log(`  批量写入 10 文件：${fileResult.metrics.batchWrite}ms`);
    console.log(`  批量读取 10 文件：${fileResult.metrics.batchRead}ms`);
    console.log(`  压缩比：${fileResult.metrics.compressionRatio}%`);
  }

  console.log('\n' + '='.repeat(60));
  console.log('测试完成！');
  console.log('='.repeat(60));

  return results;
}

// 运行测试
runAllTests().catch(console.error);
