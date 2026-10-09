// A set of questions: a practice set, a past paper or a mock exam.
//
// Two modes over the same server-rendered questions:
//   study  solutions open on demand; choice questions are checked one at a time.
//   sit    a countdown runs, solutions stay hidden until you finish; then choice questions
//          are marked automatically (with negative marking) and you award yourself points
//          on the open ones. The result is saved as an attempt.

import { clock, readData } from "../lib/util.js";

export default () => ({
  course: "",
  slug: "",
  kind: "practice",
  mode: "study",
  phase: "idle", // sit mode: ready -> running -> marking -> done
  duration: null,
  negative: 0,
  questions: [],
  byId: {},
  picks: {}, // question id -> chosen choice indexes
  checked: {}, // study mode: choice question has been checked
  open: {}, // question/part id -> solution shown
  steps: {}, // question id -> steps revealed
  awarded: {}, // sit mode: points you gave yourself on open questions
  endsAt: 0,
  startedAt: 0,
  now: Date.now(),
  ticker: null,

  init() {
    const data = readData("paper-data");
    Object.assign(this, {
      course: data.course,
      slug: data.slug,
      kind: data.kind,
      duration: data.duration,
      negative: data.negative || 0,
      questions: data.questions,
    });
    this.byId = Object.fromEntries(data.questions.map((q) => [q.id, q]));
    this.setMode(data.mode);
  },

  setMode(mode) {
    clearInterval(this.ticker);
    this.mode = mode;
    this.phase = mode === "sit" ? "ready" : "idle";
    this.picks = {};
    this.checked = {};
    this.open = {};
    this.steps = {};
    this.awarded = {};
  },

  // ---- shared ------------------------------------------------------------------------
  get revealed() {
    return this.mode === "study" || this.phase === "marking" || this.phase === "done";
  },
  objective(id) {
    return this.byId[id].kind !== "open";
  },
  status(id) {
    return this.$store.progress.status(this.course, id);
  },
  selfGrade(id, s) {
    this.$store.progress.grade(this.course, id, this.status(id) === s ? 0 : s);
  },
  toggle(id) {
    this.open[id] = !this.open[id];
  },
  isOpen(id) {
    return Boolean(this.open[id]);
  },
  stepsShown(id) {
    return this.steps[id] || 0;
  },
  nextStep(id) {
    this.steps[id] = Math.min(this.byId[id].steps.length, this.stepsShown(id) + 1);
  },

  // ---- choice questions --------------------------------------------------------------
  /** For a true/false question the two "choices" are index 1 (true) and 0 (false). */
  correctSet(id) {
    const q = this.byId[id];
    if (q.kind === "tf") return [q.correct ? 1 : 0];
    return q.choices.flatMap((choice, index) => (choice.correct ? [index] : []));
  },
  locked(id) {
    if (this.mode === "study") return Boolean(this.checked[id]);
    return this.phase !== "running";
  },
  pick(id, index) {
    if (this.locked(id)) return;
    const current = this.picks[id] || [];
    if (this.byId[id].kind === "multi") {
      this.picks[id] = current.includes(index)
        ? current.filter((i) => i !== index)
        : [...current, index];
    } else {
      this.picks[id] = current.includes(index) ? [] : [index];
    }
  },
  picked(id, index) {
    return (this.picks[id] || []).includes(index);
  },
  answered(id) {
    return (this.picks[id] || []).length > 0;
  },
  shown(id) {
    return this.mode === "study" ? Boolean(this.checked[id]) : this.revealed;
  },
  /** How a choice should look once answers are shown. */
  verdict(id, index) {
    if (!this.shown(id)) return this.picked(id, index) ? "picked" : "";
    const right = this.correctSet(id).includes(index);
    if (right) return this.picked(id, index) ? "right" : "missed";
    return this.picked(id, index) ? "wrong" : "";
  },
  isRight(id) {
    const picks = [...(this.picks[id] || [])].sort();
    const correct = this.correctSet(id).sort();
    return picks.length === correct.length && picks.every((value, i) => value === correct[i]);
  },
  check(id) {
    if (!this.answered(id)) return;
    this.checked[id] = true;
    this.$store.progress.grade(this.course, id, this.isRight(id) ? 3 : 1);
  },
  retry(id) {
    this.checked[id] = false;
    this.picks[id] = [];
  },

  // ---- sitting a paper ---------------------------------------------------------------
  get remaining() {
    return Math.max(0, this.endsAt - this.now);
  },
  get clock() {
    return this.duration ? clock(this.remaining) : clock(this.now - this.startedAt);
  },
  get low() {
    return this.duration && this.remaining < 5 * 60_000;
  },
  start() {
    this.setMode("sit");
    this.phase = "running";
    this.startedAt = this.now = Date.now();
    this.endsAt = this.startedAt + (this.duration || 0) * 60_000;
    this.ticker = setInterval(() => {
      this.now = Date.now();
      if (this.duration && this.now >= this.endsAt) this.finish();
    }, 500);
    window.scrollTo({ top: 0 });
  },
  finish() {
    clearInterval(this.ticker);
    this.now = Date.now();
    this.phase = "marking";
    for (const q of this.questions) this.steps[q.id] = q.steps.length;
    this.$nextTick(() => window.scrollTo({ top: 0, behavior: "smooth" }));
  },
  points(id) {
    return this.byId[id].points || 0;
  },
  /** Points earned on one question, or null while an open one is still unmarked. */
  earned(id) {
    if (this.objective(id)) {
      if (!this.answered(id)) return 0;
      return this.isRight(id) ? this.points(id) : -this.negative;
    }
    return this.awarded[id] ?? null;
  },
  award(id, fraction) {
    this.awarded[id] = +(this.points(id) * fraction).toFixed(2);
  },
  get unmarked() {
    return this.questions.filter((q) => this.earned(q.id) === null).length;
  },
  get score() {
    return this.questions.reduce((sum, q) => sum + (this.earned(q.id) || 0), 0);
  },
  get max() {
    return this.questions.reduce((sum, q) => sum + this.points(q.id), 0);
  },
  get seconds() {
    return Math.round((this.now - this.startedAt) / 1000);
  },
  save() {
    for (const q of this.questions) {
      const share = this.points(q.id) ? (this.earned(q.id) || 0) / this.points(q.id) : 0;
      this.$store.progress.grade(this.course, q.id, share >= 0.8 ? 3 : share >= 0.4 ? 2 : 1, {
        count: false,
      });
    }
    this.$store.progress.addAttempt(this.course, this.slug, {
      score: +this.score.toFixed(2),
      max: this.max,
      seconds: this.seconds,
    });
    this.phase = "done";
    this.$store.ui.say("Attempt saved");
  },
  get attempts() {
    return [...this.$store.progress.attempts(this.course, this.slug)].reverse();
  },
  when(attempt) {
    return new Date(attempt.t).toLocaleDateString(undefined, {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  },
  took(attempt) {
    return `${Math.max(1, Math.round(attempt.seconds / 60))} min`;
  },
});
