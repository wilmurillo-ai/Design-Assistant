#!/usr/bin/env python3
"""
agent_base.py — Oblio Agent Framework Base Class
All specialized agents inherit from this. Handles:
  - SQL memory integration via sql_memory.py
  - Model selection via model_router
  - Structured logging to DB + file
  - Graceful error handling with retry
  - Activity heartbeat
  - Ollama inference (text + embeddings)
"""

import os
import sys
import json
import time
import logging
import subprocess
import traceback
from datetime import datetime
from abc import ABC, abstractmethod

sys.path.insert(0, os.path.dirname(__file__))
from model_router import select_model
from sql_memory import SQLMemory, get_memory
from agent_reporter import AgentReport

# ── Config ────────────────────────────────────────────────────────────────────
SQLCMD     = "/opt/mssql-tools/bin/sqlcmd"
LOG_DIR    = "/home/oblio/.openclaw/workspace/logs"
OLLAMA_URL = os.getenv('OLLAMA_BASE_URL', 'http://10.0.0.110:11434')
# ──────────────────────────────────────────────────────────────────────────────


class OblioAgent(ABC):
    """
    Base class for all Oblio specialized agents.

    Subclass and implement:
        - agent_name: str
        - task_types: list[str]
        - run_task(task: dict) -> str  (return result summary)
    """

    agent_name: str = "base_agent"
    task_types: list = []
    budget: str = "free"         # default model budget tier
    max_retries: int = 3
    retry_delay: int = 5
    backend: str = "cloud"       # PRIMARY: cloud (site4now), LOCAL is backup only

    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        log_path = os.path.join(LOG_DIR, f"{self.agent_name}.log")
        logging.basicConfig(
            level=logging.INFO,
            format=f"%(asctime)s [{self.agent_name}] %(levelname)s %(message)s",
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler(sys.stdout),
            ]
        )
        self.log = logging.getLogger(self.agent_name)

        # Initialize SQL memory
        self.mem = get_memory(self.backend)
        self.log.info(f"Agent {self.agent_name} initialized (backend={self.backend}).")
        
        # Initialize reporting
        self.report = AgentReport(self.agent_name)
        self.log.info(f"Reporting initialized for {self.agent_name}.")

    # ── SQL Helpers (legacy — kept for backward compat + custom queries) ─────

    def sqlcmd(self, query: str, timeout: int = 30) -> str:
        """Raw sqlcmd execution. Prefer self.mem.* methods for standard ops."""
        return self.mem.execute(query, timeout)

    def log_activity(self, event_type: str, description: str, metadata: str = ""):
        """Log an event to ActivityLog via sql_memory."""
        self.mem.log_event(event_type, self.agent_name, description, metadata)

    def store_memory(self, category: str, content: str, key_name: str = "",
                     importance: int = 3, tags: str = ""):
        """Store a memory via sql_memory."""
        self.mem.remember(category, key_name, content, importance, tags)

    def get_pending_tasks(self) -> list:
        """Get pending tasks from the queue via sql_memory."""
        rows = self.mem.get_pending_tasks(self.agent_name, self.task_types)
        # Convert to legacy format for backward compat
        tasks = []
        for row in rows:
            tasks.append({
                "id": row.get("id", ""),
                "task_type": row.get("task_type", ""),
                "payload": row.get("payload", ""),
                "priority": row.get("priority", "5"),
                "retry_count": row.get("retry_count", "0"),
                "raw": str(row),
            })
        return tasks

    def claim_task(self, task_id: str):
        """Claim a task via sql_memory."""
        self.mem.claim_task(task_id)

    def complete_task(self, task_id: str, result: str = ""):
        """Complete a task via sql_memory."""
        self.mem.complete_task(task_id, result)

    def fail_task(self, task_id: str, error: str, retry_count: int):
        """Fail a task via sql_memory."""
        self.mem.fail_task(task_id, error, retry_count, self.max_retries)

    # ── Model Selection ───────────────────────────────────────────────────────

    def get_model(self, task_type: str = "chat", **kwargs) -> dict:
        return select_model(task_type, self.budget, **kwargs)

    def ollama_generate(self, prompt: str, model: str = "gemma3:4b",
                        base_url: str = None) -> str:
        """Generate text via Ollama API."""
        import urllib.request
        import json
        url = base_url or OLLAMA_URL
        payload = json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False
        }).encode()
        req = urllib.request.Request(
            f"{url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read())["response"].strip()
        except Exception as e:
            self.log.error(f"Ollama generate error: {e}")
            return ""

    def ollama_chat(self, messages: list, model: str = "gemma3:4b",
                    base_url: str = None) -> str:
        """Chat-style Ollama call with message history."""
        import urllib.request
        import json
        url = base_url or OLLAMA_URL
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "stream": False
        }).encode()
        req = urllib.request.Request(
            f"{url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read())["message"]["content"].strip()
        except Exception as e:
            self.log.error(f"Ollama chat error: {e}")
            return ""

    def ollama_embed(self, text: str, model: str = "nomic-embed-text",
                     base_url: str = None) -> list:
        """
        Generate text embeddings via Ollama for semantic search.
        Requires nomic-embed-text or similar embedding model.

        Returns:
            List of floats (embedding vector), or empty list on failure.
        """
        import urllib.request
        import json
        url = base_url or OLLAMA_URL
        payload = json.dumps({
            "model": model,
            "prompt": text
        }).encode()
        req = urllib.request.Request(
            f"{url}/api/embeddings",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read()).get("embedding", [])
        except Exception as e:
            self.log.error(f"Ollama embed error: {e}")
            return []

    def ollama_vision(self, prompt: str, image_path: str,
                      model: str = "moondream",
                      base_url: str = None) -> str:
        """
        Send an image + text prompt to a vision model via Ollama.

        Args:
            prompt: Text prompt describing what to analyze
            image_path: Path to the image file
            model: Vision model name (moondream, llava, etc.)

        Returns:
            Model response text
        """
        import urllib.request
        import json
        import base64
        url = base_url or OLLAMA_URL

        # Read and encode image
        with open(image_path, 'rb') as f:
            img_b64 = base64.b64encode(f.read()).decode('utf-8')

        payload = json.dumps({
            "model": model,
            "prompt": prompt,
            "images": [img_b64],
            "stream": False
        }).encode()
        req = urllib.request.Request(
            f"{url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read())["response"].strip()
        except Exception as e:
            self.log.error(f"Ollama vision error: {e}")
            return ""

    # ── Abstract Interface ────────────────────────────────────────────────────

    @abstractmethod
    def run_task(self, task: dict) -> str:
        """Execute one task. Return result summary string."""
        pass

    # ── Main Loop ─────────────────────────────────────────────────────────────

    def run_once(self):
        """Process all pending tasks once."""
        tasks = self.get_pending_tasks()
        if not tasks:
            self.log.info("No pending tasks.")
            return 0
        processed = 0
        for task in tasks:
            tid = task["id"]
            self.claim_task(tid)
            retry_count = int(task.get("retry_count", 0) or 0)
            for attempt in range(self.max_retries):
                try:
                    result = self.run_task(task)
                    self.complete_task(tid, result)
                    self.log_activity("task_complete", f"Task {tid}: {result[:200]}")
                    processed += 1
                    break
                except Exception as e:
                    err = traceback.format_exc()
                    self.log.error(f"Task {tid} attempt {attempt+1} failed: {e}")
                    if attempt == self.max_retries - 1:
                        self.fail_task(tid, err, retry_count)
                        self.log_activity("task_failed", f"Task {tid} failed: {str(e)[:200]}")
                    else:
                        time.sleep(self.retry_delay)
        return processed

    def run_loop(self, interval: int = 60):
        """Run continuously, polling for tasks."""
        self.log.info(f"Starting continuous loop (interval={interval}s)")
        while True:
            try:
                n = self.run_once()
                if n:
                    self.log.info(f"Processed {n} tasks.")
            except KeyboardInterrupt:
                self.log.info("Agent stopped by user.")
                break
            except Exception as e:
                self.log.error(f"Loop error: {e}")
            time.sleep(interval)

    # ── Reporting ────────────────────────────────────────────────────────────

    def report_processed(self, category: str, count: int, details: str = ""):
        """Record what was processed."""
        self.report.add_processed(category, count, details)

    def report_stored(self, location: str, item_count: int, samples: list = None, confidence: float = 1.0):
        """Record what was stored."""
        self.report.add_stored(location, item_count, samples, confidence)

    def report_error(self, error_type: str, severity: str, message: str, count: int = 1):
        """Log an error."""
        self.report.add_error(error_type, severity, message, count)

    def report_enrichment(self, metric: str, value: any, description: str = ""):
        """Record what we enriched / learned."""
        self.report.add_enrichment(metric, value, description)

    def report_metric(self, metric_name: str, value: float, unit: str = ""):
        """Add a quality metric."""
        self.report.add_metric(metric_name, value, unit)

    def report_forecast(self, forecast: str):
        """Add a forecast for next week."""
        self.report.add_forecast(forecast)

    def save_report(self):
        """Save the weekly report (JSON + Markdown)."""
        json_path, md_path = self.report.save_all()
        self.log.info(f"Report saved: {md_path} + {json_path}")
        return json_path, md_path
