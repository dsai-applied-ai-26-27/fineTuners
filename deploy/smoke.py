"""Ask the running site for a few pages and one static file. Exit 1 if anything is wrong.

Run inside the web container, where gunicorn listens on port 8000:

    python deploy/smoke.py [/extra/path/ ...]

The deploy script runs it after every deploy, and CI runs it against a freshly built image.
`/` must answer 200 (the landing page, or the dashboard on an open site). Extra paths must
answer 200 too: a redirect to the sign-in counts as a failure, so CI gives them to a
container started with DSAI_REQUIRE_LOGIN=0. Standard library only.
"""

import http.client
import os
import re
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"
# Django rejects a request whose Host it does not know, and redirects one that did not
# arrive over HTTPS. The proxy in front normally supplies both; here we stand in for it.
HEADERS = {
    "Host": os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost").split(",")[0],
    "X-Forwarded-Proto": "https",
}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Report a redirect as what it is instead of quietly following it."""

    def redirect_request(self, *args, **kwargs):
        return None


opener = urllib.request.build_opener(NoRedirect)


def get(path):
    request = urllib.request.Request(BASE + path, headers=HEADERS)
    try:
        with opener.open(request, timeout=10) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, (error.headers.get("Location") or "").encode()
    except (OSError, http.client.HTTPException) as error:
        return 0, str(error).encode()


def main(paths):
    failures = []
    home = b""
    for path in ["/", *paths]:
        status, body = get(path)
        print(f"  {status}  {path}")
        if status != 200:
            failures.append(f"{path} answered {status} {body[:200].decode(errors='replace')}")
        elif path == "/":
            home = body

    # Every page links the stylesheets under the hashed names collectstatic gave them.
    # One of them must be there, and must load.
    sheet = re.search(rb'href="(/static/css/tokens\.[0-9a-f]{8,}\.css)"', home)
    if home and not sheet:
        failures.append("the page links no hashed stylesheet: did collectstatic run?")
    elif sheet:
        path = sheet.group(1).decode()
        status, _ = get(path)
        print(f"  {status}  {path}")
        if status != 200:
            failures.append(f"{path} answered {status}")

    for failure in failures:
        print(f"FAILED: {failure}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
