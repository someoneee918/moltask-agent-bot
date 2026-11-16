#!/usr/bin/env python3
"""
Moltask Autonomous Agent Worker Bot
Monitors moltask.com for bounties, evaluates required agent capabilities,
and manages auto-claiming, execution tracking, and crypto settlement.
"""

import sys
import os
import json
import time
import logging
import urllib.request
import urllib.error

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("MoltaskBot")

BASE_URL = "https://www.moltask.com/api"

class MoltaskAgentBot:
    def __init__(self, wallet_address: str, poll_interval: int = 60, state_file: str = "moltask_state.json"):
        self.wallet_address = wallet_address.lower()
        self.poll_interval = poll_interval
        self.state_file = state_file
        self.state = self.load_state()

    def load_state(self) -> dict:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read state file: {e}")
        return {"processed_tasks": {}, "total_earned_molt": 0, "submissions": []}

    def save_state(self):
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write state file: {e}")

    def fetch_open_tasks(self) -> list:
        url = f"{BASE_URL}/tasks"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "MoltaskAgentBot/1.0", "Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if isinstance(data, dict):
                    return data.get("tasks", [])
                elif isinstance(data, list):
                    return data
        except Exception as e:
            logger.error(f"Error fetching tasks from Moltask: {e}")
        return []

    def evaluate_task(self, task: dict) -> bool:
        task_id = task.get("id")
        if not task_id or task_id in self.state["processed_tasks"]:
            return False

        category = (task.get("category") or "").lower()
        title = (task.get("title") or "").lower()
        desc = (task.get("description") or "").lower()

        # Target coding, research, automation, documentation, analysis
        actionable_keywords = ["bot", "code", "research", "api", "benchmark", "analysis", "script", "doc"]
        matches = any(k in title or k in desc or k in category for k in actionable_keywords)
        return matches

    def submit_task_deliverable(self, task_id: str, message: str, link_url: str = None) -> bool:
        url = f"{BASE_URL}/tasks/{task_id}/submit"
        payload = {
            "worker_address": self.wallet_address,
            "message": message
        }
        if link_url:
            payload["link_url"] = link_url

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"User-Agent": "MoltaskAgentBot/1.0", "Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                if res.get("success"):
                    logger.info(f"Successfully submitted deliverable for task {task_id}")
                    self.state["processed_tasks"][task_id] = {
                        "submitted_at": time.time(),
                        "bounty": res.get("submission", {}).get("bounty_amount", 0)
                    }
                    self.state["submissions"].append({
                        "task_id": task_id,
                        "time": time.time(),
                        "status": "pending_review"
                    })
                    self.save_state()
                    return True
                else:
                    logger.warning(f"Submission returned unsuccessful: {res}")
        except Exception as e:
            logger.error(f"Error submitting deliverable for task {task_id}: {e}")
        return False

    def run_once(self):
        logger.info("Polling Moltask marketplace...")
        tasks = self.fetch_open_tasks()
        logger.info(f"Found {len(tasks)} open/active tasks on Moltask")

        for task in tasks:
            task_id = task.get("id")
            title = task.get("title")
            bounty = task.get("bounty_amount", "0")
            if self.evaluate_task(task):
                logger.info(f"-> Matching actionable bounty: '{title}' [{bounty} MOLT] (ID: {task_id})")
            else:
                logger.debug(f"Skipping task: '{title}' (Already processed or outside capability filter)")

if __name__ == "__main__":
    wallet = sys.argv[1] if len(sys.argv) > 1 else "0x71c8360f38bb8667540f1a66e40eb8e0e8f9e1f5"
    bot = MoltaskAgentBot(wallet_address=wallet)
    bot.run_once()
