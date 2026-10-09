# DSAI Vault

A study site for university courses. Course material is turned into notes, flashcards,
problems and exam prep written as Markdown/YAML files; a Django app validates those files,
loads them into SQLite and renders them. Study progress lives in the browser.

## Two kinds of session: decide which one you are in

**Content session** — "write up lecture 3", "make cards for chapter 5", "add the past paper".

- Read [docs/AUTHORING.md](docs/AUTHORING.md) first, then the page for each content type you
  will write under [docs/content-types/](docs/content-types/).
- Create and edit files **only** under `courses/<course>/content/` and
  `courses/<course>/course.yaml`.
- `courses/<course>/source/` is read-only raw material.
- Do not touch Python, templates, CSS or JavaScript. If the site cannot show something,
  report it; do not change code to make it fit.
- Finish with `uv run python manage.py sync_content <course>` printing no errors.

**App session** — "add a page", "fix the player", "change the theme".

- Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) first.
- Do not edit course content to work around a bug; fix the code.
- Changing what a content file may contain means changing `ingest/schemas.py`, then running
  `manage.py export_schemas`, then updating the docs and the example course.
- Finish with the tests and `ruff check` clean.

## Commands

```
uv sync                                               install dependencies into .venv
uv run python manage.py runserver                     the site, http://127.0.0.1:8000
uv run python manage.py content_status [course]       what exists, what is still unwritten
uv run python manage.py sync_content [course] --check validate course files only
uv run python manage.py sync_content [course]         validate and load into the database
uv run python manage.py sync_content --watch          re-sync whenever a file changes
uv run python manage.py startcourse <slug> --title "…" --code X --year "2026-27"
uv run python manage.py export_schemas                regenerate docs/schemas and fields.md
uv run python manage.py test                          all tests
uv run ruff check . && uv run ruff format .           lint and format
```

## Map

```
config/      Django project: settings, root URL config
catalog/     the site: models, views, URLs, templates, template tags
ingest/      files -> database: schemas, Markdown renderer, sync, management commands
templates/   base page and shared fragments
static/      CSS, JavaScript (no build step), vendored libraries, fonts, icons
docs/        AUTHORING.md, ARCHITECTURE.md, content-types/, schemas/, example-course/
courses/     course folders: NOT in git (raw material and written content)
tools/       vendor_assets.py (fetch front-end libraries), katex_check.cjs
```

`db.sqlite3` and `media/` are derived from `courses/`; deleting them loses nothing that
`migrate` plus `sync_content` cannot rebuild. Progress is in the browser, not the database.

## Facts worth knowing before changing things

- Ids of cards, questions, formulas, terms and hooks are permanent. Browser progress is keyed
  `<course>/<id>`. Never rename them in content, and never change how keys are built.
- Stored HTML is trusted because `ingest/markdown.py` renders with raw HTML disabled. Keep it
  that way, or templates using `|safe` become an injection risk.
- `docs/example-course/` is both the reference for authors and the fixture for the tests.
  If you change a schema, update it in the same change.
- `docs/schemas/*.json` and `docs/content-types/fields.md` are generated. Do not edit them.
- Maths is typeset in the browser by KaTeX and verified at sync by the same KaTeX build under
  Node (optional: without Node only the structural lint runs).

## Working with the owner

- The owner is learning Django through this project. When you change application code,
  explain the Django concept involved (what it is, why Django does it that way, where it
  lives here). Prefer the idiomatic, standard Django way over a clever one.
- The visual direction is a pastel Material 3 look with a per-course hue. No decorative
  gradients, no glass effects, no emoji as icons. See the design section of ARCHITECTURE.md.
- Do not commit or push unless asked.
