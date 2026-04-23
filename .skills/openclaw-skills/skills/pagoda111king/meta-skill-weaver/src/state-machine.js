/**
 * State Machine - 任务状态机
 * 
 * 实现状态机模式，管理任务生命周期
 * 状态转换：pending → running → (completed | failed | cancelled)
 * 
 * 灵感来源：DeerFlow 的 JSON 状态机追踪任务状态
 * 应用设计模式：状态机模式（State Machine Pattern）
 */

/**
 * 任务状态枚举
 */
const TaskState = {
  PENDING: 'pending',       // 等待执行
  RUNNING: 'running',       // 执行中
  COMPLETED: 'completed',   // 已完成
  FAILED: 'failed',         // 失败
  CANCELLED: 'cancelled',   // 已取消
  PAUSED: 'paused',         // 已暂停（支持恢复）
};

/**
 * 状态转换规则
 * 定义哪些状态转换是允许的
 */
const STATE_TRANSITIONS = {
  [TaskState.PENDING]: [TaskState.RUNNING, TaskState.CANCELLED],
  [TaskState.RUNNING]: [TaskState.COMPLETED, TaskState.FAILED, TaskState.PAUSED, TaskState.CANCELLED],
  [TaskState.PAUSED]: [TaskState.RUNNING, TaskState.CANCELLED],
  [TaskState.COMPLETED]: [], // 终态，不可转换
  [TaskState.FAILED]: [TaskState.PENDING], // 允许重试
  [TaskState.CANCELLED]: [], // 终态，不可转换
};

/**
 * 状态机类
 */
class StateMachine {
  /**
   * 构造函数
   * @param {string} initialState - 初始状态
   * @param {Object} options - 配置选项
   * @param {Function} options.onStateChange - 状态变更回调
   * @param {Function} options.onEnter - 进入状态回调
   * @param {Function} options.onExit - 退出状态回调
   */
  constructor(initialState = TaskState.PENDING, options = {}) {
    this.currentState = initialState;
    this.history = [];
    this.onStateChange = options.onStateChange || (() => {});
    this.onEnter = options.onEnter || (() => {});
    this.onExit = options.onExit || (() => {});
    
    // 记录初始状态
    this._recordState(initialState, '初始化');
  }

  /**
   * 记录状态历史
   * @private
   */
  _recordState(state, reason = '') {
    this.history.push({
      state,
      timestamp: Date.now(),
      reason,
    });
  }

  /**
   * 检查状态转换是否允许
   * @param {string} fromState - 当前状态
   * @param {string} toState - 目标状态
   * @returns {boolean}
   */
  canTransition(fromState, toState) {
    const allowedTransitions = STATE_TRANSITIONS[fromState];
    return allowedTransitions && allowedTransitions.includes(toState);
  }

  /**
   * 获取所有允许的状态转换
   * @returns {string[]}
   */
  getAllowedTransitions() {
    return STATE_TRANSITIONS[this.currentState] || [];
  }

  /**
   * 转换状态
   * @param {string} newState - 新状态
   * @param {string} reason - 转换原因
   * @param {Object} context - 上下文数据
   * @returns {boolean} 是否成功
   * @throws {Error} 如果状态转换不允许
   */
  transition(newState, reason = '', context = {}) {
    const oldState = this.currentState;

    // 检查转换是否允许
    if (!this.canTransition(oldState, newState)) {
      throw new Error(
        `Invalid state transition: ${oldState} → ${newState}. ` +
        `Allowed transitions: ${this.getAllowedTransitions().join(', ')}`
      );
    }

    // 调用退出回调
    this.onExit(oldState, newState, context);

    // 更新状态
    this.currentState = newState;
    this._recordState(newState, reason);

    // 调用进入回调
    this.onEnter(newState, oldState, context);

    // 触发状态变更事件
    this.onStateChange(newState, oldState, context);

    return true;
  }

  /**
   * 开始执行（PENDING → RUNNING）
   * @param {string} reason - 原因
   * @param {Object} context - 上下文
   */
  start(reason = '任务开始执行', context = {}) {
    return this.transition(TaskState.RUNNING, reason, context);
  }

  /**
   * 完成任务（RUNNING → COMPLETED）
   * @param {Object} context - 上下文
   */
  complete(context = {}) {
    return this.transition(TaskState.COMPLETED, '任务完成', context);
  }

  /**
   * 任务失败（RUNNING → FAILED）
   * @param {Object} context - 上下文
   */
  fail(context = {}) {
    return this.transition(TaskState.FAILED, '任务失败', context);
  }

  /**
   * 暂停任务（RUNNING → PAUSED）
   * @param {Object} context - 上下文
   */
  pause(context = {}) {
    return this.transition(TaskState.PAUSED, '任务暂停', context);
  }

  /**
   * 恢复任务（PAUSED → RUNNING）
   * @param {Object} context - 上下文
   */
  resume(context = {}) {
    return this.transition(TaskState.RUNNING, '任务恢复', context);
  }

  /**
   * 取消任务
   * @param {Object} context - 上下文
   */
  cancel(context = {}) {
    return this.transition(TaskState.CANCELLED, '任务取消', context);
  }

  /**
   * 重试任务（FAILED → PENDING）
   * @param {Object} context - 上下文
   */
  retry(context = {}) {
    return this.transition(TaskState.PENDING, '任务重试', context);
  }

  /**
   * 获取当前状态
   * @returns {string}
   */
  getState() {
    return this.currentState;
  }

  /**
   * 检查是否为终态
   * @returns {boolean}
   */
  isTerminal() {
    return [TaskState.COMPLETED, TaskState.CANCELLED].includes(this.currentState);
  }

  /**
   * 检查是否可以恢复
   * @returns {boolean}
   */
  canResume() {
    return this.currentState === TaskState.PAUSED;
  }

  /**
   * 检查是否可以重试
   * @returns {boolean}
   */
  canRetry() {
    return this.currentState === TaskState.FAILED;
  }

  /**
   * 获取状态历史
   * @returns {Array}
   */
  getHistory() {
    return [...this.history];
  }

  /**
   * 导出状态为 JSON
   * @returns {Object}
   */
  toJSON() {
    return {
      currentState: this.currentState,
      history: this.history,
      allowedTransitions: this.getAllowedTransitions(),
      isTerminal: this.isTerminal(),
    };
  }

  /**
   * 从 JSON 导入状态
   * @param {Object} json - 状态数据
   * @returns {StateMachine}
   */
  static fromJSON(json) {
    const machine = new StateMachine(json.currentState);
    machine.history = json.history || [];
    return machine;
  }
}

module.exports = {
  StateMachine,
  TaskState,
  STATE_TRANSITIONS,
};
