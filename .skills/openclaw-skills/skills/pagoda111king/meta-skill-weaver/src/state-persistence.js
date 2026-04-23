/**
 * State Persistence - 状态持久化层
 * 
 * 实现状态持久化，支持任务中断恢复
 * 将任务状态保存到 JSON 文件，支持从断点恢复
 * 
 * 灵感来源：DeerFlow 的 JSON 状态机追踪任务状态，支持中断恢复
 * 应用设计模式：状态机模式 + 仓库模式（Repository Pattern）
 */

const fs = require('fs');
const path = require('path');
const { StateMachine, TaskState } = require('./state-machine');

/**
 * 状态持久化类
 */
class StatePersistence {
  /**
   * 构造函数
   * @param {string} storagePath - 存储路径
   * @param {Object} options - 配置选项
   */
  constructor(storagePath = './state-storage', options = {}) {
    this.storagePath = storagePath;
    this.autoSave = options.autoSave !== false; // 默认自动保存
    this.backupEnabled = options.backupEnabled !== false; // 默认启用备份
    this.maxBackups = options.maxBackups || 5; // 最大备份数
    
    // 确保存储目录存在
    this._ensureStorageDir();
  }

  /**
   * 确保存储目录存在
   * @private
   */
  _ensureStorageDir() {
    if (!fs.existsSync(this.storagePath)) {
      fs.mkdirSync(this.storagePath, { recursive: true });
    }
  }

  /**
   * 获取任务状态文件路径
   * @param {string} taskId - 任务 ID
   * @returns {string}
   */
  _getStateFilePath(taskId) {
    return path.join(this.storagePath, `${taskId}-state.json`);
  }

  /**
   * 获取备份文件路径
   * @param {string} taskId - 任务 ID
   * @param {number} timestamp - 时间戳
   * @returns {string}
   */
  _getBackupFilePath(taskId, timestamp) {
    return path.join(this.storagePath, `${taskId}-state-${timestamp}.json.bak`);
  }

  /**
   * 保存任务状态
   * @param {string} taskId - 任务 ID
   * @param {Object} stateData - 状态数据
   * @returns {boolean}
   */
  save(taskId, stateData) {
    try {
      const filePath = this._getStateFilePath(taskId);
      
      // 如果启用备份且文件已存在，创建备份
      if (this.backupEnabled && fs.existsSync(filePath)) {
        this._createBackup(taskId);
      }
      
      // 写入状态数据
      const data = {
        taskId,
        timestamp: Date.now(),
        state: stateData,
        version: '0.4.0',
      };
      
      fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
      
      // 清理旧备份
      if (this.backupEnabled) {
        this._cleanupOldBackups(taskId);
      }
      
      return true;
    } catch (error) {
      console.error(`[StatePersistence] 保存状态失败 [${taskId}]:`, error.message);
      return false;
    }
  }

  /**
   * 加载任务状态
   * @param {string} taskId - 任务 ID
   * @returns {Object|null}
   */
  load(taskId) {
    try {
      const filePath = this._getStateFilePath(taskId);
      
      if (!fs.existsSync(filePath)) {
        return null;
      }
      
      const data = fs.readFileSync(filePath, 'utf8');
      const parsed = JSON.parse(data);
      
      return {
        taskId: parsed.taskId,
        savedAt: parsed.timestamp,
        state: parsed.state,
        version: parsed.version,
      };
    } catch (error) {
      console.error(`[StatePersistence] 加载状态失败 [${taskId}]:`, error.message);
      return null;
    }
  }

  /**
   * 恢复任务状态机
   * @param {string} taskId - 任务 ID
   * @returns {StateMachine|null}
   */
  restoreStateMachine(taskId) {
    const data = this.load(taskId);
    
    if (!data || !data.state) {
      return null;
    }
    
    // 从保存的状态重建状态机
    const stateData = data.state;
    const machine = new StateMachine(stateData.currentState);
    
    // 恢复历史记录
    if (stateData.history) {
      machine.history = stateData.history;
    }
    
    return machine;
  }

  /**
   * 创建备份
   * @param {string} taskId - 任务 ID
   * @private
   */
  _createBackup(taskId) {
    const filePath = this._getStateFilePath(taskId);
    const timestamp = Date.now();
    const backupPath = this._getBackupFilePath(taskId, timestamp);
    
    try {
      fs.copyFileSync(filePath, backupPath);
    } catch (error) {
      console.error(`[StatePersistence] 创建备份失败 [${taskId}]:`, error.message);
    }
  }

  /**
   * 清理旧备份
   * @param {string} taskId - 任务 ID
   * @private
   */
  _cleanupOldBackups(taskId) {
    try {
      const pattern = new RegExp(`^${taskId}-state-\\d+\\.json\\.bak$`);
      const files = fs.readdirSync(this.storagePath)
        .filter(f => pattern.test(f))
        .sort()
        .reverse(); // 最新的在前
      
      // 删除超出数量的备份
      if (files.length > this.maxBackups) {
        files.slice(this.maxBackups).forEach(file => {
          const filePath = path.join(this.storagePath, file);
          fs.unlinkSync(filePath);
        });
      }
    } catch (error) {
      console.error(`[StatePersistence] 清理备份失败 [${taskId}]:`, error.message);
    }
  }

  /**
   * 删除任务状态
   * @param {string} taskId - 任务 ID
   * @returns {boolean}
   */
  delete(taskId) {
    try {
      const filePath = this._getStateFilePath(taskId);
      
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
      }
      
      // 删除所有备份
      const pattern = new RegExp(`^${taskId}-state-\\d+\\.json\\.bak$`);
      const files = fs.readdirSync(this.storagePath)
        .filter(f => pattern.test(f));
      
      files.forEach(file => {
        const filePath = path.join(this.storagePath, file);
        fs.unlinkSync(filePath);
      });
      
      return true;
    } catch (error) {
      console.error(`[StatePersistence] 删除状态失败 [${taskId}]:`, error.message);
      return false;
    }
  }

  /**
   * 列出所有保存的任务状态
   * @returns {Array}
   */
  listAll() {
    try {
      const files = fs.readdirSync(this.storagePath)
        .filter(f => f.endsWith('-state.json'));
      
      return files.map(file => {
        const taskId = file.replace('-state.json', '');
        const filePath = path.join(this.storagePath, file);
        const stats = fs.statSync(filePath);
        
        return {
          taskId,
          createdAt: stats.birthtime,
          modifiedAt: stats.mtime,
          size: stats.size,
        };
      });
    } catch (error) {
      console.error('[StatePersistence] 列出状态失败:', error.message);
      return [];
    }
  }

  /**
   * 获取可恢复的任务列表
   * @returns {Array}
   */
  listRecoverable() {
    const all = this.listAll();
    
    return all.filter(item => {
      const data = this.load(item.taskId);
      if (!data || !data.state) return false;
      
      const state = data.state.currentState;
      // 只有运行中或暂停的任务可以恢复
      return state === TaskState.RUNNING || state === TaskState.PAUSED;
    });
  }

  /**
   * 导出状态为 JSON 字符串
   * @param {string} taskId - 任务 ID
   * @returns {string|null}
   */
  exportJSON(taskId) {
    const data = this.load(taskId);
    if (!data) return null;
    
    return JSON.stringify(data, null, 2);
  }

  /**
   * 从 JSON 字符串导入状态
   * @param {string} taskId - 任务 ID
   * @param {string} jsonString - JSON 字符串
   * @returns {boolean}
   */
  importJSON(taskId, jsonString) {
    try {
      const data = JSON.parse(jsonString);
      return this.save(taskId, data.state);
    } catch (error) {
      console.error(`[StatePersistence] 导入状态失败 [${taskId}]:`, error.message);
      return false;
    }
  }
}

module.exports = {
  StatePersistence,
};
