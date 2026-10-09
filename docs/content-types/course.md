# course.yaml

One per course, at `courses/<course>/course.yaml`. It names the course and lists its topics.
Fields: [fields.md#course](fields.md#course). Example:
[example-course/example/course.yaml](../example-course/example/course.yaml).

```yaml
title: Reinforcement Learning
code: RL
year: "2026-27"          # quoted: an unquoted 2026-27 is fine too, but a bare 2026 is a number
semester: winter         # winter | summer | leave out
status: active           # active | archived
hue: 150                 # the course's colour, 0-359 on the hue wheel
order: 4                 # position among courses of the same year
description: Markov decision processes, dynamic programming, TD learning and policy gradients.

topics:
  - id: mdp
    title: Markov decision processes
    short: MDPs
  - id: dp
    title: Dynamic programming
```

## Topics

Topics are the backbone of a course. Lectures, cards, questions, formula sections, glossary
terms, hooks and palaces point at topic ids, and an exam's scope is a set of topics.

- **Order** them as they are taught. The order is used wherever topics are listed.
- **Granularity:** a topic is a chapter or a week, not a single idea. Aim for 5 to 12.
  If the course follows a textbook, its chapters are usually the right topics.
- **`short`** is an optional label for chips where the full title is too long.
- **Ids are permanent.** Choose something that will still be right if the title is reworded:
  `mdp`, `ch5`, `week3`.

Add topics as the course progresses. An id must exist here before anything refers to it.

## Colour

`hue` is the only styling a course has; the whole palette (surfaces, chips, the course card)
is computed from it. Keep courses of the same year at least 40 apart so they are easy to
tell apart: 25 red, 60 amber, 100 lime, 150 green, 200 teal, 240 blue, 285 violet, 330 pink.
