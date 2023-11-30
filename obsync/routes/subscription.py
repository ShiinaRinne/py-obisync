from fastapi import APIRouter
import time

subscript_router = APIRouter(prefix="/subscription")


@subscript_router.post("/list")
def list_subscriptions():
    return {
        "business": None,
        "publish": None,
        "sync": {
            "earlybird": False,
            "expirt_ts": (time.time() + 3600 * 24 * 365 * 10) * 1000,
            "renew": "",
        },
    }
