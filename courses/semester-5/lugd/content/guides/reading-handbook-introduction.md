---
title: 'Reading: the Handbook introduction (Ricci, Rokach, Shapira, 2022)'
topics: [intro, cf, content, group, evaluation, context, decision]
summary: The opening chapter of the Recommender Systems Handbook, third edition. Definitions, who a recommender system serves and why, the data it uses, the families of techniques, how systems are evaluated, the human-computer interaction side, and the open challenges. It is a map of the whole course.
sources:
  - misc/Introduction-Handbook-2022.pdf
---

F. Ricci, L. Rokach and B. Shapira, "Recommender Systems: Techniques, Applications, and
Challenges", chapter 1 of the *Recommender Systems Handbook*, 3rd edition, Springer, 2022,
35 pages. The handbook is the course's first recommended book, and this chapter is its
overview: it does not teach any technique in depth, it says where each one lives.

## Definitions

:::definition Recommender system
Software tools and techniques that provide suggestions for items that are most likely of
interest to a particular user. The suggestions relate to decision-making processes: what
to buy, what music to listen to, what news to read.
:::

- **Item** is the general word for what is recommended. A system normally focuses on one
  type of item, and its design, interface and core technique are all tailored to it.
- Recommender systems are aimed at people who **lack the personal experience or
  competence** to evaluate the overwhelming number of items on offer.
- Recommendations are usually **personalised**. Non-personalised ones (a top-ten list) are
  simpler, and useful when nothing is known about the user, but are not the focus of the
  research.
- In the simplest form the output is a **ranked list**; to build it the system predicts
  the most suitable items from the user's preferences and constraints.

**Where it came from.** People rely on others' recommendations for routine decisions. The
first systems mimicked this by using the recommendations of a community for an "active"
user: **collaborative filtering**, on the rationale that if the active user agreed with
certain users in the past, their other recommendations should interest her too. With
e-commerce came the need to filter very large catalogues, and the realisation that "while
choice is good, more choice is not always better". The field has been an independent
research area since the mid-1990s; its main conference, ACM RecSys, dates from 2007.

## Who it is for: stakeholders and value

:::definition Recommendation stakeholder
Any group or individual that can affect, or is affected by, the delivery of
recommendations to users. Three matter most: **consumers** (the users), **providers** (who
supply the items) and the **system owner** (who built the platform).
:::

Why providers and owners want a recommender (section 2):

| Reason | Meaning |
|---|---|
| Increase the number of items sold | More precisely, raise the **conversion rate**: users who accept a recommendation and consume an item, against visitors who only browse |
| Sell more diverse items | Help users find items that are hard to find without a precise recommendation, not only the "blockbusters" |
| Increase user satisfaction | Accurate recommendations with a usable interface raise the user's evaluation of the system |
| Increase user fidelity | The system recognises a returning user, and the longer she interacts the better her model becomes |
| Understand what the user wants | The collected or predicted preferences can be reused, for instance for stock or promotion decisions |

A recommender has to balance the needs of all three stakeholders, which is why evaluation
has to look at more than the end user.

**What users use it for.** Eleven tasks, after Herlocker et al.:

| Task | In short |
|---|---|
| Find some good items | A ranked list, perhaps with predicted ratings. The main task |
| Find all good items | When missing one is costly: medical, financial, small catalogues |
| Annotation in context | Mark, within an existing list, the items worth attention |
| Recommend a sequence | A next item, a series, a playlist |
| Recommend a bundle | A group of items that fit together, such as a travel plan |
| Just browsing | Help to browse what is likely to be of interest in this session |
| Find a credible recommender | Users test how good the system is |
| Improve the profile | Tell the system what one likes and dislikes |
| Express self | Contributing ratings and opinions matters to the user in itself |
| Help others | Contribute because the community benefits |
| Influence others | Push others towards items, sometimes maliciously |

## Data and knowledge sources

Three kinds of object (section 3):

- **Items.** Features come from metadata or have to be extracted, from text with NLP or
  from images, which can ease the **cold start** of items with few interactions.
- **Users.** The data about a user is the **user model**: in collaborative filtering just
  a list of ratings; in context-aware systems it includes contextual information; in
  content-based systems the features of the items she consumed.
- **Interactions.** Logs of what users did with items, of which the feedback is the
  important part.

| | Explicit feedback | Implicit feedback |
|---|---|---|
| What | Stated by the user: ratings | Inferred from behaviour: clicking, buying, adding to basket |
| Forms | Numerical (1 to 5 stars), ordinal (agree to disagree), binary (good or bad) | Unary: no level of preference |
| Strength | More reliable; gives a level of preference | Available for many more items, at no effort to the user |
| Weakness | Often unavailable or very sparse | Noisy, a weak positive signal; **absence of an interaction is not negative feedback** (disliked, never seen, or already consumed?) |

Data also differs in **time span**. A known, registered user has a long-term profile. For
a guest, or a user whose intent changes from visit to visit, the system can learn only
from the current session: **session-based recommendation**.

## Recommendation techniques

**The unifying view.** The system predicts the **utility** (or evaluation) of user $u$ for
item $i$, a real-valued function $R(u, i)$. It computes estimates
$\hat R(u, i_1), \dots, \hat R(u, i_N)$ for the active user and recommends the $K$ items
with the largest predicted utility, with $K$ much smaller than the catalogue. Even
"recommend the most popular songs" fits: popularity is a prediction of utility for a
generic user. Utility can also depend on **context**, such as time and location.

The classical taxonomy (Burke):

| Class | Recommends | Note |
|---|---|---|
| Content-based | Items similar to those the user liked, by item features | Keywords from descriptions; semantic techniques use concepts instead |
| Collaborative filtering | What users with similar tastes liked | "People-to-people correlation". The most popular and widely implemented |
| Community-based | What the user's friends prefer | Social recommender systems. People trust friends more than similar strangers |
| Demographic | By the user's demographic profile | Simple personalisation by language, country, age |
| Knowledge-based | By domain knowledge of how item features meet needs | Strong at the start of deployment; overtaken by learning methods unless it learns |
| Hybrid | A combination | Use the strengths of A to fix the weaknesses of B, for instance content-based prediction for the new items collaborative filtering cannot handle |

Inside collaborative filtering:

- **Neighbourhood methods** work on relationships between users or between items. The
  choice between them is the decision with the greatest effect. Where users outnumber
  items, as in typical commercial systems, **item-based** is preferred: more accurate,
  more efficient, less often updated. **User-based** tends to give more original
  recommendations.
- **Sparsity and limited coverage** are addressed by dimensionality reduction and by
  graph-based techniques.
- **Latent factor models** such as matrix factorization (SVD) map users and items to one
  latent space inferred from feedback.
- **Deep learning** has been applied since about 2010: it needs less feature engineering
  and handles raw text, sound, image and video.

**Context-aware systems** use context in one of three ways: **pre-filtering** (use only
the data matching the current context), **post-filtering** (compute without context, then
adjust the output), or **contextual modelling** (context inside the model).

**Special techniques** (section 5): group recommender systems, where individual models
must be combined; adversarial attacks and defences; reciprocal, people-to-people
recommenders that must satisfy both sides, as in dating or jobs; and cross-domain
recommenders that reuse data from one domain in another, easing cold start.

## Evaluation

Three kinds of experiment (section 6):

| Kind | How | Limit |
|---|---|---|
| **Offline** | Run algorithms on stored interaction data and compare them along several metrics | Says nothing about user satisfaction, acceptance or experience |
| **Online** | Real users use the system, often in several versions for different groups, and the logs are analysed | Needs a deployed system |
| **User study** | A small group performs tasks with versions of the system in a controlled experiment; questionnaires | Used when online evaluation is infeasible or too risky |

Points to keep:

- A system can be accurate and still not accepted. And a user may be unable to judge a
  "correct" recommendation at once: a song can be played immediately, a book cannot.
- The goals of a recommender **extend beyond accuracy**. The evaluation chapter is
  organised by properties: coverage, cold start, confidence, trust, novelty, risk,
  serendipity.
- **Multistakeholder** evaluation also asks how providers fare: those never recommended
  lose interest and leave, which in turn makes the platform less useful to users.
- **Impact.** On platforms like YouTube or Netflix a large share of interactions comes
  from recommendations, and a self-reinforcing cycle can narrow what is recommended,
  defeating information discovery.
- **Fairness** is a further dimension, complicated here by multiple stakeholders, ranked
  outputs and personalisation.
- The Netflix Prize (2006) accelerated research but addressed a simplification: predicting
  ratings while optimising RMSE.

## The human side

The assumption that presenting the "correct" recommendations is enough is "clearly an
overly simplified account" (section 7). Users need recommendations precisely because they
lack the knowledge to decide, so they cannot easily judge what they are shown.

- **Swearingen and Sinha:** effectiveness depends on more than the algorithm. The system
  must inspire trust, have a logic that is at least somewhat transparent, point to new
  items, give details about them, and offer ways to refine the recommendations.
- **McNee et al.:** accuracy metrics such as MAE, precision or NDCG are not enough;
  evaluate the similarity of recommendation lists, serendipity, and user needs and
  expectations.
- **Decision making:** a recommender is one of many tools for facilitating choice, so the
  psychology of everyday choice applies.
- **Personality** (the Five Factor Model) helps with cold start and with diversity, and
  can be acquired by questionnaire or inferred from data.
- **Explanations** justify results, increase trust, persuade, and help the decision.
  Whether they improve choices or bias them is an open question.

## Applications and challenges

Five broad application domains: **entertainment** (films, music, games), **content**
(news, documents, e-learning), **e-commerce**, **services** (travel, experts, housing,
matchmaking) and **social** (people and social media content).

Open challenges the authors single out (section 9):

- **Preference acquisition.** Implicit feedback is plentiful but only "positive or
  missing"; explicit feedback remains central where users also interact with each other,
  as in group systems. Lowering the cognitive cost of giving preferences matters.
- **Interaction.** How input is given and output presented can decide success or failure.
  Users often do not know their preferences beforehand and *construct* them during the
  session.
- **New recommendation tasks.** Complex, configurable products; sequences of
  recommendations that lead somewhere, as in learning or food; proactive recommendations
  on mobile devices, pushed when the context makes them welcome.

## Where the course topics are in this chapter

| Course topic | In the chapter |
|---|---|
| [](topic:cf) | Section 4: neighbourhood methods, latent factor models, implicit feedback, deep learning |
| [](topic:content) | Section 4: content-based and semantic approaches; knowledge-based; hybrid |
| [](topic:group) | Section 5: group recommender systems |
| [](topic:evaluation) | Section 6: offline, online, user studies; properties beyond accuracy; fairness |
| [](topic:context) | Sections 3 and 4: session-based and context-aware systems, the three paradigms |
| [](topic:conversational) | Touched only through interaction and preference elicitation in sections 7 and 9 |
| [](topic:decision) | Section 7: decision making, personality, explanations |

:::recall Why is a missing interaction not negative feedback?
Because there is usually not enough data to say why it is missing: the user may dislike
the item, may never have seen it, or may have consumed it already elsewhere.
:::
