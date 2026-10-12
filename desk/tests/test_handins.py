"""Hand-ins: an educator uploads their course, and the site takes it in if it only adds
(desk/handins.py, ingest/handin.py). The example course is the course being written."""

import io
import shutil
import zipfile
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail as outbox
from django.core.cache import caches
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase
from django.urls import reverse

from catalog.models import Card, Course, Document
from desk import handins
from desk import mail as desk_mail
from desk.models import Educator, HandIn
from ingest import handin, live
from ingest.tests.base import CourseTestCase

User = get_user_model()
C = "example"
PAGE = "/educators/"
UPLOAD = f"/educators/courses/{C}/hand-in/"
FILES = f"/educators/courses/{C}/files.zip"
DECK = "content/decks/least-squares.yaml"
NEW_GUIDE = "---\ntitle: A second look\ntopics: [lsq]\n---\n\nSomething more.\n"
NEW_CARD = "  - id: lsq-extra\n    q: One more?\n    a: Yes.\n"


class CompareTests(SimpleTestCase):
    """The rule itself: what is there stays, in order; anything may be added."""

    def change(self, before, after):
        return handin.compare({"a.yaml": before.encode()}, {"a.yaml": after.encode()})

    def test_lines_may_be_added_anywhere(self):
        change = self.change("a\nb\nc\n", "zero\na\nb\nmiddle\nc\nend\n")
        self.assertTrue(change.ok)
        self.assertEqual(change.grown, {"a.yaml": 3})

    def test_a_removed_or_rewritten_line_is_named(self):
        change = self.change("first\nsecond\nthird\n", "first\nSECOND\nthird\nfourth\n")
        self.assertFalse(change.ok)
        self.assertIn("a.yaml: 1 line removed or rewritten", change.problems[0])
        self.assertIn("line 2: second", change.problems[1])

    def test_reordering_is_not_adding(self):
        self.assertFalse(self.change("a\nb\n", "b\na\n").ok)

    def test_repeated_lines_are_counted_not_merely_found(self):
        self.assertTrue(self.change("- x\n- x\n", "- x\n- y\n- x\n").ok)
        self.assertFalse(self.change("- x\n- x\n", "- x\n- y\n").ok)

    def test_line_endings_and_trailing_spaces_do_not_count(self):
        self.assertTrue(self.change("a\nb\n", "a  \r\nb\r\n\r\n").ok)
        self.assertEqual(self.change("a\nb\n", "a\r\nb\r\n").grown, {})

    def test_files_may_be_added_but_not_dropped_and_images_not_swapped(self):
        old = {"a.yaml": b"x\n", "pic.png": b"\x89PNG1"}
        change = handin.compare(old, {"a.yaml": b"x\n", "pic.png": b"\x89PNG1", "b.md": b"new\n"})
        self.assertTrue(change.ok)
        self.assertEqual(change.added, ["b.md"])
        self.assertIn(
            "a.yaml: the file is missing", handin.compare(old, {"pic.png": b"\x89PNG1"}).problems
        )
        swapped = handin.compare(old, {"a.yaml": b"x\n", "pic.png": b"\x89PNG2"})
        self.assertIn("pic.png: the image was replaced by another", swapped.problems)

    def test_holds_is_the_same_rule_seen_from_the_other_side(self):
        snapshot = {"course.yaml": b"topics:\n  - id: a\n", "d.yaml": b"x\ny\n"}
        more = {
            "course.yaml": b"title: T\ntopics:\n  - id: a\n  - id: b\n",
            "d.yaml": b"x\ny\nz\n",
            "e.md": b"e\n",
        }
        self.assertTrue(handin.holds(more, snapshot))
        self.assertFalse(handin.holds(snapshot, more))
        self.assertFalse(handin.holds({**more, "course.yaml": b"topics: []\n"}, snapshot))


class HandInCase(CourseTestCase):
    def setUp(self):
        super().setUp()
        caches["limits"].clear()
        self.assertEqual(self.sync().status, "synced")
        self.ada = User.objects.create_user("ada", email="ada@example.test", first_name="Ada")
        self.bob = User.objects.create_user("bob", email="bob@example.test", first_name="Bob")
        self.admin = User.objects.create_superuser("root", email="root@example.test")
        for person in (self.ada, self.bob):
            Educator.objects.create(user=person, series=C)
        self.client.force_login(self.ada)
        self.mine = self.copy("ada")

    def copy(self, name):
        """What an educator has on their computer: the course as the site shows it now."""
        folder = self.tmp / name / C
        shutil.rmtree(folder, ignore_errors=True)
        shutil.copytree(live.folder(C), folder, ignore=shutil.ignore_patterns(".handin"))
        return folder

    def add(self, folder, name, text):
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            (path.read_text("utf-8") if path.exists() else "") + text, "utf-8", newline="\n"
        )

    def hand_in(self, folder, client=None):
        upload = SimpleUploadedFile("example.zip", handin.pack(folder), "application/zip")
        return (client or self.client).post(UPLOAD, {"zip": upload})

    def written(self):
        """Ada adds a card to a deck and writes a new guide."""
        self.add(self.mine, DECK, NEW_CARD)
        self.add(self.mine, "content/guides/a-second-look.md", NEW_GUIDE)


class TakingInTests(HandInCase):
    def test_additions_are_on_the_site_at_once(self):
        cards = Card.objects.count()
        self.written()
        with mock.patch("desk.views.notify") as notify, self.captureOnCommitCallbacks(execute=True):
            answer = self.hand_in(self.mine)
        record = HandIn.objects.get()
        self.assertRedirects(
            answer, f"{PAGE}?handed={record.pk}#course-{C}", fetch_redirect_response=False
        )
        self.assertEqual((record.user, record.status, record.slug), (self.ada, "live", C))
        self.assertEqual(record.new_files, ["content/guides/a-second-look.md"])
        self.assertEqual(record.grown, {DECK: 3})
        self.assertEqual(record.summary, "1 new file, 3 lines added")
        # Live: the database holds it, read from a folder of the site's own.
        self.assertEqual(Card.objects.count(), cards + 1)
        self.assertTrue(Document.objects.filter(slug="a-second-look").exists())
        self.assertEqual(live.folder(C), handins.root() / C)
        self.assertNotIn("lsq-extra", self.read(DECK))  # the owner's files are not touched
        # The owner is told that something arrived, not by whom.
        told = " ".join([*notify.call_args.args, *map(str, notify.call_args.kwargs.values())])
        self.assertIn("Hand-in on the site", told)
        self.assertNotIn("Ada", told)

        page = self.client.get(f"{PAGE}?handed={record.pk}")
        self.assertContains(page, "Taken in: 1 new file, 3 lines added")
        self.assertContains(page, "What was added so far")
        self.assertContains(page, "content/guides/a-second-look.md")
        self.assertContains(page, "· you")
        self.assertContains(page, 'git commit -m "example: handed in"')
        # A fellow educator of the course sees the same step, with the name.
        self.client.force_login(self.bob)
        self.assertContains(self.client.get(PAGE), "· Ada")

    def refused(self, answer, heading):
        self.assertEqual(answer.status_code, 200)
        self.assertContains(answer, heading)
        self.assertFalse(HandIn.objects.exists())
        self.assertFalse((handins.root() / C).exists())
        self.assertFalse(Card.objects.filter(key="lsq-extra").exists())

    def test_a_removed_line_is_refused_and_named(self):
        self.written()
        deck = self.mine / DECK
        lines = deck.read_text("utf-8").split("\n")
        gone = next(line for line in lines if line.strip().startswith("q:"))
        deck.write_text("\n".join(line for line in lines if line != gone), "utf-8")
        answer = self.hand_in(self.mine)
        self.refused(answer, "it removes or rewrites what is already there")
        self.assertContains(answer, f"{DECK}: ")
        self.assertContains(answer, "removed or rewritten")
        self.assertContains(answer, gone.strip()[:30])

    def test_a_rewritten_line_and_a_dropped_file_are_refused(self):
        deck = self.mine / DECK
        deck.write_text(
            deck.read_text("utf-8").replace("Least squares", "Least Squares!", 1), "utf-8"
        )
        self.refused(self.hand_in(self.mine), "removed or rewritten")
        self.mine = self.copy("ada")
        (self.mine / "content/reference/cheatsheet.md").unlink()
        self.refused(
            self.hand_in(self.mine), "content/reference/cheatsheet.md: the file is missing"
        )

    def test_what_is_the_owners_in_course_yaml_cannot_be_changed(self):
        course = self.mine / "course.yaml"
        course.write_text(course.read_text("utf-8").replace("code: EX101", "code: MINE"), "utf-8")
        self.refused(
            self.hand_in(self.mine), "`code` was &#x27;EX101&#x27; and is now &#x27;MINE&#x27;"
        )

    def test_content_the_site_would_refuse_is_shown_with_its_report(self):
        self.add(self.mine, DECK, "  - id: lsq-bad\n    q: Q?\n    a: A.\n    topic: nope\n")
        answer = self.hand_in(self.mine)
        self.refused(answer, "check found errors")
        self.assertContains(answer, "no topic named `nope` in this course")
        self.assertContains(answer, f"{DECK}:")

    def test_only_a_zip_of_this_course_from_its_educator(self):
        self.written()
        self.refused(
            self.client.post(UPLOAD, {"zip": SimpleUploadedFile("x.zip", b"not a zip")}),
            "not the zip",
        )
        self.refused(self.client.post(UPLOAD, {}), "No file arrived")
        other = self.tmp / "other" / "other-course"
        shutil.copytree(self.mine, other)
        self.refused(self.hand_in(other), "This zip is the course `other-course`")
        with mock.patch("desk.handins.MAX_UPLOAD", 10):
            self.refused(self.hand_in(self.mine), "The file is larger than")
        self.refused(self.hand_in(self.copy("same")), "exactly what the site already has")
        # Someone who does not write this course has no such address at all.
        carol = User.objects.create_user("carol", email="carol@example.test")
        self.client.force_login(carol)
        self.assertEqual(self.hand_in(self.mine).status_code, 404)
        self.assertEqual(self.client.post(FILES).status_code, 404)
        self.assertFalse(HandIn.objects.exists())

    def test_one_at_a_time_per_course(self):
        self.written()
        handins.root().mkdir(parents=True)
        (handins.root() / f".lock-{C}").write_text("", "utf-8")
        self.refused(self.hand_in(self.mine), "Someone is handing in this course right now")


class MovedOnTests(HandInCase):
    """Two educators of one course. The second to hand in built on what is no longer the
    latest, and is told how to catch up."""

    def setUp(self):
        super().setUp()
        other = self.client_class()
        other.force_login(self.bob)
        self.bobs_browser = other
        # Both download the course: the site notes which version each of them has.
        for client in (self.client, other):
            self.assertEqual(client.post(FILES).status_code, 200)
        self.bobs = self.copy("bob")
        self.written()
        self.assertEqual(self.hand_in(self.mine).status_code, 302)

    def test_work_built_on_an_older_version_is_refused_as_a_conflict(self):
        self.add(self.bobs, "content/reference/cheatsheet.md", "\nOne more line from Bob.\n")
        answer = self.hand_in(self.bobs, self.bobs_browser)
        self.assertContains(answer, "the course changed on the site after you took your copy")
        self.assertContains(answer, "git stash")
        self.assertContains(answer, "uv run tools/unpack.py example.zip")
        self.assertContains(answer, "git stash pop")
        self.assertContains(answer, "content/guides/a-second-look.md: the file is missing")
        self.assertEqual(HandIn.objects.count(), 1)

    def test_on_top_of_the_latest_it_goes_in_and_nothing_of_the_first_is_lost(self):
        self.bobs = self.copy("bob")  # downloads again: Ada's work is in it now
        self.add(self.bobs, "content/reference/cheatsheet.md", "\nOne more line from Bob.\n")
        self.assertEqual(self.hand_in(self.bobs, self.bobs_browser).status_code, 302)
        self.assertEqual(HandIn.objects.count(), 2)
        self.assertTrue(Card.objects.filter(key="lsq-extra").exists())
        self.assertIn(
            "One more line from Bob.",
            (live.folder(C) / "content/reference/cheatsheet.md").read_text("utf-8"),
        )

    def test_the_download_is_what_the_site_shows_and_is_a_post(self):
        self.assertEqual(self.client.get(FILES).status_code, 405)
        answer = self.bobs_browser.post(FILES)
        with zipfile.ZipFile(io.BytesIO(answer.content)) as archive:
            self.assertIn(f"{C}/content/guides/a-second-look.md", archive.namelist())
            self.assertIn("lsq-extra", archive.read(f"{C}/{DECK}").decode())
            self.assertEqual([n for n in archive.namelist() if ".handin" in n], [])
        role = Educator.objects.get(user=self.bob, series=C)
        self.assertEqual(role.synced_version, HandIn.objects.get().version)


class OwnerTests(HandInCase):
    """What the owner sees of it: the sync report, the admin, their own course files."""

    def setUp(self):
        super().setUp()
        self.written()
        self.assertEqual(self.hand_in(self.mine).status_code, 302)
        self.record = HandIn.objects.get()
        self.LIST = reverse("admin:desk_handin_changelist")

    def run_sync(self, *args):
        out = io.StringIO()
        call_command("sync_content", *args, stdout=out)
        return out.getvalue()

    def test_a_publish_without_the_hand_in_does_not_lose_it(self):
        for args in ((), ("--check",)):
            with self.subTest(args=args):
                text = self.run_sync(*args)
                self.assertIn("shown as handed in by its educators", text)
                self.assertIn("lack 1 hand-in", text)
        self.assertEqual(HandIn.objects.get().status, "live")
        self.assertTrue(Card.objects.filter(key="lsq-extra").exists())

    def test_the_owner_takes_it_in_and_the_site_lets_go_of_its_copy(self):
        self.client.force_login(self.admin)
        page = self.client.get(self.LIST)
        self.assertContains(page, "1 new file, 3 lines added")
        zipped = self.client.get(reverse("desk:handin_zip", args=[self.record.pk]))
        self.assertEqual(zipped.status_code, 200)
        saved = self.tmp / "example-handin.zip"
        saved.write_bytes(zipped.content)
        # Meanwhile the owner has written something of their own, in another file.
        self.append("content/reference/cheatsheet.md", "\nThe owner's own line.\n")

        out = io.StringIO()
        call_command("import_course", str(saved), stdout=out)
        self.assertIn("example: taken in. 1 new, 1 longer", out.getvalue())
        self.assertIn("lsq-extra", self.read(DECK))
        self.assertIn("The owner's own line.", self.read("content/reference/cheatsheet.md"))

        text = self.run_sync()  # what a publish does on the server
        self.assertNotIn("shown as handed in", text)
        record = HandIn.objects.get()
        self.assertEqual(record.status, "merged")
        self.assertIsNotNone(record.settled_at)
        self.assertFalse((handins.root() / C).exists())
        self.assertEqual(live.folder(C), self.course)
        self.assertTrue(Card.objects.filter(key="lsq-extra").exists())
        self.client.force_login(self.ada)
        self.assertContains(self.client.get(PAGE), "In the published files")

    def test_where_both_changed_a_file_the_owner_decides(self):
        saved = self.tmp / "example-handin.zip"
        saved.write_bytes(bytes(self.record.archive))
        deck = self.read(DECK)
        self.write(DECK, deck.replace("Least squares", "Least squares, by the owner", 1))
        with self.assertRaises(CommandError) as raised:
            call_command("import_course", str(saved), stdout=io.StringIO())
        self.assertIn("You and the hand-in both changed", str(raised.exception))
        self.assertIn(DECK, str(raised.exception))
        self.assertNotIn("lsq-extra", self.read(DECK))
        self.assertFalse((self.course / "content/guides/a-second-look.md").exists())
        call_command("import_course", str(saved), "--theirs", stdout=io.StringIO())
        self.assertIn("lsq-extra", self.read(DECK))

    def test_taking_it_off_the_site_puts_the_course_back(self):
        self.client.force_login(self.admin)
        chosen = {"action": "take_off", "_selected_action": [self.record.pk]}
        # Mail is sent from a thread; here it is delivered on the spot, into Django's
        # test outbox, so that the test can look at it.
        with mock.patch("desk.mail._dispatch", side_effect=desk_mail.deliver):
            self.assertRedirects(self.client.post(self.LIST, chosen), self.LIST)
        self.assertEqual(HandIn.objects.get().status, "withdrawn")
        self.assertFalse(Card.objects.filter(key="lsq-extra").exists())
        self.assertFalse(Document.objects.filter(slug="a-second-look").exists())
        self.assertFalse((handins.root() / C).exists())
        self.assertEqual([message.to for message in outbox.outbox], [["ada@example.test"]])
        self.assertIn("taken off the site", outbox.outbox[0].body)

    def test_the_sites_copy_is_rebuilt_from_the_database(self):
        shutil.rmtree(handins.root())
        self.run_sync()
        self.assertTrue((handins.root() / C / DECK).is_file())
        self.assertTrue(Card.objects.filter(key="lsq-extra").exists())

    def test_none_of_the_owners_side_is_open_to_others(self):
        self.assertEqual(
            self.client.get(reverse("desk:handin_zip", args=[self.record.pk])).status_code, 404
        )
        self.assertEqual(self.client.get(self.LIST).status_code, 302)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("admin:desk_handin_add")).status_code, 403)
        delete = reverse("admin:desk_handin_delete", args=[self.record.pk])
        self.assertEqual(self.client.post(delete, {"post": "yes"}).status_code, 403)

    def test_leaving_the_site_keeps_what_was_added_without_the_name(self):
        self.ada.delete()
        record = HandIn.objects.get()
        self.assertIsNone(record.user)
        self.assertTrue(Card.objects.filter(key="lsq-extra").exists())
        self.assertFalse(Course.objects.filter(slug=C).count() != 1)
        self.client.force_login(self.bob)
        self.assertContains(self.client.get(PAGE), "a former educator")
