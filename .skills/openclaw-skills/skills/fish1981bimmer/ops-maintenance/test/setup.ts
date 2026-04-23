/**
 * Jest 测试环境设置
 */

// 设置测试环境变量
process.env.NODE_ENV = 'test';

// 全局测试超时设置
jest.setTimeout(10000);

// 在所有测试前执行
beforeAll(() => {
    // 可以在这里设置全局的测试配置
});

// 在所有测试后执行
afterAll(() => {
    // 清理资源
});
