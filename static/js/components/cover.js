// Cover-and-recall for reference tables (formulas, glossary, hooks).
//
// Re-reading a formula sheet feels productive and teaches little. With "Cover" on, the
// answer column is hidden: you say it, then click the row to check. Optionally grade the
// row, which feeds the same progress store as flashcards.

import { COURSE } from "../lib/util.js";

export default () => ({
  covered: false,
  shown: {},
  query: "",

  toggleCover() {
    this.covered = !this.covered;
    this.shown = {};
  },
  hidden(id) {
    return this.covered && !this.shown[id];
  },
  reveal(id) {
    if (this.covered) this.shown[id] = !this.shown[id];
  },
  status(id) {
    return this.$store.progress.status(COURSE, id);
  },
  mark(id, s) {
    this.$store.progress.grade(COURSE, id, this.status(id) === s ? 0 : s);
  },
  /** Client-side filter box: does this row's text contain the query? */
  match(text) {
    return !this.query || text.toLowerCase().includes(this.query.trim().toLowerCase());
  },
});
