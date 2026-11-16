# Data cards

The same cards as section 2 of `Week_06_Handout_Sivro_Rodin.docx`, kept here so they can be read on GitHub. The handout is the submitted version.

## Primary dataset

**Name**

DSAI Vault course content. This is the courses/ folder in the repository.

**Link**

No dataset page. The Vault is a study website for DSAI students. We use a copy of its course files, the courses/ folder, kept in the repository so the notebook can be run again.

**Creator and purpose**

We wrote it from our own DSAI courses. It is study material: notes, flashcards, practice problems, exams, formulas and glossary terms. The assistant answers from these files.

**Approximate size**

39 courses, and 11 of them have any content. Those 11 have 71 documents (about 106,000 words), 870 flashcards, 168 practice problems, 53 exam questions, 251 glossary terms and 252 formulas.

**Target or label**

Every card has an answer, a derivation, or a cloze. Every practice problem has a worked solution or a final answer. Most items also have a topic tag. We grade the assistant against these answers. If we fine-tune, only the dev side of the split is trained on.

**License or terms, and course use**

We wrote the notes ourselves from the lectures, and no lecture slides are copied in. Using them for this course is fine. The notes follow the lectures closely, so the repository stays private. The past-paper files are transcriptions of real exams. We can grade against them inside the project. We will not post them anywhere.

**Quality issues**

Coverage is uneven: 11 of 39 courses have content, and those range from 8 cards (MLUT) to 143 (LUGD). All 129 MAI3 cards are tagged measure, although the course lists eight topics. All 53 CDA formulas are plain text, and the other 199 are LaTeX. Some problem sets and both CDA past papers have no topic tag. One card prompt is repeated. There are no missing answers.

**Sensitive content**

Nothing personal in courses/. Accounts and study progress sit in a local database that is not in the repository.

**Why this dataset fits**

The person using this would be a student on these courses. The questions, the answers, and the text to search are already in the files, and we can open them.

## Backup dataset

**Name**

SciQ. Johannes Welbl, Nelson F. Liu and Matt Gardner, 2017.

**Link**

https://allenai.org/data/sciq

**Target or label**

A multiple-choice science answer, and for most of the roughly 13,700 questions, a passage that supports it.

**License or terms, and course use**

CC BY-NC 3.0. Fine for a non-commercial course project.

**Why this is a viable fallback**

Each question comes with a passage, so BM25, the embedding search and the frozen model all run on it without us changing the method. If we cannot use the Vault text, SciQ is the replacement. For the "not covered" check only, the backup is SQuAD 2.0 (CC BY-SA 4.0, https://rajpurkar.github.io/SQuAD-explorer/). The Week 3 feedback asked for a small set written from our own material, so SQuAD is the backup and not the plan.
