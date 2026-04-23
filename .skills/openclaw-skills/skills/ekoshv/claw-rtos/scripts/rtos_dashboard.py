import os
import json
import subprocess
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Attempt to load librarian data if the skill is installed
try:
    import sys
    sys.path.append(str(Path.home() / '.openclaw' / 'workspace' / 'skills' / 'librarian' / 'scripts'))
    from lib_utils import get_db_conn
    from psycopg2.extras import RealDictCursor
    LIBRARIAN_AVAILABLE = True
except ImportError:
    LIBRARIAN_AVAILABLE = False

# HTML Template with improved "Analyzer" features
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ClawRTOS Monitor & Analyzer</title>
    <script src="https://unpkg.com/vis-timeline@latest/standalone/umd/vis-timeline-graph2d.min.js"></script>
    <link href="https://unpkg.com/vis-timeline@latest/styles/vis-timeline-graph2d.min.css" rel="stylesheet" type="text/css" />
    <style>
        :root {
            --bg-color: #0b0e14;
            --card-bg: #151921;
            --border-color: #2d333b;
            --text-main: #adbac7;
            --accent-purple: #9d7dfa;
            --accent-green: #44d685;
            --accent-blue: #539bf5;
            --accent-gold: #e2b714;
            --accent-red: #f47067;
        }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; 
            background: var(--bg-color); 
            color: var(--text-main); 
            margin: 0; 
            padding: 20px; 
        }
        h1, h2, h3 { color: var(--text-main); margin-top: 0; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 10px; margin-bottom: 20px; }
        .wizard-icon { font-size: 32px; filter: drop-shadow(0 0 5px var(--accent-purple)); }
        
        .grid-layout { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
        
        .card { 
            background: var(--card-bg); 
            border: 1px solid var(--border-color); 
            border-radius: 6px; 
            padding: 16px; 
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        #timeline-container { background: var(--card-bg); border-radius: 6px; margin-bottom: 20px; overflow: hidden; }
        .vis-item { border-radius: 4px; border-width: 1px; }
        .vis-item.milestone { background-color: rgba(226, 183, 20, 0.2); border-color: var(--accent-gold); }
        .vis-item.error { background-color: rgba(244, 112, 103, 0.2); border-color: var(--accent-red); }
        .vis-item.task { background-color: rgba(83, 155, 245, 0.2); border-color: var(--accent-blue); }
        
        .status-pill { padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
        .status-running { background: rgba(68, 214, 133, 0.1); color: var(--accent-green); border: 1px solid var(--accent-green); }
        .status-idle { background: rgba(173, 186, 199, 0.1); color: var(--text-main); border: 1px solid var(--text-main); }
        
        .fact-item { border-left: 3px solid var(--accent-purple); padding-left: 10px; margin-bottom: 12px; font-size: 13px; }
        .fact-predicate { color: var(--accent-blue); font-weight: bold; }
        .fact-value { color: var(--text-main); }
        
        .agent-entry { padding: 10px 0; border-bottom: 1px solid var(--border-color); }
        .agent-name { font-weight: bold; color: var(--text-main); }
        .agent-meta { font-size: 11px; color: #768390; margin-top: 4px; }
        
        #heartbeat-pulse { 
            width: 12px; height: 12px; background: var(--accent-green); border-radius: 50%; 
            display: inline-block; margin-right: 8px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(68, 214, 133, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(68, 214, 133, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(68, 214, 133, 0); }
        }

        .tab-btn { background: none; border: none; color: #768390; cursor: pointer; padding: 5px 15px; font-size: 14px; }
        .tab-btn.active { color: var(--accent-purple); border-bottom: 2px solid var(--accent-purple); }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <span class="wizard-icon">🧙🏼‍♂️</span>
            <span style="font-size: 24px; font-weight: bold; margin-left: 10px;">EKOMAN | ClawRTOS Analyzer</span>
        </div>
        <div style="font-size: 14px; color: #768390;">
            <div id="heartbeat-pulse"></div>
            System Active | <span id="last-update">Syncing...</span>
        </div>
    </div>
    
    <div id="timeline-container" class="card">
        <h3 style="margin: 0 0 10px 0; font-size: 14px; color: #768390;">Librarian Temporal Continuum</h3>
        <div id="visualization"></div>
    </div>

    <div class="grid-layout">
        <div class="left-col">
            <div class="card">
                <div style="display: flex; gap: 20px; border-bottom: 1px solid var(--border-color); margin-bottom: 15px;">
                    <button class="tab-btn active" onclick="showTab('agents')">Live Agents</button>
                    <button class="tab-btn" onclick="showTab('episodes')">Recent Episodes</button>
                </div>
                
                <div id="tab-agents">
                    <div id="agent-list">Loading active sessions...</div>
                    <div style="margin-top: 18px;">
                        <h3 style="font-size:14px; color:#768390; margin-bottom:10px;">Recent Subagent Tasks</h3>
                        <div id="subagent-list">Loading recent subagent activity...</div>
                    </div>
                </div>
                <div id="tab-episodes" style="display:none;">
                    <div id="episode-list">Loading memory events...</div>
                </div>
            </div>
        </div>
        
        <div class="right-col">
            <div class="card">
                <h3>🧠 Semantic Memory (Facts)</h3>
                <div id="fact-list">Loading core truths...</div>
            </div>
            
            <div class="card">
                <h3>⚙️ Kernel Stats</h3>
                <div style="font-size: 13px;">
                    <p>RTOS Heartbeat: <span style="color: var(--accent-green);">10.0s</span></p>
                    <p>PostgreSQL: <span style="color: var(--accent-green);">Connected</span></p>
                    <p>Memories Logged: <span id="event-count" style="color: var(--accent-blue);">0</span></p>
                    <p>Stable Facts: <span id="fact-count" style="color: var(--accent-purple);">0</span></p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const container = document.getElementById('visualization');
        const items = new vis.DataSet();
        const options = {
            stack: true,
            start: new Date(Date.now() - 1000 * 60 * 60 * 6), // Last 6 hours
            end: new Date(Date.now() + 1000 * 60 * 30),      // 30 mins future
            editable: false,
            margin: { item: 10, axis: 5 },
            orientation: 'top',
            zoomMin: 1000 * 60 * 5, // 5 mins
            zoomMax: 1000 * 60 * 60 * 24 * 7 // 1 week
        };
        const timeline = new vis.Timeline(container, items, options);

        function showTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('tab-agents').style.display = tab === 'agents' ? 'block' : 'none';
            document.getElementById('tab-episodes').style.display = tab === 'episodes' ? 'block' : 'none';
        }

        async function updateData() {
            try {
                const res = await fetch('/api/data');
                const data = await res.json();
                
                // Update Timeline
                const timelineItems = data.history.map(h => ({
                    id: h.id,
                    content: h.title || h.event_type,
                    start: h.created_at,
                    className: h.event_type === 'milestone' ? 'milestone' : (h.event_type === 'error' ? 'error' : 'task'),
                    title: h.content // Tooltip
                }));
                items.update(timelineItems);

                // Update Live Agents / Recent Sessions
                const sessions = Array.isArray(data.live.sessions) ? data.live.sessions : [];
                document.getElementById('agent-list').innerHTML = sessions.length ? sessions.map(s => {
                    const name = s.displayName || (s.key ? s.key.split(':').pop() : 'unknown');
                    const status = s.status || (s.ageMs && s.ageMs < 15 * 60 * 1000 ? 'running' : 'idle');
                    const model = s.model || 'unknown-model';
                    const tokens = Number.isFinite(s.totalTokens) ? s.totalTokens.toLocaleString() : '—';
                    const channel = s.channel || s.kind || 'webchat';
                    return `
                    <div class="agent-entry">
                        <div style="display: flex; justify-content: space-between;">
                            <span class="agent-name">${name}</span>
                            <span class="status-pill status-${status === 'running' ? 'running' : 'idle'}">${status}</span>
                        </div>
                        <div class="agent-meta">
                            ${model} | ${tokens} tokens | ${channel}
                        </div>
                    </div>
                `}).join('') : "No active or recent sessions detected.";

                // Update Subagent activity
                const activeSubs = Array.isArray(data.subagents?.active) ? data.subagents.active : [];
                const recentSubs = Array.isArray(data.subagents?.recent) ? data.subagents.recent : [];
                const mergedSubs = [...activeSubs, ...recentSubs];
                document.getElementById('subagent-list').innerHTML = mergedSubs.length ? mergedSubs.map(s => `
                    <div class="agent-entry">
                        <div style="display:flex; justify-content:space-between; gap:12px;">
                            <span class="agent-name">${s.label || s.sessionKey || 'subagent'}</span>
                            <span class="status-pill status-${s.status === 'running' ? 'running' : 'idle'}">${s.status || 'done'}</span>
                        </div>
                        <div class="agent-meta">${s.runtime || ''}${s.model ? ' | ' + s.model : ''}</div>
                    </div>
                `).join('') : 'No recent subagent activity.';

                // Update Episodes
                document.getElementById('episode-list').innerHTML = data.history.map(h => {
                    const content = h.content || '';
                    return `
                    <div style="font-size: 12px; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #222;">
                        <span style="color: var(--accent-purple);">[${new Date(h.created_at).toLocaleTimeString()}]</span> 
                        <strong style="color: #fff;">${h.title || h.event_type}</strong>
                        <div style="color: #888; margin-top: 4px;">${content.substring(0, 150)}${content.length > 150 ? '...' : ''}</div>
                    </div>
                `}).join('');

                // Update Facts
                document.getElementById('fact-list').innerHTML = data.facts.map(f => `
                    <div class="fact-item">
                        <div class="fact-predicate">${f.predicate.replace(/_/g, ' ')}</div>
                        <div class="fact-value">${f.object_text}</div>
                    </div>
                `).join('') || "No semantic facts stored yet.";

                document.getElementById('event-count').innerText = data.stats.events;
                document.getElementById('fact-count').innerText = data.stats.facts;
                document.getElementById('last-update').innerText = "Sync: " + new Date().toLocaleTimeString();
            } catch (e) {
                console.error("Analyzer sync failed", e);
                document.getElementById('last-update').innerText = "Sync Error";
            }
        }

        setInterval(updateData, 5000);
        updateData();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def get_data():
    # 1. Get Live Sessions
    try:
        live_res = subprocess.check_output(["openclaw", "sessions", "--json", "--active", "1440"], text=True)
        live_data = json.loads(live_res)
    except Exception as e:
        print(f"Error fetching sessions: {e}")
        live_data = {"sessions": [], "count": 0}

    # 1b. Get subagent activity directly
    try:
        subagent_res = subprocess.check_output(["openclaw", "subagents", "list", "--json"], text=True)
        subagent_data = json.loads(subagent_res)
    except Exception as e:
        print(f"Error fetching subagents: {e}")
        subagent_data = {"active": [], "recent": []}

    # 2. Get Librarian Data (if available)
    history = []
    facts = []
    stats = {"events": 0, "facts": 0}
    
    if LIBRARIAN_AVAILABLE:
        try:
            conn = get_db_conn()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Episodes (filter out noisy heartbeat prompt/acks from timeline and reports)
                cur.execute("""
                    SELECT id, event_type, title, content, created_at
                    FROM librarian_memory_events
                    WHERE COALESCE(content, '') NOT ILIKE '%Read HEARTBEAT.md if it exists (workspace context)%'
                      AND COALESCE(content, '') NOT ILIKE '%If nothing needs attention, reply HEARTBEAT_OK%'
                      AND COALESCE(content, '') NOT ILIKE 'HEARTBEAT_OK%'
                      AND COALESCE(title, '') NOT ILIKE '%heartbeat%'
                    ORDER BY created_at DESC
                    LIMIT 100
                """)
                history = cur.fetchall()
                
                # Semantic Facts
                cur.execute("SELECT predicate, object_text, confidence FROM librarian_facts WHERE status = 'active' ORDER BY updated_at DESC LIMIT 30")
                facts = cur.fetchall()
                
                # Simple Stats (same filtering for meaningful counts)
                cur.execute("""
                    SELECT count(*)
                    FROM librarian_memory_events
                    WHERE COALESCE(content, '') NOT ILIKE '%Read HEARTBEAT.md if it exists (workspace context)%'
                      AND COALESCE(content, '') NOT ILIKE '%If nothing needs attention, reply HEARTBEAT_OK%'
                      AND COALESCE(content, '') NOT ILIKE 'HEARTBEAT_OK%'
                      AND COALESCE(title, '') NOT ILIKE '%heartbeat%'
                """)
                stats['events'] = cur.fetchone()['count']
                cur.execute("SELECT count(*) FROM librarian_facts")
                stats['facts'] = cur.fetchone()['count']
                
            conn.close()
        except Exception as e:
            print(f"Error fetching librarian DB: {e}")

    return jsonify({
        "live": live_data,
        "subagents": subagent_data,
        "history": history,
        "facts": facts,
        "stats": stats
    })

if __name__ == '__main__':
    # Using 0.0.0.0 so it's accessible via host in WSL2
    app.run(host='0.0.0.0', port=8085)
