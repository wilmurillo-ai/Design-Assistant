/**
 * GitHub Collaboration Complete Example
 * 演示完整的多 Agent 协作系统
 */

const TaskManager = require('./task-manager');
const AgentWorker = require('./agent-worker');
const STPIntegrator = require('./stp-integrator');
const QQNotifier = require('./qq-notifier');

// 初始化系统
const dbPath = './github-collab-complete.db';
const stp = new STPIntegrator(dbPath);
const notifier = new QQNotifier(dbPath);

// 定义不同 Agent 的任务处理函数
const taskHandlers = {
  // main agent - 负责需求分析、任务分配
  main: async (task) => {
    console.log(`[main] 分析任务：${task.name}`);
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    return {
      analysis: '需求分析完成',
      subtasks: ['任务 A', '任务 B', '任务 C'],
      estimated_time: '2 小时'
    };
  },
  
  // coder agent - 负责代码开发
  coder: async (task) => {
    console.log(`[coder] 开发任务：${task.name}`);
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    return {
      code_written: true,
      files_changed: ['file1.js', 'file2.js'],
      lines_added: 150,
      commit_hash: 'abc123'
    };
  },
  
  // checker agent - 负责测试和审查
  checker: async (task) => {
    console.log(`[checker] 检查任务：${task.name}`);
    await new Promise(resolve => setTimeout(resolve, 2500));
    
    return {
      tests_passed: 45,
      tests_failed: 2,
      code_quality: 'A',
      issues_found: ['小问题 1', '小问题 2']
    };
  },
  
  // memowriter agent - 负责文档
  memowriter: async (task) => {
    console.log(`[memowriter] 编写文档：${task.name}`);
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    return {
      docs_written: ['README.md', 'API.md'],
      word_count: 2500,
      diagrams: 3
    };
  }
};

// 创建项目
async function createProject() {
  console.log('=== 创建项目 ===\n');
  
  const project = {
    name: 'Test GitHub Project',
    description: '这是一个测试项目，用于演示多 Agent 协作',
    github_url: 'https://github.com/example/test-project',
    requirements: ['用户登录', '数据展示', 'API 接口']
  };

  const result = await stp.decomposeProject(project);
  
  console.log(`\n项目创建成功: ${result.project.name}`);
  console.log(`共创建 ${result.tasks.length} 个任务\n`);
  
  return result.project.id;
}

// 启动 Agent 集群
function startAgents() {
  console.log('=== 启动 Agent 集群 ===\n');
  
  const agents = [
    { name: 'main', handler: taskHandlers.main },
    { name: 'coder', handler: taskHandlers.coder },
    { name: 'checker', handler: taskHandlers.checker },
    { name: 'memowriter', handler: taskHandlers.memowriter }
  ];

  const workers = agents.map(agent => {
    const worker = new AgentWorker(agent.name, agent.handler, dbPath, {
      pollInterval: 3000,
      heartbeatInterval: 15000
    });
    
    // 监听任务完成，发送 QQ 通知
    const originalExecuteTask = worker.executeTask.bind(worker);
    worker.executeTask = async (task) => {
      await originalExecuteTask(task);
      notifier.onTaskCompleted(task.id);
    };
    
    worker.start();
    return worker;
  });

  return workers;
}

// 监控系统状态
function monitorStatus(workers, projectId) {
  setInterval(() => {
    console.log('\n=== 系统状态 ===');
    
    // 任务状态
    const taskManager = new TaskManager(dbPath);
    const tasks = taskManager.getTasksByProject(projectId);
    const stats = taskManager.getProjectStats(projectId);
    
    console.log(`项目进度：${stats.completed}/${stats.total} (${Math.round(stats.completed / stats.total * 100)}%)`);
    console.log(`待处理：${stats.pending}, 进行中：${stats.in_progress}, 失败：${stats.failed}`);
    
    // Agent 状态
    const agents = taskManager.getActiveAgents();
    agents.forEach(agent => {
      const status = agent.status;
      const taskName = agent.task_name || '无';
      console.log(`  ${agent.name}: ${status} - ${taskName}`);
    });
    
    taskManager.close();
    
    console.log('');
  }, 10000);
}

// 生成最终报告
async function generateFinalReport(workers, projectId) {
  console.log('\n=== 生成最终报告 ===\n');
  
  const report = stp.generateProjectReport(projectId);
  console.log(report);
  
  // 发送 QQ 通知
  await notifier.sendProjectCompletionReport(projectId);
  
  // 停止所有 Agent
  workers.forEach(worker => worker.stop());
  notifier.close();
  
  console.log('\n=== 系统关闭 ===');
  process.exit(0);
}

// 主函数
async function main() {
  try {
    console.log('🚀 GitHub Collaboration System Starting...\n');
    
    // 1. 创建项目并分解任务
    const projectId = await createProject();
    
    // 2. 启动 Agent 集群
    const workers = startAgents();
    
    // 3. 启动定时报告
    notifier.startScheduledReports();
    
    // 4. 监控系统状态
    monitorStatus(workers, projectId);
    
    // 5. 运行一段时间后生成报告并退出
    setTimeout(() => {
      generateFinalReport(workers, projectId);
    }, 120000); // 运行 2 分钟

  } catch (error) {
    console.error('系统错误:', error);
    process.exit(1);
  }
}

main();
