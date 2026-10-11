import logging
import sys
from pathlib import Path

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

        if settings.DEBUG or settings.TESTING or configured():
            return
        # Every management command loads the apps as well. The warning is for the process
        # that serves the site, not for each `migrate` and `sync_content`.
        if Path(sys.argv[0]).name == "manage.py":
            return
        logger.warning(
            "BMO_NOTIFY_URL or BMO_NOTIFY_TOKEN is not set (or the address is not https): "
            "requests are stored, but nobody is notified."
        )
