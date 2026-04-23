/**
 * State Persistence Middleware - 状态持久化中间件
 * 
 * 将状态持久化作为 Middleware 链的一部分
 * 自动保存任务状态变更，支持中断恢复
 * 
 * 灵感来源：DeerFlow 的 Middleware 链设计
 * 应用设计模式：责任链模式（Chain of Responsibility）
 */

const { StatePersistence } = require('./state-persistence');
const { TaskState } = require('./state-machine');

/**
 * 创建状态持久化中间件
 * @param {Object} options - 配置选项
 * @returns {Function}
 */
function createStatePersistenceMiddleware(options = {}) {
  const storagePath = options.storagePath || './state-storage';
  const autoSaveInterval = options.autoSaveInterval || 5000; // 5 秒自动保存
  const persistence = new StatePersistence(storagePath, options);
  
  // 自动保存定时器
  const autoSaveTimers = new Map();
  
  /**
   * 启动自动保存
   * @param {string} taskId - 任务 ID
   */
  function startAutoSave(taskId, getStateFn) {
    stopAutoSave(taskId);
    
    const timer = setInterval(() => {
      const state = getStateFn();
      if (state) {
        persistence.save(taskId, state);
      }
    }, autoSaveInterval);
    
    autoSaveTimers.set(taskId, timer);
  }
  
  /**
   * 停止自动保存
   * @param {string} taskId - 任务 ID
   */
  function stopAutoSave(taskId) {
    const timer = autoSaveTimers.get(taskId);
    if (timer) {
      clearInterval(timer);
      autoSaveTimers.delete(taskId);
    }
  }
  
  /**
   * 中间件函数
   * @param {Object} context - 执行上下文
   * @param {Function} next - 下一个中间件
   * @returns {Promise}
   */
  return async function statePersistenceMiddleware(context, next) {
    const { taskId, event, payload } = context;
    
    // 根据事件类型处理状态持久化
    switch (event) {
      case 'task-started':
        // 任务开始，保存初始状态
        persistence.save(taskId, {
          currentState: TaskState.RUNNING,
          history: [{
            state: TaskState.RUNNING,
            timestamp: Date.now(),
            reason: '任务开始',
          }],
          startedAt: Date.now(),
        });
        
        // 启动自动保存
        startAutoSave(taskId, () => context.state);
        break;
        
      case 'task-state-change':
        // 状态变更，立即保存
        persistence.save(taskId, {
          currentState: payload.newState,
          history: payload.history,
          previousState: payload.oldState,
          changedAt: Date.now(),
        });
        break;
        
      case 'task-completed':
      case 'task-failed':
      case 'task-cancelled':
        // 任务结束，保存最终状态并停止自动保存
        const finalState = event === 'task-completed' ? TaskState.COMPLETED :
                          event === 'task-failed' ? TaskState.FAILED :
                          TaskState.CANCELLED;
        
        persistence.save(taskId, {
          currentState: finalState,
          history: payload.history,
          completedAt: Date.now(),
          result: payload.result,
        });
        
        stopAutoSave(taskId);
        break;
        
      case 'task-paused':
        // 任务暂停，保存状态
        persistence.save(taskId, {
          currentState: TaskState.PAUSED,
          history: payload.history,
          pausedAt: Date.now(),
        });
        
        stopAutoSave(taskId);
        break;
        
      case 'task-resumed':
        // 任务恢复，保存状态并启动自动保存
        persistence.save(taskId, {
          currentState: TaskState.RUNNING,
          history: payload.history,
          resumedAt: Date.now(),
        });
        
        startAutoSave(taskId, () => context.state);
        break;
        
      case 'task-restore':
        // 从持久化恢复状态
        const savedState = persistence.restoreStateMachine(taskId);
        if (savedState) {
          context.restoredState = savedState.toJSON();
        }
        break;
        
      case 'task-cleanup':
        // 清理任务状态
        persistence.delete(taskId);
        stopAutoSave(taskId);
        break;
    }
    
    // 继续执行下一个中间件
    return next(context);
  };
}

/**
 * 创建状态恢复中间件
 * 在任务开始时检查是否有可恢复的状态
 * @param {Object} options - 配置选项
 * @returns {Function}
 */
function createStateRestoreMiddleware(options = {}) {
  const storagePath = options.storagePath || './state-storage';
  const persistence = new StatePersistence(storagePath, options);
  
  return async function stateRestoreMiddleware(context, next) {
    const { taskId, event } = context;
    
    // 只在任务开始时尝试恢复
    if (event === 'task-init' || event === 'task-started') {
      const savedState = persistence.restoreStateMachine(taskId);
      
      if (savedState) {
        const state = savedState.getState();
        
        // 如果是暂停或运行中的状态，可以恢复
        if (state === TaskState.PAUSED || state === TaskState.RUNNING) {
          context.canRestore = true;
          context.savedState = savedState.toJSON();
          
          console.log(`[StateRestore] 发现可恢复任务 [${taskId}], 状态：${state}`);
        }
      }
    }
    
    return next(context);
  };
}

/**
 * 创建状态检查中间件
 * 在执行前检查任务状态是否允许执行
 * @returns {Function}
 */
function createStateCheckMiddleware() {
  return async function stateCheckMiddleware(context, next) {
    const { taskId, event, state } = context;
    
    // 对于需要执行的操作，检查状态
    if (['task-execute', 'task-step'].includes(event)) {
      const currentState = state?.currentState;
      
      // 只有运行中或暂停（可恢复）的任务才能执行
      if (currentState !== TaskState.RUNNING && currentState !== TaskState.PAUSED) {
        throw new Error(
          `任务 [${taskId}] 状态不允许执行：${currentState}. ` +
          `允许的状态：${TaskState.RUNNING}, ${TaskState.PAUSED}`
        );
      }
    }
    
    return next(context);
  };
}

module.exports = {
  createStatePersistenceMiddleware,
  createStateRestoreMiddleware,
  createStateCheckMiddleware,
};
