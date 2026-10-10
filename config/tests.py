"""The production side of config/settings.py.

Settings are read once, when Django starts, from environment variables. To see what a
server would get, each test starts a second Python process with the server's variables.
"""

import os
import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase

PRODUCTION = {
    "DJANGO_DEBUG": "0",
    "DJANGO_SECRET_KEY": "test-only-0123456789-abcdefghijklmnopqrstuvwxyz-ABCDEFGHIJ",
    "DJANGO_ALLOWED_HOSTS": "vault.test",
    "DJANGO_CSRF_TRUSTED_ORIGINS": "https://vault.test",
}


def manage(*args, **env):
    return subprocess.run(
        [sys.executable, "manage.py", *args],
        cwd=settings.BASE_DIR,
        env={**os.environ, **PRODUCTION, **env},
        capture_output=True,
        text=True,
        check=False,
    )


class ProductionSettingsTests(SimpleTestCase):
    def test_refuses_to_start_without_a_secret_key(self):
        """The key in the repository is public; a server must never fall back to it."""
        result = manage("check", DJANGO_SECRET_KEY="")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_SECRET_KEY must be set", result.stderr)

    def test_passes_the_deployment_checklist(self):
        result = manage("check", "--deploy", "--fail-level", "WARNING")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
