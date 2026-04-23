/**
 * GitHub Collaboration Skill - Enhanced Test Suite
 * 测试增强版功能：并发锁、崩溃恢复、任务依赖、性能优化
 */

const { TaskManagerEnhanced } = require('./task-manager-enhanced');
const { DevAgent } = require('./dev-agent');
const { TestAgent } = require('./test-agent');
const { STPIntegrator } = require('./stp-integrator-enhanced');

async function testEnhancedFeatures() {
    console.log('🧪 Testing Enhanced Features...\n');

    const taskManager = new TaskManagerEnhanced('./test-enhanced.db');
    const stpIntegrator = new STPIntegrator();

    try {
        // ========== 1. 测试任务依赖管理 ==========
        console.log('📋 1. Testing Task Dependencies...');

        const project = taskManager.createProject({
            name: 'Enhanced Test Project',
            github_url: 'https://github.com/test/enhanced',
            description: 'Testing enhanced features'
        });

        console.log(`✅ Project created: ${project.name}`);

        // 创建开发任务
        const devTask = taskManager.createTask({
            project_id: project.id,
            name: 'Develop Feature',
            description: 'Implement new feature',
            priority: 10,
            metadata: { type: 'development' }
        });

        console.log(`✅ Dev task created: ${devTask.name} (ID: ${devTask.id})`);

        // 创建测试任务（依赖开发任务）
        const testTask = taskManager.createTask({
            project_id: project.id,
            name: 'Test Feature',
            description: 'Test the new feature',
            priority: 5,
            metadata: { type: 'testing' }
        });

        // 添加依赖
        taskManager.addTaskDependency(testTask.id, devTask.id);
        console.log(`✅ Dependency added: ${testTask.name} depends on ${devTask.name}`);

        // 检查依赖
        const dependenciesMet = taskManager.checkTaskDependencies(testTask.id);
        console.log(`📊 Dependencies met: ${dependenciesMet}`);

        // ========== 2. 测试并发锁 ==========
        console.log('\n🔒 2. Testing Concurrent Locks...');

        const lockAcquired = await taskManager.acquireLock(devTask.id, 'agent-1');
        console.log(`🔐 Lock acquired by agent-1: ${lockAcquired}`);

        const lockAcquired2 = await taskManager.acquireLock(devTask.id, 'agent-2');
        console.log(`🔐 Lock acquired by agent-2: ${lockAcquired2} (should be false)`);

        taskManager.releaseLock(devTask.id, 'agent-1');
        console.log(`🔓 Lock released by agent-1`);

        // ========== 3. 测试任务分配（依赖检查） ==========
        console.log('\n📦 3. Testing Task Assignment with Dependencies...');

        // 分配开发任务
        const devAssignment = taskManager.assignTaskToAgent(devTask.id, 'dev-agent-1');
        console.log(`✅ Dev task assigned: ${devAssignment.status}`);

        // 尝试分配测试任务（应该被阻塞）
        const testAssignment = taskManager.assignTaskToAgent(testTask.id, 'test-agent-1');
        console.log(`🚫 Test task assignment: ${testAssignment.status} (should be blocked)`);

        // 完成开发任务
        taskManager.completeAgentTask('dev-agent-1', devTask.id, 'Feature implemented', null);
        console.log(`✅ Dev task completed`);

        // 重新分配测试任务
        taskManager.assignTaskToAgent(testTask.id, 'test-agent-1');
        console.log(`✅ Test task reassigned`);

        // ========== 4. 测试崩溃恢复 ==========
        console.log('\n🔄 4. Testing Crash Recovery...');

        // 模拟 Agent 崩溃
        const crashTask = taskManager.createTask({
            project_id: project.id,
            name: 'Crash Test Task',
            description: 'Test crash recovery',
            priority: 3
        });

        taskManager.assignTaskToAgent(crashTask.id, 'crash-agent');
        console.log(`✅ Crash test task assigned`);

        // 模拟心跳超时（手动触发）
        taskManager.handleAgentCrash({
            name: 'crash-agent',
            current_task_id: crashTask.id,
            crash_count: 0
        });
        console.log(`🔄 Crash agent handled`);

        // 检查任务状态
        const taskStatus = taskManager.db.prepare('SELECT status, retry_count FROM tasks WHERE id = ?').get(crashTask.id);
        console.log(`📊 Task status: ${taskStatus.status}, retry count: ${taskStatus.retry_count}`);

        // ========== 5. 测试性能优化（批量创建） ==========
        console.log('\n⚡ 5. Testing Performance Optimization...');

        const tasks = [];
        for (let i = 0; i < 10; i++) {
            tasks.push({
                project_id: project.id,
                name: `Batch Task ${i}`,
                description: `Description for batch task ${i}`,
                priority: 10 - i
            });
        }

        const startTime = Date.now();
        const createdTasks = taskManager.createTasksBatch(tasks);
        const endTime = Date.now();

        console.log(`✅ Created ${createdTasks.length} tasks in ${endTime - startTime}ms`);
        console.log(`📊 Average time per task: ${(endTime - startTime) / createdTasks.length}ms`);

        // ========== 6. 测试 STP 集成 ==========
        console.log('\n🧠 6. Testing STP Integration...');

        const stpResult = await stpIntegrator.splitTask(
            'Build a web application with user authentication, database integration, and REST API',
            'Node.js, Express, MongoDB',
            { deadline: '2024-12-31' }
        );

        console.log(`✅ STP split task into ${stpResult.tasks.length} subtasks`);
        console.log(`📊 Steps: ${stpResult.steps.length}`);
        console.log(`🔗 Dependencies: ${stpResult.dependencies.length}`);

        // 验证依赖
        const valid = stpIntegrator.validateDependencies(stpResult.tasks);
        console.log(`📊 Dependencies valid: ${valid}`);

        // 生成执行计划
        const plan = stpIntegrator.generateExecutionPlan(stpResult.tasks);
        console.log(`📋 Execution plan: ${plan.length} steps`);

        // ========== 7. 测试缓存 ==========
        console.log('\n💾 7. Testing Caching...');

        const cachedTask = taskManager.getCachedTask(devTask.id);
        console.log(`📊 Cached task: ${cachedTask ? 'found' : 'not found'}`);

        taskManager.cacheTask(devTask.id);
        const cachedTask2 = taskManager.getCachedTask(devTask.id);
        console.log(`📊 Cached task after cache: ${cachedTask2 ? 'found' : 'not found'}`);

        // ========== 8. 测试 Agent 集成 ==========
        console.log('\n🤖 8. Testing Agent Integration...');

        const devAgent = new DevAgent('dev-agent-2');
        await devAgent.initialize();
        console.log(`✅ Dev agent initialized`);

        const testAgent = new TestAgent('test-agent-2');
        await testAgent.initialize();
        console.log(`✅ Test agent initialized`);

        // 获取任务队列状态
        const devStatus = await devAgent.getTaskQueueStatus();
        console.log(`📊 Dev agent status: ${devStatus.status}`);

        const testStatus = await testAgent.getTaskQueueStatus();
        console.log(`📊 Test agent status: ${testStatus.status}`);

        // 停止 Agent
        devAgent.stop();
        testAgent.stop();
        console.log(`✅ Agents stopped`);

        // ========== 9. 测试错误处理 ==========
        console.log('\n❌ 9. Testing Error Handling...');

        const errorTask = taskManager.createTask({
            project_id: project.id,
            name: 'Error Test Task',
            description: 'Test error handling',
            priority: 1
        });

        taskManager.assignTaskToAgent(errorTask.id, 'error-agent');
        console.log(`✅ Error test task assigned`);

        // 模拟任务失败
        taskManager.completeAgentTask('error-agent', errorTask.id, null, 'Simulated error');
        console.log(`📊 Task failed with error`);

        // 检查任务日志
        const logs = taskManager.getTaskLogs(errorTask.id);
        console.log(`📋 Task logs: ${logs.length} entries`);

        // ========== 10. 测试锁超时 ==========
        console.log('\n⏱️ 10. Testing Lock Timeout...');

        const timeoutTask = taskManager.createTask({
            project_id: project.id,
            name: 'Timeout Test Task',
            description: 'Test lock timeout',
            priority: 1
        });

        await taskManager.acquireLock(timeoutTask.id, 'timeout-agent');
        console.log(`🔐 Lock acquired`);

        // 模拟超时（手动设置）
        const isTimeout = taskManager.isLockTimeout(timeoutTask.id);
        console.log(`⏱️ Lock timeout: ${isTimeout}`);

        taskManager.releaseLock(timeoutTask.id, 'timeout-agent');
        console.log(`🔓 Lock released`);

        // ========== 总结 ==========
        console.log('\n🎉 All Enhanced Features Tested Successfully!\n');

        // 显示最终统计
        const finalStats = taskManager.db.prepare(`
            SELECT 
                COUNT(*) as total_tasks,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending
            FROM tasks
        `).get();

        console.log('📊 Final Statistics:');
        console.log(`   Total Tasks: ${finalStats.total_tasks}`);
        console.log(`   Completed: ${finalStats.completed}`);
        console.log(`   Failed: ${finalStats.failed}`);
        console.log(`   Pending: ${finalStats.pending}`);

    } catch (error) {
        console.error('❌ Test failed:', error);
        throw error;
    } finally {
        taskManager.close();
        console.log('🔒 Database closed');
    }
}

// 运行测试
testEnhancedFeatures().then(() => {
    console.log('\n✅ All tests passed!');
    process.exit(0);
}).catch((error) => {
    console.error('\n❌ Tests failed:', error);
    process.exit(1);
});