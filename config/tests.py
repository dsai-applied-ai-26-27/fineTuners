"""The production side of config/settings.py.

Settings are read once, when Django starts, from environment variables. To see what a
server would get, each test starts a second Python process with the server's variables.
"""

import os
import re
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


class ContentSecurityPolicyTests(SimpleTestCase):
    def test_every_inline_script_in_a_template_carries_the_nonce(self):
        """The policy runs an inline script only with this request's nonce. One that is
        written without it would silently do nothing in the browser."""
        folders = [settings.BASE_DIR / "templates", *settings.BASE_DIR.glob("*/templates")]
        checked = 0
        for folder in folders:
            for path in folder.rglob("*.html"):
                # Template comments may mention the tag; they never reach the browser.
                text = re.sub(r"\{#.*?#\}", "", path.read_text(encoding="utf-8"))
                for tag in re.findall(r"<script\b[^>]*>", text):
                    checked += 1
                    fine = " src=" in tag or "csp_nonce" in tag or "application/json" in tag
                    self.assertTrue(fine, msg=f"{path.name}: {tag}")
        self.assertGreater(checked, 3)


class ProductionSettingsTests(SimpleTestCase):
    def test_refuses_to_start_without_a_secret_key(self):
        """The key in the repository is public; a server must never fall back to it."""
        result = manage("check", DJANGO_SECRET_KEY="")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_SECRET_KEY must be set", result.stderr)

    def test_passes_the_deployment_checklist(self):
        result = manage("check", "--deploy", "--fail-level", "WARNING")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_the_admin_offers_no_password_form_once_google_is_configured(self):
        """Nobody has a password, so the form would only invite guessing. With Google
        sign-in set up, the admin's own login page sends a visitor to the landing page."""
        look = (
            "from django.test import Client;"
            "r = Client().get('/admin/login/', secure=True, HTTP_HOST='vault.test');"
            "print('ANSWER', r.status_code, r.headers.get('Location'))"
        )
        with_google = manage(
            "shell", "-c", look, GOOGLE_OAUTH_CLIENT_ID="id", GOOGLE_OAUTH_CLIENT_SECRET="secret"
        )
        self.assertIn("ANSWER 302 /?next=/admin/login/", with_google.stdout, msg=with_google.stderr)
