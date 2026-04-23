/**
 * 模块功能测试脚本
 * 测试所有核心模块的功能
 */

const path = require('path');

// 导入模块
const { TaskManagerEnhanced } = require('../core/task-manager-enhanced');
const { STPIntegratorEnhanced } = require('../core/stp-integrator-enhanced');

async function testTaskManager() {
    console.log('=== 测试 1: TaskManagerEnhanced ===\n');
    
    const taskManager = new TaskManagerEnhanced();
    
    try {
        // 测试创建项目
        console.log('1. 创建项目...');
        const project = await taskManager.createProject({
            name: 'Test Project',
            description: '测试项目',
            github_url: 'https://github.com/test/repo'
        });
        console.log('✅ 项目创建成功:', project.id);
        
        // 测试创建任务
        console.log('\n2. 创建任务...');
        const task = await taskManager.createTask({
            project_id: project.id,
            name: 'Test Task',
            description: '测试任务',
            priority: 10
        });
        console.log('✅ 任务创建成功:', task.id);
        
        // 测试批量创建任务
        console.log('\n3. 批量创建任务...');
        const batchTasks = await taskManager.createBatchTasks(
            project.id,
            [
                { name: 'Task 1', description: 'Desc 1', priority: 10 },
                { name: 'Task 2', description: 'Desc 2', priority: 9 },
                { name: 'Task 3', description: 'Desc 3', priority: 8 }
            ]
        );
        console.log('✅ 批量创建成功:', batchTasks.length, '个任务');
        
        // 测试任务依赖
        console.log('\n4. 任务依赖...');
        const task1 = await taskManager.createTask({
            project_id: project.id,
            name: 'Task A',
            priority: 10
        });
        const task2 = await taskManager.createTask({
            project_id: project.id,
            name: 'Task B',
            priority: 9
        });
        await taskManager.addTaskDependency(task2.id, task1.id);
        console.log('✅ 依赖添加成功：Task B depends on Task A');
        
        // 测试检查依赖
        console.log('\n5. 检查依赖...');
        const depsMet1 = await taskManager.checkTaskDependencies(task1.id);
        console.log('Task A 依赖满足:', depsMet1);
        
        const depsMet2 = await taskManager.checkTaskDependencies(task2.id);
        console.log('Task B 依赖满足:', depsMet2);
        
        // 测试分配任务
        console.log('\n6. 分配任务...');
        await taskManager.assignTask(task1.id, 'dev-agent');
        console.log('✅ Task A 已分配给 dev-agent');
        
        // 测试完成任务
        console.log('\n7. 完成任务...');
        await taskManager.completeTask(task1.id, 'dev-agent');
        console.log('✅ Task A 已完成');
        
        // 测试再次检查依赖
        console.log('\n8. 再次检查依赖...');
        const depsMet3 = await taskManager.checkTaskDependencies(task2.id);
        console.log('Task B 依赖满足:', depsMet3);
        
        // 测试项目状态
        console.log('\n9. 项目状态...');
        const status = await taskManager.getProjectStatus(project.id);
        console.log('项目状态:', status);
        
        console.log('\n✅ TaskManagerEnhanced 测试通过!\n');
        return true;
    } catch (error) {
        console.error('\n❌ TaskManagerEnhanced 测试失败:', error.message);
        console.error(error.stack);
        return false;
    }
}

async function testSTPIntegrator() {
    console.log('=== 测试 2: STPIntegratorEnhanced ===\n');
    
    const stpIntegrator = new STPIntegratorEnhanced();
    
    try {
        // 测试 STP 安装状态
        console.log('1. 检查 STP 安装状态...');
        const isInstalled = stpIntegrator.isSTPInstalled();
        console.log('STP 安装状态:', isInstalled ? '✅ 已安装' : '⚠️ 未安装 (使用模拟模式)');
        
        // 测试任务分解
        console.log('\n2. 任务分解...');
        const result = await stpIntegrator.splitTask(
            '开发一个 Todo 应用，支持增删改查功能',
            'Todo App'
        );
        const tasks = result.tasks;
        console.log('✅ 任务分解成功:', tasks.length, '个子任务');
        
        // 显示任务详情
        tasks.forEach((task, index) => {
            console.log(`   ${index + 1}. ${task.name}`);
            console.log(`      类型：${task.type}`);
            console.log(`      优先级：${task.priority}`);
            console.log(`      预估时间：${task.estimated_hours} 小时`);
            console.log(`      依赖：${task.dependencies.length > 0 ? task.dependencies.join(', ') : '无'}`);
        });
        
        // 测试执行计划
        console.log('\n3. 执行计划...');
        const executionPlan = result.executionPlan;
        console.log('✅ 执行计划生成成功:', executionPlan.length, '个步骤');
        executionPlan.forEach((plan, index) => {
            console.log(`   ${index + 1}. ${plan.taskName} -> ${plan.agentType}`);
        });
        
        console.log('\n✅ STPIntegratorEnhanced 测试通过!\n');
        return true;
    } catch (error) {
        console.error('\n❌ STPIntegratorEnhanced 测试失败:', error.message);
        console.error(error.stack);
        return false;
    }
}

async function runAllTests() {
    console.log('========================================');
    console.log('       模块功能测试开始');
    console.log('========================================\n');
    
    const results = {
        taskManager: false,
        stpIntegrator: false
    };
    
    // 测试 TaskManagerEnhanced
    results.taskManager = await testTaskManager();
    
    // 测试 STPIntegratorEnhanced
    results.stpIntegrator = await testSTPIntegrator();
    
    // 输出测试结果
    console.log('========================================');
    console.log('           测试结果汇总');
    console.log('========================================');
    console.log(`TaskManagerEnhanced:      ${results.taskManager ? '✅ 通过' : '❌ 失败'}`);
    console.log(`STPIntegratorEnhanced:    ${results.stpIntegrator ? '✅ 通过' : '❌ 失败'}`);
    
    const allPassed = results.taskManager && results.stpIntegrator;
    console.log(`\n总体结果：${allPassed ? '✅ 全部通过' : '❌ 部分失败'}`);
    console.log('========================================\n');
    
    return allPassed;
}

// 运行测试
runAllTests().catch(console.error);
