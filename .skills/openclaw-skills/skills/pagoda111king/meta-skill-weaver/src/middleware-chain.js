/**
 * Middleware Chain - 中间件链
 * 灵感来源：DeerFlow 的 9 个 Middleware
 */

class MiddlewareChain {
  constructor() {
    this.middlewares = [];
  }

  use(middleware, name = 'anonymous', optional = false) {
    this.middlewares.push({ middleware, name, optional, order: this.middlewares.length });
    console.log(`[MiddlewareChain] 添加 Middleware: ${name}`);
    return this;
  }

  async execute(state) {
    const finalNext = async (finalState) => finalState;
    
    let chain = finalNext;
    for (let i = this.middlewares.length - 1; i >= 0; i--) {
      const { middleware, name, optional } = this.middlewares[i];
      const prev = chain;
      
      chain = async (currentState) => {
        try {
          console.log(`[MiddlewareChain] 执行：${name}`);
          return await middleware(currentState, prev);
        } catch (error) {
          console.error(`[MiddlewareChain] 错误：${name}`, error);
          if (optional) {
            console.log(`[MiddlewareChain] 跳过可选 Middleware: ${name}`);
            return prev(currentState);
          }
          throw error;
        }
      };
    }
    
    return await chain(state);
  }
}

// 内置 Middleware
function loggingMiddleware() {
  return async (state, next) => {
    const startTime = Date.now();
    console.log(`[LoggingMiddleware] 开始任务：${state.taskId || 'unknown'}`);
    const result = await next(state);
    const duration = Date.now() - startTime;
    console.log(`[LoggingMiddleware] 完成任务：${duration}ms`);
    result.executionTime = duration;
    return result;
  };
}

function validationMiddleware() {
  return async (state, next) => {
    if (!state.description || state.description.trim() === '') {
      throw new Error('任务描述不能为空');
    }
    return next(state);
  };
}

function timeoutMiddleware(timeoutMs) {
  return async (state, next) => {
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error(`任务超时：${timeoutMs}ms`)), timeoutMs);
    });
    return Promise.race([next(state), timeoutPromise]);
  };
}

module.exports = { MiddlewareChain, loggingMiddleware, validationMiddleware, timeoutMiddleware };
