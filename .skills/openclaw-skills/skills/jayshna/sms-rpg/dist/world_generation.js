"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateInitialWorld = generateInitialWorld;
exports.generateEpisodeSummary = generateEpisodeSummary;
exports.buildCanonReferenceFromState = buildCanonReferenceFromState;
exports.runCanonGuardianCheck = runCanonGuardianCheck;
const kimi_client_1 = require("./kimi_client");
const world_state_utils_1 = require("./world_state_utils");
const INITIAL_WORLD_PROMPT = `你是“世界初始化器”。你的任务不是续写剧情，而是根据用户想玩的世界类型，创建一个可直接进入第一回合的初始世界。

输出必须是严格 JSON，不要输出任何额外文字。

输出格式：
{
  "story_overview": "100字左右，概括这个世界、玩家处境与当前主驱动力",
  "world_state": {
    "world_context": {
      "current_location": "kebab-case-id",
      "time": "时辰描述",
      "weather": "天气描述",
      "atmosphere": "氛围关键词"
    },
    "player": {
      "name": "玩家名",
      "cultivation_level": "当前能力/境界",
      "hp": 100,
      "max_hp": 100,
      "mp": 50,
      "max_mp": 50,
      "gold": 100,
      "reputation": { "faction-id": 0 },
      "active_effects": [],
      "inventory_summary": []
    },
    "location_state": {
      "id": "与 current_location 一致",
      "name": "当前地点名称",
      "description": "地点描述",
      "connected_locations": ["相邻地点ID"],
      "present_npcs": ["当前地点的NPC ID"],
      "discovered_secrets": [],
      "environmental_status": "当前环境变化"
    },
    "active_npcs": [
      {
        "id": "npc-id",
        "name": "NPC名字",
        "short_description": "NPC简述",
        "current_status": "当前状态",
        "hp": 100,
        "max_hp": 100,
        "mp": 0,
        "max_mp": 0,
        "attitude_to_player": 0,
        "known_secrets": [],
        "last_interaction": "尚未正式互动"
      }
    ],
    "active_quests": [
      {
        "id": "quest-id",
        "title": "任务标题",
        "status": "active",
        "objective": "当前目标"
      }
    ],
    "world_memory": {
      "recent_events": ["世界刚建立时的关键事件"],
      "plot_summary": "当前剧情总览",
      "major_events": ["世界背景中的重大历史事件"]
    },
    "player_input": ""
  },
  "opening_narrative": "200-300字左右，作为开场引子，要有明确场景、人物张力与立即可行动的局势",
  "player_options": [
    { "type": "action/dialogue/combat/movement/investigate", "description": "第1个选择", "hint": "可选提示" },
    { "type": "action/dialogue/combat/movement/investigate", "description": "第2个选择", "hint": "可选提示" },
    { "type": "action/dialogue/combat/movement/investigate", "description": "第3个选择", "hint": "可选提示" }
  ]
}

强约束：
1. player_options 必须恰好 3 个
2. 所有 ID 必须稳定、可复用、使用 kebab-case
3. 当前地点、NPC、任务、世界记忆必须相互一致
4. 生成结果必须可直接作为后续回合系统输入
5. 风格要与用户要求的世界一致
6. 人物ID、地点ID、任务ID、名称、数值状态必须稳定，不能含糊，且不可随意更改
7. 剧情可以自由生成，但必须建立在既有结构化状态之上`;
const INITIAL_WORLD_MAX_TOKENS = 4096;
function parseInitialWorldSetup(raw, playerName) {
    if (!(0, world_state_utils_1.isRecord)(raw)) {
        throw new Error(`初始世界返回不是对象：${(0, world_state_utils_1.previewJson)(raw)}`);
    }
    if (!(0, world_state_utils_1.isRecord)(raw.world_state)) {
        throw new Error(`初始世界缺少 world_state：${(0, world_state_utils_1.previewJson)(raw)}`);
    }
    const worldState = (0, world_state_utils_1.normalizeWorldState)(raw.world_state, playerName);
    return {
        story_overview: typeof raw.story_overview === "string" && raw.story_overview.trim().length > 0
            ? raw.story_overview.trim()
            : "一个新的世界已经成形，你正站在故事的起点。",
        world_state: worldState,
        opening_narrative: typeof raw.opening_narrative === "string" && raw.opening_narrative.trim().length > 0
            ? raw.opening_narrative.trim()
            : "天地初开，故事自此开始。",
        player_options: (0, world_state_utils_1.ensureActionOptions)(Array.isArray(raw.player_options) ? raw.player_options : [])
    };
}
async function generateInitialWorld(client, worldRequirement, playerName, narrativeStyle = "通俗、利落，偏《庆余年》式叙事") {
    let lastError;
    for (let attempt = 1; attempt <= 3; attempt++) {
        try {
            const raw = await (0, kimi_client_1.kimiChatJson)(client, INITIAL_WORLD_PROMPT, {
                player_name: playerName,
                world_requirement: worldRequirement,
                narrative_style: narrativeStyle,
                attempt,
                previous_error: attempt > 1 ? String(lastError) : undefined,
                reminder: "必须返回包含 story_overview、world_state、opening_narrative、player_options 的严格 JSON，其中 world_state 不可缺失。opening_narrative 请控制在 200-300 字左右，风格通俗流畅，接近《庆余年》式网文叙事。"
            }, Math.max(client.maxTokens, INITIAL_WORLD_MAX_TOKENS));
            return parseInitialWorldSetup(raw, playerName);
        }
        catch (error) {
            lastError = error;
        }
    }
    throw new Error(`初始世界生成失败：${String(lastError)}`);
}
async function generateEpisodeSummary(client, episodePrompt, turnNumber, recentTurns, previousSummary, currentQuests) {
    const summaryOutput = await (0, kimi_client_1.kimiChatJson)(client, episodePrompt, {
        turns: recentTurns.map(turn => ({
            number: turn.turnNumber,
            player_input: turn.playerInput,
            narrative: turn.narrative,
            key_changes: Object.keys(turn.stateChanges || {})
        })),
        previous_summary: previousSummary,
        current_quests: currentQuests
    });
    return {
        id: `episode-${turnNumber - 4}-${turnNumber}`,
        title: summaryOutput.title,
        startTurn: turnNumber - 4,
        endTurn: turnNumber,
        content: summaryOutput.content,
        keyDecisions: summaryOutput.key_decisions || [],
        stateImpact: summaryOutput.state_impact || "",
        newQuestsStarted: summaryOutput.new_quests_started || [],
        questsCompleted: summaryOutput.quests_completed || [],
        importantDiscoveries: summaryOutput.important_discoveries || [],
        npcRelationshipChanges: summaryOutput.npc_relationship_changes || {},
        foreshadowing: summaryOutput.foreshadowing || [],
        hasActiveQuest: currentQuests.length > 0,
        involvesCurrentLocation: true
    };
}
function buildCanonReferenceFromState(state) {
    return {
        npcs: state.active_npcs.map(npc => ({
            id: npc.id,
            status: "alive",
            key_facts: [npc.short_description, npc.current_status].filter(Boolean)
        })),
        locations: [
            {
                id: state.location_state.id,
                key_features: [state.location_state.name, state.location_state.description].filter(Boolean),
                current_state: state.location_state.environmental_status
            }
        ],
        events: [
            ...state.world_memory.major_events.map((event, index) => ({
                id: `major-${index + 1}`,
                description: event,
                participants: []
            })),
            ...state.world_memory.recent_events.map((event, index) => ({
                id: `recent-${index + 1}`,
                description: event,
                participants: []
            }))
        ],
        quests: state.active_quests.map(quest => ({
            id: quest.id,
            status: quest.status,
            outcome: ""
        })),
        relationships: []
    };
}
async function runCanonGuardianCheck(client, canonPrompt, currentWorldState, output) {
    return (0, kimi_client_1.kimiChatJson)(client, canonPrompt, {
        proposal: {
            type: "state_change",
            content: output,
            generated_by: "genesis-engine-v1"
        },
        canon_reference: buildCanonReferenceFromState(currentWorldState),
        check_focus: ["npc_status", "location_consistency", "timeline", "causality"]
    });
}
