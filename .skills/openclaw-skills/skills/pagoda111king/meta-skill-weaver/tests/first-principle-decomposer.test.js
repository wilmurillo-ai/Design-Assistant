/**
 * FirstPrincipleDecomposer 单元测试
 */

const { FirstPrincipleDecomposer } = require('../src/first-principle-decomposer');

describe('FirstPrincipleDecomposer', () => {
  let decomposer;

  beforeEach(() => {
    decomposer = new FirstPrincipleDecomposer({ maxWhyDepth: 5 });
  });

  describe('构造函数', () => {
    test('应该使用默认配置初始化', () => {
      const d = new FirstPrincipleDecomposer();
      expect(d.options.maxWhyDepth).toBe(5);
      expect(d.options.minAtomicLevel).toBe(3);
    });

    test('应该使用自定义配置初始化', () => {
      const d = new FirstPrincipleDecomposer({ maxWhyDepth: 3, minAtomicLevel: 2 });
      expect(d.options.maxWhyDepth).toBe(3);
      expect(d.options.minAtomicLevel).toBe(2);
    });
  });

  describe('任务分解', () => {
    test('应该分解简单任务', () => {
      const result = decomposer.decompose('创建一个用户管理系统');

      expect(result.originalTask).toBe('创建一个用户管理系统');
      expect(result.assumptions).toBeDefined();
      expect(result.whyAnalysis).toBeDefined();
      expect(result.firstPrinciples).toBeDefined();
      expect(result.atomicTasks).toBeDefined();
      expect(result.atomicTasks.length).toBeGreaterThan(0);
    });

    test('应该识别任务中的假设', () => {
      const task = '必须使用 React 才能实现前端功能';
      const result = decomposer.decompose(task);

      expect(result.assumptions.length).toBeGreaterThan(0);
    });

    test('应该生成原子任务', () => {
      const result = decomposer.decompose('开发一个 API 服务');

      expect(result.atomicTasks.length).toBeGreaterThan(0);
      result.atomicTasks.forEach(task => {
        expect(task.id).toBeDefined();
        expect(task.action).toBeDefined();
        expect(task.description).toBeDefined();
        expect(task.isAtomic).toBe(true);
      });
    });

    test('原子任务应该有依赖关系', () => {
      const result = decomposer.decompose('构建完整应用');

      const tasksWithDeps = result.atomicTasks.filter(t => t.dependencies && t.dependencies.length > 0);
      expect(tasksWithDeps.length).toBeGreaterThan(0);
    });
  });

  describe('获取摘要', () => {
    test('应该提供分析摘要', () => {
      decomposer.decompose('测试任务');
      const summary = decomposer.getSummary();

      expect(summary.assumptionsIdentified).toBeDefined();
      expect(summary.firstPrinciplesExtracted).toBeDefined();
      expect(summary.assumptions).toBeDefined();
      expect(summary.principles).toBeDefined();
    });
  });

  describe('5 Why 分析', () => {
    test('应该返回分析结构', () => {
      const result = decomposer._fiveWhys('优化系统性能');
      expect(result).toBeDefined();
      expect(result.depth).toBeDefined();
      expect(result.analysis).toBeDefined();
      expect(Array.isArray(result.analysis)).toBe(true);
    });

    test('不应该超过最大深度', () => {
      const d = new FirstPrincipleDecomposer({ maxWhyDepth: 3 });
      const result = d._fiveWhys('复杂问题');
      expect(result.depth).toBeLessThanOrEqual(3);
    });
  });

  describe('假设识别', () => {
    test('应该返回假设数组', () => {
      const assumptions = decomposer._identifyAssumptions('测试任务');
      expect(Array.isArray(assumptions)).toBe(true);
      expect(assumptions.length).toBeGreaterThan(0);
    });

    test('假设应该有类型和内容', () => {
      const assumptions = decomposer._identifyAssumptions('必须完成 A');
      expect(assumptions[0]).toHaveProperty('type');
      expect(assumptions[0]).toHaveProperty('content');
    });
  });
});
