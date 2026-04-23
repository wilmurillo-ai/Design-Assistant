/**
 * Test Suite - 完整测试套件
 */

const assert = require('assert');
const path = require('path');

// 测试配置
const config = {
  dbPath: path.join(__dirname, 'test.db'),
  timeout: 5000
};

// 测试计数器
let testsPassed = 0;
let testsFailed = 0;

/**
 * 运行单个测试
 */
function runTest(name, testFn) {
  try {
    testFn();
    console.log(`✅ ${name}`);
    testsPassed++;
  } catch (error) {
    console.log(`❌ ${name}`);
    console.log(`   ${error.message}`);
    testsFailed++;
  }
}

/**
 * 测试工具函数
 */
function testUtils() {
  console.log('\n📦 测试工具函数...');
  
  const { formatStatus, formatPriority, createProgressBar, truncate } = require('./utils');
  
  runTest('formatStatus', () => {
    assert.strictEqual(formatStatus('completed'), '✅ 已完成');
    assert.strictEqual(formatStatus('pending'), '⏳ 待处理');
  });
  
  runTest('formatPriority', () => {
    assert.strictEqual(formatPriority(1), '🔴 高');
    assert.strictEqual(formatPriority(3), '🟡 中');
    assert.strictEqual(formatPriority(5), '🟢 低');
  });
  
  runTest('createProgressBar', () => {
    const bar = createProgressBar(50, 20);
    assert(bar.includes('█'));
    assert(bar.includes('░'));
    assert(bar.includes('50%'));
  });
  
  runTest('truncate', () => {
    assert.strictEqual(truncate('Hello World', 5), 'Hello');
    assert.strictEqual(truncate('Hello', 10), 'Hello');
  });
}

/**
 * 测试数据库操作
 */
function testDatabase() {
  console.log('\n🗄️ 测试数据库操作...');
  
  const { initDatabase, createTask, getAllTasks, getTaskById } = require('./db/task-manager');
  
  runTest('initDatabase', () => {
    initDatabase();
  });
  
  runTest('createTask', () => {
    const task = {
      project_id: 'test-project',
      title: 'Test Task',
      description: 'Test Description',
      status: 'pending',
      priority: 3
    };
    
    const result = createTask(task);
    assert(result.id > 0);
    assert.strictEqual(result.title, task.title);
  });
  
  runTest('getAllTasks', () => {
    const tasks = getAllTasks();
    assert(Array.isArray(tasks));
  });
  
  runTest('getTaskById', () => {
    const task = getTaskById(1);
    assert(task !== undefined);
  });
}

/**
 * 测试 Agent 操作
 */
function testAgents() {
  console.log('\n🤖 测试 Agent 操作...');
  
  const { initDatabase, upsertAgent, getAllAgents, getAgentByName } = require('./db/agent-manager');
  
  runTest('initDatabase', () => {
    initDatabase();
  });
  
  runTest('upsertAgent', () => {
    const agent = {
      name: 'Test Agent',
      role: 'test',
      target: 'qqbot:c2c:test',
      description: 'Test Description',
      capabilities: 'test'
    };
    
    const result = upsertAgent(agent);
    assert(result.changes > 0);
  });
  
  runTest('getAllAgents', () => {
    const agents = getAllAgents();
    assert(Array.isArray(agents));
  });
  
  runTest('getAgentByName', () => {
    const agent = getAgentByName('Test Agent');
    assert(agent !== undefined);
  });
}

/**
 * 测试任务依赖
 */
function testDependencies() {
  console.log('\n🔗 测试任务依赖...');
  
  const { initDependencies, addDependency, getTaskDependencies, canExecuteTask } = require('./db/task-dependency-manager');
  
  runTest('initDependencies', () => {
    initDependencies();
  });
  
  runTest('addDependency', () => {
    const result = addDependency(1, 2, 'BLOCKING');
    assert(result > 0);
  });
  
  runTest('getTaskDependencies', () => {
    const deps = getTaskDependencies(1);
    assert(Array.isArray(deps));
  });
  
  runTest('canExecuteTask', () => {
    const canExecute = canExecuteTask(1);
    assert(typeof canExecute === 'boolean');
  });
}

/**
 * 测试项目操作
 */
function testProjects() {
  console.log('\n📁 测试项目操作...');
  
  const { initDatabase, createProject, getAllProjects, getProjectById } = require('./db/project-manager');
  
  runTest('initDatabase', () => {
    initDatabase();
  });
  
  runTest('createProject', () => {
    const project = {
      name: 'Test Project',
      description: 'Test Description',
      status: 'active'
    };
    
    const result = createProject(project);
    assert(result.id > 0);
    assert.strictEqual(result.name, project.name);
  });
  
  runTest('getAllProjects', () => {
    const projects = getAllProjects();
    assert(Array.isArray(projects));
  });
  
  runTest('getProjectById', () => {
    const project = getProjectById(1);
    assert(project !== undefined);
  });
}

/**
 * 运行所有测试
 */
function runAllTests() {
  console.log('🚀 开始运行测试...\n');
  
  testUtils();
  testDatabase();
  testAgents();
  testDependencies();
  testProjects();
  
  console.log('\n📊 测试结果:');
  console.log(`   通过：${testsPassed}`);
  console.log(`   失败：${testsFailed}`);
  console.log(`   总计：${testsPassed + testsFailed}`);
  
  if (testsFailed === 0) {
    console.log('\n🎉 所有测试通过！');
  } else {
    console.log('\n⚠️ 部分测试失败，请检查错误信息');
  }
}

// 运行测试
runAllTests();
