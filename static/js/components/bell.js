// The bell at the top of every page (templates/components/bell.html): how many
// notifications are new, and telling the server once they have been shown.
//
// The button and the list are two elements: the list is a native popover and lives
// outside the button. The popover says "I was opened" with an event; the button, which
// holds the number, hears it, tells the server, and drops the number.

const csrf = document.documentElement.dataset.csrf || "";

export default (unread = 0) => ({
  unread,

  init() {
    window.addEventListener("bell-open", (event) => this.read(event.detail));
  },

  read(url) {
    if (!this.unread || !url) return;
    fetch(url, { method: "POST", headers: { "X-CSRFToken": csrf }, keepalive: true }).catch(() => {});
    this.unread = 0;
  },
});
