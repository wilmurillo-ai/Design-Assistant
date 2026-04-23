/**
 * GitHub Collaboration Agent Worker
 * 自动从数据库获取任务并执行，完成后更新状态并继续下一个任务
 */

const TaskManager = require('./task-manager');

class AgentWorker {
  constructor(agentName, taskHandler, dbPath = './github-collab.db', options = {}) {
    this.agentName = agentName;
    this.taskHandler = taskHandler;
    this.taskManager = new TaskManager(dbPath);
    this.currentTask = null;
    this.running = false;
    this.pollInterval = options.pollInterval || 5000;
    this.heartbeatInterval = options.heartbeatInterval || 30000;
    this.heartbeatTimer = null;
  }

  /**
   * 启动 Agent 工作循环
   */
  async start() {
    this.running = true;
    console.log(`[${this.agentName}] Agent started`);
    
    // 注册 agent
    this.taskManager.updateAgentStatus(this.agentName, 'idle');

    // 启动心跳检测
    this.heartbeatTimer = setInterval(() => {
      this.heartbeat();
    }, this.heartbeatInterval);

    // 开始工作循环
    this.workLoop();
  }

  /**
   * 停止 Agent
   */
  stop() {
    this.running = false;
    console.log(`[${this.agentName}] Agent stopped`);
    
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
    }
    
    this.taskManager.close();
  }

  /**
   * 工作循环：获取任务 -> 执行 -> 更新状态 -> 获取下一个任务
   */
  async workLoop() {
    while (this.running) {
      try {
        // 获取下一个任务
        this.currentTask = await this.taskManager.getNextTask(this.agentName);

        if (!this.currentTask) {
          console.log(`[${this.agentName}] No tasks available, waiting ${this.pollInterval}ms...`);
          await this.sleep(this.pollInterval);
          continue;
        }

        console.log(`[${this.agentName}] Processing task #${this.currentTask.id}: ${this.currentTask.name}`);

        // 执行任务
        await this.executeTask(this.currentTask);

      } catch (error) {
        console.error(`[${this.agentName}] Error in work loop:`, error);
        
        if (this.currentTask) {
          this.taskManager.updateTaskStatus(
            this.currentTask.id,
            'failed',
            null,
            error.message
          );
          this.currentTask = null;
        }

        await this.sleep(this.pollInterval);
      }
    }
  }

  /**
   * 执行单个任务
   */
  async executeTask(task) {
    try {
      console.log(`[${this.agentName}] Executing task #${task.id}: ${task.name}`);
      
      // 调用用户提供的任务处理函数
      const result = await this.taskHandler(task);

      // 任务成功完成
      this.taskManager.updateTaskStatus(task.id, 'completed', JSON.stringify(result));
      
      console.log(`[${this.agentName}] Task #${task.id} completed successfully`);
      this.taskManager.logTaskActivity(task.id, this.agentName, 'completed', 'Task completed successfully');

      // 清空当前任务，准备获取下一个
      this.currentTask = null;

    } catch (error) {
      // 任务执行失败
      this.taskManager.updateTaskStatus(
        task.id,
        'failed',
        null,
        error.message
      );

      console.error(`[${this.agentName}] Task #${task.id} failed:`, error.message);
      this.taskManager.logTaskActivity(task.id, this.agentName, 'failed', error.message);

      // 清空当前任务
      this.currentTask = null;
    }
  }

  /**
   * 睡眠函数
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 心跳检测
   */
  heartbeat() {
    if (this.running) {
      this.taskManager.agentHeartbeat(this.agentName);
    }
  }

  /**
   * 获取当前任务
   */
  getCurrentTask() {
    return this.currentTask;
  }

  /**
   * 获取任务管理器
   */
  getTaskManager() {
    return this.taskManager;
  }
}

module.exports = AgentWorker;
