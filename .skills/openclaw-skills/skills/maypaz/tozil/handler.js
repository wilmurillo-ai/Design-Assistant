/**
 * Tozil hook for OpenClaw — tracks AI costs via log-based sync.
 *
 * How it works:
 *   1. On gateway:startup, starts a periodic sync timer
 *   2. Every sync interval, reads OpenClaw session logs
 *   3. Extracts model, tokens, and cost data from log entries
 *   4. Sends batch data to Tozil API
 *
 * This approach works with every provider OpenClaw supports because
 * it reads the session logs directly — no SDK patching needed.
 *
 * Installation:
 *   1. Copy this folder to ~/.openclaw/hooks/tozil/
 *   2. Set TOZIL_API_KEY in your environment
 *   3. openclaw hooks enable tozil
 *   4. openclaw gateway restart
 *
 * Get your API key at https://agents.tozil.dev
 */

import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { syncCosts } from "./sync_costs.js";

let initialized = false;
let syncTimer = null;

// Sync every hour by default
const SYNC_INTERVAL_MS = Number(process.env.TOZIL_SYNC_INTERVAL_MS) || 60 * 60 * 1000;

// Log file for handler errors
const LOG_FILE = process.env.HOME + "/.openclaw/logs/tozil-handler.log";

/**
 * Logging function with timestamps
 */
function log(level, message, error = null) {
  try {
    const timestamp = new Date().toISOString();
    const logLine = `[${timestamp}] [${level.toUpperCase()}] [tozil-handler] ${message}`;

    // Ensure log directory exists
    const logDir = dirname(LOG_FILE);
    if (!existsSync(logDir)) {
      mkdirSync(logDir, { recursive: true });
    }

    // Write to file
    writeFileSync(LOG_FILE, logLine + '\n', { flag: 'a' });

    // Also log to console in debug mode
    if (process.env.TOZIL_DEBUG) {
      if (level === 'error' && error) {
        console.error(logLine, error);
      } else {
        console.log(logLine);
      }
    }
  } catch (logError) {
    // Fallback to console if file logging fails
    console.error('[tozil-handler] Logging failed:', logError.message);
  }
}

/**
 * Validate API key format
 */
function validateApiKey(apiKey) {
  if (!apiKey) {
    throw new Error('TOZIL_API_KEY not set');
  }

  if (!apiKey.startsWith('tz_')) {
    throw new Error('Invalid TOZIL_API_KEY format (should start with tz_)');
  }

  if (apiKey.length < 20) {
    throw new Error('TOZIL_API_KEY appears too short');
  }

  return true;
}

export default async function handler(event) {
  if (initialized) return;
  if (event.type !== "gateway:startup" && event.type !== "agent:bootstrap") return;

  try {
    log('info', `Handler triggered by event: ${event.type}`);

    // Validate API key
    const apiKey = process.env.TOZIL_API_KEY;
    validateApiKey(apiKey);
    log('info', 'API key validation passed');

    // Run initial sync
    log('info', 'Starting initial sync');
    runSync();

    // Schedule periodic syncs
    syncTimer = setInterval(() => {
      log('info', 'Running scheduled sync');
      runSync();
    }, SYNC_INTERVAL_MS);

    log('info', `Periodic sync scheduled every ${SYNC_INTERVAL_MS}ms (${SYNC_INTERVAL_MS / 60000}min)`);

    initialized = true;
    log('info', 'Handler initialization completed successfully');

  } catch (error) {
    log('error', `Handler initialization failed: ${error.message}`, error);

    // Clean up timer if it was created
    if (syncTimer) {
      clearInterval(syncTimer);
      syncTimer = null;
    }

    // Don't throw - never break OpenClaw
    return;
  }
}

/**
 * Cleanup function for graceful shutdown
 */
function cleanup() {
  if (syncTimer) {
    log('info', 'Cleaning up sync timer');
    clearInterval(syncTimer);
    syncTimer = null;
  }
}

// Handle process shutdown
process.on('SIGTERM', cleanup);
process.on('SIGINT', cleanup);

function runSync() {
  const startTime = Date.now();

  syncCosts().then(() => {
    const duration = Date.now() - startTime;
    log('info', `Sync completed successfully in ${duration}ms`);
  }).catch((error) => {
    const duration = Date.now() - startTime;
    log('error', `Sync failed after ${duration}ms: ${error.message}`, error);
  });
}
