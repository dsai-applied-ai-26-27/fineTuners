# Instructions for AI agents

The instructions for this repository are in [CLAUDE.md](CLAUDE.md) and apply to every agent,
whatever tool it runs in. Read that file first.

The short version:

- **Writing course content?** Read [docs/AUTHORING.md](docs/AUTHORING.md). Edit only
  `courses/<course>/content/` and `courses/<course>/course.yaml`. Never edit
  `courses/<course>/source/` or any code. Validate with
  `uv run python manage.py sync_content <course> --check` until it reports no errors.
- **Changing the application?** Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Run
  `uv run python manage.py test` and `uv run ruff check .` before you finish.
- **The live site.** Nothing writes to its database directly: content reaches it as files,
  through `manage.py publish`, and code through a merge to `main`. Do neither unless the
  owner asks. Details in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).
