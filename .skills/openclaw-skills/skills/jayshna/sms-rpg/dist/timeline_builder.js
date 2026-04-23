"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildTimelineEventsFromTurn = buildTimelineEventsFromTurn;
const world_state_utils_1 = require("./world_state_utils");
function buildTimelineEventsFromTurn(turnNumber, playerInput, state, output) {
    const locationIds = (0, world_state_utils_1.uniqueStrings)([
        state.world_context.current_location,
        state.location_state.id,
        ...(output.state_changes.new_locations?.map(location => location.id) || [])
    ]);
    const locationNames = (0, world_state_utils_1.uniqueStrings)([
        state.location_state.name,
        ...(output.state_changes.new_locations?.map(location => location.name) || [])
    ]);
    const relatedNPCs = (0, world_state_utils_1.uniqueStrings)([
        ...state.location_state.present_npcs,
        ...(output.state_changes.new_npcs?.map(npc => npc.id) || []),
        ...(output.state_changes.updated_npcs?.map(npc => npc.id) || []),
        ...(output.state_changes.npc_updates?.map(npc => npc.id) || [])
    ]);
    const npcNames = (0, world_state_utils_1.uniqueStrings)([
        ...state.active_npcs
            .filter(npc => relatedNPCs.includes(npc.id))
            .map(npc => npc.name),
        ...(output.state_changes.new_npcs?.map(npc => npc.name) || [])
    ]);
    const relatedQuests = (0, world_state_utils_1.uniqueStrings)([
        ...(output.state_changes.new_quests?.map(quest => quest.id) || []),
        ...(output.state_changes.updated_quests?.map(quest => quest.id) || []),
        ...state.active_quests.filter(quest => quest.status === "active").map(quest => quest.id)
    ]);
    const questTitles = (0, world_state_utils_1.uniqueStrings)([
        ...state.active_quests
            .filter(quest => relatedQuests.includes(quest.id))
            .map(quest => quest.title),
        ...(output.state_changes.new_quests?.map(quest => quest.title) || [])
    ]);
    const baseTags = (0, world_state_utils_1.uniqueStrings)([
        ...locationIds,
        ...locationNames,
        ...relatedNPCs,
        ...npcNames,
        ...relatedQuests,
        ...questTitles,
        ...(output.state_changes.world_events?.map(event => event.event_type) || [])
    ]);
    const baseImportance = output.state_changes.world_events?.some(event => event.importance === "world_shaking")
        ? "world_shaking"
        : output.state_changes.world_events?.some(event => event.importance === "major")
            ? "major"
            : "minor";
    const events = [
        {
            id: `turn-${turnNumber}-summary`,
            turn: turnNumber,
            description: output.narrative.substring(0, 80),
            category: "player",
            importance: baseImportance,
            affectedFactions: (0, world_state_utils_1.uniqueStrings)(output.state_changes.world_events?.flatMap(event => event.affected_factions || []) || []),
            relatedNPCs,
            relatedQuests,
            relatedLocations: locationIds,
            npcNames,
            questTitles,
            locationNames,
            tags: (0, world_state_utils_1.uniqueStrings)([...baseTags, "turn-summary"]),
            searchText: [
                playerInput,
                output.narrative,
                ...locationNames,
                ...npcNames,
                ...questTitles,
                ...(output.state_changes.world_events?.map(event => event.description) || [])
            ].join("；")
        }
    ];
    (output.state_changes.world_events || []).forEach((event, index) => {
        events.push({
            id: `turn-${turnNumber}-event-${index + 1}`,
            turn: turnNumber,
            description: event.description,
            category: event.event_type === "discovered"
                ? "location"
                : event.event_type === "dialogue"
                    ? "npc"
                    : event.event_type === "consequence"
                        ? "quest"
                        : "world",
            importance: event.importance || "minor",
            affectedFactions: (0, world_state_utils_1.uniqueStrings)(event.affected_factions || []),
            relatedNPCs,
            relatedQuests,
            relatedLocations: locationIds,
            npcNames,
            questTitles,
            locationNames,
            tags: (0, world_state_utils_1.uniqueStrings)([...baseTags, event.event_type]),
            searchText: [
                event.description,
                output.narrative,
                playerInput,
                ...locationNames,
                ...npcNames,
                ...questTitles
            ].join("；")
        });
    });
    return events;
}
