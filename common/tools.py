import uuid
import time


def get_uuid() -> str:
    return uuid.uuid4().hex


def get_now_timestamp() -> int:
    return int(time.time())
