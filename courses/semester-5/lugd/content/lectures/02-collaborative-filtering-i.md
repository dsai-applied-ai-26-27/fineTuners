---
title: 'Collaborative filtering I: the method and how to evaluate it'
number: 2
topics: [cf, evaluation]
summary: How user-to-user collaborative filtering predicts a missing rating from like-minded users, with Pearson and cosine similarity and the other ways to aggregate neighbours' ratings; what a recommender is for, for the provider and for the user; and how it is evaluated, with MAE, RMSE, precision, recall, F1, NDCG and ARHR.
takeaways:
  - 'Collaborative filtering predicts the opinion of the active user from their past ratings and the ratings of like-minded users: find the most similar users, take the items they rated, predict a rating for each, recommend the top N.'
  - The standard prediction is mean-centred, $r^*_{uj} = \bar r_u + K \sum_{v \in N_j(u)} w_{uv}(r_{vj} - \bar r_v)$ with $K = 1/\sum |w_{uv}|$. Neighbours contribute their deviation from their own mean, so generous and strict raters become comparable.
  - Pearson correlation measures whether two users deviate from their means in the same way; cosine compares the raw rating vectors. A user whose ratings are another's plus 1 has Pearson 1 but cosine below 1.
  - 'Evaluation splits the ratings into train and test and compares predictions with the held-out truth in three ways: the exact value (MAE, RMSE), relevant or not (precision, recall, F1), and the ranking (NDCG, ARHR).'
  - MAE weighs every test rating equally, so heavy users dominate; RMSE is never below MAE and grows with the spread of the errors. Precision and recall need to know what is relevant, which is unknown for unrated items.
sources:
  - lectures/Collaborative Filtering I.pdf
---

## Where this fits

Lecture 1 ([](lecture:01-recommender-systems)) showed collaborative filtering in two
slides. This lecture is the method in full, followed by the first half of evaluation, and
[](lecture:03-collaborative-filtering-ii) continues with neighbourhoods, association rules,
the link to classification and the reliability of similarities. Both are the core of the
first test ([](problems:practice-test-1)).

## Personalisation and social filtering

"If I have 3 million customers on the Web, I should have 3 million stores on the Web"
(Jeff Bezos). In everyday life we rely on recommendations from other people: word of mouth,
letters, reviews. A recommender system automates that: people provide recommendations as
input, the system **aggregates** them and **matches** them with those who search for
recommendations (Resnick and Varian, 1997).

The collaborative filtering (CF) idea: predict the opinion the user will have of the
different items, and recommend the "best" ones, from **the user's previous likings and the
opinions of other like-minded users**. CF is a typical Internet application: it needs many
users and a server (or many servers). There is no stand-alone CF application, because
without other people's ratings there is nothing to filter with.

## The ingredients and the five steps

The ingredients:

- a list of $m$ users and $n$ items;
- for each user, the items they gave an opinion on (possibly none): an explicit rating
  on a numerical scale, or an implicit signal such as a purchase;
- the **active user**, for whom the prediction is made;
- a similarity metric between users (and/or items);
- a method for selecting a subset of neighbours;
- a method for predicting a rating for items the active user has not rated.

The method in five steps:

1. Identify the set of ratings of the target (active) user.
2. Identify the users most similar to them by a similarity function (neighbour formation).
3. Identify the products these similar users evaluated.
4. For each such product, predict the rating the target user would give.
5. Recommend the top-$N$ products by predicted rating.

The classical model (Adomavicius et al., 2005) has users, items and contexts: a set of
ratings $r: \text{Users} \times \text{Items} \times \text{Contexts} \to \{1, \dots, 5\}$
plus features, a method to predict $r$ where it is unknown (for example the average of the
ratings $r(u', i, c')$ of users $u'$ similar to $u$ in contexts $c'$ similar to $c$), and a
choice rule: in context $c$ recommend to $u$ the item with the largest predicted rating.

## Nearest neighbours, and why one is not enough

Picture each user as a vector of like (1) and dislike (0) over 14 items. To predict the
active user's opinion of an item, find the user at the smallest Hamming distance (the
number of items on which they disagree) and copy their opinion. The slides show how
**1-nearest neighbour is easily wrong**: the nearest user may be the only one with a
positive rating of that product, so one atypical neighbour decides. This is why CF
aggregates several neighbours.

The data in practice (the Netflix prize layout): training ratings as (user, movie, date,
score) and test pairs whose score is "?". Arranged as a users-by-items **rating matrix**
it is mostly empty.

## Notation, on the lecture's example

| | The Matrix | Titanic | Die Hard | Forrest Gump | Wall-E |
|---|---|---|---|---|---|
| John | 5 | 1 | | 2 | 2 |
| Lucy | 1 | 5 | 2 | 5 | 5 |
| Eric | 2 | ? | 3 | 5 | 4 |
| Diane | 4 | 3 | 5 | 3 | |

- $U_i$: the users who rated item $i$; $I_u$: the items rated by user $u$.
- $U_{ij} = U_i \cap U_j$: the users who rated both $i$ and $j$.
- $I_{uv} = I_u \cap I_v$: the items rated by both $u$ and $v$ (the **co-rated** items).
- $N_j(u)$: a set of neighbours of $u$ who rated $j$.

## The prediction formula

With $n$ users, $m$ items and a matrix $R$ of ratings $r_{ui}$ (with $r_{ui} = {?}$ when $u$
did not rate $i$), the prediction for user $u$ and item $j$ is (Breese et al., 1998)

$$r^*_{uj} = \bar r_u + K \sum_{v \in N_j(u)} w_{uv}\,(r_{vj} - \bar r_v), \qquad K = \frac{1}{\sum_{v \in N_j(u)} |w_{uv}|}$$

where $\bar r_u$ is the average rating of $u$ and $w_{uv}$ the similarity of $u$ and $v$.

**User mean-centring** is the idea behind it: subtract each user's mean, so that a 4 from a
user who gives 5s to everything counts as below average. The example matrix centred
(means John 2.5, Lucy 3.6, Eric 3.5, Diane 3.75):

| | The Matrix | Titanic | Die Hard | Forrest Gump | Wall-E |
|---|---|---|---|---|---|
| John | 2.50 | -1.50 | | -0.50 | -0.50 |
| Lucy | -2.60 | 1.40 | -1.60 | 1.40 | 1.40 |
| Eric | -1.50 | ? | -0.50 | 1.50 | 0.50 |
| Diane | 0.25 | -0.75 | 1.25 | -0.75 | |

**The slide's worked example.** User $u_i$ has mean $3.2$; neighbours $u_5$, $u_8$, $u_9$
rated item $j$ with $4$, $3$, $5$, have means $4$, $3.5$, $3$ and similarities $0.5$,
$0.5$, $0.8$:

$$r^*_{ij} = 3.2 + \frac{0.5(4-4) + 0.5(3-3.5) + 0.8(5-3)}{0.5 + 0.5 + 0.8} = 3.2 + \frac{0 - 0.25 + 1.6}{1.8} = 3.2 + 0.75 = 3.95 .$$

## Pearson correlation

$$w_{uv} = \frac{\sum_{j \in I_{uv}} (r_{uj} - \bar r_u)(r_{vj} - \bar r_v)}{\sqrt{\sum_{j \in I_{uv}} (r_{uj} - \bar r_u)^2}\,\sqrt{\sum_{j \in I_{uv}} (r_{vj} - \bar r_v)^2}}$$

The sums run over the co-rated items. On the example:

| | John | Lucy | Eric | Diane |
|---|---|---|---|---|
| John | 1.000 | -0.938 | -0.839 | 0.659 |
| Lucy | -0.938 | 1.000 | 0.922 | -0.787 |
| Eric | -0.839 | 0.922 | 1.000 | -0.659 |
| Diane | 0.659 | -0.787 | -0.659 | 1.000 |

:::note Two ways to take the mean
The lecture's formula uses each user's mean over **all** their ratings, $I_u$. Standard
statistics libraries ignore a missing value in both series and compute the means on the
co-rated items $I_{uv}$ only. The numbers differ: John and Diane are $0.659$ with the
lecture's means but $0.97$ with the standard definition. Say which one you use.
:::

**Finishing the example.** Predict Eric's rating of *Titanic*. The neighbours who rated it
are John ($w = -0.839$), Lucy ($0.922$) and Diane ($-0.659$):

$$r^* = 3.5 + \frac{-0.839(1 - 2.5) + 0.922(5 - 3.6) - 0.659(3 - 3.75)}{0.839 + 0.922 + 0.659} = 3.5 + \frac{1.259 + 1.291 + 0.494}{2.420} = 4.76 .$$

The two negatively correlated users rated *Titanic* below their means, and a negative
weight turns that into evidence that Eric will like it. With only the positive neighbour
(Lucy), $r^* = 3.5 + 1.4 = 4.9$. Many systems discard negative neighbours
([](lecture:03-collaborative-filtering-ii)).

## Cosine similarity

Correlation can be replaced by the information-retrieval similarity of two vectors, the
cosine of the angle between them:

$$w_{uv} = \frac{\sum_{j \in I_{uv}} r_{uj}\, r_{vj}}{\sqrt{\sum_{j \in I_u} r_{uj}^2}\,\sqrt{\sum_{j \in I_v} r_{vj}^2}}$$

Breese et al. (1998) found it worse; many use it (Sarwar et al., 2000), and some report it
better (Anand and Mobasher, 2005).

**Pearson against cosine.** Over 8 products, user 2's ratings are user 1's plus 1, and
user 3 has the "opposite" preferences of user 1 (ratings mirrored around 3):

| | Pearson 1-2 | Pearson 1-3 | Cosine 1-2 | Cosine 1-3 | Cosine 2-3 |
|---|---|---|---|---|---|
| Value | 1 | -1 | 0.99 | 0.76 | 0.84 |

Pearson sees users 1 and 2 as identical (same deviations) and 1 and 3 as opposite. Cosine
calls the opposite user 3 fairly similar ($0.76$), because all ratings are positive numbers
and the vectors point roughly the same way. In a second example two pairs of users both have
Pearson $-1$ (ratings inverted around 2.5), yet their cosines differ ($0.92$ and $0.47$),
and there cosine looks the more reasonable similarity.

## Other aggregation functions

Besides the mean-centred formula:

$$r^*_{uj} = K \sum_{v \in N_j(u)} w_{uv}\, r_{vj} \qquad\text{(weighted average)}, \qquad r^*_{uj} = \frac{1}{|N_j(u)|}\sum_{v \in N_j(u)} r_{vj} \qquad\text{(plain average)}.$$

## Rating prediction as classification

The formulas above solve a **regression** problem. Neighbourhood-based **classification**
instead has the neighbours vote on rating values:

$$\mathrm{vote}(j, r, N_j(u)) = \sum_{v \in N_j(u)} \delta(r_{vj} = r)\, w_{uv}, \qquad r^*_{uj} = \arg\max_r \mathrm{vote}(j, r, N_j(u))$$

with $\delta(\cdot) = 1$ when the neighbour gave rating $r$. **Example:** neighbours
$u_5$, $u_8$, $u_9$ rated $4$, $4$, $5$ with similarities $0.3$, $0.4$, $0.8$. Then
$\mathrm{vote}(4) = 0.3 + 0.4 = 0.7$ and $\mathrm{vote}(5) = 0.8$, so the prediction is 5.

- Regression is more appropriate when the rating scale is continuous.
- Classification is the only choice when the values are discrete and cannot be ordered
  ("good for a couple" against "good for a family").
- Most implemented CF systems use regression.

**The slide's exercise.** Neighbours of equal similarity rated an item either 1 or 5.
Regression predicts their average, around 3, a value nobody gave; classification predicts
whichever of 1 and 5 has more votes. They differ. For "find good items" a confident 5 or 1
is more useful than a 3 that hides a split, but if the split is even classification is a
coin toss; the choice depends on what the prediction is used for.

## What a recommender is for

**For the service provider:**

- sell more items, because the recommended ones suit the user's needs and wants;
- sell **more diverse** items that would be hard to find without a precise recommendation;
- increase user satisfaction, and user **fidelity** (a site that recognises an old customer
  and treats them as valuable);
- understand better what the user wants: a profile usable for other personalisation tasks.

**The long tail:** the economic model in which the market for non-hits (many low-volume
items) can be significant, sometimes larger than the market for hits. Netflix streams a
large volume of less popular titles besides its hits. A recommender helps sell the long
tail, because it can surface niche items to the few users they suit.

**For the user.** Primary functions: find some good items, find all good items,
annotation in context, recommend a sequence, recommend a bundle, just browsing. Secondary
functions: find a credible recommender, improve the profile, express oneself, help others,
influence others.

## Evaluating a recommender

Most evaluation targets the "find good items" task, assuming that a user who could examine
every item could order them by preference. Three kinds of measure:

1. **Value comparison:** how well the system predicts the exact rating.
2. **Relevant or not:** how well it predicts whether an item is relevant.
3. **Ordering comparison:** how close its ranking is to the user's true ranking.

**How:** collect data, split the user-item ratings into a **train** and a **test** set,
build the model on the training set (for memory-based CF, simply store the training
ratings), and compare its predictions, recommendations or ranking with the test set using
a metric.

## Accuracy of values: MAE, RMSE, NMAE

With $\hat r_{ui}$ the predicted and $r_{ui}$ the true rating, over the test set:

$$\mathrm{MAE} = \frac{1}{|R_{test}|}\sum_{r_{ui} \in R_{test}} |\hat r_{ui} - r_{ui}|, \qquad \mathrm{RMSE} = \sqrt{\frac{1}{|R_{test}|}\sum_{r_{ui} \in R_{test}} (\hat r_{ui} - r_{ui})^2}$$

$$\mathrm{NMAE} = \frac{1}{|R_{test}|\,(r_{max} - r_{min})}\sum_{r_{ui} \in R_{test}} |\hat r_{ui} - r_{ui}|$$

- MAE may be less appropriate for "find good items", because people look only at the top.
- **Every test rating counts equally.** The slide's exercise: if some users have far more
  ratings, they dominate the MAE. The fix is to compute the MAE per user and then average
  over users.
- **RMSE** emphasises large errors. For the same sum of absolute errors it grows with the
  variance of the error sizes, and it is never below the MAE.
- **NMAE** divides by the rating range, so data sets with different scales can be compared.

Observed rating distributions are skewed towards high values (Marlin et al., 2011): users
mostly rate what they chose and liked.

## Relevant or not: precision and recall

|  | Relevant | Not relevant |
|---|---|---|
| Recommended | TP | FP |
| Not recommended | FN | TN |

Usually the user's real need is unknown, and well-rated items are assumed relevant. With
$N_{rs}$ relevant items selected, $N_s$ items selected and $N_r$ relevant items:

- **Precision** $= N_{rs} / N_s$: the share of selected items that are relevant.
- **Recall** $= N_{rs} / N_r$: the share of relevant items that were selected.

The scale must be binary, or made binary (for example, rated above 3 is relevant).

**Complete knowledge.** If the relevance of every item is known (items rated above the
average count as relevant) and the system selects 7 items of which 4 are relevant, out of 9
relevant items: precision $4/7 = 0.57$, recall $4/9 = 0.44$.

**Incomplete knowledge.** Some selected items are unrated. Precision is $4/7$ or $5/7$,
recall $4/10$ or $4/7$, depending on whether the unknowns are relevant. The convention is to
treat unrated items as irrelevant: $P = 4/7$, $R = 4/7$.

**Estimated over users.** With $T(u)$ the highly rated test items of $u$ and $L(u)$ the
recommendation list built from the training set, $L(u) \cap T(u)$ is the **hit set** and

$$P(L) = \frac{1}{|U|}\sum_{u \in U}\frac{|L(u) \cap T(u)|}{|L(u)|}, \qquad R(L) = \frac{1}{|U|}\sum_{u \in U}\frac{|L(u) \cap T(u)|}{|T(u)|}.$$

**F1** combines them, because high recall usually comes with low precision and vice versa:

$$F_1 = \frac{2PR}{P + R}; \qquad P = 0.57,\ R = 0.44 \ \Rightarrow\ F_1 = 0.5 .$$

**Precision-recall curve.** Call an item relevant if its true rating is at least 4,
retrieve all items with predicted rating at least $x$ for $x = 5, 4.5, \dots, 0$, and plot
the 11 points. Precision does not fall to 0 at recall 1: retrieving everything gives a
precision equal to the share of relevant items among the rated test items (0.7 on the
slide), high because observed ratings are skewed upwards.

**Problems with precision and recall.**

- You must know what is relevant, which is hard with thousands or millions of products.
  Recall is the harder one (it needs all relevant products); precision only needs the
  recommended ones judged, though few evaluations ask real users.
- The system may be right on rated items and wrong on the ones whose opinion is unknown.
- Optimising precision on observed ratings recommends items the user already consumed:
  not useful recommendations.
- Measured precision is typically very low (around 10% on the lecture's data sets).
- Once the precise recommendations are used up, the system cannot find novel ones.

## Ranking quality: NDCG and ARHR

**NDCG.** For a set of users $Q$, let $R(j, m)$ be the relevance (1 if rating $> 3$, else 0)
of the item at rank $m$ for user $j$, with items sorted by decreasing predicted rating:

$$\mathrm{NDCG}(Q, k) = \frac{1}{|Q|}\sum_{j=1}^{|Q|} Z_{kj}\sum_{m=1}^{k}\frac{2^{R(j,m)} - 1}{\log_2(1 + m)}$$

$Z_{kj}$ normalises so that a perfect ranking scores 1 for user $j$; if a user has fewer
than $k$ test items, the sum stops there. The logarithm discounts lower positions: a
relevant item at rank 1 counts 1, at rank 3 only $1/\log_2 4 = 0.5$.

**ARHR.** If the test set holds one random rated item $i_u$ per user,

$$\mathrm{ARHR}(L) = \frac{1}{|U|}\sum_{u \in U}\frac{1}{\mathrm{rank}(i_u, L(u))}$$

with $\mathrm{rank} = \infty$ (a contribution of 0) when $i_u$ is not in the list.

## Beyond precision

- **Novelty:** recommending items the user was not already aware of.
- **Coverage:** the percentage of the items known to the system for which it can predict.
- **Learning rate:** how quickly CF becomes a good predictor as data arrives.
- **Confidence:** how well the system can judge the likely quality of its predictions.
- **User satisfaction:** surveys, retention and usage statistics.
- **Site performance:** more items purchased or downloaded, more revenue, more retention.

## The closing questions

1. **How does CF work?** It predicts the active user's rating of an item from the ratings
   that similar users gave it, and recommends the items with the highest predictions.
2. **Can CF work on your PC if it is not networked?** No: it needs other users' ratings,
   which only a networked, shared database has.
3. **Advantages and disadvantages of CF?** It needs no content description of the items and
   can surprise with items unlike the user's past ones; but it needs many ratings (sparsity,
   cold start for new users and items), and it scales with users times items.
4. **Methods for user similarity?** Pearson correlation, cosine, Hamming distance on binary
   profiles.
5. **Other similarity measures?** For example Euclidean distance, Spearman rank
   correlation, Jaccard on the sets of rated items, or significance-weighted versions
   ([](lecture:03-collaborative-filtering-ii)).
6. **The user model in CF?** The user's vector of ratings (their interaction history).
7. **Why can a recommender help sell less popular items?** It surfaces niche items to the
   few users whose neighbours liked them: the long tail.
8. **How can CF account for old ratings?** Weight ratings by age (time decay), or use only
   recent ones.
9. **Which items should a new user be asked to rate?** Informative ones: popular enough to
   be known, with diverse ratings (high variance), so they separate tastes.
10. **Is precision more important than recall?** Usually, for "find some good items": the
    user looks only at the top of a short list. Recall matters for "find all good items".

## Where next

- Continued in [](lecture:03-collaborative-filtering-ii).
- Drill: [](deck:collaborative-filtering-i).
- Practise: [](problems:practice-test-1) and [](problems:cf-practice).
- Formulas: [the formula sheet](formulas); terms: [the glossary](glossary).
