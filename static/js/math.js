// Finishes what the server started in rendered Markdown.
//
// The server leaves LaTeX as text inside <span class="math">; KaTeX typesets it here.
// It also adds the icon to each callout title. Both run on page load and again on any
// fragment a component inserts later (a revealed answer, the next card).

const CALLOUT_ICONS = {
  note: "info",
  tip: "tip",
  warning: "warning",
  pitfall: "pitfall",
  definition: "definition",
  theorem: "theorem",
  example: "example",
  paper: "paper",
  proof: "proof",
  recall: "help",
  solution: "check",
};

export function typeset(root = document) {
  const katex = window.katex;
  if (!katex) return;
  for (const node of root.querySelectorAll(".math:not([data-done])")) {
    const tex = node.textContent;
    try {
      katex.render(tex, node, {
        displayMode: node.classList.contains("block"),
        throwOnError: true,
        strict: "ignore",
      });
    } catch (error) {
      // sync_content verifies every formula, so this is rare; show the source, not nothing.
      node.dataset.error = "1";
      node.title = String(error.message || error);
    }
    node.dataset.done = "1";
  }
}

export function decorate(root = document) {
  const sprite = document.documentElement.dataset.icons;
  for (const title of root.querySelectorAll(".callout__title:not([data-icon])")) {
    const kind = [...title.parentElement.classList]
      .find((name) => name.startsWith("callout--"))
      ?.slice("callout--".length);
    const icon = CALLOUT_ICONS[kind];
    if (icon) {
      title.insertAdjacentHTML(
        "afterbegin",
        `<svg class="icon" aria-hidden="true"><use href="${sprite}#${icon}"></use></svg>`,
      );
    }
    title.dataset.icon = "1";
  }
}

export function enhance(root = document) {
  typeset(root);
  decorate(root);
}

/** x-math="expression": like x-html, then typesets what it inserted. */
export function mathDirective(Alpine) {
  Alpine.directive("math", (el, { expression }, { effect, evaluateLater }) => {
    const read = evaluateLater(expression);
    effect(() => {
      read((html) => {
        el.innerHTML = html || "";
        enhance(el);
      });
    });
  });
}
