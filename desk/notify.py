"""Tell the owner that something arrived, through their assistant bot (BMO).

    notify("New content request: Reinforcement Learning", url=..., dedupe_key="dsai-request-12")

The bot is a small web service of the owner's that forwards a message to their phone. Its
address and its token come from the environment (BMO_NOTIFY_URL, BMO_NOTIFY_TOKEN); with
either missing, nothing is sent and nothing fails. The address must be https: the token
travels in a header, and is never sent where it could be read on the way.

Rules this module keeps:

- It never holds up or breaks what the person was doing. The message is sent from a
  separate thread, and every failure ends in a log line.
- It says that something arrived and where to read it, never who sent it or what they
  wrote. That keeps the privacy page true and the bot's log free of personal data.
- One try, then at most two more, and only for failures that may pass: a network error or
  a 5xx answer. A 400, 403 or 429 is final.
- A burst rings once. The first message makes a sound; those that follow within two
  minutes arrive silently. And there is a ceiling per hour, below the bot's own, so a
  burst cannot use up its allowance. Whatever is not sent is still in the admin.
"""

import json
import logging
import threading
import time
import urllib.error
import urllib.request

from django.conf import settings
from django.core.cache import caches

logger = logging.getLogger(__name__)

SOURCE = "DSAI Vault"
TIMEOUT = 5  # seconds
RETRY_AFTER = (2, 6)  # seconds to wait before the second and the third try
PER_HOUR = 20  # the bot accepts 30
QUIET_FOR = 120  # seconds after a message during which the next ones make no sound


def configured():
    return bool(settings.BMO_NOTIFY_TOKEN) and settings.BMO_NOTIFY_URL.startswith("https://")


def notify(title, message="", *, level="info", url="", dedupe_key="", silent=False):
    """Queue one notification. Returns at once; safe to call from a view."""
    if not configured():
        return False
    if _over_the_hourly_ceiling():
        logger.warning("BMO: hourly ceiling reached, notification skipped")
        return False
    # cache.add stores the key only if it is not there yet, and says whether it did: one
    # step that both asks "did something ring just now?" and starts the quiet period.
    if not caches["limits"].add("bmo:rang", 1, timeout=QUIET_FOR):
        silent = True
    payload = {"title": title[:120], "level": level, "source": SOURCE}
    if message:
        payload["message"] = message[:2000]
    if url:
        payload["url"] = url
    if dedupe_key:
        payload["dedupe_key"] = dedupe_key[:100]
    if silent:
        payload["silent"] = True
    _dispatch(payload)
    return True


def _over_the_hourly_ceiling():
    cache = caches["limits"]
    key = f"bmo:{int(time.time() // 3600)}"
    cache.add(key, 0, timeout=7200)
    try:
        return cache.incr(key) > PER_HOUR
    except ValueError:
        cache.set(key, 1, timeout=7200)
        return False


def _dispatch(payload):
    # A daemon thread: the request that caused this is answered without waiting for it,
    # and a restart of the server does not wait for a slow bot either.
    threading.Thread(target=deliver, args=(payload,), daemon=True).start()


def deliver(payload, sleep=time.sleep):
    """Post `payload` to the bot. True if it was accepted."""
    body = json.dumps(payload).encode()
    for attempt in range(1 + len(RETRY_AFTER)):
        if attempt:
            sleep(RETRY_AFTER[attempt - 1])
        status = _post(body)
        if status == 200:
            return True
        if status in (400, 403, 429):
            logger.warning("BMO refused a notification (%s); not retried", status)
            return False
        # None (no answer) or a 5xx: worth another try, with the same dedupe_key.
    logger.warning("BMO did not take a notification after %s tries", 1 + len(RETRY_AFTER))
    return False


def _post(body):
    """One HTTP POST. Returns the status code, or None if there was no answer."""
    request = urllib.request.Request(  # noqa: S310 (the address is the owner's own setting)
        settings.BMO_NOTIFY_URL,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "X-BMO-Token": settings.BMO_NOTIFY_TOKEN},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
            return response.status
    except urllib.error.HTTPError as error:
        return error.code
    except (urllib.error.URLError, TimeoutError, OSError):
        return None
