"""Who gets in, and how. No course content is needed, so the database starts empty."""

from io import StringIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse

from progress.models import Record

User = get_user_model()

# What the settings look like once a Google OAuth client has been configured.
GOOGLE = {
    "GOOGLE_SIGN_IN": True,
    "SOCIALACCOUNT_PROVIDERS": {
        "google": {"APPS": [{"client_id": "test-id", "secret": "test-secret"}], "SCOPE": ["email"]}
    },
}


# The middleware list a server gets with DSAI_REQUIRE_LOGIN=0.
OPEN_MIDDLEWARE = [name for name in settings.MIDDLEWARE if "LoginRequired" not in name]


class LandingTests(TestCase):
    def test_a_visitor_is_sent_to_the_landing_page_and_back_afterwards(self):
        response = self.client.get("/courses/mlpr/cards/")
        self.assertRedirects(response, "/?next=/courses/mlpr/cards/", fetch_redirect_response=False)

    def test_the_landing_page_needs_no_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/landing.html")
        self.assertNotContains(response, "data-user")

    def test_without_an_oauth_client_it_says_so(self):
        response = self.client.get("/")
        self.assertContains(response, "not set up")
        self.assertNotContains(response, "Continue with Google")

    @override_settings(**GOOGLE)
    def test_with_one_it_offers_google_and_remembers_where_you_were_going(self):
        response = self.client.get("/", {"next": "/courses/mlpr/"})
        self.assertContains(response, "Continue with Google")
        self.assertContains(response, 'action="/accounts/google/login/?')
        self.assertContains(response, "next=%2Fcourses%2Fmlpr%2F")

    @override_settings(**GOOGLE)
    def test_the_sign_in_flow_itself_is_reachable_signed_out(self):
        """The middleware must not send the sign-in pages to the sign-in page."""
        self.assertEqual(self.client.get("/accounts/google/login/").status_code, 200)
        started = self.client.post("/accounts/google/login/")
        self.assertEqual(started.status_code, 302)
        self.assertTrue(started["Location"].startswith("https://accounts.google.com/"))

    @override_settings(REQUIRE_LOGIN=False, MIDDLEWARE=OPEN_MIDDLEWARE)
    def test_with_the_requirement_off_the_site_is_open(self):
        """DSAI_REQUIRE_LOGIN=0: no landing page, and progress stays in the browser."""
        self.assertTemplateUsed(self.client.get("/"), "catalog/home.html")
        self.assertEqual(self.client.get("/settings/").status_code, 200)


class DevLoginTests(TestCase):
    def test_it_does_not_exist_outside_debug(self):
        # Tests run with DEBUG off, like a server.
        self.assertEqual(self.client.post(reverse("accounts:dev_login")).status_code, 404)
        self.assertNotContains(self.client.get("/"), "Development sign-in")

    @override_settings(DEBUG=True)
    def test_in_debug_it_signs_in_a_local_user(self):
        response = self.client.post(reverse("accounts:dev_login"), {"next": "/settings/"})
        self.assertRedirects(response, "/settings/", fetch_redirect_response=False)
        self.assertEqual(self.client.get("/settings/").status_code, 200)

    @override_settings(DEBUG=True)
    def test_next_cannot_point_at_another_site(self):
        response = self.client.post(
            reverse("accounts:dev_login"), {"next": "https://evil.example/"}
        )
        self.assertRedirects(response, "/", fetch_redirect_response=False)


class AccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ada", email="ada@example.test", first_name="Ada")
        self.client.force_login(self.user)

    def test_the_page_shows_who_is_signed_in(self):
        response = self.client.get("/settings/")
        self.assertContains(response, "ada@example.test")
        self.assertContains(response, 'class="avatar')

    def test_signing_out_needs_a_post_and_leads_to_the_landing_page(self):
        self.assertEqual(self.client.get(reverse("account_logout")).status_code, 200)  # asks first
        self.assertEqual(self.client.get("/settings/").status_code, 200)  # still signed in
        self.assertRedirects(self.client.post(reverse("account_logout")), "/")
        self.assertTemplateUsed(self.client.get("/"), "catalog/landing.html")

    def test_deleting_the_account_removes_the_person_and_their_progress(self):
        Record.objects.create(
            user=self.user, course="mlpr", key="card-1", state=3, graded_at=1, version=1
        )
        self.assertEqual(self.client.get(reverse("accounts:delete")).status_code, 405)  # POST only
        self.assertRedirects(self.client.post(reverse("accounts:delete")), "/")
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
        self.assertFalse(Record.objects.exists())  # gone with the user, by on_delete=CASCADE
        self.assertTemplateUsed(self.client.get("/"), "catalog/landing.html")


class MakeAdminTests(TestCase):
    def test_grants_and_revokes_by_email(self):
        user = User.objects.create_user("ada", email="Ada@Example.test")
        out = StringIO()
        call_command("make_admin", "ada@example.test", stdout=out)
        user.refresh_from_db()
        self.assertTrue(user.is_staff and user.is_superuser)
        call_command("make_admin", "ada@example.test", "--revoke", stdout=out)
        user.refresh_from_db()
        self.assertFalse(user.is_staff or user.is_superuser)

    def test_unknown_address_is_an_error(self):
        with self.assertRaises(CommandError):
            call_command("make_admin", "nobody@example.test", stdout=StringIO())

    def test_staff_from_google_reach_the_admin_without_a_password(self):
        user = User.objects.create_user("ada", email="ada@example.test")
        self.client.force_login(user)
        self.assertEqual(self.client.get("/admin/").status_code, 302)  # not staff: admin's login
        call_command("make_admin", "ada@example.test", stdout=StringIO())
        self.assertEqual(self.client.get("/admin/").status_code, 200)
