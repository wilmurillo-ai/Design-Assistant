import {
  GenesisOutput,
  NPCUpdates,
  NPCState,
  PlayerOption,
  WorldStateInput
} from './data_models';

export const CUSTOM_ACTION_OPTION: PlayerOption = {
  type: "action",
  description: "自定义行动（告诉我你想做什么）"
};

export function ensureSuggestedOptions(options: PlayerOption[] | undefined): PlayerOption[] {
  const normalized = (options || [])
    .filter(opt => typeof opt?.description === "string" && opt.description.trim().length > 0)
    .slice(0, 3)
    .map(opt => ({
      ...opt,
      description: opt.description.trim()
    }));

  const fallbacks: PlayerOption[] = [
    { type: "investigate", description: "观察四周环境" },
    { type: "dialogue", description: "尝试与在场人物交谈" },
    { type: "movement", description: "前往相邻区域继续探索" }
  ];

  while (normalized.length < 3) {
    normalized.push(fallbacks[normalized.length]);
  }

  return normalized;
}

export function ensureActionOptions(options: PlayerOption[] | undefined): PlayerOption[] {
  return [...ensureSuggestedOptions(options), CUSTOM_ACTION_OPTION];
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function toDisplayString(value: unknown): string | null {
  if (typeof value === "string") {
    const normalized = value.trim();
    return normalized.length > 0 ? normalized : null;
  }

  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }

  if (!isRecord(value)) {
    return null;
  }

  const candidates = [
    value.name,
    value.title,
    value.description,
    value.label,
    value.effect,
    value.item,
    value.value
  ];

  for (const candidate of candidates) {
    if (typeof candidate === "string" && candidate.trim().length > 0) {
      return candidate.trim();
    }
  }

  return null;
}

export function normalizeDisplayStrings(values: unknown[] | undefined): string[] {
  if (!Array.isArray(values)) {
    return [];
  }

  return Array.from(new Set(
    values
      .map(toDisplayString)
      .filter((value): value is string => typeof value === "string" && value.length > 0)
  ));
}

export function uniqueStrings(values: unknown[]): string[] {
  return normalizeDisplayStrings(values);
}

function normalizeInventoryItemKey(value: string): string {
  return value
    .replace(/（[^）]*）/g, "")
    .replace(/\([^)]*\)/g, "")
    .replace(/\s+/g, "")
    .trim();
}

function mergeInventoryItems(values: string[]): string[] {
  const orderedKeys: string[] = [];
  const selected = new Map<string, string>();

  for (const value of uniqueStrings(values)) {
    const key = normalizeInventoryItemKey(value) || value;
    if (!selected.has(key)) {
      orderedKeys.push(key);
      selected.set(key, value);
      continue;
    }

    const existing = selected.get(key) || "";
    if (value.length > existing.length) {
      selected.set(key, value);
    }
  }

  return orderedKeys.map(key => selected.get(key) || key);
}

export function clampNumber(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

export function previewJson(value: unknown): string {
  try {
    return JSON.stringify(value).slice(0, 600);
  } catch {
    return String(value);
  }
}

export function normalizeWorldState(state: WorldStateInput, playerName: string): WorldStateInput {
  return {
    world_context: {
      current_location: state.world_context?.current_location || state.location_state?.id || "starting-area",
      time: state.world_context?.time || "清晨",
      weather: state.world_context?.weather || "晴",
      atmosphere: state.world_context?.atmosphere || "未知"
    },
    player: {
      name: state.player?.name || playerName || "旅人",
      cultivation_level: state.player?.cultivation_level || "凡人",
      hp: typeof state.player?.hp === "number" ? state.player.hp : 100,
      max_hp: typeof state.player?.max_hp === "number" ? state.player.max_hp : 100,
      mp: typeof state.player?.mp === "number" ? state.player.mp : 50,
      max_mp: typeof state.player?.max_mp === "number" ? state.player.max_mp : 50,
      gold: typeof state.player?.gold === "number" ? state.player.gold : 100,
      reputation: state.player?.reputation || {},
      active_effects: normalizeDisplayStrings(state.player?.active_effects),
      inventory_summary: normalizeDisplayStrings(state.player?.inventory_summary)
    },
    location_state: {
      id: state.location_state?.id || state.world_context?.current_location || "starting-area",
      name: state.location_state?.name || "起始地",
      description: state.location_state?.description || "一切故事的起点。",
      connected_locations: state.location_state?.connected_locations || [],
      present_npcs: state.location_state?.present_npcs || [],
      discovered_secrets: normalizeDisplayStrings(state.location_state?.discovered_secrets),
      environmental_status: state.location_state?.environmental_status || "暂无异状"
    },
    active_npcs: (state.active_npcs || []).map(npc => ({
      ...npc,
      hp: typeof npc.hp === "number" ? npc.hp : 100,
      max_hp: typeof npc.max_hp === "number" ? npc.max_hp : 100,
      mp: typeof npc.mp === "number" ? npc.mp : 0,
      max_mp: typeof npc.max_mp === "number" ? npc.max_mp : 0,
      known_secrets: normalizeDisplayStrings(npc.known_secrets)
    })),
    active_quests: state.active_quests || [],
    world_memory: {
      recent_events: normalizeDisplayStrings(state.world_memory?.recent_events),
      plot_summary: state.world_memory?.plot_summary || "",
      major_events: normalizeDisplayStrings(state.world_memory?.major_events)
    },
    player_input: state.player_input || ""
  };
}

export function formatCurrentStateSummary(state: WorldStateInput): string {
  const activeQuestTitles = state.active_quests
    .filter(quest => quest.status === "active")
    .map(quest => quest.title);

  const npcNames = state.active_npcs
    .filter(npc => state.location_state.present_npcs.includes(npc.id))
    .map(npc => npc.name);

  return [
    `地点：${state.location_state.name}`,
    `时间：${state.world_context.time}`,
    `天气：${state.world_context.weather}`,
    `氛围：${state.world_context.atmosphere}`,
    `角色：${state.player.name}（${state.player.cultivation_level}）`,
    `生命：${state.player.hp ?? "?"}/${state.player.max_hp ?? "?"}`,
    `灵力：${state.player.mp ?? "?"}/${state.player.max_mp ?? "?"}`,
    `金钱：${state.player.gold ?? 0}`,
    `状态：${state.player.active_effects.join("、") || "无"}`,
    `背包：${state.player.inventory_summary.join("、") || "空"}`,
    `线索：${state.location_state.discovered_secrets.join("、") || "无"}`,
    `在场NPC：${npcNames.join("、") || "无"}`,
    `当前任务：${activeQuestTitles.join("、") || "无"}`
  ].join("\n");
}

export function updateWorldState(state: WorldStateInput, output: GenesisOutput): void {
  if (output.atmosphere_shift) {
    state.world_context.atmosphere = output.atmosphere_shift;
  }

  applyPlayerUpdates(state, output);
  applyLocationUpdates(state, output);
  applyNpcUpdates(state, output);
  applyQuestUpdates(state, output);
  applyWorldMemoryUpdates(state, output);
}

function applyPlayerUpdates(state: WorldStateInput, output: GenesisOutput): void {
  const playerUpdates = output.state_changes.player_updates;
  if (!playerUpdates) {
    return;
  }

  if (typeof playerUpdates.hp_delta === "number") {
    const maxHp = state.player.max_hp ?? 100;
    const currentHp = state.player.hp ?? maxHp;
    state.player.hp = clampNumber(currentHp + playerUpdates.hp_delta, 0, maxHp);
  }

  if (typeof playerUpdates.mp_delta === "number") {
    const maxMp = state.player.max_mp ?? 0;
    const currentMp = state.player.mp ?? maxMp;
    state.player.mp = clampNumber(currentMp + playerUpdates.mp_delta, 0, maxMp);
  }

  if (typeof playerUpdates.gold_delta === "number") {
    const currentGold = state.player.gold ?? 0;
    state.player.gold = Math.max(0, currentGold + playerUpdates.gold_delta);
  }

  if (playerUpdates.add_effects?.length) {
    state.player.active_effects = uniqueStrings([
      ...state.player.active_effects,
      ...playerUpdates.add_effects
    ]);
  }

  if (playerUpdates.remove_effects?.length) {
    const removeSet = new Set(uniqueStrings(playerUpdates.remove_effects));
    state.player.active_effects = state.player.active_effects.filter(effect => !removeSet.has(effect));
  }

  if (playerUpdates.add_items?.length) {
    state.player.inventory_summary = mergeInventoryItems([
      ...state.player.inventory_summary,
      ...playerUpdates.add_items
    ]);
  }

  if (playerUpdates.remove_items?.length) {
    const removeSet = new Set(uniqueStrings(playerUpdates.remove_items));
    state.player.inventory_summary = state.player.inventory_summary.filter(item => !removeSet.has(item));
  }
}

function applyLocationUpdates(state: WorldStateInput, output: GenesisOutput): void {
  if (output.state_changes.new_locations?.length) {
    const newLocationIds = output.state_changes.new_locations.map(location => location.id);
    state.location_state.connected_locations = Array.from(
      new Set([...state.location_state.connected_locations, ...newLocationIds])
    );
  }

  if (!output.state_changes.updated_locations?.length) {
    return;
  }

  for (const updated of output.state_changes.updated_locations) {
    if (updated.id !== state.location_state.id) {
      continue;
    }

    const changes = updated.changes as Record<string, unknown>;
    if (typeof changes.name === "string") state.location_state.name = changes.name;
    if (typeof changes.description === "string") state.location_state.description = changes.description;
    if (Array.isArray(changes.connected_locations)) {
      state.location_state.connected_locations = changes.connected_locations.filter((item): item is string => typeof item === "string");
    }
    if (Array.isArray(changes.present_npcs)) {
      state.location_state.present_npcs = changes.present_npcs.filter((item): item is string => typeof item === "string");
    }
    if (Array.isArray(changes.discovered_secrets)) {
      state.location_state.discovered_secrets = normalizeDisplayStrings(changes.discovered_secrets);
    }
    if (typeof changes.environmental_status === "string") {
      state.location_state.environmental_status = changes.environmental_status;
    }
  }
}

function applyNpcUpdates(state: WorldStateInput, output: GenesisOutput): void {
  createNewNpcs(state, output);
  applyUpdatedNpcSnapshots(state, output);
  applyNpcDeltaUpdates(state, output);
  applyNewItems(state, output);
}

function createNewNpcs(state: WorldStateInput, output: GenesisOutput): void {
  if (!output.state_changes.new_npcs?.length) {
    return;
  }

  for (const npc of output.state_changes.new_npcs) {
    if (!state.active_npcs.some(existing => existing.id === npc.id)) {
      state.active_npcs.push({
        id: npc.id,
        name: npc.name,
        short_description: npc.description,
        current_status: npc.is_hostile ? "hostile" : "active",
        attitude_to_player: npc.initial_attitude ?? 0,
        known_secrets: [],
        last_interaction: "初次登场"
      });
    }

    if (!state.location_state.present_npcs.includes(npc.id)) {
      state.location_state.present_npcs.push(npc.id);
    }
  }
}

function applyUpdatedNpcSnapshots(state: WorldStateInput, output: GenesisOutput): void {
  if (!output.state_changes.updated_npcs?.length) {
    return;
  }

  for (const updated of output.state_changes.updated_npcs) {
    const target = state.active_npcs.find(npc => npc.id === updated.id);
    if (!target) {
      continue;
    }

    const changes = updated.changes as Record<string, unknown>;
    if (typeof changes.name === "string") target.name = changes.name;
    if (typeof changes.short_description === "string") target.short_description = changes.short_description;
    if (typeof changes.description === "string") target.short_description = changes.description;
    if (typeof changes.current_status === "string") target.current_status = changes.current_status;
    if (typeof changes.hp === "number") target.hp = changes.hp;
    if (typeof changes.max_hp === "number") target.max_hp = changes.max_hp;
    if (typeof changes.mp === "number") target.mp = changes.mp;
    if (typeof changes.max_mp === "number") target.max_mp = changes.max_mp;
    if (typeof changes.attitude_to_player === "number") target.attitude_to_player = changes.attitude_to_player;
    if (Array.isArray(changes.known_secrets)) {
      target.known_secrets = normalizeDisplayStrings(changes.known_secrets);
    }
    if (typeof changes.last_interaction === "string") target.last_interaction = changes.last_interaction;
  }
}

function applyNpcDeltaUpdates(state: WorldStateInput, output: GenesisOutput): void {
  if (!output.state_changes.npc_updates?.length) {
    return;
  }

  for (const update of output.state_changes.npc_updates) {
    const target = state.active_npcs.find(npc => npc.id === update.id);
    if (!target) {
      continue;
    }

    applyNpcDeltaUpdate(target, update);
  }
}

function applyNpcDeltaUpdate(target: NPCState, update: NPCUpdates): void {
  if (typeof update.hp_delta === "number") {
    const maxHp = target.max_hp ?? 100;
    const currentHp = target.hp ?? maxHp;
    target.hp = clampNumber(currentHp + update.hp_delta, 0, maxHp);
  }

  if (typeof update.mp_delta === "number") {
    const maxMp = target.max_mp ?? 0;
    const currentMp = target.mp ?? maxMp;
    target.mp = clampNumber(currentMp + update.mp_delta, 0, maxMp);
  }

  if (typeof update.attitude_delta === "number") {
    target.attitude_to_player = clampNumber(target.attitude_to_player + update.attitude_delta, -100, 100);
  }

  if (typeof update.new_status === "string") {
    target.current_status = update.new_status;
  }

  if (update.add_known_secrets?.length) {
    target.known_secrets = uniqueStrings([
      ...target.known_secrets,
      ...update.add_known_secrets
    ]);
  }

  if (update.remove_known_secrets?.length) {
    const removeSet = new Set(uniqueStrings(update.remove_known_secrets));
    target.known_secrets = target.known_secrets.filter(secret => !removeSet.has(secret));
  }

  if (typeof update.last_interaction === "string") {
    target.last_interaction = update.last_interaction;
  }
}

function applyNewItems(state: WorldStateInput, output: GenesisOutput): void {
  if (!output.state_changes.new_items?.length) {
    return;
  }

  const itemNames = output.state_changes.new_items.map(item => item.name);
  state.player.inventory_summary = mergeInventoryItems([...state.player.inventory_summary, ...itemNames]);
}

function applyQuestUpdates(state: WorldStateInput, output: GenesisOutput): void {
  if (output.state_changes.new_quests?.length) {
    for (const quest of output.state_changes.new_quests) {
      if (!state.active_quests.some(existing => existing.id === quest.id)) {
        state.active_quests.push({
          id: quest.id,
          title: quest.title,
          status: "active",
          objective: quest.objectives[0] || quest.description
        });
      }
    }
  }

  if (!output.state_changes.updated_quests?.length) {
    return;
  }

  for (const updated of output.state_changes.updated_quests) {
    const target = state.active_quests.find(quest => quest.id === updated.id);
    if (!target) {
      continue;
    }

    if (updated.status) target.status = updated.status;
    if (updated.progress) target.objective = updated.progress;
    if (updated.new_objectives?.length) target.objective = updated.new_objectives[0];
  }
}

function applyWorldMemoryUpdates(state: WorldStateInput, output: GenesisOutput): void {
  if (output.state_changes.world_events?.length) {
    for (const event of output.state_changes.world_events) {
      if (event.importance === "major" || event.importance === "world_shaking") {
        state.world_memory.major_events.push(event.description);
      }
    }
  }

  state.world_memory.recent_events.push(
    `第${state.world_memory.recent_events.length + 1}回合：${output.narrative.substring(0, 40)}`
  );
  state.world_memory.recent_events = state.world_memory.recent_events.slice(-10);

  const activeQuestTitles = state.active_quests
    .filter(quest => quest.status === "active")
    .map(quest => quest.title);

  state.world_memory.plot_summary = [
    `当前地点：${state.location_state.name}`,
    activeQuestTitles.length > 0 ? `活跃任务：${activeQuestTitles.join("、")}` : "当前暂无活跃任务",
    `最新叙事：${output.narrative.substring(0, 60)}`
  ].join("；");
}
