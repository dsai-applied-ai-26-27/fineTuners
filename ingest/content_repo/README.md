# DSAI Vault course content

The course files of [DSAI Vault](https://dsai3.pages.dev), the study site for the Data
Science and AI programme. This repository is private and shared with the people who write
courses: educators.

Nothing here is the website. The site reads these files; what is merged here goes live
when the person who runs the site publishes it.

```
semester-1/ … semester-6/     one folder per semester of the programme
  <course>/
    course.yaml               what the course is, and its topics
    content/                  what the site shows: notes, flashcards, problems, exams
    source/                   raw material. On your computer only: git ignores it.
docs/                         how content is written
tools/check.py                checks your files before you hand them in
AGENTS.md                     the instructions your AI assistant follows
```

## Writing a course, start to finish

1. **Get the files.** Clone this repository. If GitHub says it does not exist, your
   account has not been given access yet: ask.
2. **Put the material in.** Copy the lecture slides, labs, homework and past papers into
   your course's `source/` folder (`semester-5/rl/source/lectures/`, `…/labs/`,
   `…/homework/`, `…/exams/`). They stay on your computer. Git ignores every `source/`
   folder, so they cannot be uploaded by accident, and they must not be: they belong to the
   lecturers.
3. **Let your assistant write.** Open this folder in an AI assistant that can read files
   and write them on your computer, and tell it:

   ```
   Update the CMS for this course: semester-5/rl
   ```

   It reads `AGENTS.md`, learns the format from `docs/`, finds what in `source/` has not
   been written up, writes it, and checks its own work. To do one piece at a time, name it:
   `Update the CMS for this course: semester-5/rl. Only lecture 3.`
4. **Check what it wrote.** This is your part and the reason the role exists. Read the
   notes against the slides. Work through at least a few cards and one solution by hand.
   An assistant writes mistakes as confidently as it writes everything else.
5. **Hand it in.** Ask the assistant to commit and open a pull request, or do it yourself:
   a branch, a commit, a pull request. It is on the site once it has been merged and
   published. If the site finds a problem the check here could not see, you get the
   report back.

By hand, without an assistant, it is the same loop: read `docs/AUTHORING.md`, write the
files, run the check.

## The check

```
uv run tools/check.py semester-5/rl
```

needs [uv](https://docs.astral.sh/uv/) and nothing else; it fetches what it needs the
first time. Without uv: `pip install pyyaml pydantic`, then
`python tools/check.py semester-5/rl`. Add `--status` to list what in `source/` is not
written up yet.

It checks the structure of your files with the site's own code. Links between files and
maths are checked by the site itself when the content is loaded.

## What is never committed

- Anything under a `source/` folder.
- Scans, photos or copies of slides, handouts and papers, also inside `content/`. Write
  your own summary; draw your own figure.
- Anything personal about anyone.

## Whose it is

Course material belongs to the lecturers and the faculty. What is written here are
students' study summaries of it. What you hand in is shown to everyone who uses the site,
and the person who runs the site may edit or remove it.

`docs/` and `tools/` are copies made from the application. Do not edit them here; a change
would be overwritten by the next copy.
