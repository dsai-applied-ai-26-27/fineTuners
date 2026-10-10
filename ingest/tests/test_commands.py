import io
import os
import tarfile
from io import StringIO
from unittest import mock

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase

from catalog.models import Course
from ingest.fields import render_markdown
from ingest.management.commands.export_schemas import FIELDS, TARGET, render
from ingest.management.commands.publish import REMOTE_COMMAND, send
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

    def test_semester_is_written_and_read_back(self):
        run("startcourse", "dms", "--title", "Dynamic Modeling", "--semester", "5")
        run("sync_content", "dms")
        self.assertEqual(Course.objects.get(slug="dms").semester, 5)
        # Left out, the field stays empty rather than becoming 0.
        run("startcourse", "aai", "--title", "Applied AI")
        run("sync_content", "aai")
        self.assertIsNone(Course.objects.get(slug="aai").semester)

    def test_another_year_of_a_course_names_its_series(self):
        run("startcourse", "example-2027", "--title", "Example", "--year", "2027-28",
            "--series", "example")  # fmt: skip
        run("sync_content", "example-2027")
        self.assertEqual(Course.objects.get(slug="example-2027").series, "example")
        with self.assertRaises(CommandError):
            run("startcourse", "x", "--title", "X", "--series", "Not A Folder")

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


class PublishCommandTests(CourseTestCase):
    """`publish` validates, packs and hands the archive to `send`, which runs ssh. Here
    `send` is replaced by a stand-in, so the tests see exactly what would have gone out
    without contacting anything."""

    SEND = "ingest.management.commands.publish.send"

    def names(self, archive):
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            return tar.getnames()

    def test_sends_course_files_but_never_source_material(self):
        (self.course / "source/lectures").mkdir(parents=True)
        (self.course / "source/lectures/L1.pdf").write_bytes(b"%PDF")
        with mock.patch(self.SEND, return_value=0) as send:
            text = run("publish", "--to", "me@server.test")
        target, archive = send.call_args.args
        self.assertEqual(target, "me@server.test")
        names = self.names(archive)
        self.assertIn("example/course.yaml", names)
        self.assertIn("example/content/decks/least-squares.yaml", names)
        self.assertIn("example/content/lectures/assets/residuals.svg", names)
        self.assertEqual([name for name in names if "source" in name.split("/")], [])
        self.assertIn("Published", text)
        self.assertFalse(Course.objects.exists(), "publishing must not touch the local database")

    def test_invalid_content_is_never_sent(self):
        self.edit("content/decks/least-squares.yaml", "topic: lsq", "topic: nope")
        out = StringIO()
        with mock.patch(self.SEND) as send, self.assertRaises(CommandError) as raised:
            call_command("publish", "--to", "me@server.test", stdout=out)
        send.assert_not_called()
        self.assertIn("Nothing was sent", str(raised.exception))
        self.assertRegex(out.getvalue(), r"content/decks/least-squares\.yaml:\d+\s+topic")

    def test_dry_run_sends_nothing(self):
        with mock.patch(self.SEND) as send:
            text = run("publish", "--dry-run")
        send.assert_not_called()
        self.assertRegex(text, r"Would send 1 course, \d+ files")

    def test_needs_to_know_the_server(self):
        with (
            mock.patch.dict(os.environ, {"DSAI_PUBLISH_SSH": ""}),
            mock.patch(self.SEND) as send,
            self.assertRaises(CommandError) as raised,
        ):
            run("publish")
        send.assert_not_called()
        self.assertIn("DSAI_PUBLISH_SSH", str(raised.exception))

    def test_a_refusal_by_the_server_is_an_error(self):
        with mock.patch(self.SEND, return_value=1), self.assertRaises(CommandError):
            run("publish", "--to", "me@server.test")

    def test_send_pipes_the_archive_to_the_deploy_script(self):
        with mock.patch("subprocess.run", return_value=mock.Mock(returncode=0)) as ssh:
            self.assertEqual(send("me@server.test", b"archive"), 0)
        command = ssh.call_args.args[0]
        self.assertEqual((command[0], command[-2:]), ("ssh", ["me@server.test", REMOTE_COMMAND]))
        self.assertIn("BatchMode=yes", command)
        self.assertEqual(ssh.call_args.kwargs["input"], b"archive")


class SchemaExportTests(SimpleTestCase):
    def test_committed_schemas_match_the_models(self):
        """docs/schemas/ is generated. If this fails, run: manage.py export_schemas"""
        for name, model in SCHEMAS.items():
            path = TARGET / f"{name}.schema.json"
            self.assertTrue(path.is_file(), f"{path} is missing")
            self.assertEqual(path.read_text(encoding="utf-8"), render(model), name)

    def test_committed_field_reference_matches_the_models(self):
        self.assertEqual(FIELDS.read_text(encoding="utf-8"), render_markdown())
