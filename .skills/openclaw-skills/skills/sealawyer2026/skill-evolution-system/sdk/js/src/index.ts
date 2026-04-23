/**
 * SSE JavaScript/TypeScript SDK
 * 
 * Skill Self-Evolution Engine 官方 JS SDK
 * 
 * Usage:
 *   import { SSEClient } from 'sse-sdk';
 *   
 *   const client = new SSEClient({ apiKey: 'your_key' });
 *   await client.track('my-skill', { durationMs: 1000 });
 */

export interface SSEConfig {
  endpoint?: string;
  apiKey: string;
  timeout?: number;
  retryCount?: number;
  retryDelay?: number;
}

export interface TrackMetrics {
  durationMs?: number;
  success?: boolean;
  satisfaction?: number;
  outputQuality?: number;
  [key: string]: any;
}

export interface TrackContext {
  userId?: string;
  sessionId?: string;
  inputParams?: Record<string, any>;
  [key: string]: any;
}

export class SSEClient {
  private config: Required<SSEConfig>;
  private version = '2.0.0';

  constructor(config: SSEConfig) {
    this.config = {
      endpoint: config.endpoint || 'http://localhost:8080',
      apiKey: config.apiKey,
      timeout: config.timeout || 30000,
      retryCount: config.retryCount || 3,
      retryDelay: config.retryDelay || 1000,
    };
  }

  /**
   * 追踪技能使用
   */
  async track(skillId: string, metrics: TrackMetrics, context?: TrackContext): Promise<any> {
    const payload: any = {
      skill_id: skillId,
      action: 'complete',
      metrics,
    };
    
    if (context) {
      payload.context = context;
    }

    return this.request('POST', '/v2/track', {
      version: this.version,
      timestamp: new Date().toISOString(),
      message_id: `track_${Date.now()}`,
      type: 'track',
      payload,
      meta: { source: 'js_sdk', skill_id: skillId },
    });
  }

  /**
   * 分析技能性能
   */
  async analyze(skillId: string, timeRange: string = '30d'): Promise<any> {
    return this.request('GET', `/v2/analyze/${skillId}?time_range=${timeRange}`);
  }

  /**
   * 生成进化计划
   */
  async plan(skillId: string, strategy: string = 'balanced'): Promise<any> {
    return this.request('POST', '/v2/plan', {
      version: this.version,
      timestamp: new Date().toISOString(),
      message_id: `plan_${Date.now()}`,
      type: 'plan',
      payload: { skill_id: skillId, strategy },
      meta: { source: 'js_sdk', skill_id: skillId },
    });
  }

  /**
   * 执行技能进化
   */
  async evolve(skillId: string, planId?: string, mode: string = 'dry_run'): Promise<any> {
    const payload: any = { skill_id: skillId, mode };
    if (planId) payload.plan_id = planId;

    return this.request('POST', '/v2/evolve', {
      version: this.version,
      timestamp: new Date().toISOString(),
      message_id: `evolve_${Date.now()}`,
      type: 'evolve',
      payload,
      meta: { source: 'js_sdk', skill_id: skillId },
    });
  }

  /**
   * 技能间同步
   */
  async sync(skillIds: string[], sourceSkill?: string): Promise<any> {
    const payload: any = { target_skills: skillIds, sync_type: 'patterns' };
    if (sourceSkill) payload.source_skill = sourceSkill;

    return this.request('POST', '/v2/sync', {
      version: this.version,
      timestamp: new Date().toISOString(),
      message_id: `sync_${Date.now()}`,
      type: 'sync',
      payload,
      meta: { source: 'js_sdk' },
    });
  }

  /**
   * 获取引擎状态
   */
  async status(): Promise<any> {
    return this.request('GET', '/v2/status');
  }

  /**
   * 发送HTTP请求
   */
  private async request(method: string, path: string, body?: any): Promise<any> {
    const url = `${this.config.endpoint}${path}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.config.apiKey}`,
      'X-SSE-Version': this.version,
    };

    for (let attempt = 0; attempt < this.config.retryCount; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

        const response = await fetch(url, {
          method,
          headers,
          body: body ? JSON.stringify(body) : undefined,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          if (response.status === 401) {
            throw new SSEAuthenticationError('Invalid API key');
          } else if (response.status === 429) {
            throw new SSERateLimitError('Rate limit exceeded');
          }
          throw new SSEError(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        if (result.status === 'error') {
          const error = result.error || {};
          throw new SSEError(error.message || 'Unknown error', error.code);
        }

        return result.data;
      } catch (error) {
        if (attempt < this.config.retryCount - 1) {
          await this.sleep(this.config.retryDelay * Math.pow(2, attempt));
          continue;
        }
        throw error;
      }
    }

    throw new SSEError('Max retry exceeded');
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

export class SSEError extends Error {
  code?: string;

  constructor(message: string, code?: string) {
    super(message);
    this.name = 'SSEError';
    this.code = code;
  }
}

export class SSEAuthenticationError extends SSEError {
  constructor(message: string) {
    super(message);
    this.name = 'SSEAuthenticationError';
  }
}

export class SSERateLimitError extends SSEError {
  constructor(message: string) {
    super(message);
    this.name = 'SSERateLimitError';
  }
}

export default SSEClient;
