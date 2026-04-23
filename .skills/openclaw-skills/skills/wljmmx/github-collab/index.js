/**
 * GitHub Collaboration Skill - Main Entry
 * GitHub 项目协作开发技能
 */

const path = require('path');

// 导出所有模块
module.exports = {
    // 任务管理
    TaskManager: require('./task-manager').TaskManager,
    TaskManagerEnhanced: require('./task-manager-enhanced').TaskManagerEnhanced,
    
    // Agent
    DevAgent: require('./dev-agent').DevAgent,
    TestAgent: require('./test-agent').TestAgent,
    MainAgent: require('./main-agent').MainAgent,
    
    // STP 集成
    STPIntegrator: require('./stp-integrator').STPIntegrator,
    STPIntegratorEnhanced: require('./stp-integrator-enhanced').STPIntegratorEnhanced,
    
    // 消息通知
    sendProgressUpdate: require('./openclaw-message').sendProgressUpdate,
    sendTaskCompletion: require('./openclaw-message').sendTaskCompletion,
    sendErrorNotification: require('./openclaw-message').sendErrorNotification,
    sendTaskAssignment: require('./openclaw-message').sendTaskAssignment,
    
    // QQ 通知
    QQNotifier: require('./qq-notifier').QQNotifier,
    
    // 配置
    Config: require('./config').Config
};

/**
 * 快速开始示例
 */
async function quickStart() {
    const { TaskManagerEnhanced, DevAgent, TestAgent } = module.exports;
    
    // 创建任务管理器
    const taskManager = new TaskManagerEnhanced();
    
    // 创建项目
    const project = await taskManager.createProject({
        name: 'Example Project',
        description: 'An example project',
        github_url: 'https://github.com/example/repo'
    });
    
    console.log(`Created project: ${project.id}`);
    
    // 创建任务
    const task = await taskManager.createTask({
        project_id: project.id,
        name: 'Implement feature',
        description: 'Implement new feature',
        priority: 10
    });
    
    console.log(`Created task: ${task.id}`);
    
    // 启动 Dev Agent
    const devAgent = new DevAgent('dev-agent');
    await devAgent.initialize();
    await devAgent.processQueue();
    
    // 启动 Test Agent
    const testAgent = new TestAgent('test-agent');
    await testAgent.initialize();
    await testAgent.processQueue();
}

// 如果直接运行此文件
if (require.main === module) {
    quickStart().catch(console.error);
}