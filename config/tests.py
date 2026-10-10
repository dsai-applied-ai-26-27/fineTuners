"""What config/ adds around the apps: the security policy, the rate limits, and the
production side of config/settings.py.

Settings are read once, when Django starts, from environment variables. To see what a
server would get, the production tests start a second Python process with the server's
variables.
"""

import os
import re
import subprocess
import sys

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.test import Client, SimpleTestCase, TestCase, override_settings

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
    """The policy fails silently: what it forbids simply does nothing in the browser. These
    tests read the templates for the two things it forbids that are easy to write by habit."""

    @staticmethod
    def templates():
        folders = [settings.BASE_DIR / "templates", *settings.BASE_DIR.glob("*/templates")]
        for folder in folders:
            for path in folder.rglob("*.html"):
                # Template comments may mention a tag; they never reach the browser.
                yield path, re.sub(r"\{#.*?#\}", "", path.read_text(encoding="utf-8"))

    def test_every_inline_script_in_a_template_carries_the_nonce(self):
        checked = 0
        for path, text in self.templates():
            for tag in re.findall(r"<script\b[^>]*>", text):
                checked += 1
                fine = " src=" in tag or "csp_nonce" in tag or "application/json" in tag
                self.assertTrue(fine, msg=f"{path.name}: {tag}")
        self.assertGreater(checked, 3)

    def test_no_template_uses_an_inline_event_handler(self):
        """onclick="..." is inline script too, and no nonce can allow it. Alpine's
        @click="..." does the same job and is permitted."""
        for path, text in self.templates():
            found = re.findall(r"""\son[a-z]+=["']""", text)
            self.assertEqual(found, [], msg=f"{path.name} has an inline handler: use @event")


class RateLimitTests(TestCase):
    """config/ratelimit.py, with one small limit so a handful of requests reaches it."""

    SYNC = "/api/progress/sync/"

    def setUp(self):
        caches["limits"].clear()
        self.addCleanup(caches["limits"].clear)
        self.ada = get_user_model().objects.create_user("ada")
        self.bob = get_user_model().objects.create_user("bob")

    def sync_as(self, user):
        client = Client()
        client.force_login(user)
        return client.post(self.SYNC, "{}", content_type="application/json")

    @override_settings(RATE_LIMITS=[("sync", "/api/progress/", 3)])
    def test_the_call_after_the_limit_is_refused_and_told_when_to_come_back(self):
        answers = [self.sync_as(self.ada).status_code for _ in range(4)]
        self.assertEqual(answers, [200, 200, 200, 429])
        refused = self.sync_as(self.ada)
        self.assertEqual(refused.json(), {"error": "too many requests"})
        self.assertTrue(1 <= int(refused["Retry-After"]) <= 60)

    @override_settings(RATE_LIMITS=[("sync", "/api/progress/", 2)])
    def test_one_account_at_its_limit_does_not_slow_another(self):
        for _ in range(3):
            self.sync_as(self.ada)
        self.assertEqual(self.sync_as(self.ada).status_code, 429)
        self.assertEqual(self.sync_as(self.bob).status_code, 200)

    @override_settings(RATE_LIMITS=[("sync", "/api/progress/", 1)])
    def test_other_pages_are_not_counted(self):
        self.client.force_login(self.ada)
        for _ in range(3):
            self.assertEqual(self.client.get("/settings/").status_code, 200)

    @override_settings(RATE_LIMITS=[("sign-in", "/accounts/", 2)])
    def test_signed_out_the_visitors_address_is_what_counts(self):
        def visit(address):
            return self.client.get("/accounts/login/", HTTP_CF_CONNECTING_IP=address).status_code

        self.assertEqual([visit("203.0.113.5") for _ in range(3)], [200, 200, 429])
        self.assertEqual(visit("203.0.113.9"), 200)  # someone else, behind the same proxy

    @override_settings(RATE_LIMITS=[("search", "/search/", 1)])
    def test_a_page_is_refused_in_plain_words(self):
        self.client.force_login(self.ada)
        self.client.get("/search/", {"q": "fisher"})
        refused = self.client.get("/search/", {"q": "fisher"})
        self.assertEqual(refused.status_code, 429)
        self.assertIn(b"Wait a minute", refused.content)

    def test_the_limits_shipped_leave_room_for_real_use(self):
        """Fast flashcard drilling saves about every three seconds."""
        limits = {name: limit for name, _, limit in settings.RATE_LIMITS}
        self.assertGreaterEqual(limits["sync"], 60)
        self.assertGreaterEqual(limits["sign-in"], 100)  # a class signing in at once


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
