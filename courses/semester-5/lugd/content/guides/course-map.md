---
title: Course map
summary: How Learning from User-Generated Data is organised and graded, what the seminar and the project ask for, and what to do week by week to pass.
sources:
  - lectures/00 Intro Lecture.pdf
  - misc/c3-notes.md
---

## Organisation

From the introduction lecture (slides 2, 3 and 7). The course is about recommender
systems; its material is adapted from Prof. Francesco Ricci, Free University of
Bozen-Bolzano.

- **Staff:** Associate Professor Amra Delić Halilović (lecturer, office 3-24), teaching
  assistants Esma Karahodza and Vedad Grbo. Consultations by arrangement over e-mail.
- **Lectures:** 30 hours, Friday 14:00 to 17:00, room 2-03.
- **Labs:** 20 hours in 10 labs; timetable to be announced.
- **Material:** on the c3 course page.

What happens in the labs (slide 7): reflecting on the lecture, clarifying doubts, solving
exercises ("you try first"), experimenting with and evaluating some systems, presenting
and discussing papers, and working on the project.

## Grading

| Component | Max points | Minimum to pass |
|---|---|---|
| S: seminar | 10 | 5 |
| P: project, in teams of 2 | 40 | 20 |
| W: written exam | 40 | 20 |
| A: attendance and activity, lectures and labs | 10 | none |
| **F = S + P + W + A** | **100** | |

Three of the four components have their own minimum (slide 13): a strong project does not
make up for a failed exam.

**The written exam** asks "questions like those asked during the lectures (see slides) and
like the exercises in the labs". The lecture slides end with such a list; see
[](exam:final).

## The seminar

- You present **one scientific paper** on a specific recommender systems topic, together
  with your project partner.
- Ideally the paper relates to your project, but it does not have to.
- The papers are pre-selected and are now on the c3 page: eleven of them, summarised in
  [](guide:seminar-papers) to help you choose.
- The seminars run during the labs.

The lecturer announced on C3 that the next lecture is on Friday, 23 October, as scheduled.

## The project

Done in pairs. **Design an innovative recommender system for a specific application
scenario** (health, learning, eGovernment, tourism and so on), choosing among the research
topics and scenarios that will be proposed. The result is

- a written report of **no more than 5,000 words**, and
- a system prototype.

The report has to describe the proposed system and make the innovative approach clear. A
full implementation of GUI and core algorithm is **not** required.

### Structure of the report

| Section | Content |
|---|---|
| Abstract | |
| 1. Introduction | The application and the technical problem; benefits for the users |
| 2. Survey | Existing similar applications and studies in the chosen domain |
| 3. Techniques | The proposed system functions: the pros and cons of the course techniques that could apply to the problem, and the core techniques used in the prototype and how they were applied to this example |
| 4. Evaluation strategy | |

### How it is evaluated

- The report follows the structure above and is clearly written.
- The proposed functions and techniques are innovative, significant and sound.
- The report shows that you investigated the problem and can convince the "client".
- The idea is developed far enough to show some of the potential benefits for users.
- The presentation at the end of the course is understandable and holds the audience.
- The presenters can answer the other participants' questions.

The final report is due on the day of the project presentation, at the end of the course.

## What to do to pass

- [ ] Read and understand the papers suggested for each lecture. The slides give only a
      general understanding of the topic.
- [ ] When something is unclear in a lecture, note it and ask, especially in the labs.
- [ ] Attend lectures and take part in the labs.
- [ ] Choose a seminar paper and prepare its presentation.
- [ ] Start the project in week 4 or 5, and submit a draft for review.
- [ ] Think critically about what the course presents.

:::warning Learn from the papers, not only from the slides
Stated twice in the introduction (slides 8 and 14). The two readings of week one are
written up here: [](guide:reading-resnick-varian-1997) and
[](guide:reading-handbook-introduction).
:::

## Tests

The lecturer announced on C3 (6 November) a first test at the beginning of the lecture on
Friday 13 November: 30 minutes, then the lecture continues. A sample test was published on
9 November; it takes longer than the real one. It is worked through in
[](problems:practice-test-1). It covers [](lecture:01-recommender-systems),
[](lecture:02-collaborative-filtering-i), [](lecture:03-collaborative-filtering-ii) and
[](lecture:04-bayes-classifier). For quick revision there is a deck made for the test,
[](deck:test-1).

## Syllabus

The topics listed on slide 5, after the introduction of
[](lecture:01-recommender-systems):

1. Collaborative filtering ([](topic:cf))
2. Content-based methods ([](topic:content))
3. Group recommender systems ([](topic:group))
4. Evaluation of recommender systems ([](topic:evaluation))
5. Context-aware systems ([](topic:context))
6. Conversational systems ([](topic:conversational))
7. Decision making ([](topic:decision))

What the course wants you to take away (slide 6): the scientific underpinnings and limits
of the field; a catalogue of techniques and tools for designing a recommender system; the
pros and cons of each technique, for every actor involved; the judgement to say when, for
which context and which products, a technique is useful; and the ability to spot new
applications.

## Literature

Research on recommender systems is young: the first works date from around 1995.

- Ricci, Rokach and Shapira (eds.), *Recommender Systems Handbook*, 3rd edition, Springer,
  2022
- Aggarwal, *Recommender Systems: The Textbook*, Springer, 2016
- Further papers shared during the course
