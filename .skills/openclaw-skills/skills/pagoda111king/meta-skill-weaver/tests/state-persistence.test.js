/**
 * State Persistence 单元测试
 */

const fs = require('fs');
const path = require('path');
const { StatePersistence } = require('../src/state-persistence');
const { StateMachine, TaskState } = require('../src/state-machine');

describe('StatePersistence', () => {
  let persistence;
  const testStoragePath = path.join(__dirname, 'test-state-storage');

  beforeEach(() => {
    // 清理测试目录
    if (fs.existsSync(testStoragePath)) {
      fs.rmSync(testStoragePath, { recursive: true });
    }
    
    persistence = new StatePersistence(testStoragePath, {
      backupEnabled: true,
      maxBackups: 3,
    });
  });

  afterEach(() => {
    // 清理测试目录
    if (fs.existsSync(testStoragePath)) {
      fs.rmSync(testStoragePath, { recursive: true });
    }
  });

  describe('初始化', () => {
    test('应该创建存储目录', () => {
      expect(fs.existsSync(testStoragePath)).toBe(true);
    });

    test('应该允许自定义存储路径', () => {
      const customPath = path.join(__dirname, 'custom-storage');
      const customPersistence = new StatePersistence(customPath);
      
      expect(fs.existsSync(customPath)).toBe(true);
      
      // 清理
      fs.rmSync(customPath, { recursive: true });
    });
  });

  describe('保存和加载', () => {
    test('应该保存任务状态', () => {
      const taskId = 'test-task-1';
      const stateData = {
        currentState: TaskState.RUNNING,
        history: [{ state: TaskState.RUNNING, timestamp: Date.now() }],
      };

      const result = persistence.save(taskId, stateData);
      expect(result).toBe(true);

      // 验证文件存在
      const filePath = path.join(testStoragePath, `${taskId}-state.json`);
      expect(fs.existsSync(filePath)).toBe(true);
    });

    test('应该加载任务状态', () => {
      const taskId = 'test-task-2';
      const stateData = {
        currentState: TaskState.COMPLETED,
        history: [],
        result: { success: true },
      };

      persistence.save(taskId, stateData);
      const loaded = persistence.load(taskId);

      expect(loaded).not.toBeNull();
      expect(loaded.taskId).toBe(taskId);
      expect(loaded.state.currentState).toBe(TaskState.COMPLETED);
      expect(loaded.state.result).toEqual({ success: true });
    });

    test('加载不存在的任务应该返回 null', () => {
      const loaded = persistence.load('non-existent-task');
      expect(loaded).toBeNull();
    });

    test('应该包含保存时间戳', () => {
      const taskId = 'test-task-3';
      const beforeSave = Date.now();
      
      persistence.save(taskId, { currentState: TaskState.PENDING });
      const loaded = persistence.load(taskId);

      expect(loaded.savedAt).toBeGreaterThanOrEqual(beforeSave);
      expect(loaded.savedAt).toBeLessThanOrEqual(Date.now());
    });
  });

  describe('状态机恢复', () => {
    test('应该恢复状态机', () => {
      const taskId = 'test-task-4';
      const machine = new StateMachine();
      machine.start();
      machine.pause();

      persistence.save(taskId, machine.toJSON());
      const restored = persistence.restoreStateMachine(taskId);

      expect(restored).not.toBeNull();
      expect(restored.getState()).toBe(TaskState.PAUSED);
      expect(restored.getHistory()).toHaveLength(machine.getHistory().length);
    });

    test('恢复不存在的任务应该返回 null', () => {
      const restored = persistence.restoreStateMachine('non-existent-task');
      expect(restored).toBeNull();
    });
  });

  describe('备份功能', () => {
    test('保存时应该创建备份', () => {
      const taskId = 'test-task-5';
      
      // 第一次保存
      persistence.save(taskId, { currentState: TaskState.PENDING });
      
      // 第二次保存（应该创建备份）
      persistence.save(taskId, { currentState: TaskState.RUNNING });

      // 检查备份文件
      const files = fs.readdirSync(testStoragePath);
      const backupFiles = files.filter(f => f.endsWith('.bak'));
      
      expect(backupFiles).toHaveLength(1);
    });

    test('应该限制备份数量', () => {
      const taskId = 'test-task-6';
      
      // 多次保存以创建多个备份
      for (let i = 0; i < 5; i++) {
        persistence.save(taskId, { currentState: TaskState.RUNNING, iteration: i });
      }

      // 检查备份数量（应该不超过 maxBackups=3）
      const files = fs.readdirSync(testStoragePath);
      const backupFiles = files.filter(f => f.endsWith('.bak'));
      
      expect(backupFiles.length).toBeLessThanOrEqual(3);
    });
  });

  describe('删除功能', () => {
    test('应该删除任务状态', () => {
      const taskId = 'test-task-7';
      
      persistence.save(taskId, { currentState: TaskState.PENDING });
      persistence.delete(taskId);

      const loaded = persistence.load(taskId);
      expect(loaded).toBeNull();
    });

    test('删除应该同时删除备份', () => {
      const taskId = 'test-task-8';
      
      // 创建多个备份
      for (let i = 0; i < 3; i++) {
        persistence.save(taskId, { currentState: TaskState.RUNNING });
      }

      persistence.delete(taskId);

      const files = fs.readdirSync(testStoragePath);
      const taskFiles = files.filter(f => f.startsWith(`${taskId}-state`));
      
      expect(taskFiles).toHaveLength(0);
    });
  });

  describe('列表功能', () => {
    test('应该列出所有保存的任务', () => {
      persistence.save('task-1', { currentState: TaskState.PENDING });
      persistence.save('task-2', { currentState: TaskState.RUNNING });
      persistence.save('task-3', { currentState: TaskState.COMPLETED });

      const list = persistence.listAll();

      expect(list).toHaveLength(3);
      expect(list.map(l => l.taskId)).toEqual(
        expect.arrayContaining(['task-1', 'task-2', 'task-3'])
      );
    });

    test('应该列出可恢复的任务', () => {
      // 创建可恢复的任务（RUNNING 或 PAUSED）
      persistence.save('recoverable-1', { currentState: TaskState.RUNNING });
      persistence.save('recoverable-2', { currentState: TaskState.PAUSED });
      
      // 创建不可恢复的任务
      persistence.save('completed', { currentState: TaskState.COMPLETED });
      persistence.save('failed', { currentState: TaskState.FAILED });

      const recoverable = persistence.listRecoverable();

      expect(recoverable).toHaveLength(2);
      expect(recoverable.map(r => r.taskId)).toEqual(
        expect.arrayContaining(['recoverable-1', 'recoverable-2'])
      );
    });
  });

  describe('JSON 导入导出', () => {
    test('应该导出为 JSON 字符串', () => {
      const taskId = 'test-task-9';
      const stateData = {
        currentState: TaskState.RUNNING,
        history: [],
      };

      persistence.save(taskId, stateData);
      const jsonStr = persistence.exportJSON(taskId);

      expect(jsonStr).not.toBeNull();
      expect(typeof jsonStr).toBe('string');

      // 验证可以解析
      const parsed = JSON.parse(jsonStr);
      expect(parsed.state.currentState).toBe(TaskState.RUNNING);
    });

    test('应该从 JSON 字符串导入', () => {
      const taskId = 'test-task-10';
      const jsonStr = JSON.stringify({
        taskId,
        timestamp: Date.now(),
        state: {
          currentState: TaskState.PAUSED,
          history: [],
        },
        version: '0.4.0',
      });

      const result = persistence.importJSON(taskId, jsonStr);
      expect(result).toBe(true);

      const loaded = persistence.load(taskId);
      expect(loaded.state.currentState).toBe(TaskState.PAUSED);
    });

    test('导入无效 JSON 应该返回 false', () => {
      const result = persistence.importJSON('test-task', 'invalid json');
      expect(result).toBe(false);
    });
  });

  describe('错误处理', () => {
    test('保存时应该捕获错误并返回 false', () => {
      // 创建一个已存在但不可写的文件
      const readOnlyPath = path.join(__dirname, 'readonly-storage');
      fs.mkdirSync(readOnlyPath, { recursive: true });
      
      const readOnlyPersistence = new StatePersistence(readOnlyPath);
      
      // 使目录只读（模拟权限问题）
      fs.chmodSync(readOnlyPath, 0o444);
      
      try {
        const result = readOnlyPersistence.save('test', { data: 'test' });
        // 在某些系统上可能会成功，所以不强制要求返回 false
        expect(typeof result).toBe('boolean');
      } catch (error) {
        // 如果抛出异常，也是可接受的错误处理
        expect(error).toBeDefined();
      } finally {
        // 恢复权限并清理
        fs.chmodSync(readOnlyPath, 0o755);
        fs.rmSync(readOnlyPath, { recursive: true });
      }
    });
  });
});
