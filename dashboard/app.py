from __future__ import annotations

import json
import sys
import inspect
from pathlib import Path
from datetime import time
from uuid import uuid4

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import DEFAULT_IMAGE_URL, NICHE, TONE
from main import run_agent
from scheduler.agent_scheduler import run_scheduled_agents

AGENTS_FILE = Path(__file__).with_name("agents.json")
TONE_OPTIONS = ["viral", "educatif", "storytelling"]


def _run_agent_safe(**kwargs: object) -> dict[str, object]:
    signature = inspect.signature(run_agent)
    if "auto_image" in signature.parameters:
        return run_agent(**kwargs)

    fallback_kwargs = dict(kwargs)
    fallback_kwargs.pop("auto_image", None)
    return run_agent(**fallback_kwargs)


def _default_agent() -> dict[str, str | bool]:
    return {
        "id": str(uuid4()),
        "name": "Agent Principal",
        "niche": NICHE,
        "tone": TONE if TONE in TONE_OPTIONS else "viral",
        "default_image_url": DEFAULT_IMAGE_URL,
        "auto_image": True,
        "enabled": True,
        "schedule_enabled": False,
        "schedule_time": "09:00",
    }


def _load_agents() -> list[dict[str, str | bool]]:
    if not AGENTS_FILE.exists():
        agents = [_default_agent()]
        _save_agents(agents)
        return agents

    try:
        payload = json.loads(AGENTS_FILE.read_text(encoding="utf-8"))
    except Exception:
        payload = []

    if not isinstance(payload, list):
        payload = []

    normalized: list[dict[str, str | bool]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "id": str(item.get("id") or uuid4()),
                "name": str(item.get("name") or "Agent"),
                "niche": str(item.get("niche") or NICHE),
                "tone": str(item.get("tone") or "viral"),
                "default_image_url": str(item.get("default_image_url") or ""),
                "auto_image": bool(item.get("auto_image", True)),
                "enabled": bool(item.get("enabled", True)),
                "schedule_enabled": bool(item.get("schedule_enabled", False)),
                "schedule_time": str(item.get("schedule_time") or "09:00"),
            }
        )

    if not normalized:
        normalized = [_default_agent()]

    _save_agents(normalized)
    return normalized


def _save_agents(agents: list[dict[str, str | bool]]) -> None:
    AGENTS_FILE.write_text(json.dumps(agents, indent=2, ensure_ascii=False), encoding="utf-8")


def _create_agent(agents: list[dict[str, str | bool]]) -> None:
    with st.sidebar.form("create_agent_form"):
        st.subheader("Créer un agent")
        name = st.text_input("Nom", value="Nouvel agent")
        niche = st.text_input("Niche", value=NICHE)
        tone = st.selectbox("Ton", options=TONE_OPTIONS, index=0)
        image_url = st.text_input("Image URL par défaut", value=DEFAULT_IMAGE_URL)
        enabled = st.checkbox("Actif", value=True)
        submitted = st.form_submit_button("Ajouter")

    if submitted:
        agents.append(
            {
                "id": str(uuid4()),
                "name": name.strip() or "Agent",
                "niche": niche.strip() or NICHE,
                "tone": tone,
                "default_image_url": image_url.strip(),
                "auto_image": True,
                "enabled": enabled,
                "schedule_enabled": False,
                "schedule_time": "09:00",
            }
        )
        _save_agents(agents)
        st.sidebar.success("Agent ajouté.")
        st.rerun()


def _render_agent_card(index: int, agent: dict[str, str | bool], agents: list[dict[str, str | bool]]) -> None:
    agent_id = str(agent["id"])
    st.markdown(f"### {agent['name']}")

    enabled = st.toggle("Actif", value=bool(agent.get("enabled", True)), key=f"enabled_{agent_id}")
    if enabled != bool(agent.get("enabled", True)):
        agent["enabled"] = enabled
        _save_agents(agents)
        st.success("Statut mis à jour.")

    name = st.text_input("Nom", value=str(agent.get("name", "Agent")), key=f"name_{agent_id}")
    niche = st.text_input("Niche", value=str(agent.get("niche", NICHE)), key=f"niche_{agent_id}")
    tone = st.selectbox(
        "Ton",
        options=TONE_OPTIONS,
        index=TONE_OPTIONS.index(str(agent.get("tone", "viral")))
        if str(agent.get("tone", "viral")) in TONE_OPTIONS
        else 0,
        key=f"tone_{agent_id}",
    )
    image_url = st.text_input(
        "Image URL",
        value=str(agent.get("default_image_url", "")),
        key=f"image_{agent_id}",
    )
    auto_image = st.checkbox(
        "Generer image IA si URL vide",
        value=bool(agent.get("auto_image", True)),
        key=f"auto_image_{agent_id}",
    )

    schedule_enabled = st.checkbox(
        "Scheduler actif",
        value=bool(agent.get("schedule_enabled", False)),
        key=f"schedule_enabled_{agent_id}",
    )
    raw_schedule_time = str(agent.get("schedule_time", "09:00"))
    hour, minute = 9, 0
    try:
        hour_str, minute_str = raw_schedule_time.split(":", 1)
        hour, minute = int(hour_str), int(minute_str)
    except Exception:
        hour, minute = 9, 0
    schedule_time_value = st.time_input(
        "Heure planifiée",
        value=time(hour=hour, minute=minute),
        key=f"schedule_time_{agent_id}",
        step=60,
    )

    col_save, col_dry, col_pub, col_del = st.columns(4)
    save_clicked = col_save.button("Sauvegarder", key=f"save_{agent_id}")
    dry_run_clicked = col_dry.button("Dry run", key=f"dry_{agent_id}")
    publish_clicked = col_pub.button("Publier", key=f"publish_{agent_id}")
    delete_clicked = col_del.button("Supprimer", key=f"delete_{agent_id}")

    if save_clicked:
        agent["name"] = name.strip() or "Agent"
        agent["niche"] = niche.strip() or NICHE
        agent["tone"] = tone
        agent["default_image_url"] = image_url.strip()
        agent["auto_image"] = auto_image
        agent["schedule_enabled"] = schedule_enabled
        agent["schedule_time"] = schedule_time_value.strftime("%H:%M")
        _save_agents(agents)
        st.success("Agent sauvegardé.")

    if dry_run_clicked:
        if not enabled:
            st.warning("Cet agent est désactivé. Active-le pour l'exécuter.")
            return
        with st.spinner("Exécution dry-run..."):
            try:
                result = _run_agent_safe(
                    image_url=image_url.strip() or None,
                    publish=False,
                    manual_caption=None,
                    niche=niche.strip() or NICHE,
                    tone=tone,
                    auto_image=auto_image,
                )
                if not isinstance(result, dict):
                    result = {"result": result}
                st.success("Dry-run terminé.")
                st.json(result)
            except Exception as error:
                st.error(str(error))

    if publish_clicked:
        if not enabled:
            st.warning("Cet agent est désactivé. Active-le pour le publier.")
            return
        if not image_url.strip() and not auto_image:
            st.error("Image URL est obligatoire pour publier si la generation IA est desactivee.")
            return
        with st.spinner("Publication en cours..."):
            try:
                result = _run_agent_safe(
                    image_url=image_url.strip(),
                    publish=True,
                    manual_caption=None,
                    niche=niche.strip() or NICHE,
                    tone=tone,
                    auto_image=auto_image,
                )
                if not isinstance(result, dict):
                    result = {"result": result}
                st.success("Publication réussie.")
                st.json(result)
            except Exception as error:
                st.error(str(error))

    if delete_clicked:
        agents.pop(index)
        if not agents:
            agents.append(_default_agent())
        _save_agents(agents)
        st.warning("Agent supprimé.")
        st.rerun()

    st.divider()


def main() -> None:
    st.set_page_config(page_title="AI Agents Dashboard", page_icon="🤖", layout="wide")
    st.title("AI Agents Dashboard")
    st.caption("Créer, activer/désactiver et exécuter plusieurs agents depuis une seule interface.")

    agents = _load_agents()
    _create_agent(agents)

    st.subheader("Scheduler par agent")
    st.markdown(
        "Chaque agent peut avoir sa propre heure. Active `Scheduler actif` puis clique `Sauvegarder` sur la carte de l'agent."
    )
    if st.button("Exécuter le scheduler maintenant", type="secondary"):
        with st.spinner("Exécution scheduler..."):
            summary = run_scheduled_agents()
        st.json(summary)

    st.code("python main.py --run-scheduled")

    st.info("Utilise Dry run pour tester sans publier. Publier enverra le post sur la cible configurée dans .env.")
    for index, agent in enumerate(agents):
        _render_agent_card(index, agent, agents)


if __name__ == "__main__":
    main()
