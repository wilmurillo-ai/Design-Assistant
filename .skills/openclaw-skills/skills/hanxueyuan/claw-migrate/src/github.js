#!/usr/bin/env node

/**
 * GitHub API 访问模块
 * 用于从 GitHub 私有仓库读取文件
 */

const https = require('https');

class GitHubReader {
  constructor(token, repo, branch = 'main', pathPrefix = '') {
    this.token = token;
    this.repo = repo; // 格式：owner/repo
    this.branch = branch;
    this.pathPrefix = pathPrefix ? pathPrefix.replace(/\/$/, '') : '';
    this.baseUrl = 'https://api.github.com';
  }

  // 发送 GitHub API 请求
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    return new Promise((resolve, reject) => {
      const reqOptions = {
        hostname: 'api.github.com',
        path: endpoint,
        method: options.method || 'GET',
        headers: {
          'Authorization': `token ${this.token}`,
          'Accept': 'application/vnd.github.v3+json',
          'User-Agent': 'openclaw-migrate-kit'
        }
      };

      if (options.body) {
        const body = JSON.stringify(options.body);
        reqOptions.headers['Content-Length'] = Buffer.byteLength(body);
        reqOptions.headers['Content-Type'] = 'application/json';
      }

      const req = https.request(reqOptions, (res) => {
        let data = '';
        
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            try {
              resolve(data ? JSON.parse(data) : null);
            } catch (e) {
              resolve(data);
            }
          } else {
            let errorMsg = `GitHub API 错误 (${res.statusCode})`;
            try {
              const errorBody = JSON.parse(data);
              if (errorBody.message) {
                errorMsg = `${errorMsg}: ${errorBody.message}`;
              }
            } catch (e) {
              errorMsg = `${errorMsg}: ${data}`;
            }
            reject(new Error(errorMsg));
          }
        });
      });

      req.on('error', reject);
      
      if (options.body) {
        req.write(JSON.stringify(options.body));
      }
      req.end();
    });
  }

  // 测试连接并获取仓库信息
  async testConnection() {
    const [owner, repo] = this.repo.split('/');
    const repoInfo = await this.request(`/repos/${owner}/${repo}`);
    return repoInfo;
  }

  // 获取文件列表
  async getFileList(type = 'all') {
    const [owner, repo] = this.repo.split('/');
    const path = this.pathPrefix || '';
    
    // 递归获取目录内容
    const files = [];
    await this.walkDirectory(owner, repo, path, files, type);
    
    return files;
  }

  // 递归遍历目录
  async walkDirectory(owner, repo, dirPath, files, type, maxDepth = 5, currentDepth = 0) {
    if (currentDepth >= maxDepth) {
      return;
    }

    const endpoint = `/repos/${owner}/${repo}/contents/${dirPath}`;
    const params = `?ref=${this.branch}`;
    
    const contents = await this.request(endpoint + params);
    
    if (!Array.isArray(contents)) {
      return;
    }

    for (const item of contents) {
      const relativePath = item.path;
      
      if (item.type === 'file') {
        // 检查文件是否应该迁移
        const category = this.getFileCategory(relativePath);
        if (category && this.shouldIncludeFile(category, type)) {
          files.push({
            path: relativePath,
            category: category,
            sha: item.sha
          });
        }
      } else if (item.type === 'dir') {
        // 递归处理子目录
        await this.walkDirectory(owner, repo, item.path, files, type, maxDepth, currentDepth + 1);
      }
    }
  }

  // 判断文件类别
  getFileCategory(filePath) {
    const { FILE_CATEGORIES } = require('./config');
    
    for (const [category, patterns] of Object.entries(FILE_CATEGORIES)) {
      for (const pattern of patterns) {
        if (this.matchPattern(filePath, pattern)) {
          return category;
        }
      }
    }
    
    return null;
  }

  // 简单的 glob 匹配
  matchPattern(filePath, pattern) {
    // 处理 **/ 前缀
    if (pattern.startsWith('**/')) {
      const suffix = pattern.slice(3);
      return filePath.endsWith(suffix) || filePath.includes('/' + suffix);
    }
    
    // 处理 */ 前缀
    if (pattern.startsWith('*/')) {
      return filePath.endsWith(pattern.slice(2));
    }
    
    // 处理目录前缀
    if (pattern.endsWith('/*')) {
      const dirPrefix = pattern.slice(0, -2);
      return filePath.startsWith(dirPrefix + '/');
    }
    
    // 精确匹配
    return filePath === pattern;
  }

  // 判断是否应该包含该文件
  shouldIncludeFile(category, type) {
    if (type === 'all') {
      return true;
    }
    
    const { CATEGORY_TYPE_MAP } = require('./config');
    const fileTypes = CATEGORY_TYPE_MAP[type] || [];
    
    return fileTypes.includes(category);
  }

  // 获取文件内容
  async getFileContent(filePath) {
    const [owner, repo] = this.repo.split('/');
    const endpoint = `/repos/${owner}/${repo}/contents/${filePath}`;
    const params = `?ref=${this.branch}`;
    
    const fileInfo = await this.request(endpoint + params);
    
    if (!fileInfo || !fileInfo.content) {
      throw new Error(`无法读取文件：${filePath}`);
    }
    
    // GitHub API 返回的是 base64 编码
    const content = Buffer.from(fileInfo.content, 'base64').toString('utf8');
    return content;
  }
}

module.exports = { GitHubReader };
