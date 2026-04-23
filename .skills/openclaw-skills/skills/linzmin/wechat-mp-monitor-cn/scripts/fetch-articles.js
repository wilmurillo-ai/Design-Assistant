#!/usr/bin/env node
/**
 * 获取微信公众号文章数据
 * 用法：node fetch-articles.js --from 2026-03-01 --to 2026-03-23
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const CONFIG_FILE = path.join(process.env.HOME, '.openclaw/wechat-mp/config.json');
const TOKEN_CACHE = '/tmp/wechat-mp-token.json';

/**
 * 解析命令行参数
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const result = { from: null, to: null };
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--from' && args[i + 1]) {
      result.from = args[i + 1];
      i++;
    } else if (args[i] === '--to' && args[i + 1]) {
      result.to = args[i + 1];
      i++;
    } else if (args[i] === '--today') {
      result.from = result.to = new Date().toISOString().split('T')[0];
    } else if (args[i] === '--yesterday') {
      const yesterday = new Date(Date.now() - 86400000);
      result.from = result.to = yesterday.toISOString().split('T')[0];
    }
  }
  
  // 默认查询昨天
  if (!result.from && !result.to) {
    const yesterday = new Date(Date.now() - 86400000);
    result.from = result.to = yesterday.toISOString().split('T')[0];
  }
  
  return result;
}

/**
 * 获取 token
 */
function getToken() {
  if (!fs.existsSync(TOKEN_CACHE)) {
    console.error('❌ Token 不存在，请先运行：node get-token.js');
    process.exit(1);
  }
  
  const { token } = JSON.parse(fs.readFileSync(TOKEN_CACHE, 'utf8'));
  return token;
}

/**
 * 调用微信 API
 */
function callAPI(endpoint, body, token) {
  return new Promise((resolve, reject) => {
    const url = `https://api.weixin.qq.com/${endpoint}?access_token=${token}`;
    
    const req = https.request(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    }, (res) => {
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
          
          resolve(data);
        } catch (e) {
          reject(new Error(`解析响应失败：${response}`));
        }
      });
    });
    
    req.on('error', reject);
    req.write(JSON.stringify(body));
    req.end();
  });
}

/**
 * 获取文章数据
 */
async function fetchArticles(token, beginDate, endDate) {
  console.log(`📊 获取文章数据：${beginDate} ~ ${endDate}`);
  
  const body = {
    begin_date: beginDate,
    end_date: endDate
  };
  
  const data = await callAPI('datacube/getarticletotaldetail', body, token);
  
  if (!data.list || data.list.length === 0) {
    console.log('ℹ️  暂无文章数据');
    return [];
  }
  
  console.log(`✅ 获取到 ${data.list.length} 篇文章`);
  return data.list;
}

/**
 * 格式化文章数据
 */
function formatArticles(articles) {
  console.log('\n📋 文章列表：\n');
  
  articles.forEach((article, index) => {
    console.log(`${index + 1}. ${article.title}`);
    console.log(`   📅 日期：${article.stat_date}`);
    console.log(`   👁️  阅读：${article.int_page_read_count} 次 | ${article.int_page_read_user_count} 人`);
    console.log(`   📤 分享：${article.share_count} 次 | ${article.share_user_count} 人`);
    console.log(`   ⭐ 收藏：${article.user_read_count} 次 | ${article.user_read_user_count} 人`);
    console.log('');
  });
  
  // 汇总统计
  const totalRead = articles.reduce((sum, a) => sum + a.int_page_read_count, 0);
  const totalReadUser = articles.reduce((sum, a) => sum + a.int_page_read_user_count, 0);
  const totalShare = articles.reduce((sum, a) => sum + a.share_count, 0);
  const totalShareUser = articles.reduce((sum, a) => sum + a.share_user_count, 0);
  
  console.log('📊 汇总统计：');
  console.log(`   📝 文章数量：${articles.length} 篇`);
  console.log(`   👁️  总阅读：${totalRead} 次 | ${totalReadUser} 人`);
  console.log(`   📤 总分享：${totalShare} 次 | ${totalShareUser} 人`);
  console.log(`   📈 篇均阅读：${Math.round(totalRead / articles.length)} 次`);
}

/**
 * 主函数
 */
async function main() {
  console.log('🦆 微信公众号文章数据获取工具\n');
  
  const args = parseArgs();
  console.log(`📅 日期范围：${args.from} ~ ${args.to}\n`);
  
  // 获取 token
  const token = getToken();
  
  // 获取文章数据
  try {
    const articles = await fetchArticles(token, args.from, args.to);
    
    if (articles.length > 0) {
      formatArticles(articles);
      
      // 保存到文件
      const outputFile = `/tmp/wechat-mp-articles-${args.from}.json`;
      fs.writeFileSync(outputFile, JSON.stringify(articles, null, 2));
      console.log(`\n💾 数据已保存：${outputFile}`);
    }
  } catch (error) {
    console.error(`❌ 失败：${error.message}`);
    process.exit(1);
  }
}

main();
