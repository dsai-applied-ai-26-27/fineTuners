# How the application works

For changing the application. If you are writing course content, read
[AUTHORING.md](AUTHORING.md) instead.

This file doubles as a map of Django as it is used here: each section names the Django
concept and the file where you can see it.

## The shape

```
courses/<course>/content/**     Markdown + YAML, written by authors
        |
        |  ingest/      manage.py sync_content
        v
SQLite                          catalog/models/    (a cache of the files)
        |
        |  catalog/     urls.py -> views/ -> templates/
        v
HTML page  +  static/js (Alpine)  +  progress: a copy in the browser,
                                     kept in step with progress/ on the server
```

Four Django **apps** of our own, listed in `INSTALLED_APPS` in
[config/settings.py](../config/settings.py):

- **`catalog`** owns the course tables and every page.
- **`ingest`** owns no tables. It turns files into `catalog` rows and provides the
  management commands.
- **`progress`** owns what a signed-in person has done, and the one endpoint that saves it.
- **`accounts`** is the little that is ours around signing in. The sign-in itself is
  django-allauth's.

The split between files and database is the main design decision: content is written as
files (so an AI can author it and a human can read a diff), but served from a database (so
pages are simple queries). The `catalog` tables can be emptied at any time; `migrate` and
`sync_content` rebuild them. The `progress` and user tables cannot: they are the only
data here that does not come from a file.

## A request, start to finish

Take `GET /courses/mlpr/cards/ch5-fisher/`.

1. **URL configuration.** [config/urls.py](../config/urls.py) includes
   [catalog/urls.py](../catalog/urls.py), where
   `path("courses/<slug:course>/cards/<slug:slug>/", views.deck, name="deck")` matches.
   The `<slug:…>` parts become keyword arguments of the view. The `name` is how the rest of
   the code refers to this address: `reverse("catalog:deck", args=[…])` in Python,
   `{% url 'catalog:deck' … %}` in templates. No URL is written out anywhere else.
2. **View.** [catalog/views/practice.py](../catalog/views/practice.py) `deck()` is a plain
   function: request in, response out. It calls `load_course()`
   ([views/common.py](../catalog/views/common.py)) for the course and the context every
   course page shares, fetches the deck with `get_object_or_404`, and builds the list of
   cards.
3. **Models and the ORM.** `deck.cards.select_related("deck", "topic")` is a lazy
   `QuerySet`: no SQL runs until it is iterated. `select_related` joins the related rows in
   the same query, which avoids one query per card (the "N+1" problem).
4. **Template.** `render(request, "catalog/deck.html", context)` fills
   [deck.html](../catalog/templates/catalog/deck.html), which `{% extends %}`
   [course_base.html](../catalog/templates/catalog/course_base.html), which extends
   [templates/base.html](../templates/base.html). Each level fills `{% block %}`s of the one
   above.
5. **Data for the browser.** `{{ player|json_script:"player-data" }}` prints the cards as
   JSON in an inert `<script>` tag, escaped so that no content can break out of it.
   [static/js/components/flashcards.js](../static/js/components/flashcards.js) reads it.

## Models

[catalog/models/](../catalog/models/) is a package; `__init__.py` re-exports every model so
Django finds them as `catalog.models.X`.

- A `Course` row is one course in **one academic year**. The same course in another
  year is another row, with its own folder, content and progress, tied to the first
  by a shared `series`. [catalog/editions.py](../catalog/editions.py) is the only
  place that reasons about that: `latest()` picks the newest year of each course for
  the dashboard and the navigation, `of()` lists a course's years for the switch at
  the top of its page. Nothing else in the code knows years exist, and adding a year
  is adding a folder (see [content-types/course.md](content-types/course.md)).
- [base.py](../catalog/models/base.py) has three **abstract** models. They create no table;
  subclasses inherit their fields and `Meta`. `CourseItem` (belongs to a course, has an
  order), `KeyedItem` (addressed by a permanent `key`, unique per course), `SluggedItem`
  (addressed by a file name).
- `related_name="%(class)ss"` on the shared foreign key gives each subclass its own reverse
  accessor: `course.cards`, `course.decks`, `course.questionsets`.
- Uniqueness is enforced by the database with `UniqueConstraint`, not only by the importer.
- Choices are `TextChoices` enums (`Document.Kind.LECTURE`), which gives
  `get_kind_display()` for free.
- Rendered HTML is stored (`body_html`, `front_html`, …). A page view never renders
  Markdown.
- Each model has `get_absolute_url()`: the one place its address is defined.

**Migrations** in [catalog/migrations/](../catalog/migrations/) are generated: after
changing a model run `manage.py makemigrations` then `migrate`. Commit the migration file.

**Admin.** [catalog/admin.py](../catalog/admin.py) registers every model read-only
(`has_change_permission` returns `False`), because an edit there would be overwritten by the
next sync. It is a browser for what the importer produced. People are the exception:
see [Accounts and progress](#accounts-and-progress).

## The ingest pipeline

`manage.py sync_content` → [ingest/sync.py](../ingest/sync.py), per course:

| Step | Module | What it does |
|---|---|---|
| discover | [discover.py](../ingest/discover.py) | Classifies files by path. Computes the content hash used to skip unchanged courses |
| load | [yamlio.py](../ingest/yamlio.py), [load.py](../ingest/load.py) | Parses YAML keeping line numbers; lints quoting, duplicate keys, anchors |
| validate | [schemas.py](../ingest/schemas.py) | Pydantic models, `extra="forbid"`. Errors are rewritten into plain language |
| index | [build.py](../ingest/build.py) `Builder.index` | Records every id and file name; checks uniqueness, topics, exam scopes |
| render | [markdown.py](../ingest/markdown.py), [refs.py](../ingest/refs.py), [assets.py](../ingest/assets.py) | Markdown → HTML, references → URLs via `reverse()`, images → `media/` |
| maths | [mathcheck.py](../ingest/mathcheck.py) | Structural lint, then KaTeX under Node if available |
| write | [store.py](../ingest/store.py) | One `transaction.atomic()`: upsert by natural key, delete what vanished |

Properties worth preserving:

- **Everything before `write` only reads.** All problems are collected in a
  [Report](../ingest/report.py) and none of them touch the database.
- **All or nothing per course.** `store.write` is wrapped in `transaction.atomic`.
- **Primary keys are stable.** Rows are matched by natural key and updated in place, so a
  future table that points at `Card` by foreign key survives re-imports.
- **Error messages are an interface.** They are read by AI agents: file, line, field, what
  is wrong, how to fix it. Tests in
  [ingest/tests/test_errors.py](../ingest/tests/test_errors.py) pin them.

**Management commands** are classes in
[ingest/management/commands/](../ingest/management/commands/). A file `foo.py` with a
`Command(BaseCommand)` class becomes `manage.py foo`.

### Markdown

One renderer for documents and for the Markdown strings inside YAML. markdown-it-py with
plugins for maths, callouts, footnotes, definition lists, task lists and attributes.

- **Raw HTML is off.** This is the security boundary: stored HTML contains only tags the
  renderer produced, which is what makes `{{ html|safe }}` in templates acceptable. If you
  ever enable raw HTML, sanitise the output (for example with `nh3`).
- Maths is not rendered on the server. `$x$` becomes `<span class="math inline">x</span>`
  and the browser typesets it. Fragments are collected so sync can verify them.
- Attributes are an allow-list (`class`, `id`, `width`, `height`, `title`).
- Fuzzy link detection is off (it would link `train.py`); typographic replacement is off
  (it would turn `(c)` into ©).

### Adding a content type

1. Model in `catalog/models/`, then `makemigrations`.
2. Schema in `ingest/schemas.py` (with field descriptions) and an entry in `SCHEMAS`.
3. Where its files live: `ingest/discover.py`. Loading: `ingest/load.py`.
4. Index and rows: `ingest/build.py`. Writing: `ingest/store.py`.
5. If it can be linked to: `ingest/refs.py`.
6. View, URL, template; an entry in `catalog/nav.py`.
7. An example in `docs/example-course/`, tests, a page in `docs/content-types/`,
   then `manage.py export_schemas`.

## Pages

- Views are functions, grouped by area in [catalog/views/](../catalog/views/).
- The dashboard sorts courses into sections by `semester`
  (`dashboard_groups` in [catalog/views/home.py](../catalog/views/home.py)): semesters with
  an active course first, the latest on top, finished semesters after. A course without
  a semester falls back to its year, or to the Archived fold once it is archived.
- `load_course()` returns the course and the shared context: navigation, counts and the
  manifest. [catalog/nav.py](../catalog/nav.py) builds those once per sync and caches them
  with Django's cache framework under a key that includes the course's content hash, so a
  new sync simply uses a new key.
- Navigation lists only sections that have content.
- `?scope=<exam>` and `?topic=<id>` narrow the card player, formulas, glossary and hooks;
  see `scope_topics()` in [views/common.py](../catalog/views/common.py).
- [catalog/context_processors.py](../catalog/context_processors.py) adds variables to every
  template (the list of active courses for the rail).
- [catalog/templatetags/ui.py](../catalog/templatetags/ui.py) defines `{% icon %}`,
  `{% topic_chips %}` and small filters.

## Front end

No bundler and no npm project. Third-party files are fetched once by
[tools/vendor_assets.py](../tools/vendor_assets.py) (pinned versions, integrity checked) and
committed under `static/vendor/`, `static/fonts/` and `static/icons.svg`.

**The logo** (a D whose inside is a keyhole) is one SVG path in
[tools/make_icons.py](../tools/make_icons.py). That script writes the tab icon and the
bitmap sizes into `static/brand/`, and the bare glyph into
[templates/components/logo.html](../templates/components/logo.html), which the page frame
includes so the mark takes the page's own colour. Change the shape there and re-run it;
do not edit its outputs.

**The landing page** ([catalog/templates/catalog/landing.html](../catalog/templates/catalog/landing.html),
[static/css/landing.css](../static/css/landing.css)) is laid out like the cover of a set
of notes: one statement in the reading typeface, the way in, one figure, and a ruled
list. It loads no JavaScript and is given no course data, so it costs no database
query. Its figure is a real chart, not decoration:
[tools/make_figure.py](../tools/make_figure.py) draws how a flashcard is recalled when
it is reviewed on the site's own schedule (`INTERVALS` in
[static/js/store/progress.js](../static/js/store/progress.js)) and writes
[templates/components/recall_figure.html](../templates/components/recall_figure.html).
The lines are an SVG stretched to fit; every label is HTML placed over it by
percentage, so text stays readable on a phone. If the schedule changes, change the
copy in the script and re-run it; a test compares the two.

**JavaScript** ([static/js/](../static/js/)) is plain ES modules.
[app.js](../static/js/app.js) registers everything with Alpine and starts it.

- `store/progress.js` is the only code that reads or writes progress, and the only code
  that talks to the server about it ([Accounts and progress](#accounts-and-progress)).
  It holds `records` (keyed `<course>/<id>`: `{s, t, k, n}`), `attempts`, `activity` and
  `clears` in one localStorage key per account.
- `lib/overview.js` turns a course's manifest and that store into one set of numbers:
  how much of the reading, the cards and the problems is solid, shaky or missed. The
  dashboard's bars and the course page's tiles both come from it.
- `store/timer.js` is the focus timer. It stores when the block *ends*, so it survives
  navigation and reloads.
- `components/` has one module per interactive piece: `flashcards`, `paper`, `palace`,
  `cover`, `nextup`, `settings`, `shell`, and `widgets` (small progress read-outs).
- `math.js` typesets `.math` nodes with KaTeX and adds callout icons. The `x-math` directive
  does the same for HTML inserted later.

A component reads `$store.progress.rev` (directly or through a store method) to re-run when
progress changes.

**CSS** ([static/css/](../static/css/)) uses cascade layers, declared in
[tokens.css](../static/css/tokens.css): `reset, tokens, base, layout, components, prose,
study, pages, utilities`. A later layer wins over an earlier one regardless of selector
specificity; remember that when a rule seems to be ignored.

### Design system

A pastel take on Material 3.

- **Colour is computed.** Every role (`--surface`, `--primary-container`, `--on-surface`, …)
  is an OKLCH colour derived from one custom property, `--hue`. A course's pages set
  `--hue` on `<html>`. An element can carry its own hue with the class `tone` (course cards
  on the dashboard). `light-dark()` supplies the dark theme.
- **Grades have fixed colours** in every course: missed, shaky, solid, key.
- **Depth is tonal.** Surfaces step through `--surface-low … --surface-highest`; shadows are
  kept for things that float.
- **Type:** Google Sans Flex for the interface, Literata for reading, JetBrains Mono for
  code.
- **Shape:** radii from `--r-xs` to `--r-xl`; pills for buttons and navigation.
- **Rules:** no decorative gradients, no blur or glass, no emoji as icons, no colour outside
  the tokens.
- Icons are Material Symbols in one sprite; add a name to `ICONS` in
  `tools/vendor_assets.py` and re-run it.

## Accounts and progress

**Signing in.** `LoginRequiredMiddleware` (in `MIDDLEWARE`, [config/settings.py](../config/settings.py))
turns the usual rule round: every view needs a signed-in person unless it says otherwise
with `@login_not_required`. Three things say otherwise: `catalog.views.home`, which shows
the landing page to a visitor and the dashboard to anyone signed in; django-allauth's own
views; and the progress endpoint, which must answer a script with `401`, not with a
redirect to a web page. An anonymous request anywhere else is sent to `LOGIN_URL` (the
landing page) with `?next=` remembering where it was going.

[django-allauth](https://docs.allauth.org/) does the OAuth exchange with Google and creates
the Django user on first sign-in (`SOCIALACCOUNT_ONLY`: there are no passwords). Its URLs
are mounted under `/accounts/` in [config/urls.py](../config/urls.py). The few pages it
renders itself use [templates/allauth/layouts/base.html](../templates/allauth/layouts/base.html):
a template placed at the same path as one inside a package overrides it, because
`TEMPLATES["DIRS"]` is searched first.

The user model is Django's own `auth.User`, referred to as `settings.AUTH_USER_MODEL`.
Anything more we need to know about a person goes in a table with a foreign key to it, as
`progress` does.

In DEBUG the landing page also offers a development sign-in
([accounts/views.py](../accounts/views.py)), so working locally needs no Google client.

**Progress.** The browser's copy is what pages read and write, so nothing waits for the
network and studying works offline. [static/js/store/progress.js](../static/js/store/progress.js)
remembers which entries the server has not seen (`dirty`) and the number the server gave
it last time (`cursor`). A few seconds after a change, on arriving at a page, and when the
tab is hidden, it POSTs the dirty entries and the cursor to `/api/progress/sync/`.

[progress/sync.py](../progress/sync.py) folds them in inside one transaction and answers
with every row whose `version` is above that cursor, from any device, plus the new cursor.
Each person has a counter ([progress/models.py](../progress/models.py), `Ledger`); every row
changed by a request is stamped with the counter's next value. That makes "what is new
since I last asked" one indexed query.

Both sides apply the same rules, so the order of events never matters:

| | Rule |
|---|---|
| records | the copy graded later wins (`t`, the grading device's clock) |
| attempts | kept if that sitting is not already known |
| activity | per day, the larger count wins |
| clears | "forget everything before this moment", per course or for all; the later moment wins and older rows are dropped |

A clear is how "Clear progress" in Settings reaches a phone that still holds the old
grades: deleting rows would not, the phone would send them straight back.

The endpoint is a plain view returning `JsonResponse`, protected like any form post: the
session cookie says who, and the CSRF token (printed into `<html data-csrf>`, sent as the
`X-CSRFToken` header) says the request came from our own page. The payload is checked
entry by entry with Pydantic; a malformed entry is skipped, never the whole request.

Anyone with a Google account can sign in and post here, so the endpoint also guards the
disk: an account may hold at most `LIMITS` rows of each kind
([progress/sync.py](../progress/sync.py)), far above honest use, and Django refuses a
request body over 2.5 MB before the view sees it (`DATA_UPLOAD_MAX_MEMORY_SIZE`).

**People in the admin.** [accounts/admin.py](../accounts/admin.py) replaces Django's own
user admin with a narrower one. The list shows each person with how much they have
graded and when they last studied, computed by correlated subqueries (`Subquery` with
`OuterRef`) because progress rows have no reverse link from the user. The page of one
person sums their progress by course. An administrator can rename a person, switch
them inactive, make them staff, delete them (progress goes along by cascade), and
clear their progress. Clearing calls `progress.sync.forget`, which records a clear
exactly as a device would, so the person's browsers drop their copies too. Nobody is
added by hand, and an administrator cannot demote or delete themselves there.
The link to the admin shows in the navigation for staff only.

With Google sign-in configured, the admin's own login page (user name and password)
is never shown: [config/urls.py](../config/urls.py) wraps it in
`staff_member_required`, which sends a visitor to the landing page instead.

**What can be marked.** Cards, questions, palace stops and formula-sheet rows always had
three grades. Documents now have them too: the reading page asks "Lost, Shaky or
Confident" ([catalog/templates/catalog/document.html](../catalog/templates/catalog/document.html)),
stored as the same record under the key `doc:<kind>:<slug>`. A plan phase stays a yes/no
mark.

## Tests

`manage.py test` runs Django's test runner.

- [ingest/tests/](../ingest/tests/): `CourseTestCase` copies the example course to a
  temporary folder; each test breaks the copy in one way and asserts the reported file,
  line and message. Also the Markdown dialect, YAML positions, the commands, and that the
  generated docs are up to date.
- [catalog/tests/](../catalog/tests/): every page renders for the example course; scope
  filtering; search; the source-file view cannot escape its folder; query counts.
- [config/tests.py](../config/tests.py): the production settings refuse to start without
  a secret key and pass `check --deploy`.
- [progress/tests/](../progress/tests/): the four merge rules, played as one or two
  devices against `sync()`; the endpoint's 401, CSRF check and query count.
- [accounts/tests/](../accounts/tests/): who is sent to the landing page, the sign-in flow
  is reachable signed out, the development sign-in is closed outside DEBUG, deleting an
  account takes its progress with it.

A test that needs a signed-in person calls `self.client.force_login(user)`, which puts a
session for that user into the test client without going through a sign-in page.

`TestCase` wraps each test in a transaction that is rolled back. `SimpleTestCase` is for
tests that need no database.

## Development and production

There is one [config/settings.py](../config/settings.py). It reads environment variables,
and with none set you get local development. The server sets `DJANGO_DEBUG=0` and its own
values; the block at the end of the file, `if not DEBUG:`, is everything that then changes.
[DEPLOYMENT.md](DEPLOYMENT.md) covers the server; the Django side of it is this:

- **WSGI.** `runserver` is a development convenience. In production
  [gunicorn](../Dockerfile) imports `config/wsgi.py` and calls Django for each request.
- **Static files** are part of the code. `collectstatic` gathers them into `STATIC_ROOT`
  when the image is built, and `STORAGES["staticfiles"]`
  ([config/storage.py](../config/storage.py)) gives each a name containing a hash of its
  contents. `{% static 'js/app.js' %}` then prints `…/app.2bee543c4f7e.js`, and the
  `import` lines inside the modules are rewritten the same way. WhiteNoise serves them
  from the Django process. In DEBUG none of this happens and files are served as written.
- **Media files** are data: images that `sync_content` copies out of course content into
  `MEDIA_ROOT`. Django serves them only in DEBUG ([config/urls.py](../config/urls.py)); in
  production the web server in front does.
- **`SECURE_PROXY_SSL_HEADER`.** Django sits behind proxies that end HTTPS and pass plain
  HTTP on. This setting names the header in which they report the original scheme, so
  `request.is_secure()` is right and secure cookies work.
- **Content Security Policy.** `SECURE_CSP` in settings, sent as a header by Django's
  `ContentSecurityPolicyMiddleware` in development and production alike, so a violation
  shows up in the browser console while developing. Pages may load scripts, styles,
  fonts and images from this site only. An inline `<script>` must carry
  `nonce="{{ csp_nonce }}"`; data for scripts goes through `json_script`, which is not
  executed and needs none. `'unsafe-eval'` is allowed because Alpine.js compiles the
  expressions in `x-data` and `@click`, and inline styles because course colours and
  KaTeX use them.
- **Rate limits.** [config/ratelimit.py](../config/ratelimit.py) is a small middleware:
  `RATE_LIMITS` in settings lists a path and how many calls a minute one account (or,
  signed out, one address) may make to it; the call after that gets `429` with
  `Retry-After`. It covers saving progress, search and starting a sign-in. The
  browser treats a refused save like being offline and sends it with the next one.
- **`check --deploy`** is Django's own review of exactly these settings. A test
  ([config/tests.py](../config/tests.py)) and CI keep it clean.
- **Tests** always run with development settings, because `config/settings.py` is read
  with no variables set. The two tests that need the production side start a second
  Python process with the server's variables.

## Not built yet, and where it would go

- **Limiting who may sign in** (faculty addresses only): an allauth adapter, described in
  [DEPLOYMENT.md](DEPLOYMENT.md#who-may-sign-in).
- **Marks on more things.** Glossary terms, hooks and formulas are graded only in their
  cover-and-recall mode, and do not count towards a course's bar
  ([static/js/lib/overview.js](../static/js/lib/overview.js) lists what does).
- **A stricter Content Security Policy.** The one in place allows `'unsafe-eval'` for
  Alpine. Dropping it means Alpine's CSP build and moving every inline expression into
  registered components.
- **Exact rate limits.** Counters live in each worker's memory; a shared cache (Redis,
  or Django's file cache on a memory disk) under the name `limits` would make them
  exact without touching [config/ratelimit.py](../config/ratelimit.py).
- **Files for download.** Source files are served only when `SERVE_SOURCE_FILES` is on
  (debug). For production, object storage (R2) behind signed URLs.
- **Search** is `icontains` over stored text. SQLite FTS5 is the next step.
- **Diagrams and plots** in content are images today.
