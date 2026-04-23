/**
 * State Machine 单元测试
 */

const { StateMachine, TaskState, STATE_TRANSITIONS } = require('../src/state-machine');

describe('StateMachine', () => {
  describe('初始化', () => {
    test('应该使用 PENDING 作为默认初始状态', () => {
      const machine = new StateMachine();
      expect(machine.getState()).toBe(TaskState.PENDING);
    });

    test('应该允许自定义初始状态', () => {
      const machine = new StateMachine(TaskState.RUNNING);
      expect(machine.getState()).toBe(TaskState.RUNNING);
    });

    test('应该记录初始状态到历史', () => {
      const machine = new StateMachine();
      const history = machine.getHistory();
      expect(history).toHaveLength(1);
      expect(history[0].state).toBe(TaskState.PENDING);
    });
  });

  describe('状态转换', () => {
    test('应该允许 PENDING → RUNNING 转换', () => {
      const machine = new StateMachine();
      expect(() => machine.start()).not.toThrow();
      expect(machine.getState()).toBe(TaskState.RUNNING);
    });

    test('应该允许 RUNNING → COMPLETED 转换', () => {
      const machine = new StateMachine();
      machine.start();
      expect(() => machine.complete()).not.toThrow();
      expect(machine.getState()).toBe(TaskState.COMPLETED);
    });

    test('应该允许 RUNNING → FAILED 转换', () => {
      const machine = new StateMachine();
      machine.start();
      expect(() => machine.fail()).not.toThrow();
      expect(machine.getState()).toBe(TaskState.FAILED);
    });

    test('应该允许 RUNNING → PAUSED 转换', () => {
      const machine = new StateMachine();
      machine.start();
      expect(() => machine.pause()).not.toThrow();
      expect(machine.getState()).toBe(TaskState.PAUSED);
    });

    test('应该允许 PAUSED → RUNNING 转换（恢复）', () => {
      const machine = new StateMachine();
      machine.start();
      machine.pause();
      expect(() => machine.resume()).not.toThrow();
      expect(machine.getState()).toBe(TaskState.RUNNING);
    });

    test('应该允许 FAILED → PENDING 转换（重试）', () => {
      const machine = new StateMachine();
      machine.start();
      machine.fail();
      expect(() => machine.retry()).not.toThrow();
      expect(machine.getState()).toBe(TaskState.PENDING);
    });

    test('应该允许任何状态 → CANCELLED 转换', () => {
      const machine = new StateMachine();
      expect(() => machine.cancel()).not.toThrow();
      expect(machine.getState()).toBe(TaskState.CANCELLED);
    });

    test('应该拒绝非法的状态转换', () => {
      const machine = new StateMachine();
      // 从 PENDING 直接到 COMPLETED 是不允许的
      expect(() => machine.transition(TaskState.COMPLETED)).toThrow();
    });

    test('应该拒绝从终态转换', () => {
      const machine = new StateMachine();
      machine.start();
      machine.complete();
      
      // COMPLETED 是终态，不能再转换
      expect(() => machine.start()).toThrow();
    });
  });

  describe('状态检查', () => {
    test('isTerminal 应该正确识别终态', () => {
      const machine1 = new StateMachine();
      machine1.start();
      machine1.complete();
      expect(machine1.isTerminal()).toBe(true);

      const machine2 = new StateMachine();
      machine2.start();
      machine2.cancel();
      expect(machine2.isTerminal()).toBe(true);

      const machine3 = new StateMachine();
      machine3.start();
      expect(machine3.isTerminal()).toBe(false);
    });

    test('canResume 应该正确识别可恢复状态', () => {
      const machine1 = new StateMachine();
      machine1.start();
      machine1.pause();
      expect(machine1.canResume()).toBe(true);

      const machine2 = new StateMachine();
      machine2.start();
      expect(machine2.canResume()).toBe(false);
    });

    test('canRetry 应该正确识别可重试状态', () => {
      const machine1 = new StateMachine();
      machine1.start();
      machine1.fail();
      expect(machine1.canRetry()).toBe(true);

      const machine2 = new StateMachine();
      machine2.start();
      expect(machine2.canRetry()).toBe(false);
    });

    test('getAllowedTransitions 应该返回正确的允许转换', () => {
      const machine = new StateMachine();
      expect(machine.getAllowedTransitions()).toContain(TaskState.RUNNING);
      expect(machine.getAllowedTransitions()).toContain(TaskState.CANCELLED);

      machine.start();
      const runningTransitions = machine.getAllowedTransitions();
      expect(runningTransitions).toContain(TaskState.COMPLETED);
      expect(runningTransitions).toContain(TaskState.FAILED);
      expect(runningTransitions).toContain(TaskState.PAUSED);
    });
  });

  describe('状态历史', () => {
    test('应该记录所有状态变更', () => {
      const machine = new StateMachine();
      machine.start();
      machine.complete();

      const history = machine.getHistory();
      expect(history).toHaveLength(3); // 初始 + start + complete
      expect(history[0].state).toBe(TaskState.PENDING);
      expect(history[1].state).toBe(TaskState.RUNNING);
      expect(history[2].state).toBe(TaskState.COMPLETED);
    });

    test('应该为历史记录添加时间戳', () => {
      const machine = new StateMachine();
      machine.start();

      const history = machine.getHistory();
      expect(history[1].timestamp).toBeDefined();
      expect(typeof history[1].timestamp).toBe('number');
    });

    test('应该为历史记录添加原因', () => {
      const machine = new StateMachine();
      machine.start('自定义启动原因');

      const history = machine.getHistory();
      expect(history[1].reason).toBe('自定义启动原因');
    });
  });

  describe('回调函数', () => {
    test('应该调用 onStateChange 回调', () => {
      const onStateChange = jest.fn();
      const machine = new StateMachine(TaskState.PENDING, { onStateChange });

      machine.start();

      expect(onStateChange).toHaveBeenCalledWith(
        TaskState.RUNNING,
        TaskState.PENDING,
        expect.any(Object)
      );
    });

    test('应该调用 onEnter 回调', () => {
      const onEnter = jest.fn();
      const machine = new StateMachine(TaskState.PENDING, { onEnter });

      machine.start();

      expect(onEnter).toHaveBeenCalledWith(
        TaskState.RUNNING,
        TaskState.PENDING,
        expect.any(Object)
      );
    });

    test('应该调用 onExit 回调', () => {
      const onExit = jest.fn();
      const machine = new StateMachine(TaskState.PENDING, { onExit });

      machine.start();

      expect(onExit).toHaveBeenCalledWith(
        TaskState.PENDING,
        TaskState.RUNNING,
        expect.any(Object)
      );
    });
  });

  describe('JSON 序列化', () => {
    test('toJSON 应该导出正确的状态数据', () => {
      const machine = new StateMachine();
      machine.start();
      machine.complete();

      const json = machine.toJSON();
      expect(json.currentState).toBe(TaskState.COMPLETED);
      expect(json.history).toHaveLength(3);
      expect(json.isTerminal).toBe(true);
    });

    test('fromJSON 应该恢复状态机', () => {
      const original = new StateMachine();
      original.start();
      original.pause();

      const json = original.toJSON();
      const restored = StateMachine.fromJSON(json);

      expect(restored.getState()).toBe(TaskState.PAUSED);
      expect(restored.getHistory()).toHaveLength(original.getHistory().length);
    });
  });

  describe('便捷方法', () => {
    test('start 方法应该启动任务', () => {
      const machine = new StateMachine();
      machine.start();
      expect(machine.getState()).toBe(TaskState.RUNNING);
    });

    test('complete 方法应该完成任务', () => {
      const machine = new StateMachine();
      machine.start();
      machine.complete();
      expect(machine.getState()).toBe(TaskState.COMPLETED);
    });

    test('fail 方法应该标记任务失败', () => {
      const machine = new StateMachine();
      machine.start();
      machine.fail();
      expect(machine.getState()).toBe(TaskState.FAILED);
    });

    test('pause 方法应该暂停任务', () => {
      const machine = new StateMachine();
      machine.start();
      machine.pause();
      expect(machine.getState()).toBe(TaskState.PAUSED);
    });

    test('resume 方法应该恢复任务', () => {
      const machine = new StateMachine();
      machine.start();
      machine.pause();
      machine.resume();
      expect(machine.getState()).toBe(TaskState.RUNNING);
    });

    test('cancel 方法应该取消任务', () => {
      const machine = new StateMachine();
      machine.start();
      machine.cancel();
      expect(machine.getState()).toBe(TaskState.CANCELLED);
    });

    test('retry 方法应该重试任务', () => {
      const machine = new StateMachine();
      machine.start();
      machine.fail();
      machine.retry();
      expect(machine.getState()).toBe(TaskState.PENDING);
    });
  });
});
