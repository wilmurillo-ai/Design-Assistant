const noop = () => {};

/**
 * Per-session message queue — producer/consumer pattern.
 *
 * - add()       : pure producer — pushes message and signals the consumer
 * - _startLoop(): pure consumer — awaits signal, then drains; runs independently
 * - The two sides communicate only via a promise signal; neither calls the other.
 *
 * Constructor options:
 *   batchProcessor  {Function}  async (sessionKey, batch) => void  — required
 *   logger          {object}    { log, logError } (default: silent)
 */
export class MessageQueue {
  constructor({ batchProcessor, logger = {} } = {}) {
    this.queues         = new Map();
    this.batchProcessor = batchProcessor;
    this.log      = logger.log      || noop;
    this.logError = logger.logError || noop;
  }

  add(sessionKey, messageData) {
    if (!this.queues.has(sessionKey)) {
      const queue = { messages: [], signal: null };
      this.queues.set(sessionKey, queue);
      this._startLoop(sessionKey, queue);
    }

    const queue = this.queues.get(sessionKey);
    queue.messages.push(messageData);
    this.log(`[QUEUE] Added to ${sessionKey}, size: ${queue.messages.length}`);

    // Wake the consumer if it's waiting
    if (queue.signal) {
      const wake = queue.signal;
      queue.signal = null;
      wake();
    }
  }

  async _startLoop(sessionKey, queue) {
    while (true) {
      // Sleep until signalled
      if (queue.messages.length === 0) {
        await new Promise(resolve => { queue.signal = resolve; });
      }

      const batch = [...queue.messages];
      queue.messages = [];
      this.log(`[QUEUE] Processing batch for ${sessionKey}, ${batch.length} messages`);

      try {
        await this.batchProcessor(sessionKey, batch);
      } catch (e) {
        this.logError(`[QUEUE] Error processing batch:`, e.message);
      }
    }
  }
}
