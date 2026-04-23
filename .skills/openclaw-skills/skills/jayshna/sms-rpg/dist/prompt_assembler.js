"use strict";
// ============================================================
// 完整上下文组装系统 - TypeScript实现
// ============================================================
Object.defineProperty(exports, "__esModule", { value: true });
exports.CanonViolationError = exports.PromptAssembler = void 0;
exports.generateTurn = generateTurn;
exports.createPromptAssembler = createPromptAssembler;
const memory_assembler_1 = require("./memory_assembler");
// ============================================================
// PromptAssembler 类
// ============================================================
class PromptAssembler {
    constructor(genesisPrompt) {
        this.currentTurnNumber = 1;
        this.genesisEnginePrompt = genesisPrompt;
        this.memoryAssembler = new memory_assembler_1.EpisodicMemoryAssembler({
            totalContextWindow: 6000,
            reservedForOutput: 0,
            recentTurns: 3,
            summaryInterval: 5
        });
    }
    // ============================================================
    // 主组装方法
    // ============================================================
    assemble(worldState) {
        // 1. 组装记忆层
        const memoryContext = this.memoryAssembler.assembleContext(this.currentTurnNumber, worldState);
        // 2. 构建用户消息
        const userMessage = this.buildUserMessage(worldState, memoryContext);
        // 3. 估算token
        const estimatedTokens = this.estimateTotalTokens(this.genesisEnginePrompt, userMessage);
        return {
            systemPrompt: this.genesisEnginePrompt,
            userMessage,
            estimatedTokens
        };
    }
    buildUserMessage(state, memory) {
        const parts = [];
        // 世界记忆（近景+中景+远景）
        parts.push(memory.recent);
        parts.push(memory.episodes);
        parts.push(memory.timeline);
        // 分隔线
        parts.push("\n" + "=".repeat(50) + "\n");
        parts.push("【当前世界状态】\n");
        // 当前状态（精简版）
        parts.push(this.formatWorldContext(state.world_context));
        parts.push(this.formatPlayerState(state.player));
        parts.push(this.formatLocationState(state.location_state));
        parts.push(this.formatActiveNPCs(state.active_npcs));
        parts.push(this.formatActiveQuests(state.active_quests));
        parts.push(this.formatSystemRules());
        // 玩家输入
        parts.push("\n" + "=".repeat(50) + "\n");
        parts.push(`【玩家行动】\n${state.player_input}\n`);
        return parts.join("\n");
    }
    // ============================================================
    // 状态格式化方法
    // ============================================================
    formatWorldContext(ctx) {
        return `\n世界概况：\n` +
            `- 当前地点：${ctx.current_location}\n` +
            `- 时间：${ctx.time}\n` +
            `- 天气：${ctx.weather}\n` +
            `- 氛围：${ctx.atmosphere}\n`;
    }
    formatPlayerState(player) {
        const reputation = Object.entries(player.reputation)
            .map(([k, v]) => `${k}:${v}`)
            .join(", ");
        const numericState = [
            typeof player.hp === "number" && typeof player.max_hp === "number"
                ? `HP：${player.hp}/${player.max_hp}`
                : null,
            typeof player.mp === "number" && typeof player.max_mp === "number"
                ? `MP：${player.mp}/${player.max_mp}`
                : null,
            typeof player.gold === "number"
                ? `金钱：${player.gold}`
                : null
        ].filter(Boolean).join("，");
        return `\n玩家状态：\n` +
            `- 姓名：${player.name}\n` +
            `- 修为：${player.cultivation_level}\n` +
            `- 数值：${numericState || "未设定"}\n` +
            `- 声望：{${reputation}}\n` +
            `- 状态：${player.active_effects.join(", ") || "无"}\n` +
            `- 物品：${player.inventory_summary.join(", ") || "无"}\n`;
    }
    formatLocationState(loc) {
        return `\n地点状态【${loc.name}】：\n` +
            `- 描述：${loc.description}\n` +
            `- 相邻：${loc.connected_locations.join(", ")}\n` +
            `- 在场NPC：${loc.present_npcs.join(", ") || "无"}\n` +
            `- 环境：${loc.environmental_status}\n`;
    }
    formatActiveNPCs(npcs) {
        if (npcs.length === 0)
            return "\n在场NPC：无\n";
        const lines = npcs.map(npc => `- ${npc.name}：${npc.short_description} ` +
            `(状态:${npc.current_status}, 态度:${npc.attitude_to_player}` +
            `${typeof npc.hp === "number" && typeof npc.max_hp === "number" ? `, HP:${npc.hp}/${npc.max_hp}` : ""}` +
            `${typeof npc.mp === "number" && typeof npc.max_mp === "number" ? `, MP:${npc.mp}/${npc.max_mp}` : ""})`);
        return `\n在场NPC：\n${lines.join("\n")}\n`;
    }
    formatSystemRules() {
        return `\n系统硬规则：\n` +
            `- 可自由生成：主线推进、支线剧情、场景细节、台词、事件演出\n` +
            `- 必须稳定：人物ID、地点ID、任务ID、名称、状态、背包、数值属性\n` +
            `- 数值优先：HP、MP、金钱、态度等变化必须与上下文一致\n` +
            `- 行动灵活：动作描述可以自由生成，但结果必须映射到既有状态\n` +
            `- 叙事篇幅：单回合 narrative 以 100-200 字为宜，要兼顾画面、动作与结果\n` +
            `- 结构化更新：玩家数值、背包、状态效果、NPC数值与态度变化必须写入 state_changes 对应字段\n`;
    }
    formatActiveQuests(quests) {
        if (quests.length === 0)
            return "\n当前任务：无\n";
        const lines = quests.map(q => `- [${q.status}] ${q.title}：${q.objective}`);
        return `\n当前任务：\n${lines.join("\n")}\n`;
    }
    // ============================================================
    // Token估算
    // ============================================================
    estimateTotalTokens(system, user) {
        // 包含消息格式的开销
        const overhead = 10;
        return this.estimateTokens(system) +
            this.estimateTokens(user) +
            overhead;
    }
    estimateTokens(text) {
        const chineseChars = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
        const otherChars = text.length - chineseChars;
        return Math.ceil(chineseChars * 1.5 + otherChars * 0.25);
    }
    // ============================================================
    // 回合管理
    // ============================================================
    setCurrentTurnNumber(turn) {
        this.currentTurnNumber = turn;
    }
    incrementTurn() {
        this.currentTurnNumber++;
    }
    getCurrentTurnNumber() {
        return this.currentTurnNumber;
    }
    addTurnRecord(record) {
        this.memoryAssembler.addTurnRecord(record);
    }
    addEpisodeSummary(summary) {
        this.memoryAssembler.addEpisodeSummary(summary);
    }
    addTimelineEvent(event) {
        this.memoryAssembler.addTimelineEvent(event);
    }
    addAchievement(achievement) {
        this.memoryAssembler.addAchievement(achievement);
    }
    setFactions(factions) {
        this.memoryAssembler.setFactions(factions);
    }
}
exports.PromptAssembler = PromptAssembler;
// ============================================================
// 错误类
// ============================================================
class CanonViolationError extends Error {
    constructor(violations) {
        super(`Canon violation: ${violations.length} issues found`);
        this.violations = violations;
        this.name = "CanonViolationError";
    }
}
exports.CanonViolationError = CanonViolationError;
// 主生成函数
async function generateTurn(worldState, llmClient, genesisPrompt, canonCheck) {
    const assembler = new PromptAssembler(genesisPrompt);
    const prompt = assembler.assemble(worldState);
    console.log(`Estimated tokens: ${prompt.estimatedTokens}`);
    const response = await llmClient.complete({
        system: prompt.systemPrompt,
        messages: [{ role: "user", content: prompt.userMessage }],
        temperature: 0.8,
        response_format: { type: "json_object" }
    });
    // 解析并验证
    const output = JSON.parse(response.content);
    // Canon Guardian检查
    if (canonCheck) {
        const canonResult = await canonCheck(output);
        if (canonResult.verdict === "rejected") {
            throw new CanonViolationError(canonResult.violations || []);
        }
    }
    return output;
}
// ============================================================
// 工厂函数
// ============================================================
function createPromptAssembler(genesisPrompt) {
    return new PromptAssembler(genesisPrompt);
}
