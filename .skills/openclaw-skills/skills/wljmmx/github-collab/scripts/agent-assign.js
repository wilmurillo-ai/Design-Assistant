#!/usr/bin/env node

/**
 * Agent 任务分配脚本
 * 将任务分配给不同的 Agent
 */

function assignAgents(repoName, tasks) {
  const agentTasks = {
    coder: tasks.filter(t => t.type === 'code'),
    checker: tasks.filter(t => t.type === 'test'),
    writer: tasks.filter(t => t.type === 'doc')
  };

  console.log('📋 任务分配结果:');
  Object.entries(agentTasks).forEach(([agent, tasks]) => {
    if (tasks.length > 0) {
      console.log(`  - ${agent}: ${tasks.length} 个任务`);
      tasks.forEach(t => {
        console.log(`    * [${t.type.toUpperCase()}] ${t.title}`);
      });
    }
  });

  return agentTasks;
}

// 导出
module.exports = { assignAgents };
