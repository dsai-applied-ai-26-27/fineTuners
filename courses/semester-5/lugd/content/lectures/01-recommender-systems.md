---
title: 'Recommender systems: a human-centred perspective'
number: 1
topics: [intro]
summary: Why too much choice is a problem, what a recommender system does about it, and its three steps of eliciting preferences, predicting them and presenting recommendations, with the human biases that affect each step and the properties beyond accuracy that matter.
takeaways:
  - Information overload is having too much information to decide or stay informed. More choice is not always better, and recommender systems exist to help people choose when they lack knowledge or face an overabundance of options.
  - 'A recommender system works in three steps: preference and behaviour elicitation, preference or behaviour prediction, and selecting and presenting the recommendations.'
  - Preferences are collected explicitly (ratings, likes, pairwise comparisons) or implicitly (clicks, visits). Both are biased, and actions are hard to interpret.
  - Collaborative filtering predicts a missing rating from the ratings of similar items or of similar users. Matrix factorization does it by learning latent features of users and items.
  - How recommendations are presented changes how they are valued. Anchoring and the attraction effect show that the decision context shapes the expected utility of an item.
  - Precision is one property among several. Diversity, fairness and privacy matter too, they trade off against each other, and users are not the only stakeholders.
sources:
  - lectures/01 Recommender Systems.pdf
---

## Where this fits

The first content lecture is an overview of the whole field, told from the user's side:
every later topic of the course (collaborative filtering, content-based methods,
evaluation, context, conversation, decision making) appears here once, in one sentence or
one example. The lecture closes with ten questions, and the written exam asks "questions
like those asked during the lectures", so those ten are the first exam material of the
course. Organisation and grading are in [](guide:course-map).

## Too much choice

A trip to one supermarket (slide 3): 85 kinds of crackers, 285 of cookies, 275 of cereal,
230 soups, 175 salad dressings, 360 types of shampoo and conditioner. And choice has
spread to domains that used to offer none: telephone services, pensions, medical care,
news, how to work, how to love, how to be.

:::definition Information overload
The state of having too much information to make a decision or to remain informed about a
topic.
:::

Search engines help to look content up. But deciding, or staying informed, needs an
**exploratory search** (comparison, knowledge acquisition, product selection), and there
the user is stuck three times over (slide 6):

- she is not aware of the range of available options;
- she may not know what to search for;
- presented with results, she may not be able to choose.

**Deciding has a cost.** Neuroscientists report that unproductivity and loss of drive can
follow from decision overload: the brain makes a limited number of decisions per day, and
processing information to separate the trivial from the important is tiring. The
processing capacity of the conscious mind is estimated at 120 bits per second (slide 7).

**The paradox of choice.** More choice means more freedom, autonomy and self-determination,
and the standard argument says added options can only help: those who care benefit, the
rest can ignore them. Yet assessments of well-being show that increased affluence comes
with *decreased* well-being (B. Schwartz, *The Paradox of Choice*, 2004).

:::recall Is having more choices always good?
No. Each option adds a cost of processing and deciding. Past a point, more options lower
well-being instead of raising it, which is Schwartz's paradox of choice.
:::

## What a recommender system is for

The goal (slide 10) is to add a recommendation function to a system so that it recommends
items that are **good for you**: relevant, timely, improving well-being, supporting
rational choices, and reducing search cost. The direction of travel is that queries
disappear: the system leverages multiple signals instead of waiting to be asked (slide 9).

How much this matters commercially: 170 engineers at Amazon work on the recommender
system, and recommendations account for about 60% of all video clicks from the YouTube
home page (slides 11 and 12).

## The three steps

Every recommender system does three things (slide 14):

1. **Preference and behaviour elicitation.** Find out what the user likes or does.
2. **Preference or behaviour prediction.** Build a model that fills in what is not known.
3. **Selecting and presenting the recommendations.**

The rest of the lecture walks through them in order.

## Step 1: eliciting preferences

Besides preferences, systems also use the user's characteristics, such as age or
personality (slide 15).

| Signal | What the user does | Example from the slides |
|---|---|---|
| Ratings | Scores an item explicitly | Amazon's stars, with the boxes "I own it", "Not interested", "This was a gift", "Don't use for recommendations" |
| Likes and reactions | Picks one of several emotional reactions | Reaction icons. Collecting them lets the system predict our reaction to new items |
| Pairwise preferences | Says which of two items is preferred | Two movies side by side with a slider between them |
| Conditional preferences | A preference that holds only under a condition | CP-network: "red shirt is preferred to white shirt if jacket and pants are black" |
| Implicit choices | Just acts | A visited link in a journal's table of contents |

Slide 16 asks why Amazon wants this additional information and leaves the answer to the
room. The answer the rest of the lecture supports: a purchase is ambiguous evidence. A
gift says little about the buyer's own taste, and an item already owned should not be
recommended again.

**Pairwise preferences** make users more aware of their choice options, and a system built
on them outperformed a rating-based one in recommendation accuracy (Blédaité and Ricci
2015; Kalloori, Ricci and Tkalčič 2016).

### Why the collected preferences cannot be taken at face value

The system interprets actions such as a click and turns them into information about
preferences. But people are "strange", and goals are hard to read from actions (slide 22).

:::note The peak-end rule (Kahneman)
What we remember of an experience is determined by how it felt at its **peak** (best or
worst) and how it felt when it **ended**. We use that summary to decide whether to repeat
the experience. So how well do we know what we want? It is doubtful that we truly prefer
one experience to a very similar one just because the first ended better.
:::

**How reliable are explicit preferences?** (slide 24)

- They cover a very small part of the catalogue.
- They depend on context, and the context is unknown to the system.
- They are biased towards good choices: we tend not to experience what we do not like, so
  we never rate it.
- They are biased by imprecise memory, as the peak-end rule shows.

**Implicit preferences** are ambiguous in their own way. The slide shows the duck-rabbit
drawing: the same observation supports two readings. A click may mean interest, curiosity
or a mistake.

## Step 2: building the model

### The data

The lecture's toy data is hotel ratings (slide 27): rows of (user, hotel, context, rating)
such as (U1, H301, Business, 4). The **training data** has the rating; the **test data**
has the same kind of row with the rating to be predicted, for instance
(U1, H301, Family, ?). Real systems use many more user and item characteristics and
contextual variables.

Stacked up, ratings form a **matrix** with users as rows and items as columns, and it is
mostly empty. For Netflix: $10^8$ users and $10^5$ items give $10^{13}$ entries, about
10,000 GB (slide 28).

### Collaborative filtering

The running example (slides 29 and 30):

| | The Matrix | Titanic | Die Hard | Forrest Gump | Wall-E |
|---|---|---|---|---|---|
| John | 5 | 1 | | 2 | 2 |
| Lucy | 1 | 5 | 2 | 5 | 5 |
| Eric | 2 | **?** | 3 | 5 | 4 |
| Diane | 4 | 3 | 5 | 3 | |

Write $r^*_{u,i}$ for the predicted rating of user $u$ for item $i$ and $w$ for a
similarity weight.

:::example Item-to-item: predict from similar items
Use the two items most similar to Titanic, namely Forrest Gump and Wall-E, with
$w_{\text{titanic, forrest}} = 1$ and $w_{\text{titanic, wall-e}} = 0.9$. Eric rated them
$5$ and $4$. The prediction is the similarity-weighted average of **Eric's own ratings**
of those neighbours:

$$r^*_{\text{eric, titanic}} = \frac{0.9 \cdot 4 + 1 \cdot 5}{0.9 + 1} = \frac{8.6}{1.9} = 4.53 .$$
:::

:::example User-to-user: predict from similar users
Use the one user most similar to Eric, namely Lucy, with $w_{\text{eric, lucy}} = 0.9$.
Lucy rated Titanic $5$. The prediction is the similarity-weighted average of **the
neighbours' ratings** of the target item:

$$r^*_{\text{eric, titanic}} = \frac{0.9 \cdot 5}{0.9} = 5 .$$

The same approach for Die Hard gives $r^*_{\text{eric, die-hard}} = 2$, Lucy's rating. But
Eric's real rating is $3$. Comparing a prediction with a known rating like this is exactly
what train and test means.
:::

:::pitfall Which ratings go into the average
Item-to-item averages the **target user's** ratings of neighbouring **items**.
User-to-user averages neighbouring **users'** ratings of the **target item**. Both divide
by the sum of the weights used. With a single neighbour the weight cancels and the
prediction is just that neighbour's rating.
:::

### Latent factors and matrix factorization

A **latent factor model** places users and items in one space of hidden features. The
slide's picture (31) has two axes, serious against escapist and geared towards males
against geared towards females: *Braveheart* sits serious and male-oriented, *The Princess
Diaries* escapist and female-oriented, *Ocean's 11* near the middle, and users are dots in
the same plane, close to the films they like.

:::definition Matrix factorization (MF)
Predicts unknown ratings by discovering latent features that determine how users rate
items. The $5 \times 4$ rating matrix $r$ is approximated by the product of a $5 \times 3$
user matrix $q$ and a $3 \times 4$ item matrix $p$. One rating is one dot product:

$$r_{42} = (a, b, c) \cdot (x, y, z) = ax + by + cz ,$$

with $(a, b, c)$ the row of user 4 in $q$ and $(x, y, z)$ the column of item 2 in $p$.
:::

The payoff is size. Netflix's $10^8 \times 10^5 = 10^{13}$ entries are approximated by
$10^9 + 10^6$ entries in the two factor matrices when 10 factors are used: $10^8$ users
times 10 numbers, plus $10^5$ items times 10 numbers.

**A model is an equation with parameters.** The slide's analogy is the parabola
$y = a(x - h)^2 + k$: three numbers fix the whole curve. A recommender is the same idea at
scale (slide 34):

| System | Parameters | At 4 bytes each |
|---|---|---|
| Netflix movie recommender | $10^{10}$ | 40 GB |
| ChatGPT | $1.75 \times 10^{11}$ | 700 GB |
| Wikipedia, for comparison | | estimated 50 GB |

### Train, test and A/B testing

A system is trained on a subset of the available data (users' likes for items); its
predictions for the remaining part are compared with the true values. But the system also
makes many more predictions that go to online users with no known answer. So recommender
systems are tested **online with A/B experiments**, where a control group and a variation
group see different versions, and algorithms are then "adapted" to perform well online,
which in practice means to increase the platform owner's revenue (slides 35 and 36).

## Step 3: selecting and presenting

Selection leaves the bad items out; presentation arranges what remains: rows of posters on
Netflix, a feed on Facebook, a chat answer (the slide shows ChatGPT asked for a restaurant
in Bolzano).

**The same recommendation can be made more or less appealing.** Slides 40 and 41 show two
lists of sights in Florence twice: once with the usual TripAdvisor photographs of the
buildings, once with the lecturer's own selection (Botticelli's Venus for the Uffizi, a
night market for Santa Croce, the interior for the Duomo). The items are identical; the
appeal is not.

For a point of interest, many features and contextual factors shape the **expected
utility** before the visit (slide 42): the traveller's knowledge of the place, what she
has already visited and when, the picture, distinguishing features, the travel party,
earlier use of the app, and popularity, fame, prestige and rank.

:::warning A perfect prediction is not a good recommendation yet
Even if the system knew the user perfectly and predicted her best option, she may not
appreciate the recommendation. She chooses by her own context-dependent assessment of the
items' utility (slide 43).
:::

### Recommendations interact

The recommender ranks items by predicted rating, but the perceived value of a presented
item depends on the quality of the presentation and on **the other options shown next to
it** (slide 44).

**Anchoring.** What is a reasonable price for a race bicycle? In a shop showing only
bicycles above 3,000 euro, 1,500 looks like too little, or like a bargain. Even if nobody
buys the most expensive models, listing them pays: people are led to the cheaper, still
expensive ones.

**The attraction effect** (Ariely, *Predictably Irrational*):

| Options offered | Web only, \$59 | Print only, \$125 | Print and web, \$125 |
|---|---|---|---|
| All three | 16% | 0% | 84% |
| Without print only | 68% | not offered | 32% |

Nobody chose "print only", yet removing it moved most people from the combination to the
cheap option. The useless option made the combination look good by comparison. **The
decision context influences the estimate of an item's expected utility.**

## Properties beyond precision

**Diversity.** What "the algorithm" recommends is often very similar from item to item, so
the system pushes users towards the same type of product. Two kinds: **individual
diversity**, giving each user a varied list, and **aggregate diversity**, improving the
variety of items across all users. Diversity is typically achieved by **reranking**.

**Fairness.** Different users may get different recommendations of different quality:

- conventional users are "more popular" (the slide's word; read: they dominate the data),
  and the algorithm is typically biased by their observed preferences;
- during A/B testing two groups get the output of a supposedly superior and a supposedly
  inferior method.

**The trade-offs** (slide 50): it is impossible to reach the same high precision for all
users (fairness against precision), and fairness and diversity are typically negatively
correlated, since the more the recommendations differ between users, the more differently
the users are treated.

**Privacy.** Four risks (slide 51): data collected or shared without the user's explicit
consent; data leaked to actors outside the system; data de-anonymised; and undesired
inferences, such as predicting gender or ethnicity. A range of architectural, algorithmic
and policy techniques is used to contain them.

**Multistakeholder systems.** The user is not the only party. In the diagram of
Abdollahpouri and Burke (2020) the recommender sits between **suppliers**, who supply
items and receive insights, and **users**, who receive recommendations and give feedback,
with **side stakeholders** above who impose constraints and limitations and receive
insights and reports.

## Summary

The lecture's own seven points (slide 54):

1. Making a choice is complex and costly.
2. Recommender systems help when we lack knowledge or there is an overabundance of options.
3. User preferences must be modelled and acquired.
4. Collected preferences are usually biased.
5. Core techniques predict, or complete, the user preference model.
6. The presentation of recommendations further influences the preference model and the
   choices.
7. Several properties of recommendations are important, precision among them.

## What an exam wants

The last slide lists ten questions. Each has a card in [](deck:recommender-systems) with a
model answer; three of them written out:

:::paper What is the basic idea of collaborative filtering?
Predict a user's unknown preference from the preferences of others. In the user-to-user
form: if two users agreed in the past, the ratings of one are evidence for what the other
will like, so the prediction is a similarity-weighted average of similar users' ratings of
the item. In the item-to-item form: the prediction is a similarity-weighted average of the
user's own ratings of similar items. Example: with $w = 0.9$ and $1$ and ratings $4$ and
$5$, $r^* = (0.9 \cdot 4 + 1 \cdot 5)/1.9 = 4.53$.
:::

:::paper Can a recommendation be made more or less appealing when presented? How?
Yes. Its perceived value depends on the quality of the presentation, for instance the
image chosen for it, and on the competing options shown with it. Anchoring: expensive
items in the list make a mid-priced one look reasonable. Attraction effect: adding a
dominated option shifts choices towards the option that dominates it (Ariely's
subscriptions, 84% against 32%).
:::

:::paper List some important properties of a good recommendation set
Relevant and precise, timely, and good for the user's well-being; diverse, both within one
user's list and across users; fair to different groups of users; respectful of privacy;
and acceptable to all stakeholders, not only the end user. State the trade-offs: fairness
against precision, fairness against diversity.
:::

## Where next

- Drill: [](deck:recommender-systems).
- Compute: [](problems:cf-practice).
- Read: the two papers of week one, [](guide:reading-resnick-varian-1997) and
  [](guide:reading-handbook-introduction). The course says more than once to learn from
  the papers and not only from the slides.
- Definitions: [the glossary](glossary).
- Next: collaborative filtering in full, [](lecture:02-collaborative-filtering-i).
