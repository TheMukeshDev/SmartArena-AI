import json
import time
import datetime
import logging

from flask import Blueprint, Response, stream_with_context

logger = logging.getLogger(__name__)

events_bp = Blueprint("events", __name__)

_incident_queue: list[dict] = []
_last_id = 0


def push_incident(incident: dict) -> None:
    global _last_id
    _last_id += 1
    _incident_queue.append({"id": _last_id, "incident": incident})


@events_bp.route("/incidents", methods=["GET"])
def stream_incidents():
    from flask import current_app

    testing = current_app.config.get("TESTING", False)

    def generate():
        sent_ids = set()
        while True:
            for item in list(_incident_queue):
                if item["id"] not in sent_ids:
                    sent_ids.add(item["id"])
                    data = json.dumps(
                        {
                            "id": item["id"],
                            "incident": item["incident"],
                            "timestamp": datetime.datetime.now(
                                datetime.timezone.utc
                            ).isoformat(),
                        }
                    )
                    yield f"event: incident\ndata: {data}\n\n"
            if testing:
                break
            time.sleep(1)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
