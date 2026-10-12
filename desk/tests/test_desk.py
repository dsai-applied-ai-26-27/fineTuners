"""The desk: asking and reporting, applying to write a course, the educator's role, and
the owner's switches for a course.

Courses are made as bare rows here. These pages only need a course to exist; what is in
it is tested with the example course elsewhere.
"""

import io
import tempfile
import zipfile
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache, caches
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Enrollment
from catalog.mine import by_semester
from catalog.models import Course
from desk.forms import BugForm, ContentForm, IdeaForm, course_choices
from desk.models import CourseSetting, Educator, EducatorApplication, Request
from desk.switches import Switches

User = get_user_model()
ASK, APPLY, EDUCATORS = "/ask/", "/educators/apply/", "/educators/"
# The page of one course for the people who write it, and the courses nobody writes yet.
WORK, OPEN = "/educators/courses/rl/", "/educators/open/"
NOTIFY = "desk.views.notify"
OPEN_MIDDLEWARE = [name for name in settings.MIDDLEWARE if "LoginRequired" not in name]


def course(slug, title, **fields):
    fields.setdefault("series", slug)
    fields.setdefault("code", slug.upper())
    return Course.objects.create(slug=slug, title=title, **fields)


class DeskTestCase(TestCase):
    """Three courses: one open and unwritten, one the owner writes, one not opened yet."""

    def setUp(self):
        cache.clear()
        caches["limits"].clear()  # the rate limiter counts across tests otherwise
        self.rl = course("rl", "Reinforcement Learning", semester=5)
        self.aai = course("aai", "Applied AI", semester=5, has_educator=True)
        self.nlp = course("nlp", "Natural Language Processing", semester=6, enabled=False)
        self.ada = User.objects.create_user(
            "ada", email="ada@example.test", first_name="Ada", last_name="Lovelace"
        )
        self.bob = User.objects.create_user("bob", email="bob@example.test")
        self.admin = User.objects.create_superuser("root", email="root@example.test")
        self.client.force_login(self.ada)

    def application(self, **changes):
        form = {
            "series": "rl",
            "name": "Ada Lovelace",
            "phone": "+387 61 123 456",
            "year": "2",
            "tools": "paid",
            "note": "I had a 10 in it.",
        }
        return {**form, **changes}


class CourseDropdownTests(DeskTestCase):
    """Where a course is picked from a dropdown, the courses stand under their semester."""

    def setUp(self):
        super().setUp()
        self.late = course("zz", "Zoology of Models", semester=6, order=2)
        self.early = course("mai1", "Mathematics for AI I", semester=1)
        self.loose = course("misc", "Reading Group")  # names no semester

    def test_semesters_in_order_and_what_names_none_last(self):
        groups = by_semester([self.late, self.loose, self.rl, self.early, self.aai])
        self.assertEqual(
            [(label, [c.slug for c in members]) for label, members in groups],
            [
                ("Semester I", ["mai1"]),
                ("Semester V", ["aai", "rl"]),
                ("Semester VI", ["zz"]),
                ("Other courses", ["misc"]),
            ],
        )

    def test_the_forms_draw_a_heading_per_semester(self):
        page = self.client.get(ASK)
        for heading in ("Semester I", "Semester V", "Semester VI", "Other courses"):
            self.assertContains(page, f'<optgroup label="{heading}">')
        text = page.text
        self.assertLess(text.index('label="Semester I"'), text.index('label="Semester V"'))
        self.assertLess(text.index('label="Semester VI"'), text.index('label="Other courses"'))
        # A course that is not open is in no group.
        self.assertNotContains(page, "Natural Language Processing")

    def test_a_course_under_a_heading_can_be_chosen(self):
        """Django looks for the value inside the groups when it checks a form."""
        answer = self.client.post(
            ASK, {"kind": "content", "series": "zz", "message": "Lecture 2 is missing."}
        )
        self.assertEqual(answer.status_code, 302)
        self.assertEqual(Request.objects.get().series, "zz")

    def test_one_semester_alone_gets_no_heading(self):
        self.assertEqual(
            course_choices([self.rl, self.aai], "Any"),
            [("", "Any"), ("aai", "AAI · Applied AI"), ("rl", "RL · Reinforcement Learning")],
        )

    def test_the_search_page_groups_them_too(self):
        page = self.client.get("/search/")
        self.assertContains(page, '<optgroup label="Semester I">')
        self.assertContains(page, '<optgroup label="Other courses">')
        self.assertNotContains(page, "Natural Language Processing")


class AskTests(DeskTestCase):
    def test_the_form_knows_the_course_and_the_page_it_was_opened_from(self):
        page = self.client.get(ASK, {"course": "rl", "kind": "bug", "from": "/courses/rl/cards/"})
        form = page.context["form"]
        self.assertIsInstance(form, BugForm)
        self.assertEqual(form.initial["series"], "rl")
        self.assertContains(page, 'name="page" value="/courses/rl/cards/"')
        self.assertContains(page, 'name="kind" value="bug"')
        self.assertContains(page, "The page you came from is sent along")
        # The three kinds are links, and each carries along where the person came from.
        kinds = {item["value"]: item for item in page.context["kinds"]}
        self.assertEqual([k for k, item in kinds.items() if item["current"]], ["bug"])
        self.assertEqual(
            kinds["content"]["url"], "/ask/?kind=content&course=rl&from=%2Fcourses%2Frl%2Fcards%2F"
        )
        self.assertContains(page, 'aria-current="page"')

    def test_a_fault_seen_on_a_course_page_is_about_that_course_without_being_told(self):
        page = self.client.get(ASK, {"kind": "bug", "from": "/courses/rl/cards/mdp/"})
        self.assertEqual(page.context["form"].initial["series"], "rl")
        # A page of a course that is not open, or no course page at all, names none.
        for path in ("/courses/nlp/", "/settings/", ""):
            page = self.client.get(ASK, {"kind": "bug", "from": path})
            self.assertEqual(page.context["form"].initial["series"], "", msg=path)

    def test_each_kind_asks_its_own_questions(self):
        """Content needs a course and what is missing; a fault needs where, what, and what
        instead; an idea needs what and what for, and is about no course."""
        asked = {
            "content": (
                ContentForm,
                ["Which course?", "What is missing?", "Which lecture or topic?"],
            ),
            "bug": (BugForm, ["Where did you see it?", "What is wrong?", "say or do instead?"]),
            "idea": (IdeaForm, ["What should the site be able to do?", "help you with?"]),
        }
        for kind, (form, questions) in asked.items():
            page = self.client.get(ASK, {"kind": kind})
            self.assertIsInstance(page.context["form"], form)
            for question in questions:
                self.assertContains(page, question)
            for other, (_, theirs) in asked.items():
                if other != kind:
                    self.assertNotContains(page, theirs[-1])
        self.assertNotContains(self.client.get(ASK, {"kind": "idea"}), 'name="series"')
        # No kind, or one that does not exist, is a request for content.
        for kind in ("", "nonsense"):
            self.assertIsInstance(self.client.get(ASK, {"kind": kind}).context["form"], ContentForm)

    def test_the_answers_are_stored_as_one_text_that_says_which_is_which(self):
        self.client.post(
            ASK,
            {
                "kind": "content",
                "series": "rl",
                "wants": ["notes", "cards"],
                "message": "Lecture 5, policy gradients.",
            },
        )
        self.client.post(
            ASK,
            {
                "kind": "bug",
                "series": "rl",
                "where": "Card 4 of the deck on MDPs",
                "message": "The discount is written as larger than 1.",
                "expected": "Smaller than 1, as in the lecture.",
            },
        )
        self.client.post(
            ASK,
            {
                "kind": "idea",
                "series": "rl",
                "message": "Print a deck.",
                "why": "To study on paper.",
            },
        )
        idea, bug, content = Request.objects.all()  # newest first
        self.assertEqual(
            (content.kind, content.series, content.message),
            ("content", "rl", "Missing: lecture notes, flashcards\n\nLecture 5, policy gradients."),
        )
        self.assertEqual(
            (bug.kind, bug.series, bug.message),
            (
                "bug",
                "rl",
                "Where: Card 4 of the deck on MDPs\n\nThe discount is written as larger than 1."
                "\n\nShould be: Smaller than 1, as in the lecture.",
            ),
        )
        # An idea is about the site: a course sent along with it is not taken.
        self.assertEqual(
            (idea.kind, idea.series, idea.message),
            ("idea", "", "Print a deck.\n\nWhy: To study on paper."),
        )
        # What was left empty leaves no trace.
        self.client.post(ASK, {"kind": "bug", "message": "The timer stops."})
        self.assertEqual(Request.objects.first().message, "The timer stops.")

    def test_only_what_the_form_offers_is_taken(self):
        answer = self.client.post(
            ASK, {"kind": "content", "series": "rl", "wants": ["money"], "message": "Please."}
        )
        self.assertEqual(answer.status_code, 200)
        self.assertFalse(Request.objects.exists())
        # The kind is the form's own, whatever else is posted beside it.
        self.client.post(
            ASK, {"kind": "idea", "message": "An idea.", "status": "done", "answer": "x"}
        )
        sent = Request.objects.get()
        self.assertEqual((sent.kind, sent.status, sent.answer), ("idea", "new", ""))

    def test_only_open_courses_can_be_asked_about(self):
        offered = [
            value for value, _ in self.client.get(ASK).context["form"].fields["series"].choices
        ]
        self.assertEqual(offered, ["", "aai", "rl"])
        # The form accepts what it offers and nothing else, even if posted by hand.
        answer = self.client.post(ASK, {"kind": "content", "series": "nlp", "message": "Please."})
        self.assertEqual(answer.status_code, 200)
        self.assertFalse(Request.objects.exists())

    def test_sending_stores_it_tells_the_owner_and_shows_it_back(self):
        # The owner is told only after the row is safely stored (transaction.on_commit).
        # A test runs inside a transaction that never commits, so Django offers
        # captureOnCommitCallbacks to run what would have run.
        with mock.patch(NOTIFY) as notify, self.captureOnCommitCallbacks(execute=True):
            answer = self.client.post(
                ASK,
                {"kind": "content", "series": "rl", "message": "Lecture 3, please.", "page": "/x/"},
            )
        self.assertRedirects(answer, f"{ASK}?sent=1")
        sent = Request.objects.get()
        self.assertEqual(
            (sent.user, sent.kind, sent.series, sent.status, sent.page),
            (self.ada, "content", "rl", "new", "/x/"),
        )
        notify.assert_called_once()
        title, message = notify.call_args.args
        self.assertEqual(title, "New request: content (Reinforcement Learning)")
        self.assertEqual(notify.call_args.kwargs["dedupe_key"], f"dsai-request-{sent.pk}")
        self.assertTrue(
            notify.call_args.kwargs["url"].endswith(f"/admin/desk/request/{sent.pk}/change/")
        )
        # Nothing about the person or what they wrote leaves the site.
        told = " ".join([title, message, *map(str, notify.call_args.kwargs.values())])
        for private in ("Ada", "ada@example.test", "Lecture 3"):
            self.assertNotIn(private, told)

        page = self.client.get(f"{ASK}?sent=1")
        self.assertContains(page, "Sent, thank you")
        self.assertContains(page, "Lecture 3, please.")
        self.assertContains(page, "Reinforcement Learning")

    def test_a_request_for_content_names_its_course(self):
        answer = self.client.post(ASK, {"kind": "content", "series": "", "message": "More."})
        self.assertContains(answer, "Say which course the content is for.")
        self.assertFalse(Request.objects.exists())
        # An idea needs none.
        self.assertRedirects(
            self.client.post(ASK, {"kind": "idea", "series": "", "message": "A dark mode."}),
            f"{ASK}?sent=1",
        )

    def test_one_person_cannot_fill_the_list(self):
        for number in range(10):
            Request.objects.create(user=self.ada, kind="idea", message=f"Idea {number}")
        with mock.patch(NOTIFY) as notify, self.captureOnCommitCallbacks(execute=True):
            answer = self.client.post(ASK, {"kind": "idea", "message": "One more."})
        self.assertContains(answer, "You have sent a lot today.")
        self.assertEqual(Request.objects.count(), 10)
        notify.assert_not_called()
        # Someone else is not held up by it.
        self.client.force_login(self.bob)
        self.assertEqual(
            self.client.post(ASK, {"kind": "idea", "message": "Mine."}).status_code, 302
        )

    def test_the_answer_shows_to_the_person_who_asked_and_to_nobody_else(self):
        Request.objects.create(
            user=self.ada, kind="bug", series="rl", message="Card 4 is wrong.",
            status="done", answer="Fixed, thank you.",
        )  # fmt: skip
        self.assertContains(self.client.get(ASK), "Fixed, thank you.")
        self.client.force_login(self.bob)
        page = self.client.get(ASK)
        self.assertNotContains(page, "Card 4 is wrong.")
        self.assertNotContains(page, "Fixed, thank you.")

    def test_the_open_site_has_nobody_to_ask(self):
        self.client.logout()
        self.assertEqual(self.client.get(ASK).status_code, 302)  # to the sign-in
        with override_settings(REQUIRE_LOGIN=False, MIDDLEWARE=OPEN_MIDDLEWARE):
            # A client reads the middleware list at its first request, so a new one.
            visitor = self.client_class()
            self.assertRedirects(visitor.get(ASK), "/")
            self.assertRedirects(visitor.post(ASK, {"kind": "idea", "message": "x"}), "/")
            self.assertNotContains(visitor.get("/"), "Ask or report")
        self.assertFalse(Request.objects.exists())


class ApplyTests(DeskTestCase):
    def test_only_courses_nobody_writes_are_offered(self):
        page = self.client.get(APPLY, {"course": "rl"})
        offered = [value for value, _ in page.context["form"].fields["series"].choices]
        self.assertEqual(offered, ["", "rl"])  # not aai (written), not nlp (not open)
        self.assertEqual(page.context["form"].initial["series"], "rl")
        self.assertContains(page, 'value="Ada Lovelace"')  # the name comes from the account
        # Asking for one that is taken says so instead of failing.
        self.assertContains(self.client.get(APPLY, {"course": "aai"}), "already has someone")

    def test_applying_stores_it_and_tells_the_owner_without_the_details(self):
        with mock.patch(NOTIFY) as notify, self.captureOnCommitCallbacks(execute=True):
            answer = self.client.post(APPLY, self.application())
        self.assertRedirects(answer, f"{EDUCATORS}?applied=1")
        offer = EducatorApplication.objects.get()
        self.assertEqual(
            (offer.user, offer.series, offer.phone, offer.year, offer.status),
            (self.ada, "rl", "+387 61 123 456", "2", "pending"),
        )
        notify.assert_called_once()
        told = " ".join([*notify.call_args.args, *map(str, notify.call_args.kwargs.values())])
        self.assertIn("Reinforcement Learning", told)
        for private in ("Ada", "387", "I had a 10"):
            self.assertNotIn(private, told)
        page = self.client.get(f"{EDUCATORS}?applied=1")
        self.assertContains(page, "Application sent")
        self.assertContains(page, "Waiting for an answer")
        # Not an educator yet: applying gives nothing by itself.
        self.assertFalse(Educator.objects.exists())
        self.assertNotContains(page, "The courses you write")
        self.assertEqual(self.client.get("/educators/courses/rl/").status_code, 404)

    def test_what_is_typed_is_checked_and_tidied(self):
        bad = self.client.post(APPLY, self.application(phone="call me"))
        self.assertContains(bad, "Write the number with digits")
        self.assertFalse(EducatorApplication.objects.exists())
        self.client.post(APPLY, self.application(phone="061  123 456"))
        self.assertEqual(EducatorApplication.objects.get().phone, "061 123 456")

    def test_the_form_asks_for_nothing_it_has_no_use_for(self):
        """It used to take a GitHub user name, to give access to a repository that is now
        public. The privacy page lists what the form stores, so the two must agree: the
        field is gone from the page, a request that still sends one is taken without it,
        and the table has no column left to keep one in."""
        self.assertNotContains(self.client.get(APPLY, {"course": "rl"}), "GitHub")
        self.client.post(APPLY, self.application(github="ada-l"))
        self.assertEqual(EducatorApplication.objects.get().name, "Ada Lovelace")
        stored = {field.name for field in EducatorApplication._meta.get_fields()}
        self.assertNotIn("github", stored)
        self.client.logout()
        privacy = self.client.get("/privacy/")
        self.assertContains(privacy, "your name, phone number, year of study and note")
        self.assertNotContains(privacy, "GitHub")

    def test_applying_again_for_the_same_course_updates_the_application(self):
        self.client.post(APPLY, self.application())
        first = EducatorApplication.objects.get()
        first.decide(EducatorApplication.Status.DECLINED)
        self.assertContains(self.client.get(APPLY, {"course": "rl"}), "You have applied")
        self.client.post(APPLY, self.application(note="I have more time now."))
        again = EducatorApplication.objects.get()  # still one row
        self.assertEqual(
            (again.pk, again.note, again.status), (first.pk, "I have more time now.", "pending")
        )
        self.assertIsNone(again.decided_at)

    def test_a_course_that_is_taken_or_closed_cannot_be_applied_for(self):
        for series in ("aai", "nlp", "nothing"):
            with self.subTest(series=series):
                answer = self.client.post(APPLY, self.application(series=series))
                self.assertEqual(answer.status_code, 200)
        self.assertFalse(EducatorApplication.objects.exists())


class EducatorTests(DeskTestCase):
    def setUp(self):
        super().setUp()
        Educator.objects.create(user=self.ada, series="rl")
        self.ask = Request.objects.create(
            user=self.bob, kind="content", series="rl", message="Lecture 5 is missing."
        )
        Request.objects.create(user=self.bob, kind="idea", series="rl", message="Make it purple.")
        Request.objects.create(user=self.bob, kind="bug", series="aai", message="AAI typo.")

    def test_an_educator_gets_a_dashboard_and_a_page_for_the_course(self):
        """Educators in the menu is their dashboard: the course as a card that leads to
        its own page. Everything about working on that course is on that page."""
        board = self.client.get(EDUCATORS)
        self.assertTemplateUsed(board, "desk/educators.html")
        self.assertContains(board, "The courses you write")
        self.assertContains(board, 'href="/educators/courses/rl/"')
        self.assertContains(board, 'action="/educators/courses/rl/files.zip"')
        self.assertContains(board, settings.EDUCATOR_KIT_URL)
        # The form that takes work is on the course's page, not here.
        self.assertNotContains(board, 'action="/educators/courses/rl/hand-in/"')

        page = self.client.get(WORK)
        self.assertContains(page, "You write this course")
        self.assertContains(page, "uv run tools/unpack.py rl.zip")
        self.assertContains(page, "Update the CMS for this course: rl")
        self.assertContains(page, "uv run tools/pack.py rl")
        self.assertContains(page, settings.EDUCATOR_KIT_URL)
        self.assertContains(page, 'action="/educators/courses/rl/files.zip"')
        self.assertContains(page, 'action="/educators/courses/rl/hand-in/"')
        # Their own course is no longer among those looking for someone.
        self.assertEqual(board.context["seeking"], 0)
        self.assertEqual(self.client.get(OPEN).context["seeking"], [])
        # Others see none of it.
        self.client.force_login(self.bob)
        other = self.client.get(EDUCATORS)
        self.assertTemplateUsed(other, "desk/become.html")
        self.assertNotContains(other, "The courses you write")
        self.assertNotContains(other, settings.EDUCATOR_KIT_URL)
        self.assertEqual(self.client.get(WORK).status_code, 404)

    def test_the_dashboard_says_what_is_waiting_most_pressing_first(self):
        """With several courses, the first thing an educator needs is where to look: a
        question someone is waiting on, then a copy the site has moved away from, then a
        course that is still empty."""
        Educator.objects.create(user=self.ada, series="aai", synced_version="an-old-one")
        with tempfile.TemporaryDirectory() as scratch:
            for slug in ("rl", "aai"):
                (Path(scratch) / slug).mkdir()
                (Path(scratch) / slug / "course.yaml").write_text(f"title: {slug}\n", "utf-8")
            with override_settings(CONTENT_ROOTS=[Path(scratch)]):
                board = self.client.get(EDUCATORS)
                page = self.client.get("/educators/courses/aai/")
        waiting = [(row["course"].slug, row["text"]) for row in board.context["waiting"]]
        self.assertEqual(
            waiting,
            [
                ("aai", "1 request to answer"),
                ("rl", "1 request to answer"),
                ("aai", "Your copy is not what the site has"),
            ],
        )
        self.assertContains(board, 'href="/educators/courses/aai/#asked"')
        self.assertContains(board, 'href="/educators/courses/aai/#files"')
        # Two cards, in the order of the dashboard, each saying how its copy stands.
        self.assertEqual([c.slug for c in board.context["desks"]], ["aai", "rl"])
        self.assertContains(board, 'data-copy="differs"')
        self.assertContains(board, 'data-copy="none"')
        self.assertContains(page, "Not what the site has.")
        # What was asked is read on the course's page, not on the dashboard.
        self.assertNotContains(board, "Lecture 5 is missing.")

    def test_nothing_waiting_is_said_too(self):
        Request.objects.all().delete()
        Course.objects.filter(slug="rl").update(content_hash="x")
        with mock.patch("desk.views.has_content", return_value=True):
            board = self.client.get(EDUCATORS)
        self.assertEqual(board.context["waiting"], [])
        self.assertContains(board, "Nothing is waiting")

    def test_someone_who_writes_a_course_can_still_take_another(self):
        board = self.client.get(EDUCATORS)
        self.assertNotContains(board, "Write another course")  # nothing is left to take
        course("cv", "Computer Vision", semester=6)
        board = self.client.get(EDUCATORS)
        self.assertContains(board, "1 course has nobody writing it yet")
        self.assertContains(board, 'href="/educators/open/"')
        page = self.client.get(OPEN)
        self.assertTemplateUsed(page, "desk/become.html")
        self.assertContains(page, "Write another course")
        self.assertContains(page, "Computer Vision")
        self.assertNotContains(page, "Reinforcement Learning")  # already theirs

    def test_an_educator_of_a_course_students_cannot_see_yet_still_has_it(self):
        Educator.objects.create(user=self.ada, series="nlp")
        page = self.client.get(EDUCATORS)
        self.assertContains(page, "Natural Language Processing")
        self.assertContains(page, 'action="/educators/courses/nlp/files.zip"')
        self.assertContains(self.client.get("/educators/courses/nlp/"), "You write this course")

    def test_they_can_download_the_files_of_their_course_and_only_theirs(self):
        """The zip is built from the course's folder, so this needs one on disk."""
        with tempfile.TemporaryDirectory() as scratch:
            folder = Path(scratch) / "rl"
            (folder / "content" / "decks").mkdir(parents=True)
            (folder / "source").mkdir()
            (folder / "course.yaml").write_text("title: Reinforcement Learning\n", "utf-8")
            (folder / "content" / "decks" / "mdp.yaml").write_text("title: MDPs\n", "utf-8")
            (folder / "source" / "L1.pdf").write_bytes(b"%PDF")
            with override_settings(CONTENT_ROOTS=[Path(scratch)]):
                answer = self.client.post("/educators/courses/rl/files.zip")
                self.assertEqual(answer.status_code, 200)
                self.assertEqual(answer["Content-Type"], "application/zip")
                self.assertIn('filename="rl.zip"', answer["Content-Disposition"])
                with zipfile.ZipFile(io.BytesIO(answer.content)) as archive:
                    self.assertEqual(
                        sorted(archive.namelist()),
                        ["rl/content/decks/mdp.yaml", "rl/course.yaml"],
                    )
                # Another course is not theirs, and another person gets nothing at all.
                self.assertEqual(
                    self.client.post("/educators/courses/aai/files.zip").status_code, 404
                )
                self.client.force_login(self.bob)
                self.assertEqual(
                    self.client.post("/educators/courses/rl/files.zip").status_code, 404
                )
                self.client.force_login(self.admin)
                self.assertEqual(
                    self.client.post("/educators/courses/rl/files.zip").status_code, 200
                )

    def test_they_see_what_was_asked_about_it_but_not_by_whom(self):
        page = self.client.get(WORK)
        self.assertContains(page, "Lecture 5 is missing.")
        self.assertNotContains(page, "Make it purple.")  # an idea for the site is the owner's
        self.assertNotContains(page, "AAI typo.")  # another course
        self.assertNotContains(page, "bob")

    def test_they_can_answer_it_and_nobody_else_can(self):
        done = reverse("desk:resolve", args=[self.ask.pk])
        self.client.force_login(self.bob)
        self.assertEqual(self.client.post(done, {"answer": "No."}).status_code, 404)
        self.client.force_login(self.ada)
        self.assertEqual(self.client.get(done).status_code, 405)  # changing things needs a POST
        answer = self.client.post(done, {"answer": "Added today."})
        self.assertRedirects(answer, f"{WORK}#asked", fetch_redirect_response=False)
        self.ask.refresh_from_db()
        self.assertEqual((self.ask.status, self.ask.answer), ("done", "Added today."))
        page = self.client.get(WORK)
        self.assertNotContains(page, "Lecture 5 is missing.")
        self.assertContains(page, "Nothing is open.")
        # The person who asked reads the answer on their own page.
        self.client.force_login(self.bob)
        self.assertContains(self.client.get(ASK), "Added today.")

    def test_a_request_about_another_course_is_not_theirs_to_answer(self):
        other = Request.objects.get(series="aai")
        answer = self.client.post(reverse("desk:resolve", args=[other.pk]), {"answer": "Done."})
        self.assertEqual(answer.status_code, 404)
        other.refresh_from_db()
        self.assertEqual(other.status, "new")


class SwitchTests(DeskTestCase):
    """Each question starts from the course's own file and is overridden by the owner's
    switch, in both directions."""

    def test_the_course_file_decides_until_the_owner_does(self):
        gate = Switches()
        self.assertEqual(
            [gate.is_open(c) for c in (self.rl, self.aai, self.nlp)], [True, True, False]
        )
        self.assertEqual(
            [gate.has_educator(c) for c in (self.rl, self.aai, self.nlp)], [False, True, False]
        )
        CourseSetting.objects.create(series="nlp", enabled=True)
        CourseSetting.objects.create(series="rl", enabled=False)
        CourseSetting.objects.create(series="aai", has_educator=False)
        gate = Switches()
        self.assertEqual(
            [gate.is_open(c) for c in (self.rl, self.aai, self.nlp)], [False, True, True]
        )
        self.assertFalse(gate.has_educator(self.aai))

    def test_an_accepted_educator_counts_as_someone_writing_it(self):
        Educator.objects.create(user=self.ada, series="rl")
        self.assertTrue(Switches().has_educator(self.rl))

    def test_a_page_asks_the_database_once_however_many_courses_it_lists(self):
        gate = Switches()
        with self.assertNumQueries(2):  # the switches, then the educators
            for _ in range(5):
                for one in (self.rl, self.aai, self.nlp):
                    gate.is_open(one)
                    gate.has_educator(one)


class ClosedCourseTests(DeskTestCase):
    """A course the owner has not opened does not exist for students."""

    def test_it_is_nowhere_a_student_looks(self):
        Enrollment.objects.create(user=self.ada, series="rl")
        self.assertEqual(self.client.get("/courses/nlp/").status_code, 404)
        choose = self.client.get("/my-courses/")
        offered = [c.slug for group in choose.context["groups"] for c in group["courses"]]
        self.assertCountEqual(offered, ["rl", "aai"])
        self.assertNotContains(self.client.get("/"), "Natural Language Processing")
        self.assertNotContains(self.client.get("/search/"), "Natural Language Processing")
        # It cannot be put on a dashboard by posting its name either.
        self.client.post("/my-courses/change/", {"series": "nlp", "action": "add"})
        self.assertEqual(Enrollment.objects.series_of(self.ada), {"rl"})

    def test_the_owner_can_look_at_it_and_is_told_it_is_closed(self):
        self.client.force_login(self.admin)
        page = self.client.get("/courses/nlp/")
        self.assertContains(page, "Students cannot see this course yet")
        self.assertNotContains(self.client.get("/courses/rl/"), "Students cannot see this course")

    def test_opening_it_in_the_admin_makes_it_appear(self):
        self.client.force_login(self.admin)
        courses = reverse("admin:catalog_course_changelist")
        self.assertContains(self.client.get(courses), "No (course file)")
        answer = self.client.post(
            courses, {"action": "open_course", "_selected_action": [self.nlp.pk]}
        )
        self.assertRedirects(answer, courses)
        self.assertTrue(CourseSetting.objects.get(series="nlp").enabled)
        self.assertContains(self.client.get(courses), "Yes (set here)")
        self.client.force_login(self.ada)
        self.assertEqual(self.client.get("/courses/nlp/").status_code, 200)

    def test_the_switches_survive_a_rebuilt_course_table(self):
        CourseSetting.objects.create(series="nlp", enabled=True)
        Course.objects.all().delete()  # what a sync from scratch does
        again = course("nlp", "Natural Language Processing", enabled=False)
        self.assertTrue(Switches().is_open(again))


class CoursePageTests(DeskTestCase):
    """What a course's own page says when it has nothing in it yet."""

    def test_an_unwritten_course_can_be_asked_for_or_taken_on(self):
        page = self.client.get("/courses/rl/")
        self.assertContains(page, "No content yet")
        self.assertContains(page, "Nobody is writing this course yet")
        self.assertContains(page, "/ask/?course=rl&amp;kind=content")
        self.assertContains(page, "/educators/apply/?course=rl")

    def test_a_course_someone_writes_only_offers_to_ask(self):
        page = self.client.get("/courses/aai/")
        self.assertContains(page, "This course is being written")
        self.assertContains(page, "/ask/?course=aai&amp;kind=content")
        self.assertNotContains(page, "Become its educator")
        # The same once an applicant has been accepted for the other one.
        Educator.objects.create(user=self.bob, series="rl")
        self.assertNotContains(self.client.get("/courses/rl/"), "Become its educator")

    def test_an_earlier_year_asks_for_nothing(self):
        course("rl-2027", "Reinforcement Learning", series="rl", year="2027-28", semester=5)
        Course.objects.filter(slug="rl").update(year="2026-27")
        old = self.client.get("/courses/rl/")
        self.assertContains(old, "Nothing was written up for this year")
        self.assertNotContains(old, "Become its educator")
        self.assertContains(self.client.get("/courses/rl-2027/"), "Become its educator")

    def test_the_menu_carries_the_way_to_ask_from_every_page(self):
        page = self.client.get("/courses/rl/")
        self.assertContains(page, "/ask/?course=rl&amp;from=/courses/rl/")
        self.assertContains(self.client.get("/settings/"), "/ask/?from=/settings/")
        self.assertContains(page, 'href="/educators/"')


class DeskAdminTests(DeskTestCase):
    def setUp(self):
        super().setUp()
        self.client.post(APPLY, self.application())
        self.offer = EducatorApplication.objects.get()
        self.ask = Request.objects.create(
            user=self.ada, kind="bug", series="rl", message="Card 4 is wrong.", page="/courses/rl/"
        )
        self.client.force_login(self.admin)
        self.OFFERS = reverse("admin:desk_educatorapplication_changelist")
        self.REQUESTS = reverse("admin:desk_request_changelist")

    def test_requests_and_applications_are_listed_with_their_course(self):
        requests = self.client.get(self.REQUESTS)
        self.assertContains(requests, "Card 4 is wrong.")
        self.assertContains(requests, "RL · Reinforcement Learning")
        offers = self.client.get(self.OFFERS)
        self.assertContains(offers, "+387 61 123 456")
        self.assertContains(offers, "Ada Lovelace")

    def test_a_request_is_answered_but_what_was_written_stays_as_it_was(self):
        page = reverse("admin:desk_request_change", args=[self.ask.pk])
        self.assertContains(self.client.get(page), "Card 4 is wrong.")
        self.client.post(page, {"status": "done", "answer": "Fixed.", "message": "Tampered."})
        self.ask.refresh_from_db()
        self.assertEqual(
            (self.ask.status, self.ask.answer, self.ask.message),
            ("done", "Fixed.", "Card 4 is wrong."),
        )
        self.assertEqual(self.client.get(reverse("admin:desk_request_add")).status_code, 403)

    def test_requests_can_be_closed_from_the_list(self):
        self.client.post(
            self.REQUESTS, {"action": "mark_declined", "_selected_action": [self.ask.pk]}
        )
        self.ask.refresh_from_db()
        self.assertEqual(self.ask.status, "declined")

    def test_accepting_an_application_makes_the_person_the_educator(self):
        chosen = {"action": "accept", "_selected_action": [self.offer.pk]}
        self.assertRedirects(self.client.post(self.OFFERS, chosen), self.OFFERS)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.status, "accepted")
        self.assertIsNotNone(self.offer.decided_at)
        self.assertTrue(Educator.objects.filter(user=self.ada, series="rl").exists())
        # Twice is the same as once.
        self.client.post(self.OFFERS, chosen)
        self.assertEqual(Educator.objects.count(), 1)

        self.client.force_login(self.ada)
        page = self.client.get(EDUCATORS)
        self.assertContains(page, "The courses you write")
        self.assertContains(page, 'href="/educators/courses/rl/"')
        # The application has become the course: it is not listed as one any more.
        self.assertNotContains(page, "Your applications")
        self.assertContains(self.client.get(WORK), "You write this course")
        self.assertNotContains(self.client.get("/courses/rl/"), "Become its educator")

    def test_taking_an_acceptance_back_takes_the_role_back(self):
        self.offer.decide(EducatorApplication.Status.ACCEPTED)
        self.client.post(self.OFFERS, {"action": "decline", "_selected_action": [self.offer.pk]})
        self.assertFalse(Educator.objects.exists())
        # The same through the form of one application.
        page = reverse("admin:desk_educatorapplication_change", args=[self.offer.pk])
        self.client.post(page, {"status": "accepted"})
        self.assertTrue(Educator.objects.filter(user=self.ada, series="rl").exists())
        self.client.post(page, {"status": "declined", "phone": "tampered"})
        self.offer.refresh_from_db()
        self.assertEqual((self.offer.status, self.offer.phone), ("declined", "+387 61 123 456"))
        self.assertFalse(Educator.objects.exists())

    def test_an_educator_can_be_added_by_hand_for_a_course_that_exists(self):
        add = reverse("admin:desk_educator_add")
        self.assertContains(self.client.get(add), "RL · Reinforcement Learning")
        self.client.post(add, {"user": self.bob.pk, "series": "nowhere"})
        self.assertFalse(Educator.objects.exists())
        self.client.post(add, {"user": self.bob.pk, "series": "aai"})
        self.assertTrue(Educator.objects.filter(user=self.bob, series="aai").exists())

    def test_the_course_list_says_who_writes_what_and_switches_it(self):
        courses = reverse("admin:catalog_course_changelist")
        page = self.client.get(courses)
        self.assertContains(page, "Nobody yet")
        self.assertContains(page, "Someone (course file)")
        self.offer.decide(EducatorApplication.Status.ACCEPTED)
        self.assertContains(self.client.get(courses), "ada@example.test")

        self.client.post(courses, {"action": "needs_writer", "_selected_action": [self.aai.pk]})
        self.assertFalse(CourseSetting.objects.get(series="aai").has_educator)
        self.assertContains(self.client.get(courses), "Nobody (set here)")
        self.client.post(courses, {"action": "follow_file", "_selected_action": [self.aai.pk]})
        self.assertFalse(CourseSetting.objects.filter(series="aai").exists())

    def test_deleting_a_person_takes_what_they_sent_along(self):
        Educator.objects.create(user=self.ada, series="rl")
        people = reverse("admin:auth_user_changelist")
        chosen = {"action": "delete_selected", "_selected_action": [self.ada.pk]}
        self.assertContains(self.client.post(people, chosen), "Are you sure")
        self.client.post(people, {**chosen, "post": "yes"})
        self.assertFalse(User.objects.filter(pk=self.ada.pk).exists())
        for model in (Request, EducatorApplication, Educator):
            self.assertFalse(model.objects.exists(), model.__name__)

    def test_none_of_it_is_open_to_other_people(self):
        self.client.force_login(self.ada)
        for path in (self.REQUESTS, self.OFFERS, reverse("admin:desk_educator_changelist")):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 302)
        self.client.post(self.OFFERS, {"action": "accept", "_selected_action": [self.offer.pk]})
        self.assertFalse(Educator.objects.exists())
