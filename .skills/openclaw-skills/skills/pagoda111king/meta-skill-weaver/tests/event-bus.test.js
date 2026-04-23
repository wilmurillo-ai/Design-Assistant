/**
 * EventBus 单元测试
 */

const { EventBus, loggingInterceptor, performanceInterceptor } = require('../src/event-bus');

describe('EventBus', () => {
  let eventBus;

  beforeEach(() => {
    eventBus = new EventBus({ historySize: 100, enableHistory: true });
  });

  afterEach(() => {
    eventBus.removeAllListeners();
    eventBus.clearHistory();
  });

  describe('构造函数', () => {
    test('应该使用默认配置初始化', () => {
      const bus = new EventBus();
      expect(bus.options.maxListeners).toBe(100);
      expect(bus.options.historySize).toBe(1000);
      expect(bus.options.enableHistory).toBe(true);
    });

    test('应该使用自定义配置初始化', () => {
      const bus = new EventBus({ maxListeners: 50, historySize: 500, enableHistory: false });
      expect(bus.options.maxListeners).toBe(50);
      expect(bus.options.historySize).toBe(500);
      expect(bus.options.enableHistory).toBe(false);
    });
  });

  describe('订阅和发布', () => {
    test('应该支持基本的事件订阅和发布', async () => {
      const listener = jest.fn();
      eventBus.on('test-event', listener);

      const result = await eventBus.emit('test-event', { data: 'test' });

      expect(listener).toHaveBeenCalled();
      expect(result.handled).toBe(true);
    });

    test('应该支持 once 订阅（只触发一次）', async () => {
      const listener = jest.fn();
      eventBus.once('once-event', listener);

      await eventBus.emit('once-event', { data: 1 });
      await eventBus.emit('once-event', { data: 2 });

      expect(listener).toHaveBeenCalledTimes(1);
    });

    test('没有监听器时应该返回 handled: false', async () => {
      const result = await eventBus.emit('no-listener-event', { data: 'test' });
      expect(result.handled).toBe(false);
    });
  });

  describe('拦截器', () => {
    test('应该支持 before 拦截器', async () => {
      const interceptor = jest.fn();
      eventBus.addBeforeInterceptor(interceptor);

      await eventBus.emit('interceptor-event', { data: 'test' });

      expect(interceptor).toHaveBeenCalled();
    });

    test('应该支持 after 拦截器', async () => {
      const interceptor = jest.fn();
      eventBus.addAfterInterceptor(interceptor);

      await eventBus.emit('after-event', { data: 'test' });

      expect(interceptor).toHaveBeenCalled();
    });

    test('拦截器应该按优先级执行', async () => {
      const executionOrder = [];
      eventBus.addBeforeInterceptor(() => executionOrder.push(1), { priority: 1 });
      eventBus.addBeforeInterceptor(() => executionOrder.push(2), { priority: 10 });
      eventBus.addBeforeInterceptor(() => executionOrder.push(3), { priority: 5 });

      await eventBus.emit('priority-event', {});

      expect(executionOrder).toEqual([2, 3, 1]);
    });
  });

  describe('事件历史', () => {
    test('应该记录事件历史', async () => {
      await eventBus.emit('history-event-1', { data: 1 });
      await eventBus.emit('history-event-2', { data: 2 });

      const history = eventBus.getHistory();

      expect(history.length).toBe(2);
    });

    test('应该支持按事件名过滤历史', async () => {
      await eventBus.emit('filter-event', { data: 1 });
      await eventBus.emit('other-event', { data: 2 });
      await eventBus.emit('filter-event', { data: 3 });

      const history = eventBus.getHistory({ event: 'filter-event' });

      expect(history.length).toBe(2);
      expect(history.every(h => h.event === 'filter-event')).toBe(true);
    });

    test('应该支持限制返回数量', async () => {
      for (let i = 0; i < 10; i++) {
        await eventBus.emit(`event-${i}`, { index: i });
      }

      const history = eventBus.getHistory({ limit: 5 });
      expect(history.length).toBe(5);
    });

    test('应该支持清除历史', async () => {
      await eventBus.emit('clear-event', { data: 1 });
      eventBus.clearHistory();

      const history = eventBus.getHistory();
      expect(history.length).toBe(0);
    });
  });

  describe('统计信息', () => {
    test('应该提供准确的统计信息', async () => {
      await eventBus.emit('stat-event-1', {});
      await eventBus.emit('stat-event-2', {});

      const stats = eventBus.getStats();

      expect(stats.totalEvents).toBe(2);
      expect(stats.completedEvents).toBe(2);
      expect(stats.failedEvents).toBe(0);
    });
  });

  describe('错误处理', () => {
    test('应该捕获监听器错误', async () => {
      eventBus.on('error-event', () => {
        throw new Error('监听器错误');
      });

      const result = await eventBus.emit('error-event', {});

      expect(result.handled).toBe(true);
      expect(result.errors).toContain('监听器错误');
    });
  });
});

describe('内置拦截器', () => {
  describe('loggingInterceptor', () => {
    test('应该记录事件日志', async () => {
      const interceptor = loggingInterceptor();
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      await interceptor({ event: 'test', payload: { data: 1 }, type: 'before' });

      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });

  describe('performanceInterceptor', () => {
    test('应该记录性能数据', async () => {
      const interceptor = performanceInterceptor();
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      const context = { eventId: 'test-1' };
      await interceptor({ event: 'perf-test', type: 'before', context });
      await interceptor({ event: 'perf-test', type: 'after', context });

      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('耗时'));
      consoleSpy.mockRestore();
    });
  });
});
