// The flashcard player.
//
// A "deck" here is whatever the current filter selects from the cards the page was given.
// It is a snapshot: grading a card does not drop it from the list you are working through,
// so a run over "Weak" visits every weak card once even as they turn solid.

import { readData, shuffle, typing } from "../lib/util.js";

const FILTERS = [
  ["all", "All"],
  ["due", "Due"],
  ["unseen", "Unseen"],
  ["weak", "Weak"],
  ["missed", "Missed"],
  ["shaky", "Shaky"],
  ["solid", "Solid"],
  ["key", "Key"],
  ["steps", "Derivations"],
  ["cloze", "Cloze"],
];

const GRADES = [
  { s: 1, name: "Missed", hint: "nothing came", cls: "missed" },
  { s: 2, name: "Shaky", hint: "slow, or with a gap", cls: "shaky" },
  { s: 3, name: "Solid", hint: "came straight out", cls: "solid" },
];

export default () => ({
  course: "",
  mode: "deck",
  all: [],
  deck: [],
  index: 0,
  filter: "all",
  topic: null,
  topics: [],
  shuffled: false,
  revealed: false,
  stepsShown: 0,
  finished: false,
  session: { 1: 0, 2: 0, 3: 0 },
  grades: GRADES,

  init() {
    const data = readData("player-data");
    this.course = data.course;
    this.mode = data.mode;
    this.all = data.cards;
    this.filter = FILTERS.some(([key]) => key === data.filter) ? data.filter : "all";
    this.topics = (readData("course-manifest")?.topics || []).filter((topic) =>
      this.all.some((card) => card.topic === topic.key),
    );
    this.build();
    if (data.focus) {
      if (!this.deck.some((card) => card.id === data.focus)) {
        this.filter = "all";
        this.build();
      }
      this.index = Math.max(0, this.deck.findIndex((card) => card.id === data.focus));
    }
  },

  // ---- what is in the deck -----------------------------------------------------------
  status(card) {
    return this.$store.progress.status(this.course, card.id);
  },
  matches(card, filter) {
    const progress = this.$store.progress;
    const s = this.status(card);
    switch (filter) {
      case "due":
        return progress.isDue(progress.record(this.course, card.id));
      case "unseen":
        return s === 0;
      case "weak":
        return s === 1 || s === 2;
      case "missed":
        return s === 1;
      case "shaky":
        return s === 2;
      case "solid":
        return s === 3;
      case "key":
        return card.hy;
      case "steps":
        return card.kind === "steps";
      case "cloze":
        return card.kind === "cloze";
      default:
        return true;
    }
  },
  get pool() {
    return this.topic ? this.all.filter((card) => card.topic === this.topic) : this.all;
  },
  get filters() {
    return FILTERS.map(([key, label]) => ({
      key,
      label,
      count: this.pool.filter((card) => this.matches(card, key)).length,
    })).filter((f) => f.key === "all" || f.count || f.key === this.filter);
  },
  build() {
    const list = this.pool.filter((card) => this.matches(card, this.filter));
    this.deck = this.shuffled ? shuffle(list) : list;
    this.index = 0;
    this.finished = false;
    this.session = { 1: 0, 2: 0, 3: 0 };
    this.resetCard();
  },
  setFilter(key) {
    this.filter = key;
    this.build();
  },
  setTopic(key) {
    this.topic = this.topic === key ? null : key;
    this.build();
  },
  shuffleDeck() {
    this.shuffled = true;
    this.build();
    this.$store.ui.say("Shuffled");
  },

  // ---- the card in front of you ------------------------------------------------------
  get card() {
    return this.deck[this.index] || null;
  },
  get grade() {
    return this.card ? this.status(this.card) : 0;
  },
  get position() {
    return this.deck.length ? `${this.index + 1} / ${this.deck.length}` : "0 / 0";
  },
  get shownSteps() {
    return this.card ? this.card.steps.slice(0, this.stepsShown) : [];
  },
  get stepsLeft() {
    return this.card ? this.card.steps.length - this.stepsShown : 0;
  },
  get revealLabel() {
    const card = this.card;
    if (!card) return "";
    if (this.stepsLeft > 0) {
      return this.stepsShown
        ? `Next step (${this.stepsShown} of ${card.steps.length})`
        : "Show step 1";
    }
    return card.kind === "cloze" ? "Reveal the blanks" : "Show answer";
  },
  resetCard() {
    this.revealed = false;
    this.stepsShown = 0;
  },
  go(index) {
    if (index < 0 || index >= this.deck.length) return;
    this.index = index;
    this.finished = false;
    this.resetCard();
  },
  /** One press of space: the next step of a derivation, or the answer. */
  advance() {
    if (!this.card || this.revealed) return;
    if (this.stepsLeft > 0) {
      this.stepsShown++;
      if (this.stepsLeft === 0) this.revealed = true;
      return;
    }
    this.revealed = true;
  },
  revealAll() {
    if (!this.card) return;
    this.stepsShown = this.card.steps.length;
    this.revealed = true;
  },
  mark(s) {
    if (!this.card) return;
    if (s === 0) {
      this.$store.progress.grade(this.course, this.card.id, 0);
      return;
    }
    if (!this.revealed) return; // no grading a card you have not checked
    this.$store.progress.grade(this.course, this.card.id, s);
    this.session[s]++;
    setTimeout(() => {
      if (this.index < this.deck.length - 1) this.go(this.index + 1);
      else this.finished = true;
    }, 170);
  },

  key(event) {
    if (typing(event) || document.querySelector("dialog[open]")) return;
    switch (event.key) {
      case " ":
      case "Enter":
        event.preventDefault();
        this.advance();
        break;
      case "1":
      case "2":
      case "3":
        this.mark(Number(event.key));
        break;
      case "0":
        this.mark(0);
        break;
      case "ArrowRight":
        this.go(this.index + 1);
        break;
      case "ArrowLeft":
        this.go(this.index - 1);
        break;
      case "s":
        this.shuffleDeck();
        break;
      case "a":
        this.revealAll();
        break;
    }
  },
});
