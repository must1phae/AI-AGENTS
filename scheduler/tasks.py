from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from config.settings import POST_HOUR, REDIS_URL
from main import run_agent

app = Celery("ig_agent", broker=REDIS_URL, backend=REDIS_URL)
app.conf.timezone = "Europe/Paris"
app.conf.beat_schedule = {
    "post-daily": {
        "task": "scheduler.tasks.daily_post",
        "schedule": crontab(hour=POST_HOUR, minute=0),
    }
}


@app.task(name="scheduler.tasks.daily_post")
def daily_post() -> dict[str, str]:
    result = run_agent()
    return {"status": "ok", "post_id": str(result.get("post_id", ""))}
