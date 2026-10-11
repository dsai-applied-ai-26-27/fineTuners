import logging

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class DeskConfig(AppConfig):
    name = "desk"
    verbose_name = "Requests and educators"

    def ready(self):
        # ready() runs once when Django has loaded every app: the place for a start-up
        # check. On a server without the bot's settings, say so once; requests are still
        # stored and shown in the admin.
        from .notify import configured

        if not settings.DEBUG and not settings.TESTING and not configured():
            logger.warning(
                "BMO_NOTIFY_URL or BMO_NOTIFY_TOKEN is not set: requests are stored, "
                "but nobody is notified."
            )
