#!/usr/bin/env node

/**
 * GitHub Collaboration - 全流程测试脚本
 * 测试项目的所有核心功能
 */

const path = require('path');
const fs = require('fs');

// 测试报告
let testReport = {
  name: 'GitHub Collaboration 全流程测试报告',
  timestamp: new Date().toISOString(),
  tests: [],
  summary: {
    total: 0,
    passed: 0,
    failed: 0
  }
};

// 测试辅助函数
function logTest(name, status, details = '') {
  const test = {
    name,
    status,
    timestamp: new Date().toISOString(),
    details
  };
  testReport.tests.push(test);
  testReport.summary.total++;
  testReport.summary[status === 'PASS' ? 'passed' : 'failed']++;
  
  const icon = status === 'PASS' ? '✅' : '❌';
  console.log(`${icon} ${name}`);
  if (details) {
    console.log(`   ${details}`);
  }
}

// 清理测试环境
function cleanup() {
  console.log('\n🧹 清理测试环境...');
  
  const testFiles = [
    './github-collab-test.db',
    './controller-state-test.json',
    '.github-collab-config-test.json'
  ];
  
  testFiles.forEach(file => {
    if (fs.existsSync(file)) {
      fs.unlinkSync(file);
      console.log(`   删除：${file}`);
    }
  });
}

// 测试 1: 数据库初始化
async function testDatabaseInit() {
  console.log('\n📊 测试 1: 数据库初始化');
  
  try {
    const { TaskManager } = require('./core/task-manager');
    const tm = new TaskManager('./github-collab-test.db');
    
    // 验证表创建
    const tables = tm.db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all();
    const tableNames = tables.map(t => t.name);
    
    const requiredTables = [
      'projects',
      'tasks',
      'agents',
      'agent_task_queue',
      'task_logs'
    ];
    
    const missingTables = requiredTables.filter(t => !tableNames.includes(t));
    
    if (missingTables.length === 0) {
      logTest('数据库表创建', 'PASS', `创建了${tableNames.length}个表`);
    } else {
      logTest('数据库表创建', 'FAIL', `缺少表：${missingTables.join(', ')}`);
    }
    
    tm.close();
    return true;
  } catch (error) {
    logTest('数据库初始化', 'FAIL', error.message);
    return false;
  }
}

// 测试 2: 项目创建
async function testProjectCreation() {
  console.log('\n📦 测试 2: 项目创建');
  
  try {
    const { TaskManager } = require('./core/task-manager');
    const tm = new TaskManager('./github-collab-test.db');
    
    const project = tm.createProject({
      name: 'Test Project',
      github_url: 'https://github.com/test/project',
      description: 'A test project for validation'
    });
    
    if (project.id && project.name === 'Test Project') {
      logTest('项目创建', 'PASS', `ID: ${project.id}, 名称：${project.name}`);
      return { tm, projectId: project.id };
    } else {
      logTest('项目创建', 'FAIL', '返回数据不正确');
      tm.close();
      return null;
    }
  } catch (error) {
    logTest('项目创建', 'FAIL', error.message);
    return null;
  }
}

// 测试 3: 任务创建
async function testTaskCreation(tm, projectId) {
  console.log('\n📝 测试 3: 任务创建');
  
  try {
    const tasks = [
      {
        name: 'Implement Feature A',
        description: 'Implement feature A with all requirements',
        priority: 10
      },
      {
        name: 'Implement Feature B',
        description: 'Implement feature B',
        priority: 5
      },
      {
        name: 'Fix Bug C',
        description: 'Fix critical bug C',
        priority: 8
      }
    ];
    
    const createdTasks = [];
    for (const task of tasks) {
      const created = tm.createTask({
        project_id: projectId,
        ...task
      });
      createdTasks.push(created);
    }
    
    if (createdTasks.length === 3) {
      logTest('批量任务创建', 'PASS', `创建了${createdTasks.length}个任务`);
      return createdTasks;
    } else {
      logTest('任务创建', 'FAIL', '任务数量不匹配');
      return null;
    }
  } catch (error) {
    logTest('任务创建', 'FAIL', error.message);
    return null;
  }
}

// 测试 4: Agent 注册
async function testAgentRegistration(tm) {
  console.log('\n🤖 测试 4: Agent 注册');
  
  try {
    // 注册 Dev Agent
    tm.updateAgentStatus('dev-agent-1', 'idle');
    tm.updateAgentStatus('dev-agent-2', 'idle');
    tm.updateAgentStatus('test-agent-1', 'idle');
    
    const agents = tm.getActiveAgents();
    
    if (agents.length === 3) {
      logTest('Agent 注册', 'PASS', `注册了${agents.length}个 Agent`);
      return agents;
    } else {
      logTest('Agent 注册', 'FAIL', `期望 3 个 Agent，实际${agents.length}个`);
      return null;
    }
  } catch (error) {
    logTest('Agent 注册', 'FAIL', error.message);
    return null;
  }
}

// 测试 5: 任务分配
async function testTaskAssignment(tm, tasks) {
  console.log('\n🔄 测试 5: 任务分配');
  
  try {
    // 分配任务给不同 Agent
    const assignment1 = tm.assignTaskToAgent(tasks[0].id, 'dev-agent-1');
    const assignment2 = tm.assignTaskToAgent(tasks[1].id, 'dev-agent-2');
    const assignment3 = tm.assignTaskToAgent(tasks[2].id, 'test-agent-1');
    
    if (assignment1 && assignment2 && assignment3) {
      logTest('任务分配', 'PASS', `分配了 3 个任务给不同 Agent`);
      
      // 验证任务状态
      const task1 = tm.db.prepare('SELECT * FROM tasks WHERE id = ?').get(tasks[0].id);
      if (task1.status === 'assigned' && task1.assigned_agent === 'dev-agent-1') {
        logTest('任务状态更新', 'PASS', '任务状态正确更新为 assigned');
      } else {
        logTest('任务状态更新', 'FAIL', '任务状态未正确更新');
      }
      
      return true;
    } else {
      logTest('任务分配', 'FAIL', '分配失败');
      return false;
    }
  } catch (error) {
    logTest('任务分配', 'FAIL', error.message);
    return false;
  }
}

// 测试 6: Agent 任务队列
async function testAgentTaskQueue(tm) {
  console.log('\n📋 测试 6: Agent 任务队列');
  
  try {
    const devAgent1Queue = tm.getAgentTaskQueue('dev-agent-1');
    const devAgent2Queue = tm.getAgentTaskQueue('dev-agent-2');
    const testAgent1Queue = tm.getAgentTaskQueue('test-agent-1');
    
    if (devAgent1Queue.length === 1 && 
        devAgent2Queue.length === 1 && 
        testAgent1Queue.length === 1) {
      logTest('Agent 任务队列', 'PASS', '每个 Agent 有正确的任务队列');
      return true;
    } else {
      logTest('Agent 任务队列', 'FAIL', 
        `dev-agent-1: ${devAgent1Queue.length}, dev-agent-2: ${devAgent2Queue.length}, test-agent-1: ${testAgent1Queue.length}`);
      return false;
    }
  } catch (error) {
    logTest('Agent 任务队列', 'FAIL', error.message);
    return false;
  }
}

// 测试 7: Agent 获取任务
async function testAgentGetTask(tm) {
  console.log('\n🎯 测试 7: Agent 获取任务');
  
  try {
    const task = tm.getAgentNextTask('dev-agent-1');
    
    if (task) {
      logTest('Agent 获取任务', 'PASS', 
        `任务：${task.name}, ID: ${task.id}`);
      
      // 验证任务状态更新（检查 tasks 表）
      const taskStatus = tm.db.prepare('SELECT status FROM tasks WHERE id = ?').get(task.id);
      if (taskStatus.status === 'in_progress') {
        logTest('任务状态流转', 'PASS', '任务状态从 queued 变为 in_progress');
      } else {
        logTest('任务状态流转', 'FAIL', `期望 in_progress，实际${taskStatus.status}`);
      }
      
      return task;
    } else {
      logTest('Agent 获取任务', 'FAIL', '没有可用任务');
      return null;
    }
  } catch (error) {
    logTest('Agent 获取任务', 'FAIL', error.message);
    return null;
  }
}

// 测试 8: 任务完成
async function testTaskCompletion(tm, task) {
  console.log('\n✅ 测试 8: 任务完成');
  
  try {
    const result = {
      code: 'console.log("Hello World");',
      tests: ['test1', 'test2'],
      documentation: 'Feature documentation'
    };
    
    tm.completeAgentTask('dev-agent-1', task.id, JSON.stringify(result), null);
    
    // 验证任务状态
    const updatedTask = tm.db.prepare('SELECT * FROM tasks WHERE id = ?').get(task.id);
    
    if (updatedTask.status === 'completed' && updatedTask.completed_at) {
      logTest('任务完成', 'PASS', 
        `任务${task.id}标记为 completed`);
      
      // 验证 Agent 状态恢复
      const agent = tm.db.prepare('SELECT * FROM agents WHERE name = ?').get('dev-agent-1');
      if (agent.status === 'idle') {
        logTest('Agent 状态恢复', 'PASS', 'Agent 状态恢复为 idle');
      } else {
        logTest('Agent 状态恢复', 'FAIL', `期望 idle，实际${agent.status}`);
      }
      
      return true;
    } else {
      logTest('任务完成', 'FAIL', '任务状态未正确更新');
      return false;
    }
  } catch (error) {
    logTest('任务完成', 'FAIL', error.message);
    return false;
  }
}

// 测试 9: 任务日志
async function testTaskLogs(tm) {
  console.log('\n📜 测试 9: 任务日志');
  
  try {
    const logs = tm.getTaskLogs(1);
    
    if (logs.length > 0) {
      logTest('任务日志记录', 'PASS', `记录了${logs.length}条日志`);
      
      // 验证日志内容
      const actions = logs.map(l => l.action);
      if (actions.includes('created') && actions.includes('assigned')) {
        logTest('日志完整性', 'PASS', '包含关键操作日志');
      } else {
        logTest('日志完整性', 'WARN', `日志动作：${actions.join(', ')}`);
      }
      
      return true;
    } else {
      logTest('任务日志记录', 'FAIL', '没有日志记录');
      return false;
    }
  } catch (error) {
    logTest('任务日志记录', 'FAIL', error.message);
    return false;
  }
}

// 测试 10: 进度报告
async function testProgressReport(tm) {
  console.log('\n📊 测试 10: 进度报告');
  
  try {
    const report = tm.generateProgressReport();
    
    if (report && report.length > 0) {
      logTest('进度报告生成', 'PASS', `报告长度：${report.length}字符`);
      
      // 验证报告内容
      if (report.includes('项目进度报告') && 
          report.includes('总体统计') && 
          report.includes('任务列表')) {
        logTest('报告内容完整性', 'PASS', '包含所有必要部分');
      } else {
        logTest('报告内容完整性', 'FAIL', '缺少必要部分');
      }
      
      // 保存报告
      fs.writeFileSync('./test-progress-report.md', report);
      logTest('报告保存', 'PASS', '已保存到 test-progress-report.md');
      
      return true;
    } else {
      logTest('进度报告生成', 'FAIL', '报告为空');
      return false;
    }
  } catch (error) {
    logTest('进度报告生成', 'FAIL', error.message);
    return false;
  }
}

// 测试 11: 项目统计
async function testProjectStats(tm, projectId) {
  console.log('\n📈 测试 11: 项目统计');
  
  try {
    const stats = tm.getProjectStats(projectId);
    
    if (stats.total > 0) {
      logTest('项目统计', 'PASS', 
        `总任务：${stats.total}, 已完成：${stats.completed}, 进行中：${stats.in_progress}`);
      
      // 验证统计准确性
      const tasks = tm.getProjectTasks(projectId);
      if (stats.total === tasks.length) {
        logTest('统计准确性', 'PASS', '统计与实际情况一致');
      } else {
        logTest('统计准确性', 'FAIL', `期望${tasks.length}，实际${stats.total}`);
      }
      
      return stats;
    } else {
      logTest('项目统计', 'FAIL', '没有任务');
      return null;
    }
  } catch (error) {
    logTest('项目统计', 'FAIL', error.message);
    return null;
  }
}

// 测试 12: Agent 工作循环（模拟）
async function testAgentWorkLoop() {
  console.log('\n🔄 测试 12: Agent 工作循环（模拟）');
  
  try {
    const { DevAgent } = require('./agents/dev-agent');
    const devAgent = new DevAgent('test-dev-agent');
    
    // 初始化
    await devAgent.initialize();
    logTest('Agent 初始化', 'PASS', 'DevAgent 初始化成功');
    
    // 获取任务队列状态
    const status = await devAgent.getTaskQueueStatus();
    logTest('任务队列状态', 'PASS', 
      `总任务：${status.stats.total}, 待处理：${status.stats.queued}`);
    
    return true;
  } catch (error) {
    logTest('Agent 工作循环', 'FAIL', error.message);
    return false;
  }
}

// 主测试流程
async function runTests() {
  console.log('🚀 开始 GitHub Collaboration 全流程测试');
  console.log('='.repeat(60));
  
  try {
    // 清理测试环境
    cleanup();
    
    // 测试 1: 数据库初始化
    await testDatabaseInit();
    
    // 测试 2-11: 核心功能测试
    const { TaskManager } = require('./core/task-manager');
    const tm = new TaskManager('./github-collab-test.db');
    
    const projectResult = await testProjectCreation();
    if (!projectResult) {
      tm.close();
      generateReport();
      return;
    }
    
    const tasks = await testTaskCreation(tm, projectResult.projectId);
    if (!tasks) {
      tm.close();
      generateReport();
      return;
    }
    
    await testAgentRegistration(tm);
    await testTaskAssignment(tm, tasks);
    await testAgentTaskQueue(tm);
    
    const task = await testAgentGetTask(tm);
    if (task) {
      await testTaskCompletion(tm, task);
    }
    
    await testTaskLogs(tm);
    await testProgressReport(tm);
    await testProjectStats(tm, projectResult.projectId);
    
    // 测试 12: Agent 工作循环
    await testAgentWorkLoop();
    
    // 关闭数据库
    tm.close();
    
    // 生成报告
    generateReport();
    
  } catch (error) {
    console.error('测试过程中发生错误:', error);
    logTest('整体测试', 'FAIL', error.message);
    generateReport();
  }
}

// 生成测试报告
function generateReport() {
  console.log('\n' + '='.repeat(60));
  console.log('📊 测试报告');
  console.log('='.repeat(60));
  console.log(`测试时间：${testReport.timestamp}`);
  console.log(`总测试数：${testReport.summary.total}`);
  console.log(`通过：${testReport.summary.passed}`);
  console.log(`失败：${testReport.summary.failed}`);
  console.log(`通过率：${((testReport.summary.passed / testReport.summary.total) * 100).toFixed(2)}%`);
  console.log('='.repeat(60));
  
  // 保存详细报告
  const reportPath = './test-report.json';
  fs.writeFileSync(reportPath, JSON.stringify(testReport, null, 2));
  console.log(`\n📄 详细报告已保存到：${reportPath}`);
  
  // 显示失败测试
  if (testReport.summary.failed > 0) {
    console.log('\n❌ 失败的测试:');
    testReport.tests
      .filter(t => t.status === 'FAIL')
      .forEach(t => console.log(`   - ${t.name}: ${t.details}`));
  }
}

// 运行测试
runTests();