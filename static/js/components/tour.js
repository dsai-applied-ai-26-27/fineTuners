// The tour: a few steps on how the site is meant to be used
// (templates/components/tour.html).
//
// It opens by itself once: the first time a person reaches their dashboard. Whether that
// has happened is the server's to say for someone signed in (`offer`, from
// catalog/welcome.py), so a second device does not bring it back; the moment it opens the
// server is told. On the open site, where nobody is signed in, the browser remembers
// instead. After that it opens only when asked: any element can dispatch a `tour` event,
// and the dialog listens for it on the window.

import { report, signedIn } from "../seen.js";

export default (offer = false) => ({
  step: 0,
  count: 0,

  init() {
    this.count = this.$root.querySelectorAll("[data-step]").length;
    if (offer && (signedIn || !this.$store.progress.pref("tour"))) {
      // Wait for the page to be drawn first: a dialog that is there before the page it
      // belongs to looks like something went wrong.
      requestAnimationFrame(() => setTimeout(() => this.open(), 350));
    }
  },

  /** `$dispatch('tour', { step: 3 })` opens it on that step (counted from 0). */
  open(event) {
    const wanted = Number(event?.detail?.step);
    this.step = Number.isInteger(wanted) ? Math.min(Math.max(wanted, 0), this.count - 1) : 0;
    if (this.$root.open) return;
    this.$root.showModal();
    report("tour", this.$root);
  },
  /** However it was closed (the last button, Skip, Escape), it has been seen. */
  seen() {
    this.$store.progress.setPref("tour", Date.now());
  },

  get last() {
    return this.step === this.count - 1;
  },
  next() {
    if (this.last) this.$root.close();
    else this.step++;
  },
  back() {
    if (this.step > 0) this.step--;
  },
});
