"""The validation gate: each test plants one mistake an author could plausibly make and
checks that sync refuses it, names the right file and line, and says how to fix it."""

from unittest import skipUnless

from ingest import mathcheck

from .base import CourseTestCase

COURSE = "course.yaml"
LECTURE = "content/lectures/01-least-squares.md"
DECK = "content/decks/least-squares.yaml"
OTHER_DECK = "content/decks/gradient-descent.yaml"
PROBLEMS = "content/problems/fitting-practice.yaml"
MIDTERM = "content/exams/midterm/assessment.yaml"
FINAL = "content/exams/final/assessment.yaml"
FORMULAS = "content/reference/formulas.yaml"


class YamlMistakes(CourseTestCase):
    def test_backslash_in_double_quotes(self):
        self.edit(
            DECK, "    q: |-\n      State the normal equations.", '    q: "State $\\\\theta$"'
        )
        issue = self.assertProblem(
            self.check(),
            "double-quoted text contains a backslash",
            file=DECK,
            line=self.line_of(DECK, 'q: "State'),
        )
        self.assertIn("block scalar", issue.hint)
        self.assertEqual(issue.where, "cards[1].q")

    def test_duplicate_key(self):
        self.edit(
            DECK,
            "    hy: true\n    q: |-\n      State",
            "    hy: true\n    hy: false\n    q: |-\n      State",
        )
        issue = self.assertProblem(self.check(), "appears twice", file=DECK)
        self.assertEqual(issue.line, self.line_of(DECK, "hy: false"))

    def test_broken_indentation(self):
        self.edit(DECK, "cards:\n  - id: lsq-loss", "cards:\n  - id: lsq-loss\n   bad: indent")
        self.assertProblem(self.check(), "not valid YAML", file=DECK)

    def test_anchor_and_alias(self):
        self.edit(DECK, "topic: lsq", "topic: &t lsq")
        self.assertProblem(self.check(), "anchors and aliases", file=DECK)

    def test_number_where_text_is_expected(self):
        self.edit(DECK, "title: Least squares", "title: 2026")
        issue = self.assertProblem(self.check(), "must be text", file=DECK)
        self.assertIn('"2026"', issue.hint)

    def test_yes_is_read_as_a_boolean(self):
        self.edit(FORMULAS, "name: Loss", "name: yes")
        issue = self.assertProblem(self.check(), "YAML read `yes` as a true/false", file=FORMULAS)
        self.assertIn('"yes"', issue.hint)


class ContractMistakes(CourseTestCase):
    def test_unknown_field_suggests_the_right_one(self):
        self.edit(PROBLEMS, "    answer: |-\n      $\\hat y", "    answers: |-\n      $\\hat y")
        issue = self.assertProblem(self.check(), "unknown field `answers`", file=PROBLEMS)
        self.assertIn("`answer`", issue.hint)
        self.assertEqual(issue.line, self.line_of(PROBLEMS, "answers: |-"))

    def test_missing_required_field(self):
        self.edit(DECK, "title: Least squares\n", "")
        self.assertProblem(self.check(), "`title` is required", file=DECK)

    def test_card_without_an_answer(self):
        self.edit(
            DECK,
            "    a: |-\n      When the columns of $X$ are **linearly independent**. "
            "Then $X^\\top X$ is invertible.\n",
            "",
        )
        issue = self.assertProblem(self.check(), "a card needs `q` and `a`", file=DECK)
        self.assertEqual(issue.where, "cards[4]")

    def test_cloze_without_a_blank(self):
        self.edit(DECK, "{{vertical}}", "vertical")
        self.edit(DECK, "{{$r_i = y_i - \\hat y_i$}}", "$r_i = y_i - \\hat y_i$")
        self.assertProblem(self.check(), "has no {{blank}}", file=DECK)

    def test_mcq_without_a_correct_choice(self):
        self.edit(
            PROBLEMS,
            "      - text: The loss grows without bound.\n        correct: true\n",
            "      - text: The loss grows without bound.\n",
        )
        self.assertProblem(self.check(), "exactly one choice", file=PROBLEMS)

    def test_open_question_without_a_solution(self):
        self.write(
            "content/problems/empty.yaml",
            "title: Empty\nquestions:\n  - id: empty-1\n    q: |-\n      Explain.\n",
        )
        self.assertProblem(self.check(), "needs a `solution`", file="content/problems/empty.yaml")

    def test_invalid_id(self):
        self.edit(DECK, "id: lsq-loss", "id: LSQ_Loss")
        issue = self.assertProblem(self.check(), "not a valid id", file=DECK)
        self.assertIn("lowercase", issue.hint)

    def test_missing_front_matter(self):
        self.write("content/guides/bare.md", "## No front matter\n\nText.\n")
        self.assertProblem(
            self.check(), "must start with front matter", file="content/guides/bare.md"
        )

    def test_bad_file_name(self):
        self.write("content/guides/My Guide.md", "---\ntitle: X\n---\nText.\n")
        self.assertProblem(self.check(), "cannot be used as an address")

    def test_file_in_an_unknown_place_is_a_warning(self):
        self.write("content/notes.txt", "stray")
        report = self.check()
        self.assertProblem(report, "not in a place the site reads", level="warning")
        self.assertTrue(report.ok)


class CrossReferenceMistakes(CourseTestCase):
    def test_duplicate_id_across_files(self):
        self.edit(DECK, "id: lsq-loss", "id: gd-update")
        issue = self.assertProblem(self.check(), "id `gd-update` is already used", file=DECK)
        self.assertIn(OTHER_DECK, issue.message)

    def test_id_shared_by_a_card_and_a_formula(self):
        self.edit(FORMULAS, "id: f-loss", "id: lsq-loss")
        self.assertProblem(self.check(), "id `lsq-loss` is already used", file=FORMULAS)

    def test_unknown_topic(self):
        self.edit(DECK, "topic: lsq", "topic: lsqq")
        issue = self.assertProblem(self.check(), "no topic named `lsqq`", file=DECK)
        self.assertIn("`lsq`", issue.hint)

    def test_unknown_lecture_on_a_deck(self):
        self.edit(DECK, "lecture: 01-least-squares", "lecture: 01-least-square")
        issue = self.assertProblem(self.check(), "no lecture named", file=DECK)
        self.assertIn("01-least-squares", issue.hint)

    def test_broken_link_in_markdown(self):
        self.edit(LECTURE, "[the deck](deck:least-squares)", "[the deck](deck:least-square)")
        issue = self.assertProblem(self.check(), "no deck named `least-square`", file=LECTURE)
        self.assertEqual(issue.line, self.line_of(LECTURE, "deck:least-square"))
        self.assertIn("`least-squares`", issue.hint)

    def test_relative_file_link_is_rejected(self):
        self.edit(
            LECTURE, "[the deck](deck:least-squares)", "[the deck](../decks/least-squares.yaml)"
        )
        issue = self.assertProblem(self.check(), "is not a link the site understands", file=LECTURE)
        self.assertIn("lecture:05-name", issue.hint)

    def test_broken_link_in_a_plan(self):
        self.edit(MIDTERM, '"card:lsq-derive"]', '"card:lsq-derived"]')
        issue = self.assertProblem(self.check(), "no card named `lsq-derived`", file=MIDTERM)
        self.assertEqual(issue.where, "plan.phases[0].tasks[0].links[1]")

    def test_question_anchor_must_be_in_that_set(self):
        self.edit(LECTURE, "problems:fitting-practice#fit-p1", "problems:fitting-practice#mid25-q1")
        self.assertProblem(self.check(), "no question in `fitting-practice`", file=LECTURE)

    def test_scope_with_unknown_lecture_number(self):
        self.edit(FINAL, "lectures: [2]", "lectures: [2, 9]")
        issue = self.assertProblem(self.check(), "no lecture number 9", file=FINAL)
        self.assertIn("[1, 2]", issue.hint)

    def test_exam_cannot_include_itself(self):
        self.edit(FINAL, "scope:\n  lectures: [2]", "includes: [comprehensive]")
        self.assertProblem(self.check(), "includes itself")

    def test_exam_folder_needs_an_assessment_file(self):
        (self.course / FINAL).unlink()
        self.write(
            "content/exams/final/mock.yaml",
            "title: M\nkind: mock\nquestions:\n  - id: m1\n    q: Q\n    answer: A\n",
        )
        self.assertProblem(self.check(), "has no assessment.yaml")

    def test_missing_image(self):
        self.edit(LECTURE, "assets/residuals.svg", "assets/missing.svg")
        self.assertProblem(self.check(), "image not found", file=LECTURE)

    def test_image_outside_the_course(self):
        self.edit(LECTURE, "assets/residuals.svg", "../../../../../README.md")
        self.assertProblem(self.check(), "leaves the course content folder", file=LECTURE)


class MarkdownMistakes(CourseTestCase):
    def test_raw_html(self):
        self.edit(LECTURE, "The two numbers", "The <b>two</b> numbers")
        issue = self.assertProblem(self.check(), "raw HTML", file=LECTURE)
        self.assertEqual(issue.line, self.line_of(LECTURE, "<b>two</b>"))

    def test_top_level_heading(self):
        self.edit(LECTURE, "## The model", "# The model")
        self.assertProblem(
            self.check(), "a `#` heading", file=LECTURE, line=self.line_of(LECTURE, "# The model")
        )

    def test_unknown_callout(self):
        self.edit(LECTURE, ":::pitfall", ":::danger")
        issue = self.assertProblem(self.check(), "`:::danger` is not a callout", file=LECTURE)
        self.assertIn("pitfall", issue.hint)

    def test_unbalanced_braces_in_maths(self):
        self.edit(DECK, "$$X^\\top X\\, w = X^\\top y$$", "$$X^{\\top X\\, w = X^\\top y$$")
        issue = self.assertProblem(self.check(), "braces are unbalanced", file=DECK)
        self.assertEqual(issue.line, self.line_of(DECK, "X^{\\top"))

    def test_unclosed_environment(self):
        self.edit(LECTURE, "\\end{pmatrix}, \\qquad", ", \\qquad")
        self.assertProblem(self.check(), "is never closed", file=LECTURE)

    @skipUnless(mathcheck.node_available(), "Node.js is needed for the KaTeX check")
    def test_misspelled_command_is_caught_by_katex(self):
        self.edit(FORMULAS, "\\frac{2}{n} X^\\top (Xw - y)", "\\fraq{2}{n} X^\\top (Xw - y)")
        issue = self.assertProblem(
            self.check(), "Undefined control sequence: \\fraq", file=FORMULAS
        )
        self.assertEqual(issue.where, "sections[1].rows[1].formula")
        self.assertEqual(issue.line, self.line_of(FORMULAS, "\\fraq"))

    def test_stray_dollar_is_a_warning(self):
        self.edit(LECTURE, "The two numbers", "The cost is 5$x and the two numbers")
        self.assertProblem(
            self.check(), "`$` was left as plain text", file=LECTURE, level="warning"
        )
