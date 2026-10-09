from io import StringIO

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase

from catalog.models import Course
from ingest.fields import render_markdown
from ingest.management.commands.export_schemas import FIELDS, TARGET, render
from ingest.schemas import SCHEMAS

from .base import CourseTestCase


def run(*args):
    out = StringIO()
    call_command(*args, stdout=out, stderr=out)
    return out.getvalue()


class SyncCommandTests(CourseTestCase):
    def test_sync_all_then_report_unchanged(self):
        self.assertIn("example: synced", run("sync_content"))
        self.assertIn("example: unchanged", run("sync_content"))

    def test_check_writes_nothing(self):
        self.assertIn("valid (check only", run("sync_content", "example", "--check"))
        self.assertFalse(Course.objects.exists())

    def test_errors_make_the_command_fail(self):
        self.edit("content/decks/least-squares.yaml", "topic: lsq", "topic: nope")
        out = StringIO()
        with self.assertRaises(CommandError):
            call_command("sync_content", stdout=out)
        text = out.getvalue()
        self.assertIn("FAILED - database not updated", text)
        self.assertRegex(text, r"content/decks/least-squares\.yaml:\d+\s+topic")

    def test_unknown_course(self):
        out = StringIO()
        with self.assertRaises(CommandError):
            call_command("sync_content", "nosuch", stdout=out)
        self.assertIn("startcourse nosuch", out.getvalue())

    def test_removed_folder_is_removed_from_the_database(self):
        run("sync_content")
        (self.course / "course.yaml").unlink()
        self.assertIn("removed from the database", run("sync_content"))
        self.assertFalse(Course.objects.exists())


class StartCourseTests(CourseTestCase):
    def test_new_course_is_valid_and_empty(self):
        run("startcourse", "rl", "--title", "Reinforcement Learning: an intro", "--year", "2026-27")
        folder = settings.COURSES_DIR / "rl"
        for name in (
            "source/lectures",
            "source/homework",
            "content/decks",
            "content/memory/palaces",
        ):
            self.assertTrue((folder / name).is_dir(), name)
        self.assertIn("rl: synced", run("sync_content", "rl"))
        course = Course.objects.get(slug="rl")
        self.assertEqual(course.title, "Reinforcement Learning: an intro")
        self.assertEqual((course.code, course.year), ("RL", "2026-27"))

    def test_refuses_to_overwrite(self):
        with self.assertRaises(CommandError):
            run("startcourse", "example", "--title", "Again")

    def test_rejects_a_bad_slug(self):
        with self.assertRaises(CommandError):
            run("startcourse", "Bad Slug", "--title", "X")


class StatusCommandTests(CourseTestCase):
    def test_lists_source_files_nothing_refers_to(self):
        (self.course / "source/lectures").mkdir(parents=True)
        (self.course / "source/lectures/L1.pdf").write_bytes(b"%PDF")
        (self.course / "source/lectures/L2.pdf").write_bytes(b"%PDF")
        self.edit(
            "content/lectures/01-least-squares.md",
            "topics: [lsq]\n",
            "topics: [lsq]\nsources: [lectures/L1.pdf]\n",
        )
        run("sync_content")
        text = run("content_status", "example")
        self.assertIn("not written up yet (1)", text)
        self.assertIn("lectures/L2.pdf", text)
        self.assertNotIn("    lectures/L1.pdf", text)


class SchemaExportTests(SimpleTestCase):
    def test_committed_schemas_match_the_models(self):
        """docs/schemas/ is generated. If this fails, run: manage.py export_schemas"""
        for name, model in SCHEMAS.items():
            path = TARGET / f"{name}.schema.json"
            self.assertTrue(path.is_file(), f"{path} is missing")
            self.assertEqual(path.read_text(encoding="utf-8"), render(model), name)

    def test_committed_field_reference_matches_the_models(self):
        self.assertEqual(FIELDS.read_text(encoding="utf-8"), render_markdown())
