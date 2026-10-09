// Small helpers shared by the components.

export const DAY = 86_400_000;

/** Parse the JSON Django printed with {{ data|json_script:"id" }}. */
export function readData(id) {
  const node = document.getElementById(id);
  return node ? JSON.parse(node.textContent) : null;
}

/** The slug of the course this page belongs to ("" outside a course). */
export const COURSE = document.documentElement.dataset.course || "";

let cachedManifest;
/** What the current course contains: cards, decks, documents, sets, exams. */
export function manifest() {
  if (cachedManifest === undefined) cachedManifest = readData("course-manifest");
  return cachedManifest;
}

let cachedAll;
/** Manifests of every course (dashboard, settings); falls back to the current course. */
export function manifests() {
  if (cachedAll === undefined) {
    cachedAll = readData("all-manifests") || (manifest() ? [manifest()] : []);
  }
  return cachedAll;
}

/** True when the keystroke belongs to a text field and must not trigger a shortcut. */
export function typing(event) {
  const el = event.target;
  return (
    event.ctrlKey ||
    event.metaKey ||
    event.altKey ||
    el.isContentEditable ||
    ["INPUT", "TEXTAREA", "SELECT"].includes(el.tagName)
  );
}

export function shuffle(list) {
  for (let i = list.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [list[i], list[j]] = [list[j], list[i]];
  }
  return list;
}

/** Local calendar day as YYYY-MM-DD (toISOString would give the UTC day). */
export function dayKey(date = new Date()) {
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${date.getFullYear()}-${month}-${day}`;
}

export function clock(ms) {
  const seconds = Math.max(0, Math.ceil(ms / 1000));
  const minutes = Math.floor(seconds / 60);
  return `${String(minutes).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
}

export function plural(count, word, many = word + "s") {
  return `${count} ${count === 1 ? word : many}`;
}

export function percent(part, whole) {
  return whole ? Math.round((100 * part) / whole) : 0;
}

/** Trigger a download of `text` as a file. */
export function download(filename, text) {
  const url = URL.createObjectURL(new Blob([text], { type: "application/json" }));
  const link = Object.assign(document.createElement("a"), { href: url, download: filename });
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}
