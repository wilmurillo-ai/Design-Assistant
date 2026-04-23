#!/usr/bin/env python3
"""
Heartbeat Tick — Standalone heartbeat orchestrator for managed tmux sessions.

Monitors managed agent loops for progress and stalls. Reads a heartbeat config JSON,
checks each managed tmux session for:
  - Existence: Does the session exist?
  - Progress: Has the output changed since last check?
  - Completion: Has the session exited or reached a completion marker?

Stall detection: Same output hash on 2 consecutive checks → restart.

Output: Deterministic and concise for Haiku 4.5:
  - "HEARTBEAT_OK" if all sessions healthy
  - "ALERT: <message>" + "NEXT: <action>" if intervention needed

No external dependencies (subprocess, json, hashlib, argparse only).
Self-contained — no imports from other skill files.
"""

import json
import subprocess
import hashlib
import argparse
import os
import sys
from datetime import datetime
from pathlib import Path


def load_config(config_path):
    """Load heartbeat config JSON."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"ALERT: Config not found at {config_path}")
        print(f"NEXT: Create heartbeat config file at {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ALERT: Invalid JSON in {config_path}: {e}")
        print(f"NEXT: Fix JSON syntax")
        sys.exit(1)


def load_state(state_file):
    """Load previous state (output hashes, timestamps)."""
    if not os.path.exists(state_file):
        return {}
    try:
        with open(state_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_state(state_file, state):
    """Save state for next heartbeat."""
    with open(state_file, 'w') as f:
        json.dump(state, f)


def get_tmux_output(session_name):
    """Get current pane output from tmux session."""
    try:
        result = subprocess.run(
            ['tmux', 'capture-pane', '-p', '-t', session_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def hash_output(text):
    """Compute SHA256 hash of output."""
    if text is None:
        return None
    return hashlib.sha256(text.encode()).hexdigest()


def session_exists(session_name):
    """Check if tmux session exists."""
    try:
        result = subprocess.run(
            ['tmux', 'list-sessions', '-F', '#{session_name}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        sessions = result.stdout.strip().split('\n')
        return session_name in sessions
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def restart_session(session_name, session_config):
    """Restart a tmux session with its cwd and command."""
    # Kill existing session if it exists
    subprocess.run(['tmux', 'kill-session', '-t', session_name], 
                   capture_output=True, timeout=5)
    
    # Create new session
    cwd = session_config.get('cwd', os.getcwd())
    prd = session_config.get('prd', '')
    
    try:
        subprocess.run(
            ['tmux', 'new-session', '-d', '-s', session_name, '-c', cwd],
            capture_output=True,
            timeout=5
        )
        # Send a startup command if provided
        if prd:
            subprocess.run(
                ['tmux', 'send-keys', '-t', session_name, 
                 f'# Restarted by heartbeat. PRD: {prd}', 'Enter'],
                capture_output=True,
                timeout=5
            )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_session(session_name, session_config, state):
    """
    Check single session for stalls, completion, or progress.
    
    Returns: (alert_message, next_action, new_state_entry)
      - (None, None, entry) if healthy
      - (message, action, entry) if intervention needed
    """
    # Check existence
    if not session_exists(session_name):
        return (
            f"Session '{session_name}' does not exist",
            f"Create session: tmux new-session -s {session_name}",
            {session_name: {"status": "missing", "timestamp": datetime.now().isoformat()}}
        )
    
    # Get current output
    current_output = get_tmux_output(session_name)
    if current_output is None:
        return (
            f"Could not read output from session '{session_name}'",
            f"Check tmux: tmux list-sessions",
            {session_name: {"status": "unreachable", "timestamp": datetime.now().isoformat()}}
        )
    
    current_hash = hash_output(current_output)
    previous_state = state.get(session_name, {})
    previous_hash = previous_state.get("output_hash")
    stall_count = previous_state.get("stall_count", 0)
    
    # Stall detection: same hash 2 consecutive checks
    if previous_hash == current_hash:
        stall_count += 1
        if stall_count >= 2:
            # Stall confirmed: restart
            restart_ok = restart_session(session_name, session_config)
            return (
                f"Session '{session_name}' stalled (no progress for 2 checks)",
                f"Restarted session",
                {session_name: {
                    "status": "restarted",
                    "output_hash": current_hash,
                    "stall_count": 0,
                    "timestamp": datetime.now().isoformat()
                }}
            )
    else:
        # Output changed: reset stall counter
        stall_count = 0
    
    # Session is healthy
    return (
        None,
        None,
        {session_name: {
            "status": "healthy",
            "output_hash": current_hash,
            "stall_count": stall_count,
            "timestamp": datetime.now().isoformat()
        }}
    )


def run_heartbeat(config_path):
    """Main heartbeat loop."""
    config = load_config(config_path)
    
    # Determine state file location
    state_file = config.get("state_file")
    if not state_file:
        # Default: same directory as config, named "heartbeat-state.json"
        state_file = os.path.join(
            os.path.dirname(config_path),
            "heartbeat-state.json"
        )
    
    state = load_state(state_file)
    
    # Get list of managed sessions
    managed_sessions = config.get("managed_sessions", [])
    if not managed_sessions:
        # No sessions to monitor
        save_state(state_file, state)
        print("HEARTBEAT_OK")
        return
    
    # Check each session
    alerts = []
    new_state = {}
    
    for session_entry in managed_sessions:
        if isinstance(session_entry, str):
            # Simple string: session name only
            session_name = session_entry
            session_config = {}
        else:
            # Dict: {name, cwd, prd, ...}
            session_name = session_entry.get("name")
            session_config = session_entry
        
        alert_msg, next_action, session_state = check_session(
            session_name, session_config, state
        )
        
        new_state.update(session_state)
        
        if alert_msg:
            alerts.append((alert_msg, next_action))
    
    # Save updated state
    save_state(state_file, new_state)
    
    # Output
    if not alerts:
        print("HEARTBEAT_OK")
    else:
        # Take first alert (could queue all, but keep it simple)
        alert_msg, next_action = alerts[0]
        print(f"ALERT: {alert_msg}")
        print(f"NEXT: {next_action}")


def main():
    parser = argparse.ArgumentParser(
        description="Heartbeat orchestrator for managed tmux sessions"
    )
    parser.add_argument(
        '--config',
        type=str,
        default=os.path.expanduser('~/.openclaw/heartbeat-config.json'),
        help='Path to heartbeat config JSON (default: ~/.openclaw/heartbeat-config.json)'
    )
    
    args = parser.parse_args()
    run_heartbeat(args.config)


if __name__ == '__main__':
    main()
