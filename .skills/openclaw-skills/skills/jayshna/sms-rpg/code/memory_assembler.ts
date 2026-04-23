// ============================================================
// Episodic Memory 组装器 - TypeScript实现
// ============================================================

import {
  MemoryLayer,
  ContextAssemblyConfig,
  TokenBudget,
  AssembledContext,
  TurnRecord,
  EpisodeSummary,
  TimelineEvent,
  FactionRecord,
  PlayerAchievement,
  StateChanges,
  WorldStateInput
} from './data_models';

type MemoryQuery = {
  currentTurn: number;
  locationIds: string[];
  locationNames: string[];
  npcIds: string[];
  npcNames: string[];
  questIds: string[];
  questTitles: string[];
  tags: string[];
  keywords: string[];
};

// ============================================================
// EpisodicMemoryAssembler 类
// ============================================================

export class EpisodicMemoryAssembler {
  private config: ContextAssemblyConfig;
  private recentMemory: TurnRecord[] = [];
  private episodeSummaries: EpisodeSummary[] = [];
  private worldTimeline: TimelineEvent[] = [];
  private factions: FactionRecord[] = [];
  private achievements: PlayerAchievement[] = [];

  constructor(config: ContextAssemblyConfig) {
    this.config = config;
  }

  // ============================================================
  // 核心组装方法
  // ============================================================
  
  assembleContext(currentTurn: number, worldState?: WorldStateInput): AssembledContext {
    const availableTokens = this.config.totalContextWindow - this.config.reservedForOutput;
    
    // 按优先级分配token预算
    const budget = this.calculateBudget(availableTokens);
    const query = worldState ? this.buildMemoryQuery(currentTurn, worldState) : null;
    const retrievedTimelineEvents = query ? this.retrieveRelevantTimelineEvents(query, 6) : [];
    
    return {
      recent: this.assembleRecentMemory(budget.recent),
      episodes: this.assembleEpisodeSummaries(budget.episodes),
      timeline: this.assembleWorldTimeline(budget.timeline, retrievedTimelineEvents),
      metadata: {
        totalTokens: 0,
        coverage: this.calculateCoverage(currentTurn),
        retrievedTimelineEvents: retrievedTimelineEvents.length
      }
    };
  }

  private calculateBudget(totalTokens: number): TokenBudget {
    // 近景：40%（精确记忆最重要）
    // 中景：35%（剧情连贯性）
    // 远景：25%（世界观锚定）
    return {
      recent: Math.floor(totalTokens * 0.40),
      episodes: Math.floor(totalTokens * 0.35),
      timeline: Math.floor(totalTokens * 0.25)
    };
  }

  // ============================================================
  // 近景组装（最近N回合完整记录）
  // ============================================================
  
  private assembleRecentMemory(budget: number): string {
    const recentTurns = this.recentMemory.slice(-this.config.recentTurns);
    
    let assembled = "【近事记忆 - 最近几回合详情】\n";
    assembled += "以下是你（创世者）最近创造的剧情，请确保连续性：\n\n";
    
    for (const turn of recentTurns) {
      assembled += `--- 第${turn.turnNumber}回合 ---\n`;
      assembled += `玩家行动：${turn.playerInput}\n`;
      assembled += `你的叙述：${turn.narrative}\n`;
      assembled += `关键变化：${this.summarizeChanges(turn.stateChanges)}\n\n`;
    }
    
    return this.truncateToBudget(assembled, budget);
  }

  // ============================================================
  // 中景组装（剧情摘要）
  // ============================================================
  
  private assembleEpisodeSummaries(budget: number): string {
    // 按时间倒序，最新的摘要最详细
    const sortedSummaries = [...this.episodeSummaries].sort((a, b) => b.endTurn - a.endTurn);
    
    let assembled = "【剧情摘要 - 过往重要事件】\n";
    assembled += "以下是之前剧情的浓缩摘要，用于保持连贯性：\n\n";
    
    for (let i = 0; i < sortedSummaries.length; i++) {
      const summary = sortedSummaries[i];
      
      // 越旧的摘要越简略
      const detailLevel = i === 0 ? "详细" : i < 3 ? "中等" : "简略";
      
      assembled += `--- ${summary.title} (${detailLevel}) ---\n`;
      assembled += `时间：第${summary.startTurn}-${summary.endTurn}回合\n`;
      assembled += `摘要：${summary.content}\n`;
      assembled += `关键决策：${summary.keyDecisions.join(", ")}\n`;
      assembled += `状态影响：${summary.stateImpact}\n\n`;
      
      // 检查预算
      if (this.estimateTokens(assembled) > budget * 0.8) {
        assembled += "...（更多历史摘要已省略）\n";
        break;
      }
    }
    
    return assembled;
  }

  // ============================================================
  // 远景组装（世界观时间线）
  // ============================================================
  
  private assembleWorldTimeline(budget: number, retrievedTimelineEvents: TimelineEvent[]): string {
    let assembled = "【世界大势 - 重大历史与格局】\n";
    assembled += "以下是影响整个世界的重要事件和势力格局：\n\n";
    
    // 1. 势力格局（始终包含）
    assembled += "【势力格局】\n";
    for (const faction of this.getMajorFactions()) {
      assembled += `- ${faction.name}：${faction.status}\n`;
      assembled += `  与玩家关系：${faction.playerRelation}\n`;
    }
    assembled += "\n";
    
    // 2. 与当前场景最相关的远景记忆
    assembled += "【相关远景记忆】\n";
    if (retrievedTimelineEvents.length > 0) {
      for (const event of retrievedTimelineEvents) {
        const refs = [
          ...(event.locationNames || []),
          ...(event.npcNames || []),
          ...(event.questTitles || [])
        ].slice(0, 4);
        const refText = refs.length > 0 ? `；关联：${refs.join("、")}` : "";
        assembled += `- 第${event.turn}回合：${event.description}${refText}\n`;
      }
    } else {
      assembled += "- 暂无与当前行动强相关的远景记忆命中\n";
    }
    assembled += "\n";

    // 3. 重大历史事件（兜底锚点）
    assembled += "【重大历史事件】\n";
    const majorEvents = this.worldTimeline
      .filter(e => e.importance === "world_shaking" || e.importance === "major")
      .sort((a, b) => b.turn - a.turn)
      .slice(0, 6);

    for (const event of majorEvents) {
      assembled += `- ${event.description}（第${event.turn}回合）\n`;
    }
    if (majorEvents.length === 0) {
      assembled += "- 暂无已记录的重大历史事件\n";
    }
    assembled += "\n";

    // 4. 玩家成就
    assembled += "【玩家成就】\n";
    for (const ach of this.achievements.slice(-5)) {
      assembled += `- ${ach.description}\n`;
    }
    if (this.achievements.length === 0) {
      assembled += "- 暂无关键成就记录\n";
    }
    
    return this.truncateToBudget(assembled, budget);
  }

  // ============================================================
  // 辅助方法
  // ============================================================
  
  private summarizeChanges(changes: StateChanges): string {
    const parts: string[] = [];
    if (changes.new_npcs?.length) parts.push(`新增NPC：${changes.new_npcs.map(n => n.name).join(", ")}`);
    if (changes.new_locations?.length) parts.push(`发现地点：${changes.new_locations.map(l => l.name).join(", ")}`);
    if (changes.updated_npcs?.length) parts.push(`NPC状态变化：${changes.updated_npcs.length}人`);
    if (changes.world_events?.length) parts.push(`事件：${changes.world_events.map(e => e.description).join("; ")}`);
    return parts.join("；") || "无重大变化";
  }

  private estimateTokens(text: string): number {
    // 粗略估计：中文字符 ≈ 1.5 tokens，英文 ≈ 0.25 tokens
    const chineseChars = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
    const otherChars = text.length - chineseChars;
    return Math.ceil(chineseChars * 1.5 + otherChars * 0.25);
  }

  private truncateToBudget(text: string, budget: number): string {
    const tokens = this.estimateTokens(text);
    if (tokens <= budget) return text;
    
    // 简单截断（实际应用中可能需要更智能的摘要）
    const ratio = budget / tokens;
    const truncateIndex = Math.floor(text.length * ratio * 0.9);
    return text.substring(0, truncateIndex) + "\n...（内容已截断以符合预算）";
  }

  private getMajorFactions(): FactionRecord[] {
    return this.factions.filter(f => 
      f.playerRelation !== 0 || 
      this.worldTimeline.some(e => e.affectedFactions.includes(f.id))
    );
  }

  private calculateCoverage(currentTurn: number): string {
    const candidates = [
      ...this.recentMemory.map(r => r.turnNumber),
      ...this.episodeSummaries.map(s => s.startTurn),
      ...this.worldTimeline.map(e => e.turn)
    ];
    if (candidates.length === 0) {
      return `覆盖第${currentTurn}-${currentTurn}回合`;
    }

    const oldestTurn = Math.min(...candidates);
    return `覆盖第${oldestTurn}-${currentTurn}回合`;
  }

  private buildMemoryQuery(currentTurn: number, state: WorldStateInput): MemoryQuery {
    const locationIds = this.uniqueTerms([
      state.world_context.current_location,
      state.location_state.id
    ]);
    const locationNames = this.uniqueTerms([state.location_state.name]);
    const presentNPCs = state.active_npcs.filter(npc => state.location_state.present_npcs.includes(npc.id));
    const npcIds = this.uniqueTerms(presentNPCs.map(npc => npc.id));
    const npcNames = this.uniqueTerms(presentNPCs.map(npc => npc.name));
    const activeQuests = state.active_quests.filter(quest => quest.status === "active");
    const questIds = this.uniqueTerms(activeQuests.map(quest => quest.id));
    const questTitles = this.uniqueTerms(activeQuests.map(quest => quest.title));
    const keywords = this.uniqueTerms(this.extractKeywords([
      state.player_input,
      state.location_state.name,
      ...npcNames,
      ...questTitles
    ]));

    return {
      currentTurn,
      locationIds,
      locationNames,
      npcIds,
      npcNames,
      questIds,
      questTitles,
      tags: this.uniqueTerms([
        ...locationIds,
        ...locationNames,
        ...npcIds,
        ...npcNames,
        ...questIds,
        ...questTitles
      ]),
      keywords
    };
  }

  private retrieveRelevantTimelineEvents(query: MemoryQuery, limit: number): TimelineEvent[] {
    const minTurn = query.currentTurn - this.config.recentTurns + 1;
    const scored = this.worldTimeline
      .filter(event => event.turn < minTurn)
      .map(event => ({
        event,
        score: this.scoreTimelineEvent(event, query)
      }))
      .filter(item => item.score > 0)
      .sort((a, b) => b.score - a.score || b.event.turn - a.event.turn)
      .slice(0, limit);

    if (scored.length > 0) {
      return scored.map(item => item.event);
    }

    return this.worldTimeline
      .filter(event => event.importance === "world_shaking" || event.importance === "major")
      .sort((a, b) => b.turn - a.turn)
      .slice(0, Math.min(limit, 3));
  }

  private scoreTimelineEvent(event: TimelineEvent, query: MemoryQuery): number {
    let relevance = 0;

    relevance += this.countOverlap(event.relatedLocations || [], query.locationIds) * 6;
    relevance += this.countOverlap(event.locationNames || [], query.locationNames) * 4;
    relevance += this.countOverlap(event.relatedNPCs || [], query.npcIds) * 5;
    relevance += this.countOverlap(event.npcNames || [], query.npcNames) * 4;
    relevance += this.countOverlap(event.relatedQuests || [], query.questIds) * 5;
    relevance += this.countOverlap(event.questTitles || [], query.questTitles) * 4;
    relevance += this.countOverlap(event.tags || [], query.tags) * 3;

    const searchable = this.normalizeTerm([
      event.description,
      event.searchText,
      ...(event.tags || []),
      ...(event.locationNames || []),
      ...(event.npcNames || []),
      ...(event.questTitles || [])
    ].filter(Boolean).join(" "));

    for (const keyword of query.keywords) {
      if (keyword.length >= 2 && searchable.includes(this.normalizeTerm(keyword))) {
        relevance += 2;
      }
    }

    if (relevance <= 0) {
      return 0;
    }

    let score = relevance;
    if (event.importance === "world_shaking") {
      score += 3;
    } else if (event.importance === "major") {
      score += 2;
    } else {
      score += 1;
    }

    return score;
  }

  private countOverlap(left: string[], right: string[]): number {
    if (left.length === 0 || right.length === 0) {
      return 0;
    }

    const rightSet = new Set(right.map(item => this.normalizeTerm(item)));
    return left.reduce((count, item) => {
      return rightSet.has(this.normalizeTerm(item)) ? count + 1 : count;
    }, 0);
  }

  private extractKeywords(values: string[]): string[] {
    const parts: string[] = [];

    for (const value of values) {
      for (const fragment of value.split(/[\s,，。！？；：“”"'\-()（）【】]+/)) {
        const normalized = fragment.trim();
        if (normalized.length >= 2) {
          parts.push(normalized);
        }
      }
    }

    return parts;
  }

  private uniqueTerms(values: string[]): string[] {
    return Array.from(new Set(
      values
        .map(value => value.trim())
        .filter(value => value.length > 0)
    ));
  }

  private normalizeTerm(value: string): string {
    return value.trim().toLowerCase();
  }

  // ============================================================
  // 数据操作方法
  // ============================================================
  
  addTurnRecord(record: TurnRecord): void {
    this.recentMemory.push(record);
    // 保持只保留最近的一定数量
    if (this.recentMemory.length > this.config.recentTurns * 2) {
      this.recentMemory = this.recentMemory.slice(-this.config.recentTurns * 2);
    }
  }

  addEpisodeSummary(summary: EpisodeSummary): void {
    this.episodeSummaries.push(summary);
  }

  addTimelineEvent(event: TimelineEvent): void {
    this.worldTimeline.push(event);
  }

  addAchievement(achievement: PlayerAchievement): void {
    this.achievements.push(achievement);
  }

  setFactions(factions: FactionRecord[]): void {
    this.factions = factions;
  }
}

// ============================================================
// 使用示例
// ============================================================

export function createMemoryAssembler(): EpisodicMemoryAssembler {
  return new EpisodicMemoryAssembler({
    totalContextWindow: 8000,
    reservedForOutput: 2000,
    recentTurns: 3,
    summaryInterval: 5
  });
}

// 示例用法：
// const assembler = createMemoryAssembler();
// const context = assembler.assembleContext(currentTurnNumber);
