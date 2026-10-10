// The page frame: navigation drawer, theme, global keyboard shortcuts.

import { typing } from "../lib/util.js";

const THEME_KEY = "dsai:theme";
const system = window.matchMedia("(prefers-color-scheme: dark)");
const systemTheme = () => (system.matches ? "dark" : "light");

function savedTheme() {
  try {
    const saved = localStorage.getItem(THEME_KEY);
    return saved === "light" || saved === "dark" ? saved : null;
  } catch {
    return null;
  }
}

export default () => ({
  drawer: false,
  // What is on screen right now: "light" or "dark". There is no third state to click
  // through. The site follows the device until the button is pressed, and goes back to
  // following it when the choice made here is the same as the device's own.
  theme: systemTheme(),

  init() {
    this.theme = savedTheme() || systemTheme();
    // The device switched (sunset, a settings change): follow it, unless overridden here.
    system.addEventListener("change", () => {
      if (!savedTheme()) this.theme = systemTheme();
    });
  },

  toggleTheme() {
    this.theme = this.theme === "dark" ? "light" : "dark";
    const root = document.documentElement;
    const override = this.theme !== systemTheme();
    // data-theme on <html> is what the stylesheet reads (static/css/tokens.css); without
    // it the browser's own light/dark preference applies.
    if (override) root.dataset.theme = this.theme;
    else delete root.dataset.theme;
    try {
      if (override) localStorage.setItem(THEME_KEY, this.theme);
      else localStorage.removeItem(THEME_KEY);
    } catch {
      /* storage is blocked: the choice lasts for this page only */
    }
    this.$store.ui.say(this.theme === "dark" ? "Dark theme" : "Light theme");
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
        this.toggleTheme();
        break;
      case "?":
        this.$refs.shortcuts.showModal();
        break;
    }
  },
});
