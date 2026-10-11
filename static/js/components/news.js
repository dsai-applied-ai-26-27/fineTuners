// "What's new": the updates a person has not been shown yet
// (templates/components/news.html). The server puts the dialog in the page only when
// there is something to show; it opens once the page is drawn and tells the server at
// that moment, so the next page does not show it again.

import { report } from "../seen.js";

export default () => ({
  init() {
    requestAnimationFrame(() =>
      setTimeout(() => {
        // The tour may have been asked for in the meantime; one dialog at a time.
        if (document.querySelector("dialog[open]")) return;
        this.$root.showModal();
        report("news", this.$root);
      }, 350),
    );
  },

  /** Close, then open the tour on the step that shows what is new. */
  tour() {
    this.$root.close();
    this.$dispatch("tour", { step: Number(this.$root.dataset.tourStep) });
  },
});
