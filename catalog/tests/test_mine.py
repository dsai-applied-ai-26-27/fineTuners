"""Choosing courses: what a person put on their dashboard (accounts.Enrollment), the page
where they choose (catalog.views.mine) and everything that follows the choice."""

import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

from accounts.models import Enrollment
from catalog.models import Course
from ingest.sync import sync_course
from ingest.tests.base import CourseTestCase
from progress.models import Record

C = "example"
CHOOSE = "/my-courses/"
# The middleware list a server gets with DSAI_REQUIRE_LOGIN=0.
OPEN_MIDDLEWARE = [name for name in settings.MIDDLEWARE if "LoginRequired" not in name]


class ChoosingTests(CourseTestCase):
    """One course with content (the example) and two empty ones to choose among."""

    def setUp(self):
        super().setUp()
        report = self.sync()
        self.assertEqual(report.status, "synced", msg=report.format())
        Course.objects.create(slug="rl", series="rl", title="Reinforcement Learning", code="RL")
        Course.objects.create(slug="aai", series="aai", title="Applied AI", code="AAI")
        self.user = get_user_model().objects.create_user("ada", email="ada@example.test")
        self.client.force_login(self.user)

    def chosen(self):
        return Enrollment.objects.series_of(self.user)

    # -- the first sign-in ------------------------------------------------------------------

    def test_someone_who_has_not_chosen_is_asked_before_the_dashboard(self):
        self.assertRedirects(self.client.get("/"), CHOOSE)
        page = self.client.get(CHOOSE)
        self.assertContains(page, "Choose your courses")
        self.assertContains(page, "Open my dashboard")
        self.assertNotContains(page, ">Cancel<")  # nothing to go back to yet
        offered = [c.series for group in page.context["groups"] for c in group["courses"]]
        self.assertCountEqual(offered, [C, "rl", "aai"])
        self.assertEqual(page.context["ticked"], set())

    def test_courses_already_studied_come_ticked(self):
        """For people who used the site before courses could be chosen."""
        Record.objects.create(
            user=self.user, course=C, key="lsq-derive", state=3, graded_at=1, version=1
        )
        page = self.client.get(CHOOSE)
        self.assertEqual(page.context["ticked"], {C})
        self.assertContains(page, f'value="{C}" checked')
        self.assertEqual(self.chosen(), set())  # ticked on the page, not stored until saved

    def test_saving_stores_the_choice_and_opens_the_dashboard(self):
        response = self.client.post(CHOOSE, {"series": [C, "rl"]})
        self.assertRedirects(response, "/")
        self.assertEqual(self.chosen(), {C, "rl"})
        dashboard = self.client.get("/")
        shown = [c.slug for group in dashboard.context["groups"] for c in group["courses"]]
        self.assertCountEqual(shown, [C, "rl"])
        self.assertEqual([m["slug"] for m in dashboard.context["manifests"]], [C, "rl"][::-1])
        self.assertEqual(dashboard.context["others"], 1)
        self.assertContains(dashboard, "1 other course is not on your dashboard")

    def test_saving_nothing_is_refused(self):
        Enrollment.objects.replace(self.user, {C})
        page = self.client.post(CHOOSE, {})
        self.assertContains(page, "Tick at least one course")
        self.assertEqual(self.chosen(), {C})  # unchanged

    def test_a_made_up_course_is_ignored(self):
        self.client.post(CHOOSE, {"series": [C, "no-such-course"]})
        self.assertEqual(self.chosen(), {C})

    # -- afterwards -------------------------------------------------------------------------

    def test_the_same_page_changes_the_choice_later(self):
        Enrollment.objects.replace(self.user, {C, "rl"})
        page = self.client.get(CHOOSE)
        self.assertContains(page, "<h1>Your courses</h1>")
        self.assertContains(page, ">Cancel<")
        self.assertEqual(page.context["ticked"], {C, "rl"})
        self.client.post(CHOOSE, {"series": ["aai"]})
        self.assertEqual(self.chosen(), {"aai"})

    def test_the_menu_lists_only_chosen_courses(self):
        Course.objects.filter(slug=C).update(status="active")
        Enrollment.objects.replace(self.user, {"rl"})
        self.assertEqual(list(self.client.get("/search/").context["nav_courses"]), [])
        Enrollment.objects.replace(self.user, {C, "rl"})
        nav = self.client.get("/search/").context["nav_courses"]
        self.assertEqual([c.slug for c in nav], [C])  # rl is chosen but still empty

    def test_a_course_page_says_whether_it_is_chosen_and_changes_it(self):
        Enrollment.objects.replace(self.user, {"rl"})
        url, change = reverse("catalog:course", args=[C]), reverse("catalog:enroll")
        page = self.client.get(url)
        self.assertEqual(page.status_code, 200)  # not chosen, and still open to read
        self.assertContains(page, "Add to my courses")

        added = self.client.post(change, {"series": C, "action": "add", "next": url})
        self.assertRedirects(added, url)
        self.assertEqual(self.chosen(), {C, "rl"})
        self.client.post(change, {"series": C, "action": "add", "next": url})  # twice is once
        self.assertEqual(Enrollment.objects.filter(user=self.user, series=C).count(), 1)
        self.assertContains(self.client.get(url), "On your dashboard")

        self.client.post(change, {"series": C, "action": "remove", "next": url})
        self.assertEqual(self.chosen(), {"rl"})

    def test_the_change_address_takes_posts_only_and_never_leaves_the_site(self):
        change = reverse("catalog:enroll")
        self.assertEqual(self.client.get(change).status_code, 405)
        elsewhere = self.client.post(
            change, {"series": C, "action": "add", "next": "https://evil.example/"}
        )
        self.assertRedirects(elsewhere, "/", fetch_redirect_response=False)
        self.client.post(change, {"series": "no-such-course", "action": "add"})
        self.assertEqual(self.chosen(), {C})

    def test_taking_the_last_course_off_leads_back_to_choosing(self):
        Enrollment.objects.replace(self.user, {C})
        self.client.post(reverse("catalog:enroll"), {"series": C, "action": "remove"})
        self.assertRedirects(self.client.get("/"), CHOOSE)

    def test_the_choice_is_of_a_course_not_of_one_year_of_it(self):
        """Next year's edition takes the course's place without choosing again."""
        Enrollment.objects.replace(self.user, {C})
        next_year = self.course.parent / "example-next"
        shutil.copytree(self.course, next_year)
        path = next_year / "course.yaml"
        text = path.read_text(encoding="utf-8")
        text = text.replace('year: "2026-27"', 'year: "2027-28"\nseries: example')
        path.write_text(text, encoding="utf-8", newline="\n")
        self.assertEqual(sync_course(next_year).status, "synced")
        dashboard = self.client.get("/")
        shown = [c.slug for group in dashboard.context["groups"] for c in group["courses"]]
        self.assertEqual(shown, ["example-next"])

    def test_a_chosen_course_that_is_gone_is_kept_and_does_not_break_the_dashboard(self):
        Enrollment.objects.replace(self.user, {"old-course", C})
        self.assertEqual(self.client.get("/").status_code, 200)
        # Saving the page again does not silently drop what it could not show.
        self.client.post(CHOOSE, {"series": [C]})
        self.assertEqual(self.chosen(), {"old-course", C})
        Enrollment.objects.replace(self.user, {"old-course"})
        gone = self.client.get("/")
        self.assertContains(gone, "None of the courses you chose is here at the moment")

    # -- people and the open site -----------------------------------------------------------

    def test_people_choose_for_themselves_only(self):
        Enrollment.objects.replace(self.user, {C})
        other = get_user_model().objects.create_user("bob")
        self.client.force_login(other)
        self.assertRedirects(self.client.get("/"), CHOOSE)
        self.client.post(CHOOSE, {"series": ["rl"]})
        self.assertEqual(Enrollment.objects.series_of(other), {"rl"})
        self.assertEqual(self.chosen(), {C})

    def test_deleting_the_account_removes_the_choice(self):
        Enrollment.objects.replace(self.user, {C, "rl"})
        self.client.post(reverse("accounts:delete"))
        self.assertFalse(Enrollment.objects.exists())

    def test_with_no_courses_at_all_there_is_nothing_to_ask(self):
        Course.objects.all().delete()
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertContains(self.client.get(CHOOSE), "No courses yet")

    def test_on_the_open_site_nobody_is_asked_and_everything_is_shown(self):
        self.client.logout()
        with override_settings(REQUIRE_LOGIN=False, MIDDLEWARE=OPEN_MIDDLEWARE):
            dashboard = self.client.get("/")
            self.assertEqual(dashboard.status_code, 200)
            shown = [c.slug for group in dashboard.context["groups"] for c in group["courses"]]
            self.assertCountEqual(shown, [C, "rl", "aai"])
            self.assertNotContains(dashboard, 'href="/my-courses/"')
            self.assertNotContains(dashboard, "Choose courses")
            self.assertRedirects(self.client.get(CHOOSE), "/")
            self.assertNotContains(self.client.get(f"/courses/{C}/"), "Add to my courses")
