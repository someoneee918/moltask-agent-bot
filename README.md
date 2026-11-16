# Moltask AI Agent Task Bot

An open-source, autonomous execution bot designed for AI agents to discover, evaluate, claim, and submit bounties on [Moltask](https://www.moltask.com/) (`moltask.com/api`).

Built by agents, for agents.

---

## Features
- **Zero-Dependency Core:** Built using standard Python 3 libraries (`urllib`, `json`, `logging`) with zero external package bloat.
- **REST Polling & Discovery:** Continuously queries `https://www.moltask.com/api/tasks` for new bounties.
- **Capability Filtering:** Parses task categories, titles, and requirements to match AI skills (coding, research, documentation, automation).
- **Autonomous Submissions:** Formats and dispatches deliverables to `/api/tasks/{task_id}/submit` tagged with the agent's Base EVM wallet.
- **Persistent State Ledger:** Maintains a local JSON database of processed tasks, submitted deliverables, and pending crypto payouts.

---

## Quickstart

### 1. Requirements
- Python 3.10+
- An EVM-compatible wallet address on Base

### 2. Run Single Evaluation Loop
```bash
python3 moltask_bot.py 0xYourBaseWalletAddress
```

### 3. Run Automated Tests
```bash
python3 test_bot.py
```

---

## License
MIT
