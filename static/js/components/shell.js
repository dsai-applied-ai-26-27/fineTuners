// The page frame: navigation drawer, theme, global keyboard shortcuts.

import { typing } from "../lib/util.js";

const THEME_KEY = "dsai:theme";
const THEMES = ["auto", "light", "dark"];

export default () => ({
  drawer: false,
  theme: "auto",

  init() {
    try {
      this.theme = localStorage.getItem(THEME_KEY) || "auto";
    } catch {
      this.theme = "auto";
    }
  },

  cycleTheme() {
    this.theme = THEMES[(THEMES.indexOf(this.theme) + 1) % THEMES.length];
    const root = document.documentElement;
    try {
      if (this.theme === "auto") {
        localStorage.removeItem(THEME_KEY);
        delete root.dataset.theme;
      } else {
        localStorage.setItem(THEME_KEY, this.theme);
        root.dataset.theme = this.theme;
      }
    } catch {
      root.dataset.theme = this.theme;
    }
    this.$store.ui.say(`Theme: ${this.theme}`);
  },

  onKey(event) {
    if (typing(event)) return;
    switch (event.key) {
      case "/":
        event.preventDefault();
        this.$refs.search.focus();
        break;
      case "t":
        this.$store.timer.toggle();
        break;
      case "d":
        this.cycleTheme();
        break;
      case "?":
        this.$refs.shortcuts.showModal();
        break;
    }
  },
});
