"""The happy path: the example course imports, and re-importing behaves."""

from datetime import timedelta

from django.utils import timezone

from catalog.models import Assessment, Card, Course, Deck, Document, Hook, Question

from .base import CourseTestCase

LECTURE = "content/lectures/01-least-squares.md"
DECK = "content/decks/least-squares.yaml"
OTHER_DECK = "content/decks/gradient-descent.yaml"


class ExampleCourseTests(CourseTestCase):
    def test_example_course_is_valid(self):
        report = self.check()
        self.assertEqual(report.status, "checked", msg=report.format())
        self.assertEqual(report.issues, [], msg=report.format())
        self.assertFalse(Course.objects.exists(), "--check must not write to the database")

    def test_sync_loads_every_content_type(self):
        report = self.sync()
        self.assertEqual(report.status, "synced", msg=report.format())
        course = Course.objects.get(slug="example")
        self.assertEqual(course.hue, 200)
        self.assertEqual(list(course.topics.values_list("key", flat=True)), ["lsq", "gd"])
        kinds = set(course.documents.values_list("kind", flat=True))
        self.assertEqual(kinds, {"lecture", "lab", "homework", "guide", "sheet"})
        self.assertEqual(course.decks.count(), 2)
        self.assertEqual(
            set(course.cards.values_list("kind", flat=True)), {"basic", "steps", "cloze"}
        )
        self.assertEqual(
            set(course.questions.values_list("kind", flat=True)), {"open", "mcq", "multi", "tf"}
        )
        self.assertEqual(
            set(course.questionsets.values_list("kind", flat=True)), {"practice", "past", "mock"}
        )
        self.assertEqual(course.formulas.count(), 6)
        self.assertEqual(course.terms.count(), 4)
        self.assertEqual(course.palaces.get().loci.count(), 4)

    def test_markdown_is_rendered_once_at_sync(self):
        self.sync()
        lecture = Document.objects.get(slug="01-least-squares")
        self.assertIn('<span class="math inline">', lecture.body_html)
        self.assertIn('class="callout callout--theorem"', lecture.body_html)
        self.assertIn('<pre class="code" data-lang="python">', lecture.body_html)
        self.assertEqual(lecture.toc[0], {"level": 2, "id": "the-model", "text": "The model"})
        self.assertEqual(len(lecture.takeaways), 3)
        self.assertGreater(lecture.reading_minutes, 0)

    def test_references_become_real_urls_with_labels(self):
        self.sync()
        html = Document.objects.get(slug="01-least-squares").body_html
        self.assertIn('href="/courses/example/lectures/02-gradient-descent/"', html)
        self.assertIn(">Gradient descent</a>", html)  # [](lecture:…) took the target's title
        self.assertIn('href="/courses/example/problems/fitting-practice/#fit-p1"', html)
        self.assertNotIn("lecture:02", html)

    def test_images_are_copied_to_media(self):
        self.sync()
        html = Document.objects.get(slug="01-least-squares").body_html
        self.assertRegex(html, r'<img src="/media/courses/example/[0-9a-f]{16}\.svg"')
        copied = list((self.tmp / "media" / "courses" / "example").iterdir())
        self.assertEqual(len(copied), 1)

    def test_exam_scope_is_derived(self):
        self.sync()
        topics = {
            exam.slug: list(exam.topics.values_list("key", flat=True))
            for exam in Assessment.objects.all()
        }
        self.assertEqual(topics["midterm"], ["lsq"])  # from lecture 1's topics
        self.assertEqual(topics["final"], ["gd"])
        self.assertEqual(topics["comprehensive"], ["lsq", "gd"])  # union via `includes`
        midterm = Assessment.objects.get(slug="midterm")
        self.assertEqual({p.kind for p in midterm.papers.all()}, {"past", "mock"})
        link = midterm.plan["phases"][0]["tasks"][0]["links"][0]
        self.assertEqual(link["url"], "/courses/example/cards/least-squares/")

    def test_card_hooks_are_collected(self):
        self.sync()
        hook = Hook.objects.get(key="lsq-normal-hook")
        self.assertEqual(hook.card.key, "lsq-normal")
        self.assertEqual(Hook.objects.count(), 4)  # two in hooks.yaml, two on cards

    def test_points_are_summed(self):
        self.sync()
        question = Question.objects.get(key="fit-p1")
        self.assertEqual([part["label"] for part in question.parts], ["(a)", "(b)", "(c)"])
        self.assertEqual(question.question_set.total_points, 22)


class ResyncTests(CourseTestCase):
    def test_unchanged_course_is_skipped(self):
        self.sync()
        self.assertEqual(self.sync().status, "unchanged")
        self.assertEqual(self.sync(force=True).status, "synced")

    def test_unchanged_sync_still_records_when_it_ran(self):
        """A file saved again with the same bytes is not re-imported, but `synced_at` moves,
        because the site compares it with file times to say "files changed"."""
        self.sync()
        an_hour_ago = timezone.now() - timedelta(hours=1)
        Course.objects.update(synced_at=an_hour_ago)
        self.assertEqual(self.sync().status, "unchanged")
        self.assertGreater(Course.objects.get().synced_at, an_hour_ago)

    def test_primary_keys_survive_a_resync(self):
        """Progress will one day point at cards by foreign key; a re-import must not
        recreate rows."""
        self.sync()
        before = dict(Card.objects.values_list("key", "pk"))
        self.edit(DECK, "State the normal equations.", "Write down the normal equations.")
        self.assertEqual(self.sync().status, "synced")
        self.assertEqual(dict(Card.objects.values_list("key", "pk")), before)
        self.assertIn("Write down", Card.objects.get(key="lsq-normal").front_html)

    def test_card_keeps_its_row_when_moved_to_another_deck(self):
        self.sync()
        pk = Card.objects.get(key="lsq-unique").pk
        block = self.read(DECK)[self.read(DECK).index("  - id: lsq-unique") :]
        self.edit(DECK, block, "")
        self.append(OTHER_DECK, "\n" + block)
        report = self.sync()
        self.assertEqual(report.status, "synced", msg=report.format())
        moved = Card.objects.get(key="lsq-unique")
        self.assertEqual(moved.pk, pk)
        self.assertEqual(moved.deck.slug, "gradient-descent")

    def test_deleted_file_removes_its_rows(self):
        self.sync()
        (self.course / OTHER_DECK).unlink()
        # The midterm plan does not mention this deck, but the palace links one of its cards.
        self.edit("content/memory/palaces/gd-loop.yaml", '    refs: ["card:gd-update"]\n', "")
        report = self.sync()
        self.assertEqual(report.status, "synced", msg=report.format())
        self.assertFalse(Deck.objects.filter(slug="gradient-descent").exists())
        self.assertFalse(Card.objects.filter(key__startswith="gd-").exists())
        self.assertFalse(Hook.objects.filter(key="gd-update-hook").exists())

    def test_failed_sync_leaves_the_database_untouched(self):
        self.sync()
        self.edit(DECK, "title: Least squares", "title: Broken\nnonsense: 1")
        report = self.sync()
        self.assertEqual(report.status, "failed")
        self.assertEqual(Deck.objects.get(slug="least-squares").title, "Least squares")

    def test_changed_image_gets_a_new_url(self):
        self.sync()
        first = Document.objects.get(slug="01-least-squares").body_html
        image = self.course / "content/lectures/assets/residuals.svg"
        image.write_text(
            image.read_text(encoding="utf-8").replace("#3b6fd4", "#000000"), encoding="utf-8"
        )
        self.sync()
        second = Document.objects.get(slug="01-least-squares").body_html
        self.assertNotEqual(first, second)
        self.assertEqual(len(list((self.tmp / "media/courses/example").iterdir())), 1)
