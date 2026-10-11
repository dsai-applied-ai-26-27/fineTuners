// Tell the server that this person has been shown the tour or the news, so that it is
// offered once per account and not once per browser (catalog/welcome.py).
//
// `upto` is the number of the site's latest update when the page was built: what was
// actually on screen. Nothing depends on the answer, so a failure is let go; the worst
// that happens is that the same thing is offered once more.

const root = document.documentElement.dataset;

/** Whether somebody is signed in. On the open site only the browser remembers. */
export const signedIn = Boolean(root.user);

export function report(what, dialog) {
  const { seen, upto } = dialog.dataset;
  if (!signedIn || !seen) return;
  fetch(seen, {
    method: "POST",
    headers: { "X-CSRFToken": root.csrf || "" },
    body: new URLSearchParams({ what, upto: upto || "0" }),
    keepalive: true, // still sent if the person leaves the page straight away
  }).catch(() => {});
}
