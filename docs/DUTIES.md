# Duties: a course's dates, for the owner's bot

Labs, tests, exams, project defences, seminars, presentations and homework deadlines: the
dated things the owner has to do or attend for a course. They are kept per course in one
file, and every change to them is sent to the owner's assistant bot (BMO), which decides
what to remind them of.

This file is **private to the owner**. Unlike everything else about a course:

- It is **not shown on the site**, to anyone, and not in the admin.
- It is **not part of the course that travels.** It sits beside `course.yaml`, not under
  `content/`, so a download, a hand-in, the editor and the history never carry it
  ([ingest/handin.py](../ingest/handin.py) takes `course.yaml` and `content/` only), and a
  hand-in that brings one is refused. Educators never see it and cannot change it.
- It is **not in the educator kit**, which is public: not this page, not the format, not
  the code. Nothing about duties belongs in [AUTHORING.md](AUTHORING.md),
  [content-types/](content-types/), [schemas/](schemas/), the example course,
  [ingest/schemas.py](../ingest/schemas.py), or any other file `export_authoring` copies.
- It reaches the server only with the owner's `publish`, and leaves it only for the bot.

## The file

`courses/semester-N/<course>/duties.yaml`:

```yaml
duties:
  - id: lab-3
    kind: lab
    title: Lab 3, convolution
    due: 2026-11-04T10:00
    place: Lab 1-12
    notes: Bring the prepared report.
  - id: midterm
    kind: test
    title: Midterm
    due: 2026-11-20
    notes: Chapters 1 to 4, closed book.
```

| Field | | |
|---|---|---|
| `id` | required | Lowercase letters, digits and single hyphens. Unique in the file, and **permanent**: the bot knows the duty as `<course>/<id>`, so a new id is a duty removed and another one added. |
| `kind` | required | One of `lab`, `test`, `exam`, `project`, `seminar`, `homework`, `presentation`, `other`. |
| `title` | required | One line: what it is, as the course calls it. |
| `due` | required | `2026-11-04` for a day, `2026-11-04T10:00` for a day and a time. **Sarajevo time**, no zone, to the minute. A date that does not exist is an error. |
| `place` | optional | Room, lab, building or "online". |
| `notes` | optional | A line or two: what it covers, what to bring, how it is handed in. |

A course with nothing dated yet has no file, or `duties: []`.

`manage.py sync_content <course>` checks the file with the rest of the course, and prints
how many duties it holds. A mistake in it stops the course like a mistake in any of its
files, and `publish` sends nothing while one is there.

## Writing it from the source material

Whenever a course is written or updated from its `source/` (lectures, the syllabus,
announcements, posts fetched from the courseware), its `duties.yaml` is brought up to date
in the same session:

- **Every dated duty goes in:** each lab session and lab deadline, each test, quiz and
  midterm (kolokvij), each exam term (rok), project milestones and defences, seminars,
  presentations, homework deadlines. One item per date: three exam terms are three items.
- **Only what the material dates.** Never guess a date. Something announced without one
  is left out until it has one; say so at the end of the session.
- **The newest word wins.** An announcement that moves a date overrides the syllabus.
  Change `due` (and `place`) in place and keep the `id`; remove an item that was cancelled.
- **Dates as published, in Sarajevo time.** A time only when the material gives one; a
  deadline "by the end of the day" is the day alone.
- **Ids that say what they are and stay:** `lab-3`, `hw-2`, `midterm`, `exam-jan`,
  `exam-feb`, `project-defence`. Number by the course's own numbering.
- The year is the folder's academic year. A date outside it is almost always a typo.

It is written by hand in a content session like any course file, committed in the
`courses/` repository only when the owner asks, and never under `source/`.

## How the bot hears of it

```
duties.yaml --publish--> the server's course files --sync_content--> desk/duties.py --POST--> BMO
```

After every real `sync_content` on the server (each `publish`, and each deploy, which
loads the content again), [desk/duties.py](../desk/duties.py) reads every course's
`duties.yaml`, compares it with what the bot was last told (the `desk.ToldDuty` table,
one row per duty), and sends what is new, changed or gone:

```json
{
  "source": "DSAI Vault",
  "batch_id": "dsai-duties-<32 hex>",
  "items": [
    {"key": "dms/lab-3", "change": "new", "course": "DMS", "course_title": "…",
     "kind": "lab", "title": "Lab 3, convolution", "due": "2026-11-04T10:00",
     "place": "Lab 1-12", "notes": "…", "url": "https://dsai3.pages.dev/…"}
  ]
}
```

- `change` is `new`, `changed` or `removed`; a removed item carries what the bot was last
  told about it. `url` is the course's page.
- At most 50 items in one POST; more are sent as several.
- `batch_id` is the same for the same changes from the same state, so a batch sent again
  after a lost answer is one the bot can recognise.
- Delivery is the one of [desk/notify.py](../desk/notify.py): `X-BMO-Token` with the
  bot's token, https only, two more tries for a network error or a 5xx, a refusal final,
  and a failure is a log line, never a failed sync. What the bot did not take is not
  recorded as told, so the next sync sends it again.
- A course whose file has errors is left out: the bot keeps what it has for it.
- The address is `BMO_DUTIES_URL`, or by default `BMO_NOTIFY_URL` with `bmo-notify`
  changed to `bmo-duties` ([DEPLOYMENT.md](DEPLOYMENT.md#day-to-day)).
  On a computer without the bot's settings nothing is sent and nothing is recorded.
