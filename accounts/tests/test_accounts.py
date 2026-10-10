"""Who gets in, and how. No course content is needed, so the database starts empty."""

import re
from io import StringIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Enrollment
from catalog.models import Course
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

    def test_the_landing_page_says_what_the_site_is_for_and_nothing_about_its_courses(self):
        Course.objects.create(slug="rl", title="Reinforcement Learning", code="RL")
        # Not one query: nothing is looked up for a visitor who has not signed in.
        with self.assertNumQueries(0):
            response = self.client.get("/")
        self.assertContains(response, "Data&nbsp;Science and&nbsp;AI curriculum")
        self.assertNotContains(response, "Reinforcement Learning")

    def test_the_figure_on_the_landing_page_shows_the_real_review_schedule(self):
        """The chart is drawn by tools/make_figure.py from a copy of the schedule the
        flashcards follow. If the schedule changes, the figure has to be drawn again."""
        schedule = (settings.BASE_DIR / "static/js/store/progress.js").read_text(encoding="utf-8")
        days = re.search(r"const INTERVALS = \[([0-9, ]+)\];", schedule).group(1).split(", ")
        response = self.client.get("/")
        for wait in days:
            self.assertContains(response, f"<b>{wait}")
        self.assertContains(response, " and then ".join([", ".join(days[:-1]), days[-1]]))

    def test_pages_carry_a_content_security_policy(self):
        response = self.client.get("/")
        policy = response.headers["Content-Security-Policy"]
        self.assertIn("default-src 'self'", policy)
        self.assertIn("frame-ancestors 'none'", policy)
        # The one inline script of the page carries the number the header announces.
        nonce = re.search(r"'nonce-([^']+)'", policy).group(1)
        self.assertContains(response, f'<script nonce="{nonce}">')
        # Signing in posts a form that Google's redirect follows; see SECURE_CSP.
        self.assertNotIn("form-action", policy)

    def test_the_privacy_page_is_public_and_linked(self):
        """Google wants a privacy link before the sign-in may be offered to everyone."""
        response = self.client.get("/privacy/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delete my account")
        self.assertNotContains(response, "mailto:")  # no contact address configured
        self.assertContains(self.client.get("/"), 'href="/privacy/"')
        with self.settings(CONTACT_EMAIL="owner@example.test"):
            self.assertContains(self.client.get("/privacy/"), "mailto:owner@example.test")

    def test_every_frame_carries_the_logo_and_the_tab_icon(self):
        for path in ("/", "/privacy/", "/accounts/logout/"):
            with self.subTest(path=path):
                response = self.client.get(path, follow=True)
                self.assertContains(response, 'class="brand__glyph"')
                self.assertContains(response, 'rel="icon" href="/static/brand/logo.svg"')

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


class PeopleAdminTests(TestCase):
    """The admin's pages about people (accounts/admin.py)."""

    LIST = "/admin/auth/user/"

    def setUp(self):
        self.admin = User.objects.create_user(
            "owner", email="owner@example.test", is_staff=True, is_superuser=True
        )
        self.ada = User.objects.create_user("ada", email="ada@example.test", first_name="Ada")
        self.client.force_login(self.admin)
        for key, state in (("card-1", 3), ("card-2", 3), ("card-3", 1)):
            Record.objects.create(
                user=self.ada, course="mlpr", key=key, state=state, graded_at=1_760_000_000_000,
                version=1,
            )  # fmt: skip

    def page_of(self, user):
        return f"{self.LIST}{user.pk}/change/"

    def test_the_site_links_to_the_admin_for_staff_only(self):
        self.assertContains(self.client.get("/settings/"), 'href="/admin/"')
        self.client.force_login(self.ada)
        self.assertNotContains(self.client.get("/settings/"), 'href="/admin/')

    def test_the_list_counts_what_each_person_graded(self):
        response = self.client.get(self.LIST)
        self.assertContains(response, "ada@example.test")
        graded = {user.email: user.n_graded for user in response.context["cl"].result_list}
        self.assertEqual(graded, {"ada@example.test": 3, "owner@example.test": None})

    def test_the_page_of_a_person_sums_their_progress_by_course(self):
        response = self.client.get(self.page_of(self.ada))
        self.assertContains(response, "<td>mlpr</td><td>2</td><td>0</td><td>1</td>", html=False)
        self.assertNotContains(response, 'name="password')  # nobody has one to manage

    def test_the_page_of_a_person_names_the_courses_they_chose(self):
        self.assertContains(self.client.get(self.page_of(self.ada)), "No course chosen yet.")
        Enrollment.objects.replace(self.ada, {"rl", "mlpr"})
        self.assertContains(self.client.get(self.page_of(self.ada)), "mlpr, rl")

    def test_a_course_name_sent_by_a_browser_is_escaped(self):
        Record.objects.create(
            user=self.ada, course="<b>x</b>", key="k", state=3, graded_at=1, version=1
        )
        response = self.client.get(self.page_of(self.ada))
        self.assertContains(response, "&lt;b&gt;x&lt;/b&gt;")
        self.assertNotContains(response, "<td><b>x</b></td>")

    def test_a_person_can_be_renamed_and_locked_out(self):
        response = self.client.post(
            self.page_of(self.ada),
            {"email": "ada@example.test", "first_name": "Ada", "last_name": "Lovelace"},
        )  # is_active left out of the form: unticked
        self.assertRedirects(response, self.LIST)
        self.ada.refresh_from_db()
        self.assertEqual(self.ada.last_name, "Lovelace")
        self.assertFalse(self.ada.is_active)

    def test_people_are_not_added_by_hand(self):
        self.assertEqual(self.client.get(f"{self.LIST}add/").status_code, 403)

    def test_an_administrator_cannot_remove_or_demote_themselves_here(self):
        self.assertEqual(self.client.post(f"{self.LIST}{self.admin.pk}/delete/").status_code, 403)
        self.client.post(self.page_of(self.admin), {"email": "owner@example.test"})
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_staff and self.admin.is_superuser and self.admin.is_active)

    def test_deleting_a_person_takes_their_progress_along(self):
        response = self.client.post(f"{self.LIST}{self.ada.pk}/delete/", {"post": "yes"})
        self.assertRedirects(response, self.LIST)
        self.assertFalse(User.objects.filter(pk=self.ada.pk).exists())
        self.assertFalse(Record.objects.exists())

    def test_clearing_progress_asks_first_and_reaches_the_persons_devices(self):
        chosen = {"action": "forget_progress", "_selected_action": [self.ada.pk]}
        asked = self.client.post(self.LIST, chosen)
        self.assertContains(asked, "cannot be undone")
        self.assertEqual(Record.objects.count(), 3)  # nothing happened yet

        self.assertRedirects(self.client.post(self.LIST, {**chosen, "confirmed": "yes"}), self.LIST)
        self.assertFalse(Record.objects.exists())
        # What the person's browser is told at its next sync: forget everything before now.
        self.client.force_login(self.ada)
        answer = self.client.post(
            reverse("progress:sync"), {"cursor": 0}, content_type="application/json"
        ).json()
        self.assertIn("*", answer["clears"])

    def test_other_people_cannot_open_any_of_it(self):
        self.client.force_login(self.ada)
        for path in (self.LIST, self.page_of(self.admin)):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 302)
        self.client.post(
            self.LIST, {"action": "forget_progress", "_selected_action": [self.ada.pk]}
        )
        self.assertEqual(Record.objects.count(), 3)
