/**
 * Claw Office 工作上报 - OpenClaw 钩子
 * 在任务开始和结束时自动触发上报
 */

const skill = require('./index');

/**
 * 截取任务核心关键词作为 detail，避免太长
 */
function getBriefDetail(fullText) {
  if (!fullText) return '处理任务';
  
  // 截取前 30 个字符作为简要描述
  let brief = fullText.trim().replace(/[\n\r]+/g, ' ');
  if (brief.length > 30) {
    brief = brief.substring(0, 27) + '...';
  }
  
  return brief;
}

module.exports = {
  /**
   * 任务开始前触发
   */
  beforeTask: (context) => {
    const fullTask = context.task || context.query || '处理任务';
    const detail = getBriefDetail(fullTask);
    
    // 根据任务类型判断状态
    let state = 'working';
    if (fullTask.includes('搜索') || fullTask.includes('查找') || fullTask.includes('查询') || fullTask.includes('查下')) {
      state = 'researching';
    } else if (fullTask.includes('写') || fullTask.includes('文档') || fullTask.includes('整理') || fullTask.includes('规划')) {
      state = 'writing';
    } else if (fullTask.includes('执行') || fullTask.includes('运行') || fullTask.includes('命令') || fullTask.includes('优化') || fullTask.includes('完善')) {
      state = 'executing';
    }

    skill.start(state, detail);
  },

  /**
   * 任务完成后触发
   */
  afterTask: (context, result) => {
    const fullTask = context.task || context.query || '处理任务';
    const detail = getBriefDetail(fullTask);
    skill.stop(detail);
  }
};
