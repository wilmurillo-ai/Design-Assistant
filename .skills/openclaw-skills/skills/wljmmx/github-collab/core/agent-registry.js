/**
 * Agent Registry - Agent 注册表
 * 管理所有 Agent 实例，提供任务分发功能
 */

const { DevAgent } = require('../agents/dev-agent');
const { TestAgent } = require('../agents/test-agent');

class AgentRegistry {
    constructor() {
        this.agents = new Map(); // agentId -> Agent 实例
        this.agentTypes = new Map(); // agentId -> agentType (dev/test)
    }

    /**
     * 注册 Agent
     * @param {string} agentId - Agent ID
     * @param {Object} agentInstance - Agent 实例
     * @param {string} agentType - Agent 类型 (dev/test)
     */
    register(agentId, agentInstance, agentType = 'dev') {
        this.agents.set(agentId, agentInstance);
        this.agentTypes.set(agentId, agentType);
        console.log(`[AgentRegistry] Registered agent: ${agentId} (type: ${agentType})`);
    }

    /**
     * 获取 Agent 实例
     * @param {string} agentId - Agent ID
     * @returns {Object|null} Agent 实例
     */
    get(agentId) {
        return this.agents.get(agentId) || null;
    }

    /**
     * 获取 Agent 类型
     * @param {string} agentId - Agent ID
     * @returns {string} Agent 类型
     */
    getAgentType(agentId) {
        return this.agentTypes.get(agentId) || 'unknown';
    }

    /**
     * 检查 Agent 是否存在
     * @param {string} agentId - Agent ID
     * @returns {boolean}
     */
    has(agentId) {
        return this.agents.has(agentId);
    }

    /**
     * 获取所有注册的 Agent
     * @returns {Array} Agent ID 列表
     */
    getAll() {
        return Array.from(this.agents.keys());
    }

    /**
     * 获取指定类型的 Agent
     * @param {string} agentType - Agent 类型
     * @returns {Array} Agent ID 列表
     */
    getByType(agentType) {
        return Array.from(this.agents.entries())
            .filter(([_, entry]) => this.agentTypes.get(entry) === agentType)
            .map(([id, _]) => id);
    }

    /**
     * 分发任务给 Agent
     * @param {number} taskId - 任务 ID
     * @param {string} agentId - Agent ID
     */
    async dispatchTask(taskId, agentId) {
        const agent = this.get(agentId);
        
        if (!agent) {
            console.error(`[AgentRegistry] Agent not found: ${agentId}`);
            return false;
        }

        console.log(`[AgentRegistry] Dispatching task ${taskId} to agent ${agentId}`);
        
        try {
            // 调用 Agent 的 processTask 方法
            await agent.processTask(taskId);
            return true;
        } catch (error) {
            console.error(`[AgentRegistry] Failed to dispatch task ${taskId} to ${agentId}:`, error.message);
            return false;
        }
    }

    /**
     * 创建并注册 Dev Agent
     * @param {string} agentId - Agent ID
     * @returns {DevAgent}
     */
    createDevAgent(agentId) {
        const agent = new DevAgent(agentId);
        this.register(agentId, agent, 'dev');
        return agent;
    }

    /**
     * 创建并注册 Test Agent
     * @param {string} agentId - Agent ID
     * @returns {TestAgent}
     */
    createTestAgent(agentId) {
        const agent = new TestAgent(agentId);
        this.register(agentId, agent, 'test');
        return agent;
    }

    /**
     * 获取 Agent 状态
     * @param {string} agentId - Agent ID
     * @returns {Object} Agent 状态
     */
    async getAgentStatus(agentId) {
        const agent = this.get(agentId);
        
        if (!agent) {
            return { error: 'Agent not found' };
        }

        // 获取任务队列状态
        const queueStatus = await agent.getTaskQueueStatus();
        
        return {
            agentId,
            type: this.getAgentType(agentId),
            currentTask: agent.currentTask,
            queue: queueStatus.queue,
            stats: queueStatus.stats
        };
    }

    /**
     * 获取所有 Agent 状态
     * @returns {Object} 所有 Agent 状态
     */
    async getAllAgentStatus() {
        const status = {};
        
        for (const agentId of this.getAll()) {
            status[agentId] = await this.getAgentStatus(agentId);
        }
        
        return status;
    }

    /**
     * 移除 Agent
     * @param {string} agentId - Agent ID
     */
    unregister(agentId) {
        const agent = this.get(agentId);
        
        if (agent) {
            // 停止 Agent
            if (agent.shutdown) {
                agent.shutdown();
            }
            
            this.agents.delete(agentId);
            this.agentTypes.delete(agentId);
            console.log(`[AgentRegistry] Unregistered agent: ${agentId}`);
        }
    }

    /**
     * 清空所有 Agent
     */
    clear() {
        for (const agentId of this.getAll()) {
            this.unregister(agentId);
        }
    }
}

module.exports = { AgentRegistry };
