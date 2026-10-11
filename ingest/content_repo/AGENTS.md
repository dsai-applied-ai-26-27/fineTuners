# DSAI Vault course content: instructions for an AI assistant

This repository holds the course content of DSAI Vault, a study site for the Data Science
and AI programme. Each course is a folder. The site shows what is in a course's `content/`
folder, and you write those files from the raw material in its `source/` folder.

You are most likely here because someone told you:

```
Update the CMS for this course: semester-5/rl
```

That means: follow the procedure below for exactly that one course folder. If they named
a lecture or a file, do that part; if they did not, the work list in step 2 tells you what
is missing.

## The layout

```
semester-5/rl/        one course
  course.yaml         what the course is, and its list of topics
  source/             raw material: slides, labs, homework, past papers. READ ONLY.
  content/            what the site shows. This is where you write.
docs/                 the format: how content files are written. Read it, never edit it.
tools/                the checker. Never edit it.
```

`source/` exists only on the computer of the person you are working for. Git ignores it on
purpose and it is never committed. If it is empty, stop and ask them to put the lecture
material there: there is nothing to write from.

## Rules that are never broken

1. **One course per task.** Create and edit files only in that course's `content/` folder,
   and in its `course.yaml` only as rule 4 allows. Leave every other course, `docs/` and
   `tools/` exactly as they are.
2. **`source/` is read-only and stays where it is.** The slides and papers belong to the
   lecturers. Do not copy their pages, scans or figures into `content/`; write your own
   summary in your own words. A diagram you draw yourself or a plot you generate is fine.
3. **Ids and file names are permanent.** Every card, question, formula, term and hook has
   an `id`, and a document's file name is its address. Each student's progress is stored
   under them. Never rename, renumber or reuse one. To improve an item, edit it in place.
4. **`course.yaml` is mostly not yours.** You may add `topics` (and reword a topic's
   `title`), and write the `description`. Do not change `title`, `code`, `year`, `series`,
   `semester`, `status`, `enabled`, `has_educator`, `hue` or `order`, and never change or
   remove a topic's `id`.
5. **Write what the source supports.** If you add something that is not in the material
   (an extra example, background the slides assume), say so in your report. Never invent
   exam dates, weights, or what "will be on the exam".
6. **No commit, push or pull request unless you are asked.** The person checks what you
   wrote against the lecture first. That check is theirs and cannot be skipped.

## The procedure

1. **Learn the format.** Read `docs/AUTHORING.md` completely. Then read the page under
   `docs/content-types/` for each kind of file you are about to write, and nothing you do
   not need. `docs/example-course/example/` is a complete, valid course that uses every
   feature once: copy its shapes.

   That guide was written for the application's own repository, so its commands differ
   here. Where it says `manage.py content_status <course>`, run step 2 below. Where it
   says `manage.py sync_content <course> --check`, run step 5 below. Loading into the
   site and `publish` are not part of your work: the person who runs the site does both.

2. **See what exists and what is missing.**
   ```
   uv run tools/check.py --status semester-5/rl
   ```
   It prints what the course contains and, under "not written up yet", the files in
   `source/` that no document names in its `sources:` field. That is the work list.
3. **Read the sources completely.** Every page of a PDF, every cell of a notebook. Do not
   write from a skim, a table of contents or a file name. If you cannot read a file (a
   scan without text, a format you cannot open), say so in the report; do not guess its
   contents.
4. **Write or update the files** under `content/`. Update in place; leave alone what you
   were not asked to change. Add a topic to `course.yaml` before the first file refers to
   it. Name the source files a document was written from in its `sources:` field: that is
   how step 2 knows the material is covered.

   For one lecture this usually means its notes (`content/lectures/NN-name.md`), a deck of
   flashcards (`content/decks/`), and, where the course has exercises, problems with
   worked solutions (`content/problems/`), plus new rows for the formula sheet and the
   glossary. `docs/AUTHORING.md` has a playbook for each type of course and the quality bar
   every file must meet.
5. **Check.**
   ```
   uv run tools/check.py semester-5/rl
   ```
   Every problem is reported as `file:line  field`, a message, and usually a `->` line
   saying how to fix it. Fix and re-run until it says the structure is valid.
6. **Report** to the person, in this order: the files you created and the files you
   changed; what in `source/` you could not read; anything you wrote that is not in the
   source; and what they should look at first when they check your work (derivations,
   numbers, anything you were unsure about).

Without `uv`: `pip install pyyaml pydantic` once, then `python tools/check.py ...`.

## What the check covers

`tools/check.py` is the first half of the site's own importer, the same code. It catches
files in the wrong place, YAML that does not parse, unknown or missing fields, wrong
types, an id used twice, and a `topic` that `course.yaml` does not declare.

It cannot see what needs the whole site: links between files (`lecture:03-search`,
`card:mdp-01`), the Markdown inside your text, and whether the maths typesets. So be
exact there:

- A link names something that exists, spelled as its file name or id is spelled.
- Maths is LaTeX between `$…$` or `$$…$$`, with every brace and environment closed.
- In YAML, prose and maths go in block scalars (`|-`). A double-quoted string with a
  backslash in it is an error: `"\theta"` is a TAB followed by `heta`.

Those are checked when the content is loaded into the site. If something fails there you
will be given the report, in the same `file:line` form, to fix.

## Handing it in (only when asked)

1. Work on a branch named after the course and the piece: `rl/lecture-03`.
2. `git status` must show files under that course's `content/` (and perhaps its
   `course.yaml`) and nothing else. If a file under a `source/` folder ever shows up
   there, stop and say so: it must not be committed.
3. Commit with a message that says what was added: `rl: lecture 3 notes, deck, problems`.
4. Push the branch and open a pull request. It goes on the site once the person who runs
   it has merged it and published.
