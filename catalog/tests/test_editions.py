"""One course in several academic years (catalog/editions.py)."""

import shutil

from django.test import SimpleTestCase

from catalog import editions
from catalog.models import Course
from catalog.tests.test_views import sign_in
from ingest.sync import sync_course
from ingest.tests.base import CourseTestCase


class LatestTests(SimpleTestCase):
    """`latest` only reads attributes, so unsaved courses do and no database is needed."""

    @staticmethod
    def course(slug, year, series=""):
        return Course(slug=slug, title=slug, code=slug, year=year, series=series)

    def test_one_per_series_and_it_is_the_newest_year(self):
        old = self.course("mlpr", "2025-26", "mlpr")
        new = self.course("mlpr-2026", "2026-27", "mlpr")
        other = self.course("rl", "2026-27", "rl")
        self.assertEqual(editions.latest([old, other, new]), [other, new])

    def test_a_course_without_a_series_stands_for_itself(self):
        # Rows made before the field existed, or by hand, must not be merged into one.
        a, b = self.course("a", "2026-27"), self.course("b", "2026-27")
        self.assertEqual(editions.latest([a, b]), [a, b])

    def test_a_year_beats_no_year(self):
        undated = self.course("x-old", "", "x")
        dated = self.course("x", "2024-25", "x")
        self.assertEqual(editions.latest([undated, dated]), [dated])


class TwoYearsTests(CourseTestCase):
    """The example course, and a copy of it standing in for next year's edition."""

    def setUp(self):
        super().setUp()
        self.next_year = self.course.parent / "example-next"
        shutil.copytree(self.course, self.next_year)
        path = self.next_year / "course.yaml"
        text = path.read_text(encoding="utf-8")
        text = text.replace('year: "2026-27"', 'year: "2027-28"\nseries: example')
        path.write_text(text, encoding="utf-8", newline="\n")
        for folder in (self.course, self.next_year):
            report = sync_course(folder)
            self.assertEqual(report.status, "synced", msg=report.format())
        sign_in(self)

    def test_a_folder_without_series_is_its_own(self):
        self.assertEqual(Course.objects.get(slug="example").series, "example")
        self.assertEqual(Course.objects.get(slug="example-next").series, "example")

    def test_the_dashboard_shows_the_course_once_and_opens_the_latest_year(self):
        response = self.client.get("/")
        shown = [c.slug for group in response.context["groups"] for c in group["courses"]]
        self.assertEqual(shown, ["example-next"])
        self.assertEqual([m["slug"] for m in response.context["manifests"]], ["example-next"])
        self.assertContains(response, 'href="/courses/example-next/"')
        self.assertNotContains(response, 'href="/courses/example/"')

    def test_both_years_are_offered_at_the_top_of_either_one(self):
        for slug, current in (("example", "2026/27"), ("example-next", "2027/28")):
            with self.subTest(opened=slug):
                response = self.client.get(f"/courses/{slug}/")
                years = [c.year_label for c in response.context["editions"]]
                self.assertEqual(years, ["2027/28", "2026/27"])  # newest first
                self.assertContains(response, f'aria-current="true">{current}</span>')
        self.assertContains(self.client.get("/courses/example/"), 'href="/courses/example-next/"')
        self.assertContains(self.client.get("/courses/example-next/"), 'href="/courses/example/"')

    def test_the_older_year_stays_reachable_and_keeps_its_own_pages(self):
        self.assertEqual(self.client.get("/courses/example/cards/").status_code, 200)
        self.assertEqual(self.client.get("/courses/example-next/cards/").status_code, 200)

    def test_a_single_year_is_shown_as_a_label(self):
        Course.objects.get(slug="example-next").delete()
        response = self.client.get("/courses/example/")
        self.assertContains(response, 'aria-current="true">2026/27</span>')
        self.assertEqual(len(response.context["editions"]), 1)
        self.assertNotContains(response, "example-next")
