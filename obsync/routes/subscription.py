from fastapi import APIRouter

from obsync.utils import milisec

subscript_router = APIRouter(prefix="/subscription")


@subscript_router.post("/list")
def list_subscriptions():
    return {
        "business": None,
        "publish": None,
        "sync": {
            "earlybird": False,
            "expirt_ts": milisec(offset=365 * 24 * 60 * 60),
            "renew": "",
        },
    }
