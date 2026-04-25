from __future__ import annotations

import json
import inspect
from datetime import datetime
from pathlib import Path
from typing import Any

from config.settings import NICHE, TONE
from main import run_agent

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENTS_FILE = PROJECT_ROOT / "dashboard" / "agents.json"
STATE_FILE = PROJECT_ROOT / "scheduler" / "state.json"


def _run_agent_safe(**kwargs: Any) -> dict[str, Any]:
    signature = inspect.signature(run_agent)
    if "auto_image" in signature.parameters:
        return run_agent(**kwargs)

    fallback_kwargs = dict(kwargs)
    fallback_kwargs.pop("auto_image", None)
    return run_agent(**fallback_kwargs)


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def run_scheduled_agents(now: datetime | None = None) -> dict[str, Any]:
    current = now or datetime.now()
    current_time = current.strftime("%H:%M")
    today = current.date().isoformat()

    agents = _load_json(AGENTS_FILE, [])
    if not isinstance(agents, list):
        agents = []

    state = _load_json(STATE_FILE, {})
    if not isinstance(state, dict):
        state = {}

    triggered: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for raw_agent in agents:
        if not isinstance(raw_agent, dict):
            continue

        agent_id = str(raw_agent.get("id") or "")
        agent_name = str(raw_agent.get("name") or "Agent")
        enabled = bool(raw_agent.get("enabled", True))
        schedule_enabled = bool(raw_agent.get("schedule_enabled", False))
        schedule_time = str(raw_agent.get("schedule_time") or "09:00").strip()

        if not enabled:
            skipped.append({"id": agent_id, "name": agent_name, "reason": "disabled"})
            continue
        if not schedule_enabled:
            skipped.append({"id": agent_id, "name": agent_name, "reason": "schedule_disabled"})
            continue
        if schedule_time != current_time:
            skipped.append({"id": agent_id, "name": agent_name, "reason": "time_mismatch"})
            continue

        if not agent_id:
            skipped.append({"id": "", "name": agent_name, "reason": "missing_id"})
            continue

        agent_state = state.get(agent_id, {})
        last_run = ""
        if isinstance(agent_state, dict):
            last_run = str(agent_state.get("last_run_date") or "")

        if last_run == today:
            skipped.append({"id": agent_id, "name": agent_name, "reason": "already_ran_today"})
            continue

        try:
            result = _run_agent_safe(
                image_url=str(raw_agent.get("default_image_url") or "") or None,
                publish=True,
                manual_caption=None,
                niche=str(raw_agent.get("niche") or NICHE),
                tone=str(raw_agent.get("tone") or TONE),
                auto_image=bool(raw_agent.get("auto_image", True)),
            )
            state[agent_id] = {
                "last_run_date": today,
                "last_status": "ok",
                "last_post_id": str(result.get("post_id") or ""),
                "last_timestamp": current.isoformat(timespec="seconds"),
            }
            triggered.append(
                {
                    "id": agent_id,
                    "name": agent_name,
                    "status": "ok",
                    "post_id": str(result.get("post_id") or ""),
                }
            )
        except Exception as error:
            state[agent_id] = {
                "last_run_date": today,
                "last_status": "error",
                "last_error": str(error),
                "last_timestamp": current.isoformat(timespec="seconds"),
            }
            triggered.append(
                {
                    "id": agent_id,
                    "name": agent_name,
                    "status": "error",
                    "error": str(error),
                }
            )

    _save_json(STATE_FILE, state)
    return {
        "time": current_time,
        "date": today,
        "triggered": triggered,
        "skipped": skipped,
    }
