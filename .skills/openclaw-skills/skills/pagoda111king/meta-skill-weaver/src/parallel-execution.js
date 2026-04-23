/**
 * Parallel Execution - 并发执行
 * 灵感来源：DeerFlow 的 asyncio.gather + 并发限制
 */

class ParallelExecutor {
  constructor(maxConcurrency = 3, timeout = 15 * 60 * 1000) {
    this.maxConcurrency = maxConcurrency;
    this.timeout = timeout;
  }

  async executeParallel(tasks, executeFn) {
    const results = [];
    const executing = new Map();
    const pending = [...tasks];
    
    while (pending.length > 0 || executing.size > 0) {
      // 启动新任务直到达到并发限制
      while (pending.length > 0 && executing.size < this.maxConcurrency) {
        const task = pending.shift();
        const taskId = task.id || `task-${Date.now()}`;
        
        const promise = this.executeWithTimeout(task, executeFn)
          .then(result => ({ taskId, success: true, result }))
          .catch(error => ({ taskId, success: false, error: error.message }));
        
        executing.set(taskId, promise);
      }
      
      // 等待至少一个任务完成
      if (executing.size > 0) {
        const settled = await Promise.race(
          Array.from(executing.entries()).map(([taskId, promise]) => 
            promise.then(result => ({ taskId, result }))
          )
        );
        
        executing.delete(settled.taskId);
        results.push(settled.result);
      }
    }
    
    return results;
  }

  async executeWithTimeout(task, executeFn) {
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error(`任务超时：${this.timeout}ms`)), this.timeout);
    });
    return Promise.race([executeFn(task), timeoutPromise]);
  }
}

module.exports = { ParallelExecutor };
