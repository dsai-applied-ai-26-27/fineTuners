---
title: 'Reading: Resnick and Varian, Recommender Systems (1997)'
topics: [intro, cf]
summary: The three-page paper that named the field. What a recommender system is, the five design dimensions that distinguish early systems, the incentive and privacy problems, and the business models, with their link to lecture 1.
sources:
  - misc/resnick-varian97.pdf
---

P. Resnick and H. R. Varian, "Recommender Systems", *Communications of the ACM* 40(3),
March 1997, pp. 56 to 58. It is the guest editors' introduction to a special section
describing five systems, and one of the first works of the field (the course dates the
field from about 1995).

## The idea

We often have to choose without enough personal experience of the alternatives. In daily
life we lean on other people: word of mouth, recommendation letters, reviews, restaurant
guides. Recommender systems **assist and augment this natural social process**.

:::definition Recommender system, in the paper's sense
A system in which people provide recommendations as inputs, which the system then
aggregates and directs to appropriate recipients. Its value may lie in the aggregation, or
in matching recommenders with those seeking recommendations.
:::

**Why not "collaborative filtering"?** The developers of the first such system, Tapestry,
coined that phrase. The authors prefer "recommender system" for two reasons:

1. recommenders may not explicitly *collaborate* with recipients, who may not even know
   each other;
2. recommendations may point out particularly interesting items, not only *filter* out the
   bad ones.

## The technical design space

Five dimensions distinguish the systems (figure 1 of the paper):

1. **Contents of an evaluation:** anything from a single bit (recommended or not) to
   unstructured text.
2. **Explicit or implicit entry:** typed in by people, or gathered from behaviour.
3. **Identity:** anonymous, attributed to the source, or under a pseudonym.
4. **Aggregation:** how the evaluations are combined. The authors call this one of the
   richest areas for exploration.
5. **Use:** filter out negatively rated items, sort by the evaluations, or display the
   evaluations next to the items.

| System | Evaluation | Entry | Identity | Aggregation | Use |
|---|---|---|---|---|---|
| GroupLens | Numeric 1 to 5; reading time in seconds | Explicit; monitored reading time | Pseudonymous | Personalised weighting by past agreement among recommenders | Shown beside articles in existing summary views |
| Fab | Numeric 1 to 7 | Explicit | Pseudonymous | Personalised weighting, combined with content analysis | Selection and filtering |
| ReferralWeb | Mention of a person or a document | Mined from public data | Attributed | Referral chain assembled to the desired person | Display |
| PHOAKS | Mention of a URL | Mined from Usenet postings | Attributed | One person, one vote per URL | Sorted display |
| Siteseer | Mention of a URL | Mined from existing bookmark folders | Anonymous | Frequency of mention in overlapping folders | Display |

Three of the five already mine **implicit** evidence (reading times, mentions,
bookmarks), and Fab is an early **hybrid** of collaborative weighting and content
analysis. Both ideas return in lecture 1.

## The domain space

The right design depends on what is recommended and among whom (figures 2 and 3).

**The items.** Their volume matters: detailed text reviews are practical for restaurants
or films, not for thousands of daily Netnews messages. So does their lifetime: short-lived
media need evaluations gathered and distributed fast. And so does the **cost structure**
of a choice: how costly is it to miss a good item or to sample a bad one, compared with
the benefit of hitting a good one? When wrong decisions are costly, as with medical
treatments, evaluations that carry more nuance are more useful.

| System | Items | Volume | Lifetime | Cost structure |
|---|---|---|---|---|
| GroupLens | Netnews articles | Thousands a day | 1 to 2 weeks | Misses unimportant; a false positive costs very little; hits have small value |
| PHOAKS, Siteseer, Fab | URLs | Hundreds a day | 2 days to 2 years | Misses unimportant; false positives cost little; hits have medium value |
| ReferralWeb | People | A few million reachable online | Many years | Depends on how the referral chain is used |

**The people.** Who provides recommendations, and do they evaluate many items in common,
giving a dense set of recommendations? How many consumers are there, and how much do
their tastes vary? Matching people by taste automatically is far more valuable in a large
set of people who do not know each other, and personalised aggregation is more valuable
when tastes differ than when a few experts suffice. GroupLens and Fab are "somewhat
dense"; PHOAKS is "extremely sparse".

## Social implications

**Two incentive problems.**

- **Free riding.** Once you have a profile of interests it is easy to consume other
  people's evaluations and contribute none. Gathering evaluations implicitly does not
  fully solve this. Future systems will probably need incentives: making contribution a
  prerequisite for receiving recommendations, or paying for it.
- **Manipulation.** If anyone can recommend, content owners can generate mountains of
  praise for their own material and criticism of competitors: "vote early and often".

**Privacy.** The more people know about the recommendations, the better they can evaluate
them, but people may not want their habits or views widely known. Anonymity and pseudonyms
are not a complete answer, since some want a blend of privacy and credit for their effort.

:::note The analogy the paper offers
Academic peer review is an evaluation-sharing system with the same two problems. On
incentives: every editor knows the best source of a prompt, careful review is an author
with a paper under consideration. On privacy: blind and double-blind refereeing. Those
practices evolved to solve problems inherent in refereeing and may be worth building into
automated systems.
:::

## Business models

Running a recommender is costly. Three ways to pay for it:

1. charge the **recipients**, by subscription or pay-per-use;
2. **advertiser** support, attractive because the system yields detailed marketing
   information about consumers;
3. charge the **owners of the evaluated items**, as film-makers pay for official ratings.

The last two carry a **danger of corruption**: magazines carrying both ads and reviews are
accused of favouring advertisers, and the *perception* of bias is almost as bad as the
reality. A system taking money from interested parties must keep unbiased recommendations
and advertisements clearly apart.

**Economies of scale.** The bigger the set of users, the more likely I am to find someone
like me, so other things being equal I prefer the biggest system. Competing systems in one
market should therefore fight intensely and leave one or two big players per medium or
subject area, who might sell recommendations to many sellers as a service. An independent
rating service would also help with credibility.

## Reading it next to lecture 1

| In the paper (1997) | In lecture 1 |
|---|---|
| People rely on others' recommendations when they lack experience | Recommender systems help when we lack knowledge or face an overabundance of options |
| Explicit entry against implicit evaluations (reading time, mentions) | Explicit against implicit preferences, and why both are biased |
| "Personalised weighting based on past agreement among recommenders" | User-to-user collaborative filtering |
| Cost structure of a choice | Expected utility of an item depends on context |
| Privacy; credibility of a system paid by interested parties | Privacy risks; multistakeholder systems; fairness |
| Manipulation, "vote early and often" | Adversarial attacks on recommender systems, in the handbook |

:::recall Why did Resnick and Varian prefer "recommender system" to "collaborative filtering"?
Because recommenders need not collaborate with the recipients, who may not know each
other, and because recommendations can highlight interesting items and not only filter
out bad ones.
:::
