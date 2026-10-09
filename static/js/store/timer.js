// Focus timer (pomodoro).
//
// The old exam kits counted a number down inside one page, so the timer died on every
// navigation. Here the store saves the moment the block ENDS. Any page can then work out
// what is left from the clock, which makes the timer survive page changes, reloads and a
// sleeping laptop.

import { clock } from "../lib/util.js";

const KEY = "dsai:v1:timer";
const MINUTE = 60_000;

function read() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || {};
  } catch {
    return {};
  }
}

function chime() {
  try {
    const context = new (window.AudioContext || window.webkitAudioContext)();
    [660, 880, 1174.7].forEach((frequency, index) => {
      const start = context.currentTime + index * 0.22;
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      oscillator.type = "sine";
      oscillator.frequency.value = frequency;
      gain.gain.setValueAtTime(0.0001, start);
      gain.gain.exponentialRampToValueAtTime(0.2, start + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, start + 0.34);
      oscillator.connect(gain).connect(context.destination);
      oscillator.start(start);
      oscillator.stop(start + 0.36);
    });
    setTimeout(() => context.close(), 1500);
  } catch {
    /* no audio available: the dialog still appears */
  }
}

export function createTimer(progress) {
  const saved = read();
  const focusMin = saved.focusMin || 25;
  let interval = null;
  let flashing = null;
  const title = document.title;

  return {
    phase: saved.phase || "focus",
    running: false,
    endsAt: saved.endsAt || 0,
    remaining: saved.remaining ?? focusMin * MINUTE,
    focusMin,
    breakMin: saved.breakMin || 5,
    sound: saved.sound ?? true,
    auto: saved.auto ?? false,
    hidden: saved.hidden ?? false,
    now: Date.now(),
    alert: { title: "", body: "", action: "" },

    init() {
      if (saved.running && saved.endsAt > Date.now()) {
        this.running = true;
        this.tickEvery();
      } else if (saved.running) {
        this.finish({ away: true }); // the block ended while no page was open
      }
      // Another tab started or stopped the timer.
      window.addEventListener("storage", (event) => {
        if (event.key !== KEY) return;
        const other = read();
        Object.assign(this, other, { running: Boolean(other.running) });
        other.running ? this.tickEvery() : this.stopTicking();
      });
    },

    get left() {
      return this.running ? Math.max(0, this.endsAt - this.now) : this.remaining;
    },
    get display() {
      return this.hidden && this.running ? "• • •" : clock(this.left);
    },
    get todayMinutes() {
      return progress.days(1)[0].minutes;
    },

    toggle() {
      this.running ? this.pause() : this.start();
    },
    start() {
      this.now = Date.now();
      this.endsAt = this.now + this.remaining;
      this.running = true;
      this.tickEvery();
      this.save();
    },
    pause() {
      this.remaining = this.left;
      this.running = false;
      this.stopTicking();
      this.save();
    },
    reset() {
      this.stopTicking();
      this.running = false;
      this.phase = "focus";
      this.remaining = this.focusMin * MINUTE;
      this.save();
    },
    setLength(phase, minutes) {
      this[`${phase}Min`] = minutes;
      if (!this.running && this.phase === phase) this.remaining = minutes * MINUTE;
      this.save();
    },

    tickEvery() {
      this.stopTicking();
      interval = setInterval(() => {
        this.now = Date.now();
        if (this.running && this.now >= this.endsAt) this.finish();
      }, 500);
    },
    stopTicking() {
      clearInterval(interval);
      interval = null;
    },

    finish({ away = false } = {}) {
      const ended = this.phase;
      this.stopTicking();
      this.running = false;
      if (ended === "focus") progress.log("minutes", this.focusMin);
      this.phase = ended === "focus" ? "break" : "focus";
      this.remaining = (this.phase === "focus" ? this.focusMin : this.breakMin) * MINUTE;
      this.save();
      if (away) return;
      if (this.sound) chime();
      if (this.auto) {
        this.start();
        return;
      }
      this.alert =
        ended === "focus"
          ? {
              title: "Focus block done",
              body: `${this.focusMin} minutes. Stand up, look out of a window, drink something.`,
              action: `Start the ${this.breakMin}-minute break`,
            }
          : {
              title: "Break over",
              body: "Back to the one next action.",
              action: `Start ${this.focusMin} minutes`,
            };
      document.getElementById("timer-alert")?.showModal();
      this.flashTitle(this.alert.title);
    },
    next() {
      this.dismiss();
      this.start();
    },
    dismiss() {
      document.getElementById("timer-alert")?.close();
      this.stopFlash();
    },

    flashTitle(message) {
      this.stopFlash();
      let on = false;
      flashing = setInterval(() => {
        on = !on;
        document.title = on ? `● ${message}` : title;
      }, 900);
    },
    stopFlash() {
      clearInterval(flashing);
      flashing = null;
      document.title = title;
    },

    save() {
      const { phase, running, endsAt, remaining, focusMin, breakMin, sound, auto, hidden } = this;
      try {
        localStorage.setItem(
          KEY,
          JSON.stringify({ phase, running, endsAt, remaining, focusMin, breakMin, sound, auto, hidden }),
        );
      } catch {
        /* storage blocked: the timer still works within this page */
      }
    },
  };
}
