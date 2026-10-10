// Settings page: move progress between browsers, or clear it.

import { dayKey, download, manifests, plural } from "../lib/util.js";

export default () => ({
  confirm: null, // { title, body, run }

  get totals() {
    return this.$store.progress.totals();
  },
  courseStats(slug) {
    const course = manifests().find((m) => m.slug === slug);
    if (!course) return { graded: 0, total: 0 };
    const stats = this.$store.progress.stats(
      slug,
      course.cards.map((card) => card.id),
    );
    return { graded: stats.total - stats.unseen, total: stats.total };
  },

  exportFile() {
    download(`dsai-progress-${dayKey()}.json`, this.$store.progress.exportText());
    this.$store.ui.say("Progress exported");
  },
  importFile(event) {
    const file = event.target.files[0];
    event.target.value = "";
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const changed = this.$store.progress.importText(reader.result);
        this.$store.ui.say(changed ? `Merged ${plural(changed, "newer record")}` : "Nothing newer in that file");
      } catch (error) {
        this.$store.ui.say(error.message || "That file could not be read", 4000);
      }
    };
    reader.readAsText(file);
  },

  ask(title, body, run) {
    this.confirm = { title, body, run };
    this.$refs.confirm.showModal();
  },
  get where() {
    return this.$store.progress.account ? "your account and every device signed in to it" : "this browser";
  },
  resetCourse(slug, title) {
    this.ask(`Clear progress for ${title}?`, `Grades, ratings and attempts for this course are removed from ${this.where}. Export first if you want a copy.`, () =>
      this.$store.progress.reset(slug),
    );
  },
  resetAll() {
    this.ask("Clear all progress?", `Everything is removed from ${this.where}: grades, ratings, attempts and activity. Export first if you want a copy.`, () =>
      this.$store.progress.reset(),
    );
  },
  /** Before the account is deleted: drop this browser's copy, so nothing is left behind. */
  forget() {
    this.$store.progress.forgetLocal();
  },
  proceed() {
    this.confirm?.run();
    this.$refs.confirm.close();
    this.$store.ui.say("Cleared");
  },
});
