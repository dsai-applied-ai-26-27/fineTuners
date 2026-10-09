// Walking a memory palace.
//
// Each stop is recalled in two moves, the way the technique is practised: first the image
// you placed there, then what the image stands for. Only then do you grade the stop.

import { readData, typing } from "../lib/util.js";

export default () => ({
  course: "",
  palace: "",
  loci: [],
  index: -1, // -1 = looking at the route, not walking yet
  stage: 0, // 0 = place only, 1 = image shown, 2 = meaning shown
  done: false,

  init() {
    const data = readData("walk-data");
    Object.assign(this, { course: data.course, palace: data.palace, loci: data.loci });
  },

  key(id) {
    return `locus:${this.palace}:${id}`;
  },
  status(id) {
    return this.$store.progress.status(this.course, this.key(id));
  },
  get walking() {
    return this.index >= 0 && !this.done;
  },
  get locus() {
    return this.loci[this.index] || null;
  },
  get label() {
    return ["Show the image", "Show what it means"][this.stage] || "";
  },
  get solid() {
    return this.loci.filter((locus) => this.status(locus.id) === 3).length;
  },

  start() {
    this.index = 0;
    this.stage = 0;
    this.done = false;
  },
  stop() {
    this.index = -1;
    this.done = false;
  },
  advance() {
    if (this.walking && this.stage < 2) this.stage++;
  },
  mark(s) {
    if (!this.walking || this.stage < 2) return;
    this.$store.progress.grade(this.course, this.key(this.locus.id), s);
    setTimeout(() => {
      if (this.index < this.loci.length - 1) {
        this.index++;
        this.stage = 0;
      } else {
        this.done = true;
      }
    }, 170);
  },

  onKey(event) {
    if (typing(event) || !this.walking || document.querySelector("dialog[open]")) return;
    if (event.key === " " || event.key === "Enter") {
      event.preventDefault();
      this.advance();
    } else if (["1", "2", "3"].includes(event.key)) {
      this.mark(Number(event.key));
    } else if (event.key === "Escape") {
      this.stop();
    }
  },
});
