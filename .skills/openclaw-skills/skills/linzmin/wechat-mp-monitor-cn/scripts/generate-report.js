#!/usr/bin/env node
/**
 * 生成微信公众号日报
 * 用法：node generate-report.js --date 2026-03-23
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

/**
 * 生成日报 Markdown
 */
function generateDailyReport(articles, date) {
  const totalRead = articles.reduce((sum, a) => sum + a.int_page_read_count, 0);
  const totalReadUser = articles.reduce((sum, a) => sum + a.int_page_read_user_count, 0);
  const totalShare = articles.reduce((sum, a) => sum + a.share_count, 0);
  const totalShareUser = articles.reduce((sum, a) => sum + a.share_user_count, 0);
  
  let markdown = `# 📊 公众号日报 - ${date}\n\n`;
  
  markdown += `## 今日概览\n`;
  markdown += `- 📝 发文数量：**${articles.length}** 篇\n`;
  markdown += `- 👁️ 总阅读量：**${totalRead}** | 人数：**${totalReadUser}**\n`;
  markdown += `- 📤 分享次数：**${totalShare}** | 人数：**${totalShareUser}**\n`;
  markdown += `- 📈 篇均阅读：**${Math.round(totalRead / articles.length)}** 次\n\n`;
  
  markdown += `## 文章详情\n\n`;
  
  // 按阅读量排序
  const sorted = [...articles].sort((a, b) => b.int_page_read_count - a.int_page_read_count);
  
  sorted.forEach((article, index) => {
    markdown += `### ${index + 1}. ${article.title}\n\n`;
    markdown += `| 指标 | 次数 | 人数 |\n`;
    markdown += `|------|------|------|\n`;
    markdown += `| 阅读 | ${article.int_page_read_count} | ${article.int_page_read_user_count} |\n`;
    markdown += `| 分享 | ${article.share_count} | ${article.share_user_count} |\n`;
    markdown += `| 收藏 | ${article.user_read_count} | ${article.user_read_user_count} |\n\n`;
  });
  
  markdown += `---\n`;
  markdown += `*生成时间：${new Date().toISOString().split('T')[0]}*\n`;
  
  return markdown;
}

/**
 * 发送报告到微信
 */
function sendToWechat(markdown, notifyUser) {
  const tempFile = '/tmp/wechat-mp-report.md';
  fs.writeFileSync(tempFile, markdown);
  
  const cmd = `openclaw message send --channel openclaw-weixin --account d72d5b576646-im-bot --target "${notifyUser}" --message "$(cat ${tempFile})"`;
  
  try {
    execSync(cmd, { stdio: 'inherit' });
    console.log('✅ 报告已发送到微信');
  } catch (error) {
    console.error('❌ 发送失败:', error.message);
  }
}

/**
 * 主函数
 */
function main() {
  const args = process.argv.slice(2);
  let date = new Date().toISOString().split('T')[0];
  let send = false;
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--date' && args[i + 1]) {
      date = args[i + 1];
      i++;
    } else if (args[i] === '--send') {
      send = true;
    }
  }
  
  console.log(`🦆 生成公众号日报：${date}\n`);
  
  // 读取文章数据
  const dataFile = `/tmp/wechat-mp-articles-${date}.json`;
  if (!fs.existsSync(dataFile)) {
    console.error(`❌ 数据文件不存在：${dataFile}`);
    console.error('请先运行：node fetch-articles.js --date ' + date);
    process.exit(1);
  }
  
  const articles = JSON.parse(fs.readFileSync(dataFile, 'utf8'));
  
  if (articles.length === 0) {
    console.log('ℹ️  当日无文章');
    return;
  }
  
  // 生成报告
  const markdown = generateDailyReport(articles, date);
  
  // 保存到文件
  const reportFile = `/tmp/wechat-mp-daily-${date}.md`;
  fs.writeFileSync(reportFile, markdown);
  console.log(`💾 报告已保存：${reportFile}`);
  
  // 发送到微信
  if (send) {
    const config = JSON.parse(fs.readFileSync(
      path.join(process.env.HOME, '.openclaw/wechat-mp/config.json'),
      'utf8'
    ));
    sendToWechat(markdown, config.notifyUser);
  } else {
    console.log('\n📄 报告预览：');
    console.log(markdown);
    console.log('\n💡 使用 --send 参数发送到微信');
  }
}

main();
