/**
 * meta-skill-weaver - 任务追踪器
 * 版本：v0.1.0
 * 
 * 核心功能：任务分解、状态追踪、中断恢复、数据收集
 * 
 * 灵感来源：
 * - DeerFlow Super Agent Harness
 * - Linux Kernel 模块调用机制
 */

// ============================================================
// 配置与常量
// ============================================================

const TASK_STATUS = {
  PENDING: 'pending',
  RUNNING: 'running',
  BLOCKED: 'blocked',
  COMPLETED: 'completed',
  FAILED: 'failed',
  PAUSED: 'paused'
};

const SKILL_TYPES = {
  ANALYSIS: 'analysis',           // 分析类技能
  CREATION: 'creation',           // 创建类技能
  EVALUATION: 'evaluation',       // 评估类技能
  RESEARCH: 'research',           // 研究类技能
  ORCHESTRATION: 'orchestration'  // 编排类技能
};

// 已安装技能注册表
const SKILL_REGISTRY = {
  'first-principle-analyzer': {
    type: SKILL_TYPES.ANALYSIS,
    capabilities: ['问题分解', '假设质疑', '重构方案'],
    status: 'available'
  },
  'skill-curator': {
    type: SKILL_TYPES.EVALUATION,
    capabilities: ['技能评估', '策展报告'],
    status: 'planned'
  },
  'expert-pattern-extractor': {
    type: SKILL_TYPES.RESEARCH,
    capabilities: ['模式提取', '专家分析'],
    status: 'planned'
  },
  'code-essence': {
    type: SKILL_TYPES.ANALYSIS,
    capabilities: ['代码分析', '设计模式提取'],
    status: 'planned'
  },
  'meta-skill-weaver': {
    type: SKILL_TYPES.ORCHESTRATION,
    capabilities: ['任务编排', '状态追踪'],
    status: 'available'
  }
};

// ============================================================
// 任务追踪核心
// ============================================================

/**
 * 任务类
 */
class Task {
  constructor(id, description, parentTaskId = null) {
    this.id = id;
    this.description = description;
    this.status = TASK_STATUS.PENDING;
    this.parentTaskId = parentTaskId;
    this.subTasks = [];
    this.assignedSkill = null;
    this.startTime = null;
    this.endTime = null;
    this.result = null;
    this.error = null;
    this.metadata = {
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
  }

  updateStatus(status, metadata = {}) {
    this.status = status;
    this.metadata.updatedAt = new Date().toISOString();
    
    if (status === TASK_STATUS.RUNNING && !this.startTime) {
      this.startTime = new Date().toISOString();
    }
    
    if (status === TASK_STATUS.COMPLETED && !this.endTime) {
      this.endTime = new Date().toISOString();
    }
    
    Object.assign(this.metadata, metadata);
  }

  assignSkill(skillName) {
    this.assignedSkill = skillName;
    this.metadata.skillAssignedAt = new Date().toISOString();
  }

  setResult(result) {
    this.result = result;
    this.updateStatus(TASK_STATUS.COMPLETED);
  }

  setError(error) {
    this.error = error;
    this.updateStatus(TASK_STATUS.FAILED);
  }
}

/**
 * 任务追踪器类
 */
class TaskTracker {
  constructor() {
    this.tasks = new Map();
    this.taskCounter = 0;
    this.executionHistory = [];
  }

  /**
   * 创建新任务
   */
  createTask(description, parentTaskId = null) {
    const id = `task-${++this.taskCounter}-${Date.now()}`;
    const task = new Task(id, description, parentTaskId);
    this.tasks.set(id, task);
    
    if (parentTaskId) {
      const parentTask = this.tasks.get(parentTaskId);
      if (parentTask) {
        parentTask.subTasks.push(id);
      }
    }
    
    console.log(`[TaskTracker] 创建任务：${id} - ${description}`);
    return id;
  }

  /**
   * 分解任务为子任务
   */
  decomposeTask(taskId, subTaskDescriptions) {
    const task = this.tasks.get(taskId);
    if (!task) {
      throw new Error(`任务不存在：${taskId}`);
    }
    
    const subTaskIds = [];
    for (const desc of subTaskDescriptions) {
      const subTaskId = this.createTask(desc, taskId);
      subTaskIds.push(subTaskId);
    }
    
    task.metadata.decomposedAt = new Date().toISOString();
    task.metadata.subTaskCount = subTaskIds.length;
    
    console.log(`[TaskTracker] 任务分解：${taskId} → ${subTaskIds.length} 个子任务`);
    return subTaskIds;
  }

  /**
   * 为任务分配技能
   */
  assignSkill(taskId, skillName) {
    const task = this.tasks.get(taskId);
    if (!task) {
      throw new Error(`任务不存在：${taskId}`);
    }
    
    if (!SKILL_REGISTRY[skillName]) {
      throw new Error(`技能不存在：${skillName}`);
    }
    
    task.assignSkill(skillName);
    console.log(`[TaskTracker] 任务 ${taskId} 分配技能：${skillName}`);
  }

  /**
   * 开始执行任务
   */
  startTask(taskId) {
    const task = this.tasks.get(taskId);
    if (!task) {
      throw new Error(`任务不存在：${taskId}`);
    }
    
    task.updateStatus(TASK_STATUS.RUNNING);
    console.log(`[TaskTracker] 开始执行任务：${taskId}`);
  }

  /**
   * 完成任务
   */
  completeTask(taskId, result) {
    const task = this.tasks.get(taskId);
    if (!task) {
      throw new Error(`任务不存在：${taskId}`);
    }
    
    task.setResult(result);
    
    // 记录到执行历史
    this.executionHistory.push({
      taskId: taskId,
      skill: task.assignedSkill,
      duration: task.endTime - task.startTime,
      status: TASK_STATUS.COMPLETED,
      timestamp: new Date().toISOString()
    });
    
    console.log(`[TaskTracker] 完成任务：${taskId}`);
  }

  /**
   * 失败任务
   */
  failTask(taskId, error) {
    const task = this.tasks.get(taskId);
    if (!task) {
      throw new Error(`任务不存在：${taskId}`);
    }
    
    task.setError(error);
    
    // 记录到执行历史
    this.executionHistory.push({
      taskId: taskId,
      skill: task.assignedSkill,
      error: error,
      status: TASK_STATUS.FAILED,
      timestamp: new Date().toISOString()
    });
    
    console.log(`[TaskTracker] 任务失败：${taskId} - ${error}`);
  }

  /**
   * 暂停任务
   */
  pauseTask(taskId) {
    const task = this.tasks.get(taskId);
    if (!task) {
      throw new Error(`任务不存在：${taskId}`);
    }
    
    task.updateStatus(TASK_STATUS.PAUSED);
    console.log(`[TaskTracker] 暂停任务：${taskId}`);
  }

  /**
   * 恢复任务
   */
  resumeTask(taskId) {
    const task = this.tasks.get(taskId);
    if (!task) {
      throw new Error(`任务不存在：${taskId}`);
    }
    
    if (task.status === TASK_STATUS.PAUSED) {
      task.updateStatus(TASK_STATUS.RUNNING);
      console.log(`[TaskTracker] 恢复任务：${taskId}`);
    } else {
      throw new Error(`任务状态不是 PAUSED: ${task.status}`);
    }
  }

  /**
   * 获取任务状态
   */
  getTaskStatus(taskId) {
    const task = this.tasks.get(taskId);
    if (!task) {
      throw new Error(`任务不存在：${taskId}`);
    }
    
    return {
      id: task.id,
      description: task.description,
      status: task.status,
      assignedSkill: task.assignedSkill,
      subTasks: task.subTasks,
      parentTaskId: task.parentTaskId,
      startTime: task.startTime,
      endTime: task.endTime,
      result: task.result,
      error: task.error,
      metadata: task.metadata
    };
  }

  /**
   * 获取所有任务状态
   */
  getAllTasksStatus() {
    const status = [];
    for (const [id, task] of this.tasks) {
      status.push(this.getTaskStatus(id));
    }
    return status;
  }

  /**
   * 获取任务进度报告
   */
  getProgressReport(taskId) {
    const task = this.tasks.get(taskId);
    if (!task) {
      throw new Error(`任务不存在：${taskId}`);
    }
    
    const report = {
      taskId: task.id,
      description: task.description,
      overallStatus: task.status,
      progress: this.calculateProgress(task),
      subTasks: [],
      executionStats: this.getExecutionStats(task)
    };
    
    for (const subTaskId of task.subTasks) {
      const subTask = this.tasks.get(subTaskId);
      if (subTask) {
        report.subTasks.push({
          id: subTask.id,
          description: subTask.description,
          status: subTask.status,
          assignedSkill: subTask.assignedSkill
        });
      }
    }
    
    return report;
  }

  /**
   * 计算任务进度
   */
  calculateProgress(task) {
    if (task.subTasks.length === 0) {
      return task.status === TASK_STATUS.COMPLETED ? 100 : 
             task.status === TASK_STATUS.FAILED ? 0 : 50;
    }
    
    let completed = 0;
    for (const subTaskId of task.subTasks) {
      const subTask = this.tasks.get(subTaskId);
      if (subTask && subTask.status === TASK_STATUS.COMPLETED) {
        completed++;
      }
    }
    
    return Math.round((completed / task.subTasks.length) * 100);
  }

  /**
   * 获取执行统计
   */
  getExecutionStats(task) {
    const stats = {
      totalSubTasks: task.subTasks.length,
      completed: 0,
      running: 0,
      pending: 0,
      failed: 0,
      averageDuration: 0
    };
    
    const durations = [];
    
    for (const subTaskId of task.subTasks) {
      const subTask = this.tasks.get(subTaskId);
      if (subTask) {
        switch (subTask.status) {
          case TASK_STATUS.COMPLETED:
            stats.completed++;
            if (subTask.startTime && subTask.endTime) {
              durations.push(new Date(subTask.endTime) - new Date(subTask.startTime));
            }
            break;
          case TASK_STATUS.RUNNING:
            stats.running++;
            break;
          case TASK_STATUS.PENDING:
            stats.pending++;
            break;
          case TASK_STATUS.FAILED:
            stats.failed++;
            break;
        }
      }
    }
    
    if (durations.length > 0) {
      stats.averageDuration = durations.reduce((a, b) => a + b, 0) / durations.length;
    }
    
    return stats;
  }

  /**
   * 导出任务状态（用于持久化）
   */
  exportState() {
    const state = {
      tasks: Array.from(this.tasks.entries()).map(([id, task]) => ({
        id,
        description: task.description,
        status: task.status,
        parentTaskId: task.parentTaskId,
        subTasks: task.subTasks,
        assignedSkill: task.assignedSkill,
        startTime: task.startTime,
        endTime: task.endTime,
        result: task.result,
        error: task.error,
        metadata: task.metadata
      })),
      taskCounter: this.taskCounter,
      executionHistory: this.executionHistory,
      exportedAt: new Date().toISOString()
    };
    
    return JSON.stringify(state, null, 2);
  }

  /**
   * 导入任务状态（用于恢复）
   */
  importState(jsonState) {
    const state = JSON.parse(jsonState);
    
    this.tasks.clear();
    this.taskCounter = state.taskCounter;
    this.executionHistory = state.executionHistory;
    
    for (const taskData of state.tasks) {
      const task = new Task(taskData.id, taskData.description, taskData.parentTaskId);
      Object.assign(task, taskData);
      this.tasks.set(taskData.id, task);
    }
    
    console.log(`[TaskTracker] 导入状态：${this.tasks.size} 个任务`);
  }

  /**
   * 获取可恢复的任务列表
   */
  getRecoverableTasks() {
    const recoverable = [];
    
    for (const [id, task] of this.tasks) {
      if (task.status === TASK_STATUS.PAUSED || 
          task.status === TASK_STATUS.RUNNING) {
        recoverable.push({
          id: task.id,
          description: task.description,
          status: task.status,
          progress: this.calculateProgress(task)
        });
      }
    }
    
    return recoverable;
  }
}

// ============================================================
// 技能编排器
// ============================================================

class SkillOrchestrator {
  constructor(taskTracker) {
    this.taskTracker = taskTracker;
  }

  /**
   * 编排复杂任务
   */
  orchestrate(description, subTasks, skillAssignments) {
    console.log('[SkillOrchestrator] 开始编排任务:', description);
    
    // 创建主任务
    const mainTaskId = this.taskTracker.createTask(description);
    
    // 分解为子任务
    const subTaskIds = this.taskTracker.decomposeTask(mainTaskId, subTasks);
    
    // 分配技能
    subTaskIds.forEach((taskId, index) => {
      if (skillAssignments[index]) {
        this.taskTracker.assignSkill(taskId, skillAssignments[index]);
      }
    });
    
    console.log('[SkillOrchestrator] 编排完成:', {
      mainTaskId,
      subTaskCount: subTaskIds.length,
      skillAssignments
    });
    
    return {
      mainTaskId,
      subTaskIds,
      status: 'orchestrated'
    };
  }

  /**
   * 执行编排的任务
   */
  async execute(mainTaskId) {
    const task = this.taskTracker.tasks.get(mainTaskId);
    if (!task) {
      throw new Error(`任务不存在：${mainTaskId}`);
    }
    
    console.log('[SkillOrchestrator] 开始执行任务:', mainTaskId);
    
    this.taskTracker.startTask(mainTaskId);
    
    // 按顺序执行子任务
    for (const subTaskId of task.subTasks) {
      const subTask = this.taskTracker.tasks.get(subTaskId);
      
      if (!subTask) continue;
      
      console.log('[SkillOrchestrator] 执行子任务:', subTaskId);
      this.taskTracker.startTask(subTaskId);
      
      // 模拟技能执行（实际应该调用真实技能）
      const result = await this.executeSkill(subTask.assignedSkill, subTask.description);
      
      if (result.success) {
        this.taskTracker.completeTask(subTaskId, result.data);
      } else {
        this.taskTracker.failTask(subTaskId, result.error);
        // 根据错误类型决定是否继续
        if (result.critical) {
          this.taskTracker.pauseTask(mainTaskId);
          return { success: false, error: result.error };
        }
      }
    }
    
    this.taskTracker.completeTask(mainTaskId, {
      message: '任务执行完成',
      subTaskResults: task.subTasks.map(id => {
        const subTask = this.taskTracker.tasks.get(id);
        return {
          taskId: id,
          status: subTask.status,
          result: subTask.result
        };
      })
    });
    
    return { success: true };
  }

  /**
   * 执行技能（模拟）
   */
  async executeSkill(skillName, taskDescription) {
    console.log(`[SkillOrchestrator] 执行技能：${skillName} - ${taskDescription}`);
    
    // 模拟执行延迟
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 这里应该调用真实的技能
    // 现在返回模拟结果
    return {
      success: true,
      data: {
        message: `技能 ${skillName} 执行完成`,
        taskDescription
      }
    };
  }
}

// ============================================================
// 导出接口
// ============================================================

module.exports = {
  TASK_STATUS,
  SKILL_TYPES,
  SKILL_REGISTRY,
  Task,
  TaskTracker,
  SkillOrchestrator
};
