#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const CONFIG = { baseUrl: 'https://www.hsciq.com', apiKey: '', endpoints: { toolsList: '/mcp/tools/list', toolsCall: '/mcp/tools/call' } };

function loadConfig() {
  // 优先读取 JSON 配置文件
  const jsonPaths = [
    path.join(process.env.HOME, 'openclaw/workspace/hsciq-mcp-config.json'),
    path.join(process.env.HOME, '.openclaw/workspace/hsciq-mcp-config.json'),
    path.join(process.cwd(), 'hsciq-mcp-config.json')
  ];
  
  for (const jsonPath of jsonPaths) {
    if (fs.existsSync(jsonPath)) {
      try {
        const config = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
        if (config.apiKey) {
          CONFIG.apiKey = config.apiKey;
          CONFIG.baseUrl = config.baseUrl || 'https://www.hsciq.com';
          return;
        }
      } catch (e) {
        // JSON 解析失败，继续尝试其他方式
      }
    }
  }
  
  // 回退到 .env 格式
  const envPaths = [
    path.join(process.env.HOME, 'openclaw/workspace/.env.hsciq'),
    path.join(process.env.HOME, '.openclaw/workspace/.env.hsciq'),
    path.join(process.cwd(), '.env.hsciq')
  ];
  
  for (const envPath of envPaths) {
    if (fs.existsSync(envPath)) {
      const content = fs.readFileSync(envPath, 'utf-8');
      content.split('\n').forEach(line => {
        const [key, value] = line.split('=');
        if (key === 'HSCIQ_API_KEY') CONFIG.apiKey = value?.trim();
        else if (key === 'HSCIQ_BASE_URL') CONFIG.baseUrl = value?.trim();
      });
      if (CONFIG.apiKey) return;
    }
  }
  
  // 最后尝试环境变量
  if (process.env.HSCIQ_API_KEY) {
    CONFIG.apiKey = process.env.HSCIQ_API_KEY;
    CONFIG.baseUrl = process.env.HSCIQ_BASE_URL || 'https://www.hsciq.com';
    return;
  }
  
  if (!CONFIG.apiKey) {
    console.error('错误：未找到 HSCIQ_API_KEY，请检查以下配置文件之一：');
    console.error('  - ~/.openclaw/workspace/hsciq-mcp-config.json');
    console.error('  - ~/openclaw/workspace/hsciq-mcp-config.json');
    console.error('  - ~/.openclaw/workspace/.env.hsciq');
    console.error('  - 或设置环境变量 HSCIQ_API_KEY');
    process.exit(1);
  }
}

async function callTool(toolName, args = {}) {
  const url = `${CONFIG.baseUrl}${CONFIG.endpoints.toolsCall}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-API-Key': CONFIG.apiKey },
    body: JSON.stringify({ toolName, arguments: args })
  });
  if (!response.ok) throw new Error(`API 请求失败 (${response.status})`);
  const result = await response.json();
  if (!result.ok) throw new Error(`工具调用失败`);
  return result.data;
}

async function searchCode(keywords, country = 'CN', pageIndex = 1, pageSize = 10) {
  return await callTool('search_code', { keywords, country, pageIndex, pageSize, filterFailureCode: true });
}

async function getCodeDetail(code, country = 'CN') {
  return await callTool('get_code_detail', { code, country });
}

async function searchInstance(keywords, country = 'CN', pageIndex = 1, pageSize = 10) {
  return await callTool('search_instance', { keywords, country, pageIndex, pageSize, filterFailureCode: true });
}

async function searchUnified(keywords, unifiedType = 'ciq', pageIndex = 1, pageSize = 10) {
  return await callTool('search_unified', { keywords, unifiedType, pageIndex, pageSize, filterFailureCode: true, searchType: 1 });
}

async function main() {
  loadConfig();
  const args = process.argv.slice(2);
  const command = args[0];
  const params = {};
  for (let i = 1; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      const value = args[i + 1];
      if (value && !value.startsWith('--')) { params[key] = value; i++; }
      else { params[key] = true; }
    }
  }
  try {
    let result;
    switch (command) {
      case 'search-code':
        result = await searchCode(params.keywords || '', params.country || 'CN', parseInt(params.pageIndex) || 1, parseInt(params.pageSize) || 10);
        break;
      case 'get-detail':
        result = await getCodeDetail(params.code || '', params.country || 'CN');
        break;
      case 'search-instance':
        result = await searchInstance(params.keywords || '', params.country || 'CN', parseInt(params.pageIndex) || 1, parseInt(params.pageSize) || 10);
        break;
      case 'search-unified':
        result = await searchUnified(params.keywords || '', params.type || 'ciq', parseInt(params.pageIndex) || 1, parseInt(params.pageSize) || 10);
        break;
      default:
        console.log('用法：hsciq-client.js [search-code|get-detail|search-instance|search-unified] --keywords xxx --country CN');
        process.exit(0);
    }
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error(`错误：${error.message}`);
    process.exit(1);
  }
}

module.exports = { callTool, searchCode, getCodeDetail, searchInstance, searchUnified, CONFIG };
if (require.main === module) main();
