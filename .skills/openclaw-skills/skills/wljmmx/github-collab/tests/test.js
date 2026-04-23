/**
 * GitHub Collaboration Skill - 完整测试脚本
 */

const skill = require('./index');
const { DevAgent } = require('./dev-agent');
const { TestAgent } = require('./test-agent');

async function runTests() {
    console.log('=== GitHub Collaboration Skill 测试 ===\n');
    console.log('测试时间：', new Date().toLocaleString('zh-CN'));
    console.log('='.repeat(50) + '\n');
    
    // 测试 1: 创建项目
    console.log('=== 测试 1: 创建项目 ===\n');
    
    try {
        const project = await skill.createProject(
            '开发一个 Todo 应用，支持增删改查功能，使用 React + Node.js',
            'Todo App',
            null
        );
        
        console.log(`✅ 项目创建成功`);
        console.log(`项目名称：${project.projectName}`);
        console.log(`GitHub URL: ${project.githubUrl}`);
        console.log(`任务数：${project.taskCount}`);
        console.log(`项目 ID: ${project.projectId}\n`);
    } catch (error) {
        console.error(`❌ 项目创建失败：${error.message}\n`);
        return;
    }
    
    // 测试 2: 生成项目报告
    console.log('=== 测试 2: 生成项目报告 ===\n');
    
    try {
        const report = await skill.getProjectReport(1);
        console.log(report);
    } catch (error) {
        console.error(`❌ 生成报告失败：${error.message}\n`);
    }
    
    // 测试 3: 列出所有项目
    console.log('\n=== 测试 3: 列出所有项目 ===\n');
    
    try {
        const projects = await skill.listProjects();
        console.log(`共有 ${projects.length} 个项目`);
        projects.forEach(p => {
            console.log(`- ${p.name} (${p.github_url})`);
        });
    } catch (error) {
        console.error(`❌ 列出项目失败：${error.message}\n`);
    }
    
    // 测试 4: Dev Agent 获取任务
    console.log('\n=== 测试 4: Dev Agent 获取任务 ===\n');
    
    try {
        const devAgent = new DevAgent('dev-agent');
        await devAgent.initialize();
        const status = await devAgent.getTaskQueueStatus();
        
        console.log(`Dev Agent 任务队列状态:`);
        console.log(`总任务：${status.stats.total}`);
        console.log(`待处理：${status.stats.queued}`);
        console.log(`进行中：${status.stats.in_progress}`);
        console.log(`已完成：${status.stats.completed}`);
        console.log(`失败：${status.stats.failed}`);
        
        const task = await devAgent.getNextTask();
        if (task) {
            console.log(`\n✅ 获取到任务：${task.name} (ID: ${task.id})`);
            await devAgent.executeTask(task, {
                code: 'console.log("Implementing Todo App");',
                progress: 100
            });
        } else {
            console.log(`\n⚠️ 没有可用任务`);
        }
    } catch (error) {
        console.error(`❌ Dev Agent 测试失败：${error.message}\n`);
    }
    
    // 测试 5: Test Agent 获取任务
    console.log('\n=== 测试 5: Test Agent 获取任务 ===\n');
    
    try {
        const testAgent = new TestAgent('test-agent');
        await testAgent.initialize();
        const testStatus = await testAgent.getTaskQueueStatus();
        
        console.log(`Test Agent 任务队列状态:`);
        console.log(`总任务：${testStatus.stats.total}`);
        console.log(`待处理：${testStatus.stats.queued}`);
        console.log(`进行中：${testStatus.stats.in_progress}`);
        console.log(`已完成：${testStatus.stats.completed}`);
        console.log(`失败：${testStatus.stats.failed}`);
        
        const testTask = await testAgent.getNextTask();
        if (testTask) {
            console.log(`\n✅ 获取到测试任务：${testTask.name} (ID: ${testTask.id})`);
            await testAgent.executeTask(testTask, {
                passed: 5,
                failed: 0,
                total: 5,
                coverage: 85,
                progress: 100
            });
        } else {
            console.log(`\n⚠️ 没有可用测试任务`);
        }
    } catch (error) {
        console.error(`❌ Test Agent 测试失败：${error.message}\n`);
    }
    
    // 测试 6: 生成最终报告
    console.log('\n=== 测试 6: 生成最终报告 ===\n');
    
    try {
        const finalReport = await skill.getProjectReport(1);
        console.log(finalReport);
    } catch (error) {
        console.error(`❌ 生成最终报告失败：${error.message}\n`);
    }
    
    console.log('\n' + '='.repeat(50));
    console.log('✅ 所有测试完成！');
    console.log('='.repeat(50) + '\n');
}

// 运行测试
runTests().catch(error => {
    console.error('测试执行失败:', error);
    process.exit(1);
});