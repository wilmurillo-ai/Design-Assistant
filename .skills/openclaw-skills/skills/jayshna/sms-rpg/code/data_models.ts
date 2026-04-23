// ============================================================
// 数据模型定义 - TypeScript
// ============================================================

// ============================================================
// 世界状态输入类型
// ============================================================

export interface WorldStateInput {
  world_context: WorldContext;
  player: PlayerState;
  location_state: LocationState;
  active_npcs: NPCState[];
  active_quests: QuestState[];
  world_memory: WorldMemory;
  player_input: string;
}

export interface WorldContext {
  current_location: string;
  time: string;
  weather: string;
  atmosphere: string;
}

export interface PlayerState {
  name: string;
  cultivation_level: string;
  hp?: number;
  max_hp?: number;
  mp?: number;
  max_mp?: number;
  gold?: number;
  reputation: Record<string, number>;
  active_effects: string[];
  inventory_summary: string[];
}

export interface LocationState {
  id: string;
  name: string;
  description: string;
  connected_locations: string[];
  present_npcs: string[];
  discovered_secrets: string[];
  environmental_status: string;
}

export interface NPCState {
  id: string;
  name: string;
  short_description: string;
  current_status: string;
  hp?: number;
  max_hp?: number;
  mp?: number;
  max_mp?: number;
  attitude_to_player: number;
  known_secrets: string[];
  last_interaction: string;
}

export interface QuestState {
  id: string;
  title: string;
  status: "active" | "completed" | "failed";
  objective: string;
}

export interface WorldMemory {
  recent_events: string[];
  plot_summary: string;
  major_events: string[];
}

export interface AssembledContext {
  recent: string;
  episodes: string;
  timeline: string;
  metadata: {
    totalTokens: number;
    coverage: string;
    retrievedTimelineEvents?: number;
  };
}

export interface AssembledPrompt {
  systemPrompt: string;
  userMessage: string;
  estimatedTokens: number;
}

export interface LLMResponse {
  content: string;
}

export interface MemoryLayer {
  priority: number;
  maxTokens: number;
  content: string;
}

export interface ContextAssemblyConfig {
  totalContextWindow: number;
  reservedForOutput: number;
  recentTurns: number;
  summaryInterval: number;
}

export interface TokenBudget {
  recent: number;
  episodes: number;
  timeline: number;
}

// ============================================================
// 回合记录（近景记忆）
// ============================================================

export interface TurnRecord {
  turnNumber: number;
  timestamp: number;
  playerInput: string;
  narrative: string;
  stateChanges: StateChanges;
  selectedOption: number;
}

// ============================================================
// 剧情摘要（中景记忆）
// ============================================================

export interface EpisodeSummary {
  id: string;
  title: string;
  startTurn: number;
  endTurn: number;
  content: string;
  keyDecisions: string[];
  stateImpact: string;
  newQuestsStarted: string[];
  questsCompleted: string[];
  importantDiscoveries: string[];
  npcRelationshipChanges: Record<string, string>;
  foreshadowing: string[];
  hasActiveQuest: boolean;
  involvesCurrentLocation: boolean;
}

// ============================================================
// 时间线事件（远景记忆）
// ============================================================

export interface TimelineEvent {
  id: string;
  turn: number;
  description: string;
  category?: "world" | "location" | "npc" | "quest" | "player" | "relationship";
  importance: "minor" | "major" | "world_shaking";
  affectedFactions: string[];
  relatedNPCs: string[];
  relatedQuests: string[];
  relatedLocations?: string[];
  npcNames?: string[];
  questTitles?: string[];
  locationNames?: string[];
  tags?: string[];
  searchText?: string;
}

// ============================================================
// 势力记录
// ============================================================

export interface FactionRecord {
  id: string;
  name: string;
  description: string;
  status: string;
  playerRelation: number;
  keyMembers: string[];
  territories: string[];
}

// ============================================================
// 玩家成就
// ============================================================

export interface PlayerAchievement {
  id: string;
  turn: number;
  description: string;
  type: "combat" | "exploration" | "social" | "story";
}

// ============================================================
// Genesis Engine 输出类型
// ============================================================

export interface GenesisOutput {
  narrative: string;
  atmosphere_shift?: string;
  state_changes: StateChanges;
  player_options: PlayerOption[];
  gm_notes?: GMNotes;
}

export interface StateChanges {
  player_updates?: PlayerUpdates;
  new_locations?: NewLocation[];
  updated_locations?: UpdatedLocation[];
  new_npcs?: NewNPC[];
  updated_npcs?: UpdatedNPC[];
  npc_updates?: NPCUpdates[];
  new_items?: NewItem[];
  new_quests?: NewQuest[];
  updated_quests?: UpdatedQuest[];
  new_relationships?: NewRelationship[];
  world_events?: WorldEvent[];
}

export interface PlayerUpdates {
  hp_delta?: number;
  mp_delta?: number;
  gold_delta?: number;
  add_effects?: string[];
  remove_effects?: string[];
  add_items?: string[];
  remove_items?: string[];
}

export interface NPCUpdates {
  id: string;
  hp_delta?: number;
  mp_delta?: number;
  attitude_delta?: number;
  new_status?: string;
  add_known_secrets?: string[];
  remove_known_secrets?: string[];
  last_interaction?: string;
}

export interface NewLocation {
  id: string;
  name: string;
  description: string;
  connected_to?: string[];
  secrets?: string[];
  first_visit_narrative?: string;
}

export interface UpdatedLocation {
  id: string;
  changes: Record<string, unknown>;
  change_reason?: string;
}

export interface NewNPC {
  id: string;
  name: string;
  description: string;
  faction?: string;
  secrets?: string[];
  motivation?: string;
  initial_attitude?: number;
  is_hostile?: boolean;
  can_trade?: boolean;
  can_teach?: boolean;
  combat_strength?: "weak" | "average" | "strong" | "master" | "legendary";
}

export interface UpdatedNPC {
  id: string;
  changes: Record<string, unknown>;
  change_reason?: string;
}

export interface NewItem {
  id: string;
  name: string;
  type: "weapon" | "armor" | "consumable" | "material" | "quest" | "misc";
  rarity: "common" | "uncommon" | "rare" | "epic" | "legendary";
  description: string;
  properties?: Record<string, unknown>;
  obtained_from?: string;
}

export interface NewQuest {
  id: string;
  title: string;
  description: string;
  type: "main" | "side" | "faction" | "personal";
  objectives: string[];
  related_npcs?: string[];
  time_limit?: string;
}

export interface UpdatedQuest {
  id: string;
  status?: "active" | "completed" | "failed";
  progress?: string;
  new_objectives?: string[];
}

export interface NewRelationship {
  npc_id: string;
  relationship_type: "friend" | "rival" | "mentor" | "student" | "enemy" | "lover";
  relationship_level?: number;
  formed_reason?: string;
}

export interface WorldEvent {
  event_type: "combat" | "discovered" | "trade" | "dialogue" | "consequence";
  description: string;
  importance?: "minor" | "major" | "world_shaking";
  affected_factions?: string[];
}

export interface PlayerOption {
  type: "action" | "dialogue" | "combat" | "movement" | "investigate";
  description: string;
  hint?: string;
  consequence_hint?: string;
}

export interface GMNotes {
  hidden_clues?: string[];
  foreshadowing?: string[];
  npc_intentions?: Record<string, string>;
  suggested_future_events?: string[];
}

// ============================================================
// Canon Guardian 输出类型
// ============================================================

export interface CanonGuardianOutput {
  verdict: "approved" | "rejected" | "needs_review";
  confidence: number;
  violations?: CanonViolation[];
  warnings?: CanonWarning[];
  metadata?: CanonMetadata;
}

export interface CanonViolation {
  severity: "critical" | "warning" | "info";
  type: "npc_status" | "location_consistency" | "timeline" | "causality" | "character";
  description: string;
  canon_reference?: string;
  proposal_content?: string;
  suggested_fix?: string;
}

export interface CanonWarning {
  type: string;
  description: string;
  suggested_action?: string;
}

export interface CanonMetadata {
  checked_rules?: string[];
  check_duration_ms?: number;
  canon_entries_consulted?: number;
}

// ============================================================
// 世界状态类型（输入到Genesis Engine）
// ============================================================

export interface WorldStateInput {
  world_context: WorldContextInput;
  player: PlayerStateInput;
  location_state: LocationStateInput;
  active_npcs: NPCStateInput[];
  active_quests: QuestStateInput[];
  world_memory: WorldMemoryInput;
  player_input: string;
}

export interface WorldContextInput {
  current_location: string;
  time: string;
  weather: string;
  atmosphere: string;
}

export interface PlayerStateInput {
  name: string;
  cultivation_level: string;
  hp?: number;
  max_hp?: number;
  mp?: number;
  max_mp?: number;
  gold?: number;
  reputation: Record<string, number>;
  active_effects: string[];
  inventory_summary: string[];
}

export interface LocationStateInput {
  id: string;
  name: string;
  description: string;
  connected_locations: string[];
  present_npcs: string[];
  discovered_secrets: string[];
  environmental_status: string;
}

export interface NPCStateInput {
  id: string;
  name: string;
  short_description: string;
  current_status: string;
  hp?: number;
  max_hp?: number;
  mp?: number;
  max_mp?: number;
  attitude_to_player: number;
  known_secrets: string[];
  last_interaction: string;
}

export interface QuestStateInput {
  id: string;
  title: string;
  status: "active" | "completed" | "failed";
  objective: string;
}

export interface WorldMemoryInput {
  recent_events: string[];
  plot_summary: string;
  major_events: string[];
}

// ============================================================
// 配置类型
// ============================================================

export interface ContextAssemblyConfig {
  totalContextWindow: number;
  reservedForOutput: number;
  recentTurns: number;
  summaryInterval: number;
}

export interface GameConfig {
  maxOptionsPerTurn: number;
  minOptionsPerTurn: number;
  maxNarrativeLength: number;
  contextWindowSize: number;
  enableCanonGuardian: boolean;
  canonConfidenceThreshold: number;
}

// ============================================================
// 默认配置
// ============================================================

export const DEFAULT_CONTEXT_CONFIG: ContextAssemblyConfig = {
  totalContextWindow: 8000,
  reservedForOutput: 2000,
  recentTurns: 3,
  summaryInterval: 5
};

export const DEFAULT_GAME_CONFIG: GameConfig = {
  maxOptionsPerTurn: 6,
  minOptionsPerTurn: 3,
  maxNarrativeLength: 150,
  contextWindowSize: 8000,
  enableCanonGuardian: true,
  canonConfidenceThreshold: 0.8
};
