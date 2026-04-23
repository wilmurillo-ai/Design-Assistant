"use strict";
// ============================================================
// 数据模型定义 - TypeScript
// ============================================================
Object.defineProperty(exports, "__esModule", { value: true });
exports.DEFAULT_GAME_CONFIG = exports.DEFAULT_CONTEXT_CONFIG = void 0;
// ============================================================
// 默认配置
// ============================================================
exports.DEFAULT_CONTEXT_CONFIG = {
    totalContextWindow: 8000,
    reservedForOutput: 2000,
    recentTurns: 3,
    summaryInterval: 5
};
exports.DEFAULT_GAME_CONFIG = {
    maxOptionsPerTurn: 6,
    minOptionsPerTurn: 3,
    maxNarrativeLength: 150,
    contextWindowSize: 8000,
    enableCanonGuardian: true,
    canonConfidenceThreshold: 0.8
};
