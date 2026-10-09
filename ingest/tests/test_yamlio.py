from django.test import SimpleTestCase

from ingest.report import Report
from ingest.yamlio import load_yaml, split_front_matter

SAMPLE = """\
title: Deck
cards:
  - id: one
    q: |-
      First line
      second line
    a: 'single \\quoted'
  - id: two
    q: plain \\text
"""


class YamlTests(SimpleTestCase):
    def load(self, text, **options):
        self.report = Report("test")
        return load_yaml(text, file="f.yaml", report=self.report, **options)

    def test_positions_of_values(self):
        loaded = self.load(SAMPLE)
        self.assertEqual(self.report.issues, [])
        self.assertEqual(loaded.line(("title",)), 1)
        self.assertEqual(loaded.line(("cards", 0, "id")), 3)
        self.assertEqual(loaded.line(("cards", 1, "q")), 9)

    def test_block_scalar_text_starts_on_the_next_line(self):
        loaded = self.load(SAMPLE)
        self.assertEqual(loaded.line(("cards", 0, "q")), 4)
        self.assertEqual(loaded.text_line(("cards", 0, "q")), 5)
        self.assertEqual(loaded.text_line(("cards", 0, "a")), 7)

    def test_unknown_path_falls_back_to_the_nearest_parent(self):
        loaded = self.load(SAMPLE)
        self.assertEqual(loaded.line(("cards", 1, "missing")), 8)

    def test_backslashes_are_literal_except_in_double_quotes(self):
        loaded = self.load(SAMPLE)
        self.assertEqual(loaded.data["cards"][0]["a"], "single \\quoted")
        self.assertEqual(loaded.data["cards"][1]["q"], "plain \\text")
        self.load('q: "a \\\\theta b"')
        self.assertEqual(len(self.report.errors), 1)

    def test_double_quotes_without_backslash_are_fine(self):
        self.load('links: ["deck:one", "card:two"]')
        self.assertEqual(self.report.issues, [])

    def test_line_offset_for_front_matter(self):
        loaded = self.load("title: X\ntitle: Y\n", line_offset=1)
        self.assertEqual(self.report.errors[0].line, 3)
        self.assertEqual(loaded.line(("title",)), 3)

    def test_merge_keys_are_rejected(self):
        self.load("a:\n  <<: {b: 1}\n")
        self.assertTrue(any("merge keys" in e.message for e in self.report.errors))

    def test_front_matter_split(self):
        front, body, line = split_front_matter("---\ntitle: X\n---\n\n## Heading\n")
        self.assertEqual(front, "title: X")
        self.assertEqual(body, "\n## Heading\n")
        self.assertEqual(line, 4)

    def test_no_front_matter(self):
        self.assertEqual(split_front_matter("## Heading\n")[0], None)
        self.assertEqual(split_front_matter("---\ntitle: never closed\n")[0], None)
