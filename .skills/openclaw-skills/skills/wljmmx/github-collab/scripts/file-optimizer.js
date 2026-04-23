/**
 * 优化的文件读写模块
 * 包含：文件缓存、流式读写、批量操作、压缩大文件
 */

const fs = require('fs');
const fsPromises = require('fs/promises');
const path = require('path');
const zlib = require('zlib');
const { LRUCache } = require('./cache');

/**
 * 文件操作优化器
 */
class FileOptimizer {
  constructor(options = {}) {
    // 文件内容缓存
    this.fileCache = new LRUCache({
      maxSize: options.cacheSize || 100,
      defaultTTL: options.cacheTTL || 5 * 60 * 1000, // 5 分钟
      onEvict: options.onEvict || null
    });

    // 文件句柄缓存（用于批量操作）
    this.handleCache = new Map();

    // 压缩配置
    this.compressionConfig = {
      level: options.compressionLevel || 6, // 1-9
      threshold: options.compressionThreshold || 1024 * 1024 // 1MB 以上压缩
    };

    // 临时目录
    this.tempDir = options.tempDir || path.join(process.cwd(), '.temp');
  }

  /**
   * 读取文件（带缓存）
   * @param {string} filePath - 文件路径
   * @param {Object} options - 选项
   * @param {number} options.ttl - 缓存 TTL
   * @param {boolean} options.useCache - 是否使用缓存
   * @returns {Promise<string>} 文件内容
   */
  async readFile(filePath, options = {}) {
    const useCache = options.useCache !== false;
    const ttl = options.ttl || null;

    // 尝试从缓存读取
    if (useCache) {
      const cached = this.fileCache.get(filePath);
      if (cached !== undefined) {
        return cached;
      }
    }

    // 读取文件
    const content = await fsPromises.readFile(filePath, 'utf8');

    // 缓存结果
    if (useCache) {
      this.fileCache.set(filePath, content, ttl);
    }

    return content;
  }

  /**
   * 写入文件（带缓存失效）
   * @param {string} filePath - 文件路径
   * @param {string} content - 内容
   * @param {boolean} options.invalidateCache - 是否失效缓存
   * @returns {Promise<void>}
   */
  async writeFile(filePath, content, options = {}) {
    const invalidateCache = options.invalidateCache !== false;

    await fsPromises.writeFile(filePath, content, 'utf8');

    // 失效缓存
    if (invalidateCache) {
      this.fileCache.delete(filePath);
    }
  }

  /**
   * 流式读取大文件
   * @param {string} filePath - 文件路径
   * @param {Object} options - 选项
   * @param {number} options.chunkSize - 块大小
   * @returns {ReadableStream} 可读流
   */
  streamRead(filePath, options = {}) {
    const chunkSize = options.chunkSize || 64 * 1024; // 64KB
    return fs.createReadStream(filePath, { highWaterMark: chunkSize });
  }

  /**
   * 流式写入大文件
   * @param {string} filePath - 文件路径
   * @param {Object} options - 选项
   * @param {number} options.chunkSize - 块大小
   * @returns {WritableStream} 可写流
   */
  streamWrite(filePath, options = {}) {
    const chunkSize = options.chunkSize || 64 * 1024; // 64KB
    return fs.createWriteStream(filePath, { highWaterMark: chunkSize });
  }

  /**
   * 流式复制文件（适合大文件）
   * @param {string} source - 源文件
   * @param {string} destination - 目标文件
   * @returns {Promise<void>}
   */
  async streamCopy(source, destination) {
    return new Promise((resolve, reject) => {
      const readStream = this.streamRead(source);
      const writeStream = this.streamWrite(destination);

      readStream.pipe(writeStream);

      writeStream.on('finish', () => {
        resolve();
      });

      writeStream.on('error', (err) => {
        reject(err);
      });

      readStream.on('error', (err) => {
        reject(err);
      });
    });
  }

  /**
   * 压缩文件
   * @param {string} filePath - 文件路径
   * @param {string} outputFilePath - 输出文件路径
   * @returns {Promise<void>}
   */
  async compressFile(filePath, outputFilePath = null) {
    if (!outputFilePath) {
      outputFilePath = filePath + '.gz';
    }

    return new Promise((resolve, reject) => {
      const readStream = this.streamRead(filePath);
      const compressStream = zlib.createGzip({ level: this.compressionConfig.level });
      const writeStream = this.streamWrite(outputFilePath);

      readStream.pipe(compressStream).pipe(writeStream);

      writeStream.on('finish', () => {
        resolve();
      });

      writeStream.on('error', reject);
      readStream.on('error', reject);
    });
  }

  /**
   * 解压缩文件
   * @param {string} filePath - 压缩文件路径
   * @param {string} outputFilePath - 输出文件路径
   * @returns {Promise<void>}
   */
  async decompressFile(filePath, outputFilePath = null) {
    if (!outputFilePath) {
      outputFilePath = filePath.replace(/\.gz$/, '');
    }

    return new Promise((resolve, reject) => {
      const readStream = this.streamRead(filePath);
      const decompressStream = zlib.createGunzip();
      const writeStream = this.streamWrite(outputFilePath);

      readStream.pipe(decompressStream).pipe(writeStream);

      writeStream.on('finish', () => {
        resolve();
      });

      writeStream.on('error', reject);
      readStream.on('error', reject);
    });
  }

  /**
   * 批量读取文件
   * @param {string[]} filePaths - 文件路径列表
   * @param {Object} options - 选项
   * @returns {Promise<Map<string, string>>} 文件路径到内容的映射
   */
  async batchReadFiles(filePaths, options = {}) {
    const useCache = options.useCache !== false;
    const results = new Map();

    // 并行读取（带并发限制）
    const concurrency = options.concurrency || 10;
    const chunks = this._chunkArray(filePaths, concurrency);

    for (const chunk of chunks) {
      const chunkResults = await Promise.all(
        chunk.map(async (filePath) => {
          const content = await this.readFile(filePath, { useCache });
          return { filePath, content };
        })
      );

      for (const { filePath, content } of chunkResults) {
        results.set(filePath, content);
      }
    }

    return results;
  }

  /**
   * 批量写入文件
   * @param {Map<string, string>} files - 文件路径到内容的映射
   * @param {Object} options - 选项
   * @returns {Promise<void>}
   */
  async batchWriteFiles(files, options = {}) {
    const concurrency = options.concurrency || 10;
    const entries = Array.from(files.entries());
    const chunks = this._chunkArray(entries, concurrency);

    for (const chunk of chunks) {
      await Promise.all(
        chunk.map(async ([filePath, content]) => {
          await this.writeFile(filePath, content, options);
        })
      );
    }
  }

  /**
   * 批量删除文件
   * @param {string[]} filePaths - 文件路径列表
   * @returns {Promise<void>}
   */
  async batchDeleteFiles(filePaths) {
    await Promise.all(
      filePaths.map(async (filePath) => {
        try {
          await fsPromises.unlink(filePath);
          this.fileCache.delete(filePath); // 失效缓存
        } catch (err) {
          if (err.code !== 'ENOENT') {
            throw err;
          }
        }
      })
    );
  }

  /**
   * 读取文件并解析 JSON（带缓存）
   * @param {string} filePath - 文件路径
   * @returns {Promise<Object>} JSON 对象
   */
  async readJsonFile(filePath) {
    const content = await this.readFile(filePath);
    return JSON.parse(content);
  }

  /**
   * 写入 JSON 文件
   * @param {string} filePath - 文件路径
   * @param {Object} data - 数据
   * @returns {Promise<void>}
   */
  async writeJsonFile(filePath, data) {
    const content = JSON.stringify(data, null, 2);
    await this.writeFile(filePath, content);
  }

  /**
   * 流式处理大文件（逐行处理）
   * @param {string} filePath - 文件路径
   * @param {Function} lineHandler - 每行处理函数
   * @returns {Promise<number>} 处理的行数
   */
  async processFileLineByLine(filePath, lineHandler) {
    const stream = this.streamRead(filePath);
    let line = '';
    let count = 0;

    return new Promise((resolve, reject) => {
      stream.on('data', (chunk) => {
        line += chunk.toString();
        let newlineIndex;

        while ((newlineIndex = line.indexOf('\n')) >= 0) {
          const currentLine = line.substring(0, newlineIndex).trim();
          line = line.substring(newlineIndex + 1);

          if (currentLine) {
            lineHandler(currentLine, count++);
          }
        }
      });

      stream.on('end', () => {
        if (line.trim()) {
          lineHandler(line.trim(), count++);
        }
        resolve(count);
      });

      stream.on('error', reject);
    });
  }

  /**
   * 数组分块
   */
  _chunkArray(arr, size) {
    const chunks = [];
    for (let i = 0; i < arr.length; i += size) {
      chunks.push(arr.slice(i, i + size));
    }
    return chunks;
  }

  /**
   * 获取缓存统计
   */
  getCacheStats() {
    return this.fileCache.getStats();
  }

  /**
   * 清空缓存
   */
  clearCache() {
    this.fileCache.clear();
  }

  /**
   * 关闭所有句柄
   */
  close() {
    for (const [key, handle] of this.handleCache) {
      try {
        handle.close();
      } catch (e) {
        // 忽略关闭错误
      }
    }
    this.handleCache.clear();
  }
}

module.exports = { FileOptimizer };
