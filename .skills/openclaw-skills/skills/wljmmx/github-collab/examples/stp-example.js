/**
 * STP Integration Example - STP 集成示例
 * 展示 STP 任务规划功能
 */

const { 
    TaskManagerEnhanced, 
    DevAgent, 
    TestAgent,
    STPIntegratorEnhanced
} = require('../skills/github-collab');

async function runSTPExample() {
    console.log('=== STP Integration Example ===\n');
    
    // 1. 创建任务管理器
    const taskManager = new TaskManagerEnhanced();
    
    // 2. 创建项目
    const project = await taskManager.createProject({
        name: 'STP Example Project',
        description: 'Demonstrating STP task planning',
        github_url: 'https://github.com/example/stp-repo'
    });
    
    console.log('✅ Created project:', project.id);
    
    // 3. 创建 STP 集成器
    const stp = new STPIntegratorEnhanced();
    
    // 4. 定义复杂任务
    const complexTask = 'Build a full-stack e-commerce application with user authentication, product catalog, shopping cart, and payment integration';
    const techStack = 'React, Node.js, Express, MongoDB, Stripe API';
    
    console.log('📝 Complex Task:', complexTask);
    console.log('🛠️  Tech Stack:', techStack);
    console.log();
    
    // 5. 使用 STP 拆分任务
    const stpResult = await stp.splitTask(
        complexTask,
        techStack,
        { 
            deadline: '2024-12-31',
            include_dependencies: true
        }
    );
    
    console.log('✅ STP Analysis Complete');
    console.log('   - Split into', stpResult.tasks.length, 'subtasks');
    console.log('   - Execution plan generated');
    console.log();
    
    // 6. 显示拆分后的任务
    console.log('📋 Split Tasks:');
    stpResult.tasks.forEach((task, index) => {
        console.log(`   ${index + 1}. [${task.type}] ${task.name}`);
        console.log(`      Priority: ${task.priority}`);
        console.log(`      Estimated Hours: ${task.estimated_hours}`);
        if (task.dependencies && task.dependencies.length > 0) {
            console.log(`      Dependencies: ${task.dependencies.join(', ')}`);
        }
        console.log();
    });
    
    // 7. 显示执行计划
    console.log('📅 Execution Plan:');
    stpResult.executionPlan.forEach((phase, index) => {
        console.log(`   Phase ${index + 1}: ${phase.name}`);
        console.log(`      Tasks: ${phase.tasks.join(', ')}`);
        console.log(`      Duration: ${phase.duration} hours`);
        console.log();
    });
    
    // 8. 批量创建任务
    const tasks = [];
    for (const stpTask of stpResult.tasks) {
        const task = await taskManager.createTask({
            project_id: project.id,
            name: stpTask.name,
            description: stpTask.description,
            priority: stpTask.priority,
            type: stpTask.type,
            estimated_hours: stpTask.estimated_hours
        });
        tasks.push(task);
    }
    
    console.log('✅ Created', tasks.length, 'tasks in task manager');
    
    // 9. 设置任务依赖
    for (const stpTask of stpResult.tasks) {
        const task = tasks.find(t => t.name === stpTask.name);
        if (task && stpTask.dependencies) {
            for (const depName of stpTask.dependencies) {
                const depTask = tasks.find(t => t.name === depName);
                if (depTask) {
                    taskManager.addTaskDependency(task.id, depTask.id);
                }
            }
        }
    }
    
    console.log('✅ Set up task dependencies');
    
    // 10. 验证依赖关系
    const validation = await stp.validateDependencies(stpResult.tasks);
    console.log('✅ Dependency validation:', validation.valid ? 'PASSED' : 'FAILED');
    
    // 11. 分配任务
    const devAgent = new DevAgent('dev-agent-1');
    await devAgent.initialize();
    
    for (const task of tasks) {
        const dependenciesMet = taskManager.checkTaskDependencies(task.id);
        if (dependenciesMet) {
            await taskManager.assignTask(task.id, 'dev-agent-1');
        }
    }
    
    console.log('✅ Tasks assigned to dev-agent-1');
    
    // 12. Dev Agent 处理任务
    await devAgent.processQueue();
    
    // 13. 创建测试任务
    const testTask = await taskManager.createTask({
        project_id: project.id,
        name: 'End-to-End Testing',
        description: 'Test the complete e-commerce application',
        priority: 1,
        type: 'testing'
    });
    
    // 添加依赖
    for (const task of tasks) {
        taskManager.addTaskDependency(testTask.id, task.id);
    }
    
    const testAgent = new TestAgent('test-agent-1');
    await testAgent.initialize();
    
    const testDependenciesMet = taskManager.checkTaskDependencies(testTask.id);
    if (testDependenciesMet) {
        await taskManager.assignTask(testTask.id, 'test-agent-1');
        await testAgent.processQueue();
    }
    
    console.log('✅ STP Example Completed Successfully');
    
    // 14. 显示项目状态
    const projectStatus = await taskManager.getProjectStatus(project.id);
    console.log('\n📊 Project Status:');
    console.log(`   Name: ${projectStatus.project.name}`);
    console.log(`   Total Tasks: ${projectStatus.totalTasks}`);
    console.log(`   Completed: ${projectStatus.completedTasks}`);
    console.log(`   Progress: ${projectStatus.progress}%`);
}

// 运行示例
runSTPExample().catch(console.error);