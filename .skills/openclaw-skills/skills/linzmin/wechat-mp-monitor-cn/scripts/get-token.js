#!/usr/bin/env node
/**
 * 获取微信公众号 access_token
 * 用法：node get-token.js
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// 配置路径
const CONFIG_FILE = path.join(process.env.HOME, '.openclaw/wechat-mp/config.json');
const TOKEN_CACHE = '/tmp/wechat-mp-token.json';

/**
 * 读取配置
 */
function loadConfig() {
  if (!fs.existsSync(CONFIG_FILE)) {
    console.error(`❌ 配置文件不存在：${CONFIG_FILE}`);
    console.error('请先创建配置文件：');
    console.error(`mkdir -p ~/.openclaw/wechat-mp`);
    console.error(`cat > ~/.openclaw/wechat-mp/config.json << 'EOF'`);
    console.error(`{`);
    console.error(`  "appId": "你的 APPID",`);
    console.error(`  "appSecret": "你的 APPSECRET",`);
    console.error(`  "notifyUser": "你的微信 ID@im.wechat"`);
    console.error(`}`);
    console.error(`EOF`);
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
}

/**
 * 获取缓存的 token
 */
function getCachedToken() {
  if (!fs.existsSync(TOKEN_CACHE)) {
    return null;
  }
  
  try {
    const { token, expiresAt } = JSON.parse(fs.readFileSync(TOKEN_CACHE, 'utf8'));
    
    // 提前 5 分钟刷新
    if (Date.now() < expiresAt - 300000) {
      console.log('✅ 使用缓存的 token');
      return token;
    }
    
    console.log('⏰ Token 即将过期，需要刷新');
    return null;
  } catch (e) {
    console.warn('⚠️ 读取缓存失败:', e.message);
    return null;
  }
}

/**
 * 刷新 token
 */
async function refreshToken(appId, appSecret) {
  console.log('🔄 正在获取新的 access_token...');
  
  const url = `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${appId}&secret=${appSecret}`;
  
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      const chunks = [];
      res.on('data', chunk => chunks.push(chunk));
      res.on('end', () => {
        const response = Buffer.concat(chunks).toString('utf8');
        try {
          const data = JSON.parse(response);
          
          if (data.errcode) {
            reject(new Error(`微信 API 错误：${data.errcode} - ${data.errmsg}`));
            return;
          }
          
          // 缓存 token（提前 5 分钟过期）
          const expiresAt = Date.now() + (data.expires_in - 300) * 1000;
          fs.writeFileSync(TOKEN_CACHE, JSON.stringify({
            token: data.access_token,
            expiresAt,
            obtainedAt: new Date().toISOString()
          }, null, 2));
          
          console.log(`✅ Token 获取成功，有效期：${Math.floor((expiresAt - Date.now()) / 60000)} 分钟`);
          resolve(data.access_token);
        } catch (e) {
          reject(new Error(`解析响应失败：${response}`));
        }
      });
    }).on('error', reject);
  });
}

/**
 * 主函数
 */
async function main() {
  console.log('🦆 微信公众号 Token 管理工具\n');
  
  // 1. 尝试获取缓存
  const cached = getCachedToken();
  if (cached) {
    console.log(`\n✅ Token: ${cached.substring(0, 20)}...`);
    return;
  }
  
  // 2. 读取配置
  const config = loadConfig();
  console.log(`📋 公众号：${config.appId}`);
  
  // 3. 刷新 token
  try {
    const token = await refreshToken(config.appId, config.appSecret);
    console.log(`\n✅ Token: ${token.substring(0, 20)}...`);
    console.log(`💾 已缓存到：${TOKEN_CACHE}`);
  } catch (error) {
    console.error(`❌ 失败：${error.message}`);
    process.exit(1);
  }
}

main();
