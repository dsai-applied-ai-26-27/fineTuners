---
title: 'Seminar papers: the eleven to choose from'
topics: [group, evaluation, context, conversational, decision]
summary: The eleven papers on the courseware for the seminar presentation, each with what it asks, what the authors did, what they found and which part of the course it belongs to, to help you and your project partner pick one.
takeaways:
  - You present one paper together with your project partner, during the labs. The seminar is worth 10 points, with 5 needed to pass.
  - Ideally the paper is related to your project, though it does not have to be.
  - The papers cluster around three themes, evaluation beyond accuracy (diversity, user bias, dynamic preferences, simulated users), explanations, and LLM-based systems, plus one each on groups, tourism, location and misinformation.
sources:
  - misc/seminar-papers/Alves-tourism-2022.pdf
  - misc/seminar-papers/Consensus vs. Dissent - Dynamic LLM Modeling of Subjective Preferences in Group Recommenders.pdf
  - misc/seminar-papers/Curmei-psychologically-gounded-2022.pdf
  - misc/seminar-papers/DoWe Care About Personalization and Explainability An Interview Study with News Recommendation Engineers.pdf
  - misc/seminar-papers/Gedikli-Explanations-2014.pdf
  - misc/seminar-papers/Hansen-diverse-music-2021.pdf
  - misc/seminar-papers/Safety-Aware Next-POI Recommendation with Large Language.pdf
  - misc/seminar-papers/Simulating Diverse User Behavioral Stereotypes for Evaluating Agentic Conversational Recommenders.pdf
  - misc/seminar-papers/Tommasel-misinformation-2022.pdf
  - misc/seminar-papers/Wang-bias-2021.pdf
  - misc/seminar-papers/When Do Contrastive Explanations Really Matter in Recommender Systems.pdf
  - misc/c3-notes.md
---

## How the seminar works

From the introductory lecture ([](guide:course-map)):

- You present **one scientific paper** on a recommender-systems topic, **together with the
  colleague you do the project with**.
- Ideally the paper relates to your project, but it does not have to.
- The papers were selected by the lecturer and are in the "Seminars - Papers" folder on
  the courseware. The seminars run during the labs.
- The seminar is worth **10 points, with a minimum of 5** to pass.

The summaries below are written from each paper's abstract and first pages, to help you
choose. They are not a substitute for reading the one you pick: the lecturer says "you must
learn from the papers, not only from the slides".

## At a glance

| Paper | Year, venue | Course topic | Kind of study |
|---|---|---|---|
| Tourists' personality | 2020, UMAP | Context, personalisation | Survey of 508 people, factor analysis |
| Consensus vs. dissent | 2026, RecSys | Group recommenders | Fine-tuned LLMs, user study of 284 |
| Psychologically grounded preferences | 2022, RecSys | Evaluation, user modelling | Models and simulation |
| Do we care about explainability? | 2026, RecSys | Explanations, practice | 15 interviews in 9 news organisations |
| How should I explain? | 2014, IJHCS | Explanations, evaluation | User study of 10 explanation types |
| Diverse music | 2021, WSDM | Evaluation beyond accuracy | Spotify rankers, including reinforcement learning |
| Safety-aware POI | 2026, RecSys | Context-aware | Fine-tuned LLM with crime data |
| Simulated user stereotypes | 2026, RecSys | Conversational, evaluation | User simulator, four systems benchmarked |
| Misinformation spreaders | 2022, RecSys | Social impact, collaborative filtering | Friend recommenders on COVID-19 Twitter data, simulation |
| User bias beyond accuracy | 2021, RecSys | Evaluation, fairness | Survey data of over 11,000 users |
| Contrastive explanations | 2026, RecSys | Explanations, decision making | User study of 87, three domains, three algorithms |

## The papers

### Tourists' personality and preferences for attractions

Alves, Saraiva, Carneiro, Campos, Martins, Marreiros et al., *Modeling Tourists'
Personality in Recommender Systems: How Does Personality Influence Preferences for Tourist
Attractions?* UMAP 2020. (The file on the courseware is named 2022.)

- **Question.** Does a tourist's personality (the Big Five dimensions) predict which kinds
  of attractions they prefer?
- **What they did.** An online questionnaire answered by 508 Portuguese people from
  academia and their relatives and friends; exploratory and confirmatory factor analysis
  grouped attractions into 11 categories, then they tested which personality dimensions
  predict preference for each.
- **Result.** The first model relating the five personality dimensions to preferences for
  tourist attractions, meant as a base for recommenders that model tourists from their
  personality.
- **Good fit if** your project is in tourism, or uses psychological traits to address the
  cold-start problem.

### Consensus vs. dissent: LLMs choosing a group aggregation strategy

Waterschoot, Tintarev and Barile, *Consensus vs. Dissent: Dynamic LLM Modeling of
Subjective Preferences in Group Recommenders.* RecSys 2026.

- **Question.** In a group recommender, the best way to aggregate members' preferences
  depends on how preferences are spread in the group. Can an LLM pick the aggregation
  strategy that people would judge fairest and most satisfying?
- **What they did.** Fine-tuned LLMs ("Judgmental Llama" and "Judgmental OLMo") on human
  survey data and reasoning distilled from DeepSeek-V3.1, used them to judge candidates
  produced by social-choice aggregation strategies, and validated the choices in a user
  study with 284 participants.
- **Result.** Highest satisfaction and group consensus scores; the LLM's judgments matched
  people best when the group's configuration (for example a minority, or a coalition) was
  taken into account.
- **Good fit if** your project recommends for groups (friends, families, teams), or you
  want an LLM paper with a clear user study.

### Psychologically grounded dynamic preference models

Curmei, Haupt, Hadfield-Menell and Recht, *Towards Psychologically-Grounded Dynamic
Preference Models.* RecSys 2022.

- **Question.** Recommendations change what people like. How should those changing
  preferences be modelled so that the models are psychologically plausible?
- **What they did.** A method for building dynamic preference models grounded in
  psychology, shown on three classic effects: **mere exposure** (liking what you see
  often), **operant conditioning** (reward shapes behaviour) and **hedonic adaptation**
  (pleasure fades with repetition). Simulations show how each behaves.
- **Result.** The models behave distinctly and can inform design; the method critiques
  earlier models with implausible predictions; and engagement and diversity metrics may
  fail to capture what a good recommender should do.
- **Good fit if** you like modelling and simulation, or your project worries about
  feedback loops and filter bubbles.

### Do news engineers care about personalisation and explainability?

Kareem, Mehrotra, Willemsen and de Rijke, *Do We Care About Personalization and
Explainability? An Interview Study with News Recommendation Engineers.* RecSys 2026.

- **Question.** Explainability research focuses on end users. How do the engineers who
  build news recommenders see personalisation and explainability?
- **What they did.** 15 semi-structured interviews in nine news organisations, public and
  private, across regions.
- **Result.** Personalisation is not always wanted (user tracking, editorial control and
  resources limit it); even where it is in production, explainability is rarely a priority
  and is defined very differently between organisations. The paper ends with practical
  guidelines for adopting explainability in a news pipeline.
- **Good fit if** your project is about news or media, or you prefer a qualitative study
  to an algorithmic one.

### How should I explain? Ten explanation types compared

Gedikli, Jannach and Ge, *How should I explain? A comparison of different explanation
types for recommender systems.* International Journal of Human-Computer Studies 72 (2014).

- **Question.** Which way of explaining a recommendation works best for users?
- **What they did.** A user study with 10 explanation types, known visualisations from the
  literature plus two new ones based on tag clouds, measured on several dimensions.
- **Result.** Content-based **tag cloud** explanations raised perceived transparency and
  satisfaction, even though they demand more cognitive effort. The paper derives guidelines
  for designing or selecting explanations.
- **Good fit if** your prototype shows users why something was recommended. The oldest
  paper on the list, and a journal article rather than a conference paper.

### Shifting consumption towards diverse music

Hansen, Mehrotra, Hansen, Brost, Maystre and Lalmas (Spotify and University of
Copenhagen), *Shifting Consumption towards Diverse Content on Music Streaming Platforms.*
WSDM 2021.

- **Question.** Can recommendations shift listening towards less popular music and away
  from users' usual tastes, without losing satisfaction?
- **What they did.** Two notions of diversity (taste similarity and popularity); four
  rankers of increasing complexity, including a feedback-aware neural ranker and a
  reinforcement learning ranker; four ways to add diversity explicitly (interleaving,
  submodularity, interpolation, RL reward modelling).
- **Result.** More complex models gain satisfaction but lose diversity; the RL
  reward-modelling approach gives the best trade-off.
- **Good fit if** your project touches popularity bias, filter bubbles or beyond-accuracy
  evaluation.

### Safety-aware next-POI recommendation with LLMs

Zaboura, Boratto and Solomon, *Safety-Aware Next-POI Recommendation with Large Language
Models.* RecSys 2026.

- **Question.** Point-of-interest recommenders optimise relevance. Can they also account
  for the user's safety?
- **What they did.** Combined crime statistics with POI data, encoded safety information
  into the trajectory prompts, and fine-tuned an LLM to predict the next POI.
- **Result.** Recommended places are substantially safer, and overall accuracy beats
  state-of-the-art baselines.
- **Good fit if** your project is location-based, in tourism or mobility, or about
  context-aware recommendation.

### Simulating user stereotypes to evaluate conversational agents

Petruzzelli, Martina, Musto et al., *Simulating Diverse User Behavioral Stereotypes for
Evaluating Agentic Conversational Recommenders.* RecSys 2026.

- **Question.** Conversational recommenders are evaluated with simulated users who know
  exactly what they want. What happens with users who are vague?
- **What they did.** An open-weight user simulator conditioned on three stereotypes:
  **Direct**, **Vague-Proactive** and **Vague-Reactive**; four state-of-the-art agentic
  conversational recommenders benchmarked across four e-commerce domains.
- **Result.** Three findings: "Unproductive Stagnation" (the user stops adding information
  while the agent keeps acting), a "Robustness Gap" (accuracy collapses as users get more
  passive, while conversations grow longer), and evidence that eliciting preferences and
  retrieving items are separate abilities that one accuracy score mixes together.
- **Good fit if** your project is a chatbot-style or conversational recommender.

### Do recommenders help misinformation spreaders?

Tommasel and Menczer, *Do Recommender Systems Make Social Media More Susceptible to
Misinformation Spreaders?* RecSys 2022 (short paper, 6 pages).

- **Question.** Do friend ("who to follow") recommenders increase the influence of
  accounts that spread misinformation?
- **What they did.** Applied several user recommenders (link prediction) to a COVID-19
  misinformation dataset from Twitter, and simulated "what-if" changes in spreading
  behaviour on the recommended network.
- **Result.** Recommenders can indeed change how misinformation spreaders interact with
  other users and how much they influence them.
- **Good fit if** you are interested in the social effects of recommenders. The shortest
  paper on the list.

### User bias in beyond-accuracy measurement

Wang et al. (Hong Kong Baptist University), *User Bias in Beyond-Accuracy Measurement of
Recommendation Algorithms.* RecSys 2021.

- **Question.** Do recommendation algorithms serve different groups of users differently
  on relevance, diversity, novelty, unexpectedness and serendipity, not just accuracy?
- **What they did.** A survey dataset from a commercial platform with over 11,000 users'
  ratings of those five objectives and eight user characteristics (gender, age, the Big
  Five, curiosity); four algorithms compared (HOT, Rel-CF, Nov-CF, Ser-CF).
- **Result.** Biases between user groups exist on these measures; part of them comes from
  how groups use ratings (some give more positive ratings), and the authors separate
  problematic biases that may lead to unfairness.
- **Good fit if** your project evaluates fairness or beyond-accuracy metrics; it connects
  directly to the evaluation lecture.

### When do contrastive explanations matter?

Tran, Lubos, Felfernig et al. (Graz University of Technology), *When Do Contrastive
Explanations Really Matter in Recommender Systems?* RecSys 2026.

- **Question.** Besides "why this item", systems can explain contrastively: "something
  different?" or "why not item Y?". When are such explanations worth it?
- **What they did.** A user study with 87 participants, two contrastive explanation types,
  three domains (movies, shopping, housing) and three algorithms (collaborative filtering,
  content-based, constraint-based).
- **Result.** Contrastive explanations do not consistently beat ordinary ones; the
  benefit is selective, most needed for constraint-based recommenders, and (descriptively)
  in higher-involvement decisions like housing. They should be offered selectively.
- **Good fit if** your project explains recommendations, or uses constraint-based
  (knowledge-based) recommendation for a decision.

## Choosing with your partner

1. **Start from the project.** Same domain (tourism, music, news, location) or the same
   kind of system (groups, conversation, explanations) makes the seminar feed the report.
2. **Pick the method you can explain.** A user study or interview study is easier to
   present than fine-tuning LLMs; a simulation paper needs comfort with models.
3. **Check the length.** Most are 10 pages; the misinformation paper is 6, the
   psychological models paper 14, the explanation-types journal paper 16.
4. **Split the talk by section**, not by slide: one of you takes question and method, the
   other results and limitations, and both should be ready for questions on all of it.

## Where next

- How the course and the project are organised: [](guide:course-map).
- The evaluation and beyond-accuracy ideas several papers use start with
  [](lecture:01-recommender-systems).
