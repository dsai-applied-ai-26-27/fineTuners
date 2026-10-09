import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.test import TestCase, override_settings

from ingest.sync import sync_course


class CourseTestCase(TestCase):
    """Gives each test its own copy of the example course to break.

    The copy lives in a temporary folder, and CONTENT_ROOTS / MEDIA_ROOT are pointed there,
    so tests never touch courses/, docs/example-course/ or media/. Django's TestCase wraps
    every test in a transaction that is rolled back, so database rows do not leak either.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="dsai-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.course = self.tmp / "courses" / "example"
        shutil.copytree(settings.EXAMPLE_COURSE_ROOT / "example", self.course)
        override = override_settings(
            CONTENT_ROOTS=[self.tmp / "courses"],
            COURSES_DIR=self.tmp / "courses",
            MEDIA_ROOT=self.tmp / "media",
        )
        override.enable()
        self.addCleanup(override.disable)
        cache.clear()

    # -- editing the copy ---------------------------------------------------------------

    def read(self, rel):
        return (self.course / rel).read_text(encoding="utf-8")

    def write(self, rel, text):
        path = self.course / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def edit(self, rel, old, new):
        text = self.read(rel)
        self.assertIn(old, text, msg=f"{rel} does not contain {old!r}")
        self.write(rel, text.replace(old, new, 1))

    def append(self, rel, text):
        self.write(rel, self.read(rel) + text)

    def line_of(self, rel, needle):
        for number, line in enumerate(self.read(rel).split("\n"), start=1):
            if needle in line:
                return number
        self.fail(f"{rel} has no line containing {needle!r}")

    # -- running the pipeline -----------------------------------------------------------

    def check(self):
        return sync_course(self.course, check_only=True)

    def sync(self, **options):
        return sync_course(self.course, **options)

    def assertProblem(self, report, fragment, *, file=None, line=None, level="error"):
        """Assert the report has an issue whose message contains `fragment`."""
        matches = [
            issue
            for issue in report.issues
            if fragment in issue.message
            and issue.level == level
            and (file is None or issue.file == file)
        ]
        self.assertTrue(matches, msg=f"no {level} containing {fragment!r} in:\n{report.format()}")
        if line is not None:
            self.assertEqual(matches[0].line, line, msg=report.format())
        return matches[0]
