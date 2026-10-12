"""E-mail to educators, and to the site's own address.

    mail.send([user, ...], "Subject", "Plain text.")
    mail.send_owner("New request: content (Reinforcement Learning)", "Open the admin.", url)

The site writes to people in one situation so far: about the role they asked for. An
application was accepted, a hand-in was taken off the site, the kit has a new version.
The address is the one their Google account signed in with.

Like the owner's notifications (desk/notify.py), a message never holds up or breaks what
caused it: it is sent from a separate thread and a failure ends in a log line. Without a
mail server configured (DSAI_EMAIL_HOST) nothing is sent; locally the messages are printed
to the terminal instead (settings.MAILERS).
"""

import logging
import threading

from django.conf import settings
from django.core.mail import EmailMessage, mailers

logger = logging.getLogger(__name__)

SIGNATURE = "\n\nDSAI Vault\n{site}\nYou get this message because you are an educator there."
OWNER_SIGNATURE = "\n\nDSAI Vault\n{site}\nSent to the site's own address: something arrived."


def configured():
    backend = settings.MAILERS["default"]["BACKEND"]
    return backend != "django.core.mail.backends.dummy.EmailBackend"


def send(users, subject, body):
    """Queue one message per person. Returns how many were queued."""
    text = body.rstrip() + SIGNATURE.format(site=settings.SITE_URL)
    messages = [
        # One message each, never one message to all: nobody sees another's address.
        EmailMessage(subject=subject, body=text, to=[user.email])
        for user in users
        if user.email and user.is_active
    ]
    if not messages or not configured():
        return 0
    _dispatch(messages)
    return len(messages)


def send_owner(subject, body, url=""):
    """One message to the site's contact address (settings.CONTACT_EMAIL): what the
    owner's bot is told (desk/notify.py), by e-mail as well. Returns how many were queued.

    The bot's rule holds here too: that something arrived and where to read it, never who
    sent it or what they wrote. The link leads to the admin, which asks who is there.
    """
    if not settings.CONTACT_EMAIL or not configured():
        return 0
    text = body.rstrip() + (f"\n\n{url}" if url else "")
    text += OWNER_SIGNATURE.format(site=settings.SITE_URL)
    _dispatch([EmailMessage(subject=subject, body=text, to=[settings.CONTACT_EMAIL])])
    return 1


def _dispatch(messages):
    threading.Thread(target=deliver, args=(messages,), daemon=True).start()


def deliver(messages):
    try:
        # One connection for all of them. `mailers.default` is the mail server named in
        # settings.MAILERS, as `connection` is the database named in DATABASES.
        return mailers.default.send_messages(messages) or 0
    except Exception as error:  # noqa: BLE001 (a mail server's failure must stay in here)
        # The kind of failure only. A mail server's own message often quotes the address
        # it turned away, and the log is no place for people's addresses.
        logger.warning(
            "Mail: %s message(s) could not be sent (%s)", len(messages), type(error).__name__
        )
        return 0
