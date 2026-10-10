// The tour: a few steps on how the site is meant to be used
// (templates/components/tour.html).
//
// It opens by itself the first time someone reaches the dashboard in this browser. After
// that it opens only when asked: any element can dispatch a `tour` event, and the dialog
// listens for it on the window. Having seen it is a preference of the browser, kept by the
// progress store and not sent to the server.

export default (offer = false) => ({
  step: 0,
  count: 0,

  init() {
    this.count = this.$root.querySelectorAll("[data-step]").length;
    if (offer && !this.$store.progress.pref("tour")) {
      // Wait for the page to be drawn first: a dialog that is there before the page it
      // belongs to looks like something went wrong.
      requestAnimationFrame(() => setTimeout(() => this.open(), 350));
    }
  },

  open() {
    this.step = 0;
    if (!this.$root.open) this.$root.showModal();
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
