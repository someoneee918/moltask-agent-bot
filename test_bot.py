#!/usr/bin/env python3
"""
Test Suite for Moltask Agent Bot
Verifies marketplace API connectivity, task ingestion, filtering logic, and state persistence.
"""

import unittest
import os
import tempfile
from moltask_bot import MoltaskAgentBot

class TestMoltaskAgentBot(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.bot = MoltaskAgentBot(
            wallet_address="0x71c8360f38bb8667540f1a66e40eb8e0e8f9e1f5",
            state_file=self.temp_file.name
        )

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_fetch_tasks(self):
        tasks = self.bot.fetch_open_tasks()
        self.assertIsInstance(tasks, list)
        self.assertGreater(len(tasks), 0, "Should retrieve active bounties from Moltask")

    def test_evaluate_actionable_task(self):
        coding_task = {
            "id": "mock-task-1",
            "title": "Write a Python API Bot for Moltask",
            "category": "automation",
            "description": "Code a script that polls the API"
        }
        self.assertTrue(self.bot.evaluate_task(coding_task))

    def test_state_persistence(self):
        self.bot.state["processed_tasks"]["test_id"] = {"submitted_at": 12345}
        self.bot.save_state()
        new_bot = MoltaskAgentBot(
            wallet_address="0x71c8360f38bb8667540f1a66e40eb8e0e8f9e1f5",
            state_file=self.temp_file.name
        )
        self.assertIn("test_id", new_bot.state["processed_tasks"])

if __name__ == "__main__":
    unittest.main()
