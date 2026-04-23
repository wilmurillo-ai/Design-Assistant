/**
 * Task Manager Enhanced - 增强版任务管理器
 * 支持任务优先级、依赖、分布等高级功能
 */

const { TaskManager } = require('../db/task-manager');
const { TaskPriorityManager } = require('../db/task-priority-manager');
const { TaskDependencyManager } = require('../db/task-dependency-manager');
const { TaskDistributionManager } = require('../db/task-distribution-manager');
const { Logger } = require('../logger');
const { Config } = require('../config');

class TaskManagerEnhanced {
  constructor() {
    this.taskManager = new TaskManager();
    this.priorityManager = new TaskPriorityManager();
    this.dependencyManager = new TaskDependencyManager();
    this.distributionManager = new TaskDistributionManager();
    this.logger = new Logger('TaskManagerEnhanced');
    this.config = new Config();
  }

  async initialize() {
    this.logger.info('TaskManagerEnhanced initializing...');
    await this.config.load();
    await this.taskManager.initialize();
    this.logger.info('TaskManagerEnhanced initialized');
  }

  async createProject(projectData) {
    return await this.taskManager.createProject(projectData);
  }

  async createTask(taskData) {
    this.logger.info(`Creating task: ${taskData.name}`);
    const task = await this.taskManager.createTask(taskData);

    // 设置优先级
    if (taskData.priority) {
      await this.priorityManager.setPriority(task.id, taskData.priority);
    }

    // 设置依赖
    if (taskData.dependencies && taskData.dependencies.length > 0) {
      await this.dependencyManager.addDependencies(task.id, taskData.dependencies);
    }

    return task;
  }

  async getTask(taskId) {
    const task = await this.taskManager.getTask(taskId);
    if (!task) return null;

    // 获取优先级
    const priority = await this.priorityManager.getPriority(taskId);
    task.priority = priority;

    // 获取依赖
    const dependencies = await this.dependencyManager.getDependencies(taskId);
    task.dependencies = dependencies;

    return task;
  }

  async getTasksByProject(projectId) {
    const tasks = await this.taskManager.getTasksByProject(projectId);

    // 按优先级排序
    const sortedTasks = await this.sortByPriority(tasks);

    return sortedTasks;
  }

  async sortByPriority(tasks) {
    for (const task of tasks) {
      const priority = await this.priorityManager.getPriority(task.id);
      task.priority = priority;
    }

    return tasks.sort((a, b) => b.priority - a.priority);
  }

  async assignTask(taskId, agentId) {
    this.logger.info(`Assigning task ${taskId} to agent ${agentId}`);
    await this.taskManager.assignTask(taskId, agentId);
    await this.distributionManager.recordAssignment(taskId, agentId);
  }

  async updateTaskStatus(taskId, status) {
    await this.taskManager.updateTaskStatus(taskId, status);
  }

  async getTaskDependencies(taskId) {
    return await this.dependencyManager.getDependencies(taskId);
  }

  async checkTaskReady(taskId) {
    // 检查所有依赖是否完成
    const dependencies = await this.dependencyManager.getDependencies(taskId);
    for (const depId of dependencies) {
      const depTask = await this.taskManager.getTask(depId);
      if (depTask && depTask.status !== 'completed') {
        return false;
      }
    }
    return true;
  }

  async distributeTasks(agentIds) {
    this.logger.info('Distributing tasks to agents...');
    await this.distributionManager.distributeTasks(agentIds);
  }

  async close() {
    await this.taskManager.close();
  }
}

module.exports = { TaskManagerEnhanced };
