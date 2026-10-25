"""A course's duties: checked with the course, shown nowhere, told to the owner's bot alone.

Nothing here touches the network: the one function that does (`desk.notify._post`) is
replaced."""

import io
import json
import shutil
import zipfile
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse

from desk import duties as bot
from desk.models import ToldDuty
from editor import source
from ingest import duties, handin
from ingest.management.commands import export_authoring
from ingest.report import Report
from ingest.tests.base import CourseTestCase

BOT = override_settings(
    BMO_NOTIFY_URL="https://bot.example.test/bmo-notify",
    BMO_NOTIFY_TOKEN="s3cret",
    BMO_DUTIES_URL="",
    SITE_URL="https://site.example.test",
)

LIST = """\
duties:
  - id: lab-1
    kind: lab
    title: Lab 1, least squares
    due: 2026-11-04T10:00
    place: Lab 1-12
  - id: midterm
    kind: test
    title: Midterm
    due: 2026-11-20
    notes: Chapters 1 to 4.
"""
LAB = """\
  - id: lab-1
    kind: lab
    title: Lab 1, least squares
    due: 2026-11-04T10:00
    place: Lab 1-12
"""


class FileTests(CourseTestCase):
    def test_a_list_is_read_and_its_dates_are_kept_as_written(self):
        self.write("duties.yaml", LIST)
        found = duties.read(self.course, Report(course="example"))
        self.assertEqual([duty.due for duty in found], ["2026-11-04T10:00", "2026-11-20"])
        self.assertEqual((found[1].place, found[1].notes), ("", "Chapters 1 to 4."))
        report = self.sync()
        self.assertTrue(report.ok, report.format())
        self.assertEqual(report.counts["duties"], 2)

    def test_no_file_is_no_duties(self):
        self.assertEqual(duties.read(self.course, Report(course="example")), [])
        self.assertNotIn("duties", self.sync().counts)

    def test_a_mistake_stops_the_course_like_one_in_any_of_its_files(self):
        self.assertEqual(self.sync().status, "synced")
        cases = [
            ("kind: lab", "kind: party", "kind"),
            ("due: 2026-11-20", "due: 2026-11-31", "not a date that exists"),
            ("due: 2026-11-20", "due: next week", "must be a day"),
            ("due: 2026-11-20", "due: 2026-11-20T10:00:30", "to the minute"),
            ("place: Lab 1-12", "room: Lab 1-12", "unknown field `room`"),
            ("id: midterm", "id: lab-1", "used twice"),
            ("title: Midterm", "title: ''", "title"),
        ]
        for old, new, fragment in cases:
            with self.subTest(new=new):
                self.write("duties.yaml", LIST.replace(old, new, 1))
                self.assertProblem(self.check(), fragment, file="duties.yaml")
                # The rest of the course is unchanged, and the mistake still counts.
                self.assertEqual(self.sync().status, "failed")


class PrivateTests(CourseTestCase):
    """Only the owner's own files hold duties, and only the bot is told of them."""

    def setUp(self):
        super().setUp()
        self.write("duties.yaml", LIST)
        self.assertEqual(self.sync().status, "synced")

    def test_they_never_travel_to_an_educator(self):
        self.assertNotIn("duties.yaml", handin.files_of(self.course))
        with zipfile.ZipFile(io.BytesIO(handin.pack(self.course))) as archive:
            self.assertFalse([name for name in archive.namelist() if "duties" in name])
        # A hand-in cannot carry them in either, nor can the editor open them.
        with self.assertRaises(handin.HandInError):
            handin.check({**handin.files_of(self.course), "duties.yaml": LIST.encode()})
        self.assertFalse(source.plain("duties.yaml"))

    def test_no_page_shows_them(self):
        owner = get_user_model().objects.create_superuser("root", email="root@example.test")
        self.client.force_login(owner)
        for url in (
            reverse("catalog:course", args=["example"]),
            reverse("editor:files", args=["example"]),
        ):
            with self.subTest(url=url):
                page = self.client.get(url)
                self.assertEqual(page.status_code, 200)
                self.assertNotContains(page, "least squares")
                self.assertNotContains(page, "duties")

    def test_the_kit_carries_neither_the_file_nor_a_word_of_it(self):
        target = self.tmp / "kit" / "example"
        export_authoring.copy(self.course, target)
        self.assertTrue((target / "course.yaml").is_file())
        self.assertFalse((target / "duties.yaml").exists())
        for name in export_authoring.RULES:
            with self.subTest(name=name):
                text = (settings.BASE_DIR / "ingest" / name).read_text(encoding="utf-8")
                self.assertNotIn("duties", text.lower())
        docs = settings.BASE_DIR / "docs"
        guide = [docs / "AUTHORING.md", *sorted((docs / "content-types").glob("*.md"))]
        guide += sorted((docs / "schemas").glob("*.json"))
        for path in guide:
            with self.subTest(path=path.name):
                self.assertNotIn("duties", path.read_text(encoding="utf-8").lower())


@BOT
class PushTests(CourseTestCase):
    def setUp(self):
        super().setUp()
        self.write("duties.yaml", LIST)

    def push(self, *answers, only=None):
        with mock.patch("desk.notify._post", side_effect=list(answers) or [200] * 10) as post:
            told = bot.push(only)
        return told, [(json.loads(call.args[0]), call.args[1]) for call in post.call_args_list]

    def test_the_first_push_tells_everything_as_new(self):
        told, [(payload, url)] = self.push()
        self.assertEqual(url, "https://bot.example.test/bmo-duties")
        self.assertEqual(payload["source"], "DSAI Vault")
        self.assertRegex(payload["batch_id"], r"^dsai-duties-[0-9a-f]{32}$")
        self.assertEqual(
            payload["items"][0],
            {
                "key": "example/lab-1",
                "change": "new",
                "course": "EX101",
                "course_title": "Example 101: Fitting a Line",
                "kind": "lab",
                "title": "Lab 1, least squares",
                "due": "2026-11-04T10:00",
                "place": "Lab 1-12",
                "notes": "",
                "url": "https://site.example.test" + reverse("catalog:course", args=["example"]),
            },
        )
        self.assertEqual(
            [item["key"] for item in payload["items"]], ["example/lab-1", "example/midterm"]
        )
        self.assertEqual((told.new, told.changed, told.removed), (2, 0, 0))
        self.assertEqual(str(told), "told about 2 new")
        self.assertEqual(ToldDuty.objects.count(), 2)

    def test_when_nothing_changed_nothing_is_sent(self):
        self.push()
        told, posts = self.push()
        self.assertEqual(posts, [])
        self.assertEqual(str(told), "nothing new to tell")

    def test_only_what_changed_is_sent(self):
        self.push()
        self.edit("duties.yaml", "due: 2026-11-20", "due: 2026-11-27")
        self.edit("duties.yaml", LAB, "")
        self.append(
            "duties.yaml",
            "  - id: project\n    kind: project\n    title: Defence\n    due: 2027-01-15T09:00\n",
        )
        told, [(payload, _url)] = self.push()
        self.assertEqual(
            {item["key"]: (item["change"], item["due"]) for item in payload["items"]},
            {
                "example/lab-1": ("removed", "2026-11-04T10:00"),
                "example/midterm": ("changed", "2026-11-27"),
                "example/project": ("new", "2027-01-15T09:00"),
            },
        )
        self.assertEqual(str(told), "told about 1 new, 1 changed, 1 removed")
        self.assertEqual(
            list(ToldDuty.objects.values_list("key", flat=True)),
            ["example/midterm", "example/project"],
        )

    def test_what_the_bot_did_not_take_is_sent_again_with_the_same_id(self):
        with self.assertLogs("desk.notify", "WARNING") as logs:
            told, [(first, _url)] = self.push(403)
        self.assertNotIn("s3cret", " ".join(logs.output))
        self.assertEqual(told.waiting, 2)
        self.assertFalse(ToldDuty.objects.exists())
        told, [(again, _url)] = self.push(200)
        self.assertEqual(again["batch_id"], first["batch_id"])
        self.assertEqual(told.new, 2)

    def test_coming_back_to_an_earlier_date_is_a_batch_of_its_own(self):
        ids = [self.push()[1][0][0]["batch_id"]]
        for old, new in (("2026-11-20", "2026-11-27"), ("2026-11-27", "2026-11-20")):
            self.edit("duties.yaml", f"due: {old}", f"due: {new}")
            ids.append(self.push()[1][0][0]["batch_id"])
        self.assertEqual(len(set(ids)), 3)

    def test_at_most_fifty_in_one_post(self):
        rows = "".join(
            f"  - id: hw-{n}\n    kind: homework\n    title: Homework {n}\n    due: 2026-12-01\n"
            for n in range(120)
        )
        self.write("duties.yaml", "duties:\n" + rows)
        told, posts = self.push()
        self.assertEqual([len(payload["items"]) for payload, _url in posts], [50, 50, 20])
        self.assertEqual(len({payload["batch_id"] for payload, _url in posts}), 3)
        self.assertEqual(told.new, 120)

    def test_a_broken_file_keeps_what_the_bot_has(self):
        self.push()
        self.write("duties.yaml", "duties:\n  - id: x\n")
        told, posts = self.push()
        self.assertEqual(posts, [])
        self.assertEqual(told.skipped, ["example"])
        self.assertEqual(ToldDuty.objects.count(), 2)

    def test_removing_the_file_removes_its_duties(self):
        self.push()
        (self.course / "duties.yaml").unlink()
        told, [(payload, _url)] = self.push()
        self.assertEqual({item["change"] for item in payload["items"]}, {"removed"})
        self.assertEqual(payload["items"][0]["title"], "Lab 1, least squares")
        self.assertEqual(told.removed, 2)
        self.assertFalse(ToldDuty.objects.exists())

    def test_a_course_that_is_gone_is_removed_only_by_a_sync_of_everything(self):
        self.push()
        shutil.rmtree(self.course)
        _told, posts = self.push(only=["other"])
        self.assertEqual(posts, [])
        told, [(payload, _url)] = self.push()
        self.assertEqual(told.removed, 2)

    def test_a_sync_of_one_course_leaves_the_others_alone(self):
        self.push()
        _told, posts = self.push(only=["another"])
        self.assertEqual(posts, [])
        self.assertEqual(ToldDuty.objects.count(), 2)


class AddressTests(CourseTestCase):
    def test_the_address_comes_from_the_one_for_notifications(self):
        cases = [
            ("https://bot.test/bmo-notify", "", "https://bot.test/bmo-duties"),
            ("https://bot.test/bmo-notify", "https://other.test/in", "https://other.test/in"),
            # Nothing to change: never the address of notifications, which would read
            # the list as a message.
            ("https://bot.test/hook", "", ""),
            ("", "", ""),
        ]
        for notify_url, duties_url, expected in cases:
            with (
                self.subTest(notify_url=notify_url, duties_url=duties_url),
                override_settings(BMO_NOTIFY_URL=notify_url, BMO_DUTIES_URL=duties_url),
            ):
                self.assertEqual(bot.address(), expected)

    def test_without_the_bot_nothing_happens(self):
        self.write("duties.yaml", LIST)
        cases = [
            {"BMO_NOTIFY_TOKEN": ""},
            {"BMO_NOTIFY_TOKEN": "s", "BMO_DUTIES_URL": "http://bot.test/bmo-duties"},
            {"BMO_NOTIFY_TOKEN": "s", "BMO_NOTIFY_URL": ""},
        ]
        for values in cases:
            with (
                self.subTest(values=values),
                BOT,
                override_settings(**values),
                mock.patch("desk.notify._post") as post,
            ):
                self.assertIsNone(bot.push())
                post.assert_not_called()
        self.assertFalse(ToldDuty.objects.exists())


class CommandTests(CourseTestCase):
    def run_command(self, *args):
        out = io.StringIO()
        try:
            call_command("sync_content", *args, stdout=out, stderr=out)
        except Exception as error:  # noqa: BLE001 - the output is what is asserted
            out.write(str(error))
        return out.getvalue()

    @BOT
    def test_a_sync_tells_the_bot_and_a_check_does_not(self):
        self.write("duties.yaml", LIST)
        with mock.patch("desk.notify._post", return_value=200) as post:
            self.assertNotIn("Duties", self.run_command("--check"))
            post.assert_not_called()
            said = self.run_command()
        post.assert_called_once()
        self.assertIn("2 duties", said)
        self.assertIn("Duties: told about 2 new.", said)
        self.assertNotIn("least squares", said)

    def test_without_the_bot_the_sync_says_nothing_of_it(self):
        self.write("duties.yaml", LIST)
        self.assertNotIn("Duties:", self.run_command())
