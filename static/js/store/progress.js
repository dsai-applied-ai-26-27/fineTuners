// Study progress. This is the only module that reads or writes browser storage for it,
// and the only one that talks to the server about it.
//
// Everything is one flat map of records keyed "<course>/<id>":
//     { s: 0-3, t: timestamp, k: solid streak, n: times graded }
// s = 1 missed, 2 shaky, 3 solid (also "lost / shaky / confident" for a lecture and "done"
// for a plan phase); s = 0 is a tombstone left by clearing a grade.
//
// The browser's copy is the one pages work from, so nothing ever waits for the network.
// When someone is signed in, the same data is also kept on the server so it follows them
// to another device. The two copies are brought together by four rules, applied the same
// way here (merge, below) and on the server (progress/sync.py):
//     records    the copy graded later wins
//     attempts   kept if not already known
//     activity   per day, the larger count wins
//     clears     "forget everything before this moment": the later moment wins
// Because the rules give the same result in any order, a sync can fail, repeat or arrive
// late without harm. Import uses the same merge.

import { DAY, dayKey } from "../lib/util.js";

const root = document.documentElement.dataset;
const USER = root.user || ""; // "" when nobody is signed in
const SYNC_URL = USER ? root.sync || "" : "";
const CSRF = root.csrf || "";

const LEGACY_KEY = "dsai:v1"; // progress made before there were accounts
// Each account has its own copy in this browser, so two people sharing a computer never
// see, or upload, each other's grades.
const KEY = USER ? `${LEGACY_KEY}:u${USER}` : LEGACY_KEY;
const SYNC_KEY = `${KEY}:sync`;

// Written into an exported file so Import can tell it is ours. The second name is what the
// site was called before it became DSAI Vault; files exported back then still import.
const EXPORT_IDS = ["dsai-vault", "dsai.pages"];
// Days before a solid card comes back, by how many times in a row it was solid.
const INTERVALS = [1, 3, 7, 14, 30];
const EVERYTHING = "*"; // the scope of a clear that covers all courses
const KINDS = ["records", "attempts", "activity", "clears"];

const blank = () => ({ v: 1, records: {}, attempts: {}, activity: {}, clears: {}, prefs: {} });
// What the server has not been told yet (`dirty`), and the number it gave us last time:
// "send me what changed after this" (`cursor`).
const blankSync = () => ({
  cursor: 0,
  at: 0,
  dirty: { records: {}, attempts: {}, activity: {}, clears: {} },
});

let state = blank();
let meta = blankSync();

function read(key) {
  try {
    return JSON.parse(localStorage.getItem(key));
  } catch {
    return null;
  }
}

function markAllDirty() {
  for (const kind of KINDS) for (const key of Object.keys(state[kind])) meta.dirty[kind][key] = 1;
}

function load() {
  const saved = read(KEY);
  const savedSync = read(SYNC_KEY);
  state = { ...blank(), ...saved };
  meta = { ...blankSync(), ...savedSync, dirty: { ...blankSync().dirty, ...savedSync?.dirty } };
  if (USER && !saved) {
    // First sign-in in this browser: take over what was studied here before accounts
    // existed, once, and remove the old copy so a second account cannot take it too.
    const legacy = read(LEGACY_KEY);
    if (legacy) {
      state = { ...blank(), ...legacy };
      markAllDirty();
      try {
        localStorage.setItem(KEY, JSON.stringify(state));
        localStorage.removeItem(LEGACY_KEY);
      } catch {
        /* storage is blocked: nothing was taken over, nothing to remove */
      }
    }
  }
}

function storageWorks() {
  try {
    localStorage.setItem("dsai:probe", "1");
    localStorage.removeItem("dsai:probe");
    return true;
  } catch {
    return false;
  }
}

/** Fold `incoming` into `target` by the four rules above. Returns how much changed. */
export function merge(target, incoming) {
  let changed = 0;
  target.clears ||= {};
  for (const [scope, moment] of Object.entries(incoming.clears || {})) {
    if (!(moment > (target.clears[scope] || 0))) continue;
    target.clears[scope] = moment;
    // Activity has no course and no exact time, so a full clear from elsewhere drops it.
    if (scope === EVERYTHING) target.activity = {};
    changed++;
  }
  // Nothing graded at or before this moment is kept, for the course the key belongs to.
  const floor = (key) =>
    Math.max(target.clears[EVERYTHING] || 0, target.clears[key.split("/")[0]] || 0);

  for (const key of Object.keys(target.records)) {
    if (target.records[key].t <= floor(key)) delete target.records[key];
  }
  for (const key of Object.keys(target.attempts)) {
    const kept = target.attempts[key].filter((a) => a.t > floor(key));
    if (kept.length) target.attempts[key] = kept;
    else delete target.attempts[key];
  }

  for (const [key, theirs] of Object.entries(incoming.records || {})) {
    if (!theirs || !(theirs.t > floor(key))) continue;
    const mine = target.records[key];
    if (!mine || theirs.t > mine.t) {
      target.records[key] = theirs;
      changed++;
    }
  }
  for (const [key, list] of Object.entries(incoming.attempts || {})) {
    const known = new Set((target.attempts[key] || []).map((a) => a.t));
    const fresh = list.filter((a) => !known.has(a.t) && a.t > floor(key));
    if (fresh.length) {
      target.attempts[key] = [...(target.attempts[key] || []), ...fresh].sort((a, b) => a.t - b.t);
      changed += fresh.length;
    }
  }
  for (const [day, theirs] of Object.entries(incoming.activity || {})) {
    const mine = (target.activity[day] ||= { cards: 0, minutes: 0 });
    // The same day seen on two devices: keep the larger count rather than adding twice.
    mine.cards = Math.max(mine.cards || 0, theirs.cards || 0);
    mine.minutes = Math.max(mine.minutes || 0, theirs.minutes || 0);
  }
  return changed;
}

export function createProgress() {
  load();
  let saveTimer = null;
  let syncTimer = null;
  let syncing = false;
  let again = false;
  let gone = false; // set once the account is being deleted

  // Alpine wraps the store in a proxy that notices changes. Code that runs later, from a
  // timer or a network reply, must write through that proxy for the page to update.
  const live = () => window.Alpine?.store("progress") || store;
  const isDirty = () => KINDS.some((kind) => Object.keys(meta.dirty[kind]).length);

  function save() {
    if (gone) return true;
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
      if (USER) localStorage.setItem(SYNC_KEY, JSON.stringify(meta));
      return true;
    } catch {
      return false;
    }
  }

  function schedule(ms) {
    if (!SYNC_URL) return;
    clearTimeout(syncTimer);
    syncTimer = setTimeout(() => sync(), ms);
  }

  /** Send what changed here, receive what changed elsewhere. Safe to call at any time. */
  async function sync({ keepalive = false } = {}) {
    const self = live();
    if (!SYNC_URL || self.sync === "signed-out") return;
    if (syncing) {
      again = true;
      return;
    }
    syncing = true;
    // Only what the server has not seen. A dirty key that no longer exists was cleared.
    const sent = { cursor: meta.cursor };
    for (const kind of KINDS) {
      sent[kind] = {};
      for (const key of Object.keys(meta.dirty[kind])) {
        if (key in state[kind]) sent[kind][key] = state[kind][key];
        else delete meta.dirty[kind][key];
      }
    }
    if (isDirty()) self.sync = "saving";
    try {
      const response = await fetch(SYNC_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": CSRF },
        body: JSON.stringify(sent),
        credentials: "same-origin",
        keepalive,
      });
      if (response.status === 401 || response.status === 403) {
        self.sync = "signed-out";
        return;
      }
      if (!response.ok) throw new Error(`sync answered ${response.status}`);
      const answer = await response.json();

      // What was sent is now known to the server, unless it changed again meanwhile.
      for (const kind of KINDS) {
        for (const [key, value] of Object.entries(sent[kind])) {
          if (JSON.stringify(state[kind][key]) === JSON.stringify(value)) delete meta.dirty[kind][key];
        }
      }
      // The server lost track of this browser (its database was rebuilt): offer everything.
      if (answer.resync) {
        markAllDirty();
        again = true;
      }
      const changed = merge(state, answer);
      meta.cursor = answer.cursor;
      meta.at = Date.now();
      self.persistent = save();
      if (changed) self.rev++;
      self.sync = isDirty() ? "saving" : "saved";
    } catch {
      // Offline, or the server is restarting. Everything is still saved here and stays
      // marked as unsent, so the next sync carries it.
      self.sync = "offline";
    } finally {
      syncing = false;
      if (again) {
        again = false;
        schedule(400);
      }
    }
  }

  const store = {
    // Reading `rev` inside a getter makes Alpine re-run it whenever progress changes.
    rev: 0,
    persistent: storageWorks(),
    account: Boolean(SYNC_URL),
    // local (no account) | saving (something is waiting to be sent) | saved | offline |
    // signed-out
    sync: SYNC_URL ? (isDirty() ? "saving" : "saved") : "local",

    get saveLabel() {
      if (!this.persistent && !this.account) return "Storage blocked: progress is not saved";
      return {
        local: "Progress saved in this browser",
        saving: "Saving to your account…",
        saved: "Saved to your account",
        offline: "Offline: saved here, will sync later",
        "signed-out": "Signed out: reload to keep saving",
      }[this.sync];
    },
    get saveState() {
      if (this.sync === "offline" || this.sync === "signed-out") return "off";
      if (!this.persistent && !this.account) return "off";
      return "on";
    },

    touch() {
      this.rev++;
      clearTimeout(saveTimer);
      saveTimer = setTimeout(() => this.flush(), 120);
      if (this.account && this.sync !== "signed-out") this.sync = "saving";
      // A study session is many small changes: wait for a pause, then send them together.
      schedule(2500);
    },
    flush() {
      this.persistent = save();
    },
    syncNow(options) {
      return sync(options);
    },

    // ---- preferences -----------------------------------------------------------------
    // Small settings of this browser, such as having seen the tour. They are stored with
    // the progress, but a merge, a clear and the server never touch them.
    pref(name) {
      return state.prefs?.[name];
    },
    setPref(name, value) {
      state.prefs = { ...state.prefs, [name]: value };
      this.persistent = save();
    },

    // ---- records ---------------------------------------------------------------------
    record(course, id) {
      this.rev;
      return state.records[`${course}/${id}`];
    },
    status(course, id) {
      return this.record(course, id)?.s || 0;
    },
    grade(course, id, s, { count = true } = {}) {
      const key = `${course}/${id}`;
      const previous = state.records[key];
      state.records[key] = {
        s,
        t: Date.now(),
        k: s === 3 ? (previous?.k || 0) + 1 : 0,
        n: (previous?.n || 0) + (s ? 1 : 0),
      };
      meta.dirty.records[key] = 1;
      if (s && count) this.log("cards", 1);
      this.touch();
    },
    /** A yes/no mark (a plan phase done) stored the same way as a grade. */
    set(course, id, on) {
      this.grade(course, id, on ? 3 : 0, { count: false });
    },
    isDue(record, now = Date.now()) {
      if (!record || !record.s) return false;
      if (record.s === 1) return true;
      if (record.s === 2) return now - record.t >= DAY;
      const days = INTERVALS[Math.min(record.k || 1, INTERVALS.length) - 1];
      return now - record.t >= days * DAY;
    },
    stats(course, ids) {
      this.rev;
      const out = { total: ids.length, solid: 0, shaky: 0, missed: 0, unseen: 0, due: 0 };
      const now = Date.now();
      for (const id of ids) {
        const record = state.records[`${course}/${id}`];
        const s = record?.s || 0;
        out[["unseen", "missed", "shaky", "solid"][s]]++;
        if (this.isDue(record, now)) out.due++;
      }
      return out;
    },
    countMarked(course, ids) {
      this.rev;
      return ids.filter((id) => state.records[`${course}/${id}`]?.s).length;
    },

    // ---- mock exam attempts ----------------------------------------------------------
    attempts(course, paper) {
      this.rev;
      return state.attempts[`${course}/${paper}`] || [];
    },
    addAttempt(course, paper, attempt) {
      const key = `${course}/${paper}`;
      (state.attempts[key] ||= []).push({ ...attempt, t: Date.now() });
      meta.dirty.attempts[key] = 1;
      this.touch();
    },

    // ---- activity --------------------------------------------------------------------
    log(kind, amount) {
      const key = dayKey();
      const day = (state.activity[key] ||= { cards: 0, minutes: 0 });
      day[kind] = (day[kind] || 0) + amount;
      meta.dirty.activity[key] = 1;
      this.touch();
    },
    /** The last `count` days, oldest first. */
    days(count) {
      this.rev;
      const out = [];
      for (let back = count - 1; back >= 0; back--) {
        const date = new Date(Date.now() - back * DAY);
        const key = dayKey(date);
        out.push({ key, date, cards: 0, minutes: 0, ...state.activity[key] });
      }
      return out;
    },
    streak() {
      this.rev;
      const active = (key) => {
        const day = state.activity[key];
        return day && (day.cards > 0 || day.minutes > 0);
      };
      let length = 0;
      // A streak is still alive if today has nothing yet but yesterday did.
      let back = active(dayKey()) ? 0 : 1;
      while (active(dayKey(new Date(Date.now() - back * DAY)))) {
        length++;
        back++;
      }
      return length;
    },

    // ---- moving data -----------------------------------------------------------------
    exportText() {
      return JSON.stringify({ app: EXPORT_IDS[0], exported: new Date().toISOString(), ...state }, null, 2);
    },
    importText(text) {
      const incoming = JSON.parse(text);
      if (!EXPORT_IDS.includes(incoming?.app) || typeof incoming.records !== "object") {
        throw new Error("This file is not a DSAI Vault progress export.");
      }
      const changed = merge(state, incoming);
      // Whatever the file brought has to reach the account as well.
      for (const kind of KINDS) {
        for (const key of Object.keys(incoming[kind] || {})) {
          if (key in state[kind]) meta.dirty[kind][key] = 1;
        }
      }
      this.touch();
      return changed;
    },
    /** Forget one course's progress, or all of it, here and on every other device. */
    reset(course = null) {
      const scope = course || EVERYTHING;
      // Not "delete": a moment before which nothing counts. merge() drops what is older
      // here, and another device that still holds the old grades learns the moment at
      // its next sync and drops them too.
      merge(state, { clears: { [scope]: Date.now() } });
      for (const kind of KINDS) {
        for (const key of Object.keys(meta.dirty[kind])) {
          if (!(key in state[kind])) delete meta.dirty[kind][key];
        }
      }
      meta.dirty.clears[scope] = 1;
      this.touch();
      this.flush();
      schedule(200);
    },
    /** Remove this browser's copy for the signed-in account. Used when it is deleted. */
    forgetLocal() {
      clearTimeout(saveTimer);
      clearTimeout(syncTimer);
      this.sync = "signed-out"; // nothing more is sent
      gone = true; // nor written back when the page closes
      state = blank();
      meta = blankSync();
      try {
        localStorage.removeItem(KEY);
        localStorage.removeItem(SYNC_KEY);
      } catch {
        /* nothing was stored */
      }
    },
    totals() {
      this.rev;
      const records = Object.values(state.records).filter((r) => r.s);
      return { records: records.length, days: Object.keys(state.activity).length };
    },
  };

  // Another tab changed progress: pick it up, so two open tabs never overwrite each other.
  window.addEventListener("storage", (event) => {
    if (event.key !== KEY && event.key !== SYNC_KEY) return;
    const unsent = meta.dirty;
    const cursor = meta.cursor;
    load();
    // Keep this tab's own unsent marks: sending something twice is harmless, losing a
    // mark is not.
    meta.cursor = Math.max(meta.cursor, cursor);
    for (const kind of KINDS) Object.assign(meta.dirty[kind], unsent[kind]);
    live().rev++;
  });
  // A page change within 120 ms of a grade must not lose it, here or on the server.
  // `keepalive` lets the request finish after the page is gone.
  window.addEventListener("pagehide", () => {
    store.flush();
    if (isDirty()) sync({ keepalive: true });
  });
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") {
      if (isDirty()) sync({ keepalive: true });
    } else if (Date.now() - meta.at > 60_000) {
      schedule(100);
    }
  });
  // On arrival: send anything left unsent, and fetch what other devices did. Skipped when
  // this browser synced within the last minute and has nothing to say.
  if (isDirty() || Date.now() - meta.at > 60_000) schedule(150);

  return store;
}
