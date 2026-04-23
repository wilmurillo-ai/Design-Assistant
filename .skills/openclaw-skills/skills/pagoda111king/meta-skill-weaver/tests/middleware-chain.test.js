/**
 * MiddlewareChain 单元测试
 */

const { MiddlewareChain, loggingMiddleware, validationMiddleware, timeoutMiddleware } = require('../src/middleware-chain');

describe('MiddlewareChain', () => {
  let chain;

  beforeEach(() => {
    chain = new MiddlewareChain();
  });

  describe('构造函数', () => {
    test('应该初始化空的中间件列表', () => {
      expect(chain.middlewares).toEqual([]);
    });
  });

  describe('添加中间件', () => {
    test('应该支持添加中间件', () => {
      const middleware = jest.fn();
      chain.use(middleware, 'test-middleware');

      expect(chain.middlewares.length).toBe(1);
      expect(chain.middlewares[0].name).toBe('test-middleware');
      expect(chain.middlewares[0].optional).toBe(false);
    });

    test('应该支持添加可选中间件', () => {
      const middleware = jest.fn();
      chain.use(middleware, 'optional-middleware', true);

      expect(chain.middlewares[0].optional).toBe(true);
    });

    test('应该支持链式调用', () => {
      const result = chain.use(jest.fn());
      expect(result).toBe(chain);
    });

    test('应该按添加顺序记录中间件', () => {
      chain.use(jest.fn(), 'first');
      chain.use(jest.fn(), 'second');
      chain.use(jest.fn(), 'third');

      expect(chain.middlewares[0].order).toBe(0);
      expect(chain.middlewares[1].order).toBe(1);
      expect(chain.middlewares[2].order).toBe(2);
    });
  });

  describe('执行中间件链', () => {
    test('应该按顺序执行中间件', async () => {
      const executionOrder = [];
      chain.use(async (state, next) => {
        executionOrder.push('before-1');
        await next(state);
        executionOrder.push('after-1');
      }, 'm1');
      chain.use(async (state, next) => {
        executionOrder.push('before-2');
        await next(state);
        executionOrder.push('after-2');
      }, 'm2');

      await chain.execute({});

      expect(executionOrder).toEqual(['before-1', 'before-2', 'after-2', 'after-1']);
    });

    test('应该传递状态', async () => {
      chain.use(async (state, next) => {
        state.value1 = 'test1';
        return next(state);
      });
      chain.use(async (state, next) => {
        state.value2 = 'test2';
        return next(state);
      });

      const result = await chain.execute({});

      expect(result.value1).toBe('test1');
      expect(result.value2).toBe('test2');
    });

    test('没有中间件时应该返回状态', async () => {
      const result = await chain.execute({ data: 'test' });
      expect(result.data).toBe('test');
    });
  });

  describe('错误处理', () => {
    test('应该捕获中间件错误', async () => {
      chain.use(async () => {
        throw new Error('中间件错误');
      });

      await expect(chain.execute({})).rejects.toThrow('中间件错误');
    });

    test('可选中间件错误应该被跳过', async () => {
      chain.use(async () => {
        throw new Error('可选错误');
      }, 'optional', true);
      chain.use(async (state, next) => next(state));

      await expect(chain.execute({})).resolves.toBeDefined();
    });

    test('应该记录错误日志', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      chain.use(async () => { throw new Error('test'); });

      try {
        await chain.execute({});
      } catch (e) {}

      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });

  describe('内置中间件', () => {
    describe('loggingMiddleware', () => {
      test('应该记录执行时间', async () => {
        const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
        const middleware = loggingMiddleware();
        const next = jest.fn().mockResolvedValue({});

        await middleware({ taskId: 'test' }, next);

        expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('开始任务'));
        expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('完成'));
        consoleSpy.mockRestore();
      });
    });

    describe('validationMiddleware', () => {
      test('应该验证空描述', async () => {
        const middleware = validationMiddleware();
        const next = jest.fn();

        await expect(middleware({ description: '' }, next)).rejects.toThrow('不能为空');
      });

      test('应该通过有效描述', async () => {
        const middleware = validationMiddleware();
        const next = jest.fn().mockResolvedValue({});

        await expect(middleware({ description: '有效任务' }, next)).resolves.toBeDefined();
      });
    });

    describe('timeoutMiddleware', () => {
      test('应该在超时前完成', async () => {
        const middleware = timeoutMiddleware(1000);
        const next = jest.fn().mockResolvedValue({ result: 'ok' });

        const result = await middleware({}, next);
        expect(result.result).toBe('ok');
      });

      test('应该超时', async () => {
        const middleware = timeoutMiddleware(10);
        const next = jest.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

        await expect(middleware({}, next)).rejects.toThrow('超时');
      });
    });
  });
});
