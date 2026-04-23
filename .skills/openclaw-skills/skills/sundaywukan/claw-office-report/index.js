/**
 * Claw Office 工作自动上报 Skill
 * 自动上报工作状态到 Claw Office 微信小程序，静默执行不打扰对话
 */

const { exec } = require('child_process');
const os = require('os');
const path = require('path');

// 从环境变量获取 Claw Key
const CLAW_OFFICE_KEY = process.env.CLAW_OFFICE_KEY;
const API_BASE = process.env.CLAW_OFFICE_API || 'https://clawoffice.zjhzwukan.xyz/api';
const API_URL = `${API_BASE}/user/report-work`;

/**
 * 静默执行 curl 上报
 */
function report(action, state = 'working', detail = '') {
  if (!CLAW_OFFICE_KEY) {
    // 未配置 Key，静默忽略
    return;
  }

  const body = {};
  body.clawKey = CLAW_OFFICE_KEY;
  body.action = action;
  body.state = state;
  
  // 只有 stop 时才带 detail，start 时不带
  if (action === 'stop' && detail) {
    body.detail = detail;
  }

  const bodyStr = JSON.stringify(body);

  const cmd = `curl -s -X POST "${API_URL}" -H "Content-Type: application/json" -d '${body}' >/dev/null 2>&1 &`;
  
  exec(cmd, (error) => {
    // 静默处理任何错误
    if (error) {
      console.debug('[claw-office-report]', error.message);
    }
  });
}

/**
 * 开始工作
 * @param {string} state 工作状态
 * @param {string} detail 任务描述
 */
function start(state = 'working', detail = '') {
  report('start', state, detail);
}

/**
 * 结束工作
 */
function stop(detail = '') {
  report('stop', 'idle', detail);
}

/**
 * 更新工作状态
 * @param {string} state 工作状态
 * @param {string} detail 任务描述
 */
function update(state, detail = '') {
  report('update', state, detail);
}

module.exports = {
  start,
  stop,
  update,
  report
};
