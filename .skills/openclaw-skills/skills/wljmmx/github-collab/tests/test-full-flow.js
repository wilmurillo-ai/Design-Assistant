/**
 * 全流程模拟测试脚本
 * 模拟完整的项目开发流程
 */

const path = require('path');

// 导入模块
const { TaskManagerEnhanced } = require('../core/task-manager-enhanced');
const { STPIntegratorEnhanced } = require('../core/stp-integrator-enhanced');

async function simulateFullFlow() {
    console.log('========================================');
    console.log('       全流程模拟测试开始');
    console.log('========================================\n');
    
    const results = {
        steps: [],
        success: false
    };
    
    try {
        // 步骤 1: 初始化系统
        console.log('步骤 1: 初始化系统...');
        const taskManager = new TaskManagerEnhanced();
        const stpIntegrator = new STPIntegratorEnhanced();
        console.log('✅ 系统初始化完成\n');
        results.steps.push({ step: '系统初始化', status: 'success' });
        
        // 步骤 2: 创建项目
        console.log('步骤 2: 创建项目...');
        const project = await taskManager.createProject({
            name: 'Todo App',
            description: '一个简单的待办事项应用',
            github_url: null
        });
        console.log('✅ 项目创建成功:', project.id);
        console.log('   项目名称:', project.name);
        console.log('   项目描述:', project.description);
        results.steps.push({ step: '创建项目', status: 'success', data: project });
        
        // 步骤 3: 任务分解
        console.log('\n步骤 3: 任务分解...');
        const result = await stpIntegrator.splitTask(
            '开发一个 Todo 应用，支持增删改查功能',
            project.name
        );
        const tasks = result.tasks;
        console.log('✅ 任务分解成功:', tasks.length, '个子任务');
        tasks.forEach((task, index) => {
            console.log(`   ${index + 1}. ${task.name}`);
        });
        results.steps.push({ step: '任务分解', status: 'success', data: tasks });
        
        // 步骤 4: 执行计划
        console.log('\n步骤 4: 生成执行计划...');
        const executionPlan = result.executionPlan;
        console.log('✅ 执行计划生成成功:', executionPlan.length, '个步骤');
        executionPlan.forEach((plan, index) => {
            console.log(`   ${index + 1}. ${plan.taskName} -> ${plan.agentType}`);
        });
        results.steps.push({ step: '生成执行计划', status: 'success', data: executionPlan });
        
        // 步骤 5: 批量创建任务
        console.log('\n步骤 5: 批量创建任务...');
        const createdTasks = await taskManager.createBatchTasks(
            project.id,
            tasks.map(t => ({
                name: t.name,
                description: t.description,
                priority: t.priority,
                agent_type: t.type === 'development' ? 'dev-agent' : 
                           t.type === 'testing' ? 'test-agent' : 'dev-agent'
            }))
        );
        console.log('✅ 批量创建成功:', createdTasks.length, '个任务');
        results.steps.push({ step: '批量创建任务', status: 'success', data: createdTasks });
        
        // 步骤 6: 模拟任务执行
        console.log('\n步骤 6: 模拟任务执行...');
        let completedCount = 0;
        for (const task of createdTasks) {
            // 模拟任务执行
            await taskManager.assignTask(task.id, task.agent_type);
            console.log(`   执行任务：${task.name} (${task.agent_type})`);
            
            // 模拟任务完成
            await taskManager.completeTask(task.id, task.agent_type);
            console.log(`   ✅ 任务完成：${task.name}`);
            completedCount++;
        }
        console.log(`✅ 任务执行完成：${completedCount}/${createdTasks.length}`);
        results.steps.push({ step: '任务执行', status: 'success', data: { completed: completedCount, total: createdTasks.length } });
        
        // 步骤 7: 项目状态检查
        console.log('\n步骤 7: 项目状态检查...');
        const status = await taskManager.getProjectStatus(project.id);
        console.log('✅ 项目状态:', status);
        console.log('   总任务数:', status.totalTasks);
        console.log('   已完成任务:', status.completedTasks);
        console.log('   进行中任务:', status.runningTasks);
        console.log('   待处理任务:', status.pendingTasks);
        results.steps.push({ step: '项目状态检查', status: 'success', data: status });
        
        // 步骤 8: 生成测试报告
        console.log('\n步骤 8: 生成测试报告...');
        const report = {
            projectName: project.name,
            projectId: project.id,
            totalTasks: createdTasks.length,
            completedTasks: completedCount,
            successRate: (completedCount / createdTasks.length * 100).toFixed(2) + '%',
            steps: results.steps,
            timestamp: new Date().toISOString()
        };
        console.log('✅ 测试报告生成成功');
        console.log('   项目名称:', report.projectName);
        console.log('   总任务数:', report.totalTasks);
        console.log('   完成率:', report.successRate);
        results.steps.push({ step: '生成测试报告', status: 'success', data: report });
        
        results.success = true;
        results.report = report;
        
    } catch (error) {
        console.error('\n❌ 全流程模拟测试失败:', error.message);
        console.error(error.stack);
        results.steps.push({ step: '错误', status: 'failed', data: error.message });
    }
    
    // 输出测试结果
    console.log('\n=========================================');
    console.log('           全流程测试汇总');
    console.log('=========================================');
    
    results.steps.forEach((step, index) => {
        const status = step.status === 'success' ? '✅' : '❌';
        console.log(`${index + 1}. ${step.step}: ${status}`);
    });
    
    console.log(`\n总体结果：${results.success ? '✅ 全部通过' : '❌ 部分失败'}`);
    console.log('=========================================\n');
    
    return results;
}

// 运行测试
simulateFullFlow().catch(console.error);
