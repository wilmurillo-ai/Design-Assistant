#!/usr/bin/env node

/**
 * 任务拆解脚本
 * 将复杂任务拆解为编码、测试、文档三类 TODO
 */

function breakdownTask(task) {
  const tasks = [];

  // 默认任务分类
  tasks.push({
    type: 'code',
    title: '实现核心功能模块',
    description: `开发 ${task} 的核心功能模块`,
    priority: 'high'
  });

  tasks.push({
    type: 'test',
    title: '编写单元测试',
    description: `为核心功能编写测试用例，确保代码质量`,
    priority: 'medium'
  });

  tasks.push({
    type: 'doc',
    title: '编写项目文档',
    description: '编写 README.md 和 API 文档',
    priority: 'medium'
  });

  tasks.push({
    type: 'doc',
    title: '编写操作手册',
    description: '编写用户操作手册和部署指南',
    priority: 'low'
  });

  return tasks;
}

// 导出
module.exports = { breakdownTask };
