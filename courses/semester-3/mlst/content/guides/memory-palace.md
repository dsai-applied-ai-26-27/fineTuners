---
title: 'The memory palace: how to build it and walk it'
summary: 'Twelve rooms of your own home, one per topic, with an exam-ready code pattern at every stop. The technique in six steps, the route, and how to rehearse it.'
---

Twelve rooms of your own home, seventy-seven stops. Every stop holds one exam-ready code pattern or idea, with the theory that justifies it and its arguments decoded. Walk the rooms in order; the order is the index. The palaces are on [the memory page](memory).

:::note The one rule that makes it work
You are not memorising code. You are memorising a *scene*, and the scene tells you which class to write and which decisions to make. Your fingers already know `fit` and `predict`. What goes missing under pressure is *which* object, in *which* order, with *which* arguments. That is what each image stores.
:::

## How to build it

It takes one evening to install and about fifteen minutes a day to keep.

1. **Fix the route before you place anything.** Walk your home once, physically, in this order: front door, hallway, kitchen, the cupboard next to the kitchen, bathroom, living room, desk or work corner, bedroom, balcony or window, a storage cupboard, the highest place you know (attic, loft, top of the stairs), and finally outside on the roof or in front of the building. Say the twelve names out loud until you can recite them cold. That list is your table of contents; nothing else in this page works until it is automatic.
2. **Put one image on one object.** Each station names a real object in that room — the doormat, the sink, the mirror. Stand in front of it in your mind and let the scene happen ON it. Not next to it, not floating. On it.
3. **Make it move, make it wrong.** Memory ignores the reasonable. Exaggerate scale, add motion, add noise and smell, and put yourself in the scene doing something. A kettle that boils is forgettable; a kettle the size of a bathtub that you stir with a canoe paddle is not. The scenes here are already written that way — but they land harder if you rewrite one or two in your own words.
4. **Walk, don't browse.** Learning happens on the walk, not on the page. Close this, start at the front door, and narrate: room, object, image, and only then the code. When a station is blank, come back and re-place it. Blanks are information — they tell you which image was too tame.
5. **Rehearse on a schedule.** Same evening, next morning, two days later, five days later, then weekly. Four short walks beat one long grind. Turn on Recall mode so the code hides and you have to produce it from the image.
6. **Build in three sittings.** Rooms 1–4 tonight, 5–8 tomorrow, 9–12 the day after. Twelve rooms in one evening will not stick, and half-stuck images are worse than none — they give you a false sense of coverage.

## The route

Front door to roof, never backwards. Substitute freely: with no attic, use a stairwell, a garage, a friend's spare room. What matters is that the sequence is fixed and you can walk it with your eyes shut.

| Room | Place | Topic | Stops | Notes |
|---|---|---|---|---|
| 1 | [Front Door](palace:01-front-door) | Framing + first look | 6 | [](guide:01-framing) |
| 2 | [Hallway](palace:02-hallway) | Preprocessing pipeline | 6 | [](guide:02-preprocessing) |
| 3 | [Kitchen](palace:03-kitchen) | Linear regression + gradient descent | 8 | [](guide:03-linear) |
| 4 | [Pantry](palace:04-pantry) | Regularization + early stopping | 4 | [](guide:04-regularization) |
| 5 | [Bathroom](palace:05-bathroom) | Evaluation, metrics, resampling | 9 | [](guide:05-evaluation) |
| 6 | [Living Room](palace:06-living-room) | The classifier zoo | 7 | [](guide:06-classifiers) |
| 7 | [Home Office](palace:07-home-office) | Decision trees (CART) | 5 | [](guide:07-trees) |
| 8 | [Bedroom](palace:08-bedroom) | Support Vector Machines | 6 | [](guide:08-svm) |
| 9 | [Balcony](palace:09-balcony) | Ensembles | 8 | [](guide:09-ensembles) |
| 10 | [Storage Closet](palace:10-storage-closet) | Dimensionality reduction | 5 | [](guide:10-dimred) |
| 11 | [Attic](palace:11-attic) | Sequences: RNNs and 1D CNNs | 7 | [](guide:11-sequences) |
| 12 | [Roof Terrace](palace:12-roof-terrace) | NLP: embeddings, seq2seq, attention | 6 | [](guide:12-nlp) |

Rooms 1 to 4 are everything before and around a linear model; 5 and 6 are how you judge and choose one; 7 to 10 are the model families; 11 and 12 are deep learning on sequences.

:::warning Not for the night before
Twelve rooms in one evening will not stick, and half-stuck images are worse than none: they give a false sense of coverage. With less than three days to go, use [the night-before plan](exam:final) instead.
:::

## Beside the rooms

- [](deck:look-alikes): models that look alike in code and differ in one line.
- [](guide:parameter-reference): every argument, sorted by whether to memorise it, derive it or reason about it.
- [](problems:lab-drills) and the two sample papers under [](exam:final): read the prompt, name the room out loud, write the code on paper, then reveal.
