---
title: 'Collaborative filtering II: neighbours, association rules and reliability'
number: 3
topics: [cf, evaluation, classification]
summary: How sparse rating data is, a top-N evaluation with most-frequent-item recommendation and why its F1 is so low, how many neighbours to use, CF as k-nearest-neighbour classification and its link to the Bayes error, association rules with support and confidence, memory-based against model-based CF, and how to make user similarities more reliable with significance weighting, shrinkage and inverse user frequency.
takeaways:
  - Sparsity is the share of missing ratings, $1 - \#\text{ratings} / (\#\text{users} \times \#\text{items})$; it is above 0.9 in typical data. Measured precision, recall and F1 are low partly because their ceilings are low.
  - Neighbours are chosen by a fixed $k$ or by a similarity threshold. Too large a $k$ brings in dissimilar users; a threshold can give too many neighbours as data grows. With Pearson, negative neighbours are often discarded.
  - CF is k-nearest-neighbour learning, a lazy, memory-based method. 1-NN's asymptotic error is less than twice the Bayes error, and k-NN approaches the Bayes error as $k$ grows with the data.
  - 'Association rules $X \to Y$ are scored by support, $S = n(X \cap Y)/N$, and confidence, $C = n(X \cap Y)/n(X) = S(X \to Y)/S(X)$. Confidence is the probability of $Y$ given $X$, and is never below the support.'
  - 'Similarities from few co-rated items are unreliable. Significance weighting scales $w_{uv}$ by $\min\{|I_{uv}|, \gamma\}/\gamma$; shrinkage by $|I_{uv}|/(|I_{uv}| + \beta)$. Both rank well-supported neighbours above lucky ones.'
sources:
  - lectures/Collaborative Filtering II.pdf
---

## Where this fits

The second half of collaborative filtering, after [](lecture:02-collaborative-filtering-i).
It connects CF to classification learning, which the Bayes classifier sheet
([](lecture:04-bayes-classifier)) then develops, and it is half of the first test
([](problems:practice-test-1)).

## Sparsity

Sarwar et al. (2000) evaluated CF on two data sets:

- **MovieLens:** 100,000 ratings from 943 users on 1,682 movies. Sparsity
  $= 1 - \frac{100{,}000}{943 \cdot 1682} = 0.9369$; on average $100{,}000/943 = 106$
  ratings per user.
- **E-commerce:** 6,502 customers, 23,554 products, 97,045 purchase records. Sparsity
  $0.9994$; on average 14.9 ratings per user.

**Sparsity** is the proportion of missing ratings among all possible ratings,
$\#\text{missing} / \#\text{all possible}$. At 94% the rating matrix is mostly empty; at
99.9% it is almost entirely empty.

## A top-N evaluation

The procedure of Sarwar et al.:

- top-$N$ recommendation, 10 items per user;
- ratings split 80% train, 20% test;
- the **hit set** is the intersection of the top-$N$ with the user's test set;
- precision $=$ |hit set| / $N$, recall $=$ |hit set| / |test set|;
- all rated items count as relevant; neighbours found with cosine.

**Most-frequent-item recommendation.** Instead of the weighted average of ratings, they
scanned the neighbours' purchases, counted how many neighbours bought each product not
already in the target user's training profile, sorted by that frequency and returned the
$N$ most frequent. It builds a list **without estimating any rating**.

**Why is F1 so small?** The slide asks for the maximum precision and recall per user. A
MovieLens user has 106 ratings, so about 21 test items: a perfect top-10 has precision 1
but recall at most $10/21 \approx 0.47$. An e-commerce user has 14.9, so about 3 test items:
recall can reach 1, but precision at most $3/10 = 0.3$. The ceilings, not only the
algorithm, keep F1 low (the same reasoning as question 3 of the practice test).

## How many neighbours

Neighbourhoods matter for accuracy and for speed (fewer neighbours, fewer computations).

- **Fixed $k$** (the usual choice). If $k$ is too large, users who are not very similar
  enter the prediction and accuracy drops, especially for users with unusual tastes, whose
  $k$ nearest neighbours are far away.
- **Similarity threshold.** A fixed threshold can mean completely different neighbourhoods
  at two points of the space, and as the number of ratings grows a user can have too many
  neighbours above it.
- With Pearson it is common to **discard neighbours with negative similarity**.
- Advanced methods form neighbourhoods adaptively, from the global data and the specific
  user and item.

## CF as nearest-neighbour learning

**1-NN.** Learning is just storing the training examples $D$. To classify a new instance
$x$: compute its similarity to every example and give it the class of the most similar one.
No generalisation or class prototype is built, so it is also called case-based, memory-based
or **lazy** learning. Its rationale is the contiguity hypothesis (similar instances share a
class); its decision boundary is a Voronoi tessellation.

**k-NN.** One atypical or mislabelled example can decide 1-NN. More robust: take the $k$
most similar examples and return their majority class, with $k$ odd to avoid ties (3 and 5
are common). As a classifier of a user $d$ into class $c$ (for example "likes the target
item"): find the $k$ nearest neighbours $N(d)$, count those in class $c$, estimate
$P(c \mid d) = c_{N(d)}/k$, and choose $\arg\max_c P(c \mid d)$.

**k-NN is close to optimal** (Cover and Hart, 1967). Asymptotically, that is with
unlimited training data, the error rate of 1-NN is less than twice the Bayes rate.
Corollary: if the Bayes rate is 0, so is 1-NN's asymptotic error. And k-NN is guaranteed to
approach the Bayes error for some $k$ that grows with the number of data points.

## Probability basics and the Bayes error

A probability space $(\Omega, \mathcal F, P)$: outcomes, events, a probability measure. For
$P(B) > 0$ the **conditional probability** is $P(A \mid B) = P(A \cap B)/P(B)$ (undefined if
$P(B) = 0$). $A$ and $B$ are **independent** if $P(A \cap B) = P(A)P(B)$, and then
$P(A \mid B) = P(A)$.

**Bayes error rate.** A classifier splits the space into regions $R_1$ and $R_2$ for classes
$\omega_1$ and $\omega_2$. It errs when an $\omega_1$ point falls in $R_2$ or an $\omega_2$
point in $R_1$:

$$P(\text{error}) = P(x \in R_2 \mid \omega_1)P(\omega_1) + P(x \in R_1 \mid \omega_2)P(\omega_2) = \int_{R_2} p(x \mid \omega_1)P(\omega_1)\,dx + \int_{R_1} p(x \mid \omega_2)P(\omega_2)\,dx .$$

The error is smallest when the boundary $x_B$ is where the two weighted densities cross,
but an "unavoidable" error remains where they overlap. More in
[](lecture:04-bayes-classifier).

## Association rules

Association rules find sets of co-purchased products: the presence of some products
"implies" others. With products $P = \{p_1, \dots, p_m\}$ and transactions $T \subseteq P$,
a rule $X \to Y$ has non-overlapping $X$ (antecedent) and $Y$ (consequent), and means:
in the transactions $T_1, \dots, T_N$, if the products in $X$ are present, those in $Y$
are likely present too. In CF a transaction can be all the products a user rated or bought,
ignoring the rating values (as Sarwar et al. did).

$$S(X \to Y) = \frac{\#\text{transactions containing } X \text{ and } Y}{\#\text{transactions}}, \qquad C(X \to Y) = \frac{\#\text{transactions containing } X \text{ and } Y}{\#\text{transactions containing } X} = \frac{S(X \to Y)}{S(X)}$$

- **Support** measures how often the pattern is observed; **confidence** the strength of the
  rule, the conditional probability of seeing $Y$ given $X$.
- **The slide's example:** 6 transactions, 4 contain $X$, 3 contain $X$ and $Y$. Support
  $3/6$, confidence $3/4$.
- Because $n(X) \leq N$, confidence is never below support, and in general
  $C(X \to Y) \neq C(Y \to X)$.

**Recommending with rules** (Sarwar et al., 2000):

1. From the transactions (one per user for a long-term profile, or one per shopping session
   for a short-term one) build rules with a minimum support and confidence, for example with
   the Apriori algorithm; possibly only from users close to the target, a mix of rules and CF.
2. For each user, find the rules whose $X$ is in the training part of their profile.
3. Rank each product on the right-hand side by the (maximal) confidence of the rules that
   predict it.
4. Select the top-$N$.

**Rules against CF.** With little data, advanced personalisation does not help and all
methods perform similarly. On the second comparison CF had a clear advantage, and the slide
asks why. A likely answer: with more ratings per user, a user's own neighbourhood carries
more evidence than rules built from global co-occurrence, which recommend what is popular
overall.

## Recommendation as classification

Users are instances described by their ratings, and the class is the rating they gave a
target product (or items are instances, and the class is the target user's rating). It
differs from classical machine-learning classification:

- the data are sparse;
- there is no single preferred class to predict: the real problem is choosing which item
  ratings are worth predicting;
- predicting every item and taking the best is usually too expensive, unless there are few
  items. A bank, for example, profiles each customer from behavioural and demographic data
  and builds one buy/not-buy model per type of insurance (Mahmood, 2022).

**Lazy and eager learning.**

- **Lazy** learners wait for the query before generalising: k-NN, case-based reasoning.
  They can build many local approximations.
- **Eager** learners build a model before seeing the query: radial basis function networks,
  ID3, neural networks, Naive Bayes, SVM. They must build one global approximation.

**Model-based CF** builds and stores a (probabilistic) model and predicts with it:

$$r^*_{uj} = E[r_{uj}] = \sum_{r=1}^{5} r \cdot P\big(r_{uj} = r \mid \{r_{uk},\, k \in I_u\}\big)$$

the expected rating given the user's other ratings (the user model), with the
probabilities estimated by a classifier trained on the other users' profiles, such as Naive
Bayes (or k-NN). The CF of the previous lecture is **memory-based**.

## Sparsity and the neighbours you can find

On Amazon, with millions of books, two users who each rated 100 of a million books have a
common book with probability about $0.01$ (with 50 ratings each and 10 million books,
$0.00025$), if all books are equally likely. With few users you may not find a single
neighbour. With 10 million users you can still expect $10^7 \cdot 0.00025 = 2{,}500$.

## Reliability of the similarity

User-to-user similarities are often computed on few co-rated items $I_{uv}$, so how
**dependable** a similarity is matters, not only its value (Herlocker et al., 1999).

**Significance weighting:**

$$w'_{uv} = \frac{\min\{|I_{uv}|, \gamma\}}{\gamma} \cdot w_{uv}$$

Similarities from fewer than $\gamma$ co-rated items are scaled down linearly; from $\gamma$
on they are kept whole. $\gamma$ is chosen by cross-validation; 50 was best on MovieLens.
It improves prediction accuracy (MAE).

**Shrinkage.** A weak estimator improves if it is shrunk towards a null value (prior); the
null value of a similarity is 0. Take $\alpha \cdot 0 + (1 - \alpha) w_{uv}$ with
$\alpha = \beta/(|I_{uv}| + \beta)$:

$$w'_{uv} = \frac{|I_{uv}|}{|I_{uv}| + \beta} \cdot w_{uv}$$

The larger $\beta$, the more you shrink; the larger $|I_{uv}|$, the less. Half the value is
kept when $|I_{uv}| = \beta$, and it is never kept in full.

:::tip Practice
Question 4 of [](problems:practice-test-1) applies both to three neighbours: a Pearson of
$0.95$ on 4 co-rated items drops below $0.70$ on 40.
:::

**Low- and high-variance items.** Items whose ratings vary little are less informative for
similarity than items with diverse ratings (Herlocker et al., 1999), but weighting the
high-variance items more did not improve accuracy. Baltrunas and Ricci (2008) did better by
using only the items most correlated with the target item: the similarity becomes dependent
on the item being predicted, since two people may be similar on some items only.

**Inverse user frequency.** Items rated by few users may be more informative, like rare
terms in documents. With $\lambda_i = \log(|U|/|U_i|)$:

$$\mathrm{FWPC}(u, v) = \frac{\sum_{i \in I_{uv}} \lambda_i (r_{ui} - \bar r_u)(r_{vi} - \bar r_v)}{\sqrt{\sum_{i \in I_{uv}} \lambda_i (r_{ui} - \bar r_u)^2}\,\sqrt{\sum_{i \in I_{uv}} \lambda_i (r_{vi} - \bar r_v)^2}}$$

Breese et al. (1998) found that this frequency-weighted Pearson correlation improves
prediction accuracy.

## Popular and unpopular items

- Predicting popular items is **easier** (many neighbours rated them) but of questionable
  use: it could be guessed more simply, and the system does not look smart.
- Predicting unpopular items is **risky** (few neighbours) but can bring a lot of value.

## Scalability

Nearest-neighbour CF grows with both customers and products. The worst case is
$O(m \cdot n)$ for $m$ customers and $n$ products. In practice it is closer to $O(m + n)$:
each profile holds few products, so one loop over the $m$ customers computes the
similarities and one over the $n$ products the predictions.

Remedies: indexing, approximate distances, discarding customers with few purchases,
discarding very popular items, partitioning products into categories, dimensionality
reduction (LSI, clustering). All of them may also reduce recommendation quality (Linden
et al., 2003).

## The closing questions

1. **Two ways to select the nearest neighbours?** A fixed number $k$ of most similar users,
   or all users above a similarity threshold.
2. **A measure of reliability of a similarity?** Its support: the number of co-rated items
   $|I_{uv}|$, used in significance weighting or shrinkage.
3. **Complexity of naive CF, and in practice?** $O(m \cdot n)$ in the worst case; about
   $O(m + n)$ in practice, because profiles are sparse.
4. **CF against association rules?** Rules use global co-occurrence (support and
   confidence) and ignore rating values; CF uses the user's own neighbourhood. With little
   data they perform alike; with more data CF does better.
5. **Recommendation learning against classification learning?** Sparse data, no single
   class to predict, and the main problem is choosing which items' ratings to predict.
6. **CF with very popular or very rare products?** Popular ones are easy to predict but add
   little value; rare ones have few neighbours, so predictions are unreliable but valuable.
7. **Better for popular or unpopular items?** More accurate for popular items, more useful
   for unpopular ones.

## Where next

- Drill: [](deck:collaborative-filtering-ii).
- Then [](lecture:04-bayes-classifier), and [](problems:practice-test-1).
- Formulas: [the formula sheet](formulas); terms: [the glossary](glossary).
