// How far along a course is, as one set of numbers used by the dashboard and the course
// page. Three kinds of thing can be marked missed / shaky / solid:
//     reading    lectures, labs, homework, guides (rated at the foot of the page)
//     cards      flashcards
//     problems   questions in practice sets and papers
// Each kind that the course has counts equally, however many items it holds. Otherwise
// forty flashcards would drown out four lectures.

const GROUPS = [
  ["reading", "Reading", (course) => course.docs.map((doc) => doc.key)],
  ["cards", "Cards", (course) => course.cards.map((card) => card.id)],
  ["problems", "Problems", (course) => course.sets.flatMap((set) => set.questions)],
];

/**
 * `course` is a manifest, `progress` the progress store. Returns
 * { groups: [{ name, label, stats }], solid, shaky, missed (percent of the course),
 *   started, total }.
 */
export function overview(course, progress) {
  const groups = [];
  for (const [name, label, ids] of GROUPS) {
    const list = ids(course);
    if (list.length) groups.push({ name, label, stats: progress.stats(course.slug, list) });
  }
  const share = (kind) =>
    groups.length
      ? (100 * groups.reduce((sum, group) => sum + group.stats[kind] / group.stats.total, 0)) / groups.length
      : 0;
  return {
    groups,
    solid: share("solid"),
    shaky: share("shaky"),
    missed: share("missed"),
    started: groups.some((group) => group.stats.unseen < group.stats.total),
    total: groups.reduce((sum, group) => sum + group.stats.total, 0),
  };
}

/** The share of one group, for a bar segment: `width(stats, "solid")` -> percent. */
export function width(stats, kind) {
  return stats.total ? (100 * stats[kind]) / stats.total : 0;
}

/** s (0-3) as a word, for data-state attributes and labels. */
export const STATES = ["", "missed", "shaky", "solid"];
