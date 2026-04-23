/**
 * Event Bus - 事件总线系统
 * 版本：v1.0.0
 */

const EventEmitter = require('events');

class EventBus extends EventEmitter {
  constructor(options = {}) {
    super();
    
    this.options = {
      maxListeners: 100,
      historySize: options.historySize || 1000,
      enableHistory: options.enableHistory !== false,
      ...options
    };
    
    this.interceptors = { before: [], after: [] };
    this.history = [];
    this.historyIndex = 0;
    this.contexts = new Map();
    this.listenerMap = new Map(); // 追踪原始监听器到包装监听器的映射
    
    this.setMaxListeners(this.options.maxListeners);
  }

  on(event, listener, options = {}) {
    const { priority = 0, once = false } = options;
    const wrappedListener = this._wrapListener(listener, { event, priority, once });
    
    // 保存映射
    if (!this.listenerMap.has(event)) {
      this.listenerMap.set(event, []);
    }
    this.listenerMap.get(event).push({ original: listener, wrapped: wrappedListener });
    
    if (once) {
      super.once(event, wrappedListener);
    } else {
      super.on(event, wrappedListener);
    }
    return this;
  }

  once(event, listener, options = {}) {
    return this.on(event, listener, { ...options, once: true });
  }

  off(event, listener) {
    // 找到包装的监听器
    const listeners = this.listenerMap.get(event) || [];
    const mapping = listeners.find(m => m.original === listener);
    
    if (mapping) {
      super.removeListener(event, mapping.wrapped);
      // 移除映射
      const index = listeners.indexOf(mapping);
      if (index > -1) listeners.splice(index, 1);
    }
    return this;
  }

  async emit(event, payload, context = {}) {
    const eventId = this._generateEventId();
    const timestamp = new Date().toISOString();
    const eventRecord = { id: eventId, event, payload, context, timestamp, status: 'pending', duration: 0 };
    const startTime = Date.now();
    
    try {
      await this._executeInterceptors('before', event, payload, context);
      this.contexts.set(eventId, { ...context, eventId, timestamp });
      const result = await this._triggerEvent(event, payload, context);
      await this._executeInterceptors('after', event, payload, context, result);
      
      eventRecord.status = 'completed';
      eventRecord.result = result;
      eventRecord.duration = Date.now() - startTime;
      
      if (this.options.enableHistory) this._addToHistory(eventRecord);
      return result;
    } catch (error) {
      eventRecord.status = 'failed';
      eventRecord.error = error.message;
      eventRecord.duration = Date.now() - startTime;
      if (this.options.enableHistory) this._addToHistory(eventRecord);
      throw error;
    } finally {
      // 延迟清理上下文，让测试可以获取
      setTimeout(() => this.contexts.delete(eventId), 100);
    }
  }

  addBeforeInterceptor(interceptor, options = {}) {
    const { priority = 0 } = options;
    this.interceptors.before.push({ interceptor, priority });
    this.interceptors.before.sort((a, b) => b.priority - a.priority);
    return this;
  }

  addAfterInterceptor(interceptor, options = {}) {
    const { priority = 0 } = options;
    this.interceptors.after.push({ interceptor, priority });
    this.interceptors.after.sort((a, b) => b.priority - a.priority);
    return this;
  }

  getHistory(filter = {}) {
    let records = [...this.history];
    if (filter.event) records = records.filter(r => r.event === filter.event);
    if (filter.status) records = records.filter(r => r.status === filter.status);
    const limit = filter.limit || this.options.historySize;
    return records.slice(-limit);
  }

  clearHistory() {
    this.history = [];
    this.historyIndex = 0;
    return this;
  }

  getContext(eventId) {
    return this.contexts.get(eventId) || null;
  }

  getStats() {
    const history = this.history;
    return {
      totalEvents: history.length,
      completedEvents: history.filter(r => r.status === 'completed').length,
      failedEvents: history.filter(r => r.status === 'failed').length,
      avgDuration: history.length > 0 ? history.reduce((sum, r) => sum + r.duration, 0) / history.length : 0,
      listenerCount: this.listenerCount ? this.listenerCount() : 0,
      contextCount: this.contexts.size
    };
  }

  _wrapListener(listener, meta) {
    const wrapped = async (...args) => {
      try { return await listener(...args); }
      catch (error) {
        console.error(`[EventBus] 监听器错误 (${meta.event}):`, error);
        throw error;
      }
    };
    wrapped._originalListener = listener;
    wrapped._meta = meta;
    return wrapped;
  }

  _generateEventId() {
    return `evt_${Date.now()}_${++this.historyIndex}`;
  }

  async _executeInterceptors(type, event, payload, context, result) {
    for (const { interceptor } of this.interceptors[type]) {
      try { await interceptor({ event, payload, context, result, type }); }
      catch (error) { console.error(`[EventBus] ${type}拦截器错误:`, error); }
    }
  }

  async _triggerEvent(event, payload, context) {
    const listeners = this.listeners(event);
    if (listeners.length === 0) return { event, payload, handled: false };
    
    const results = await Promise.allSettled(listeners.map(listener => listener(payload, context)));
    const fulfilled = results.filter(r => r.status === 'fulfilled').map(r => r.value);
    const rejected = results.filter(r => r.status === 'rejected').map(r => r.reason);
    
    if (rejected.length > 0) console.warn(`[EventBus] ${rejected.length} 个监听器失败`);
    
    return { event, payload, handled: true, results: fulfilled, errors: rejected.map(e => e.message) };
  }

  _addToHistory(record) {
    this.history.push(record);
    if (this.history.length > this.options.historySize) this.history.shift();
  }
}

function loggingInterceptor() {
  return async ({ event, payload, type }) => {
    console.log(`[EventBus:Logging] ${type} - ${event}`, { payloadSize: JSON.stringify(payload).length });
  };
}

function performanceInterceptor() {
  const timings = new Map();
  return async ({ event, type, context }) => {
    const key = `${event}_${context.eventId}`;
    if (type === 'before') timings.set(key, Date.now());
    else if (type === 'after' && timings.has(key)) {
      console.log(`[EventBus:Performance] ${event} 耗时：${Date.now() - timings.get(key)}ms`);
      timings.delete(key);
    }
  };
}

module.exports = { EventBus, loggingInterceptor, performanceInterceptor };
