---
title: 'Recommender systems'
number: 6
topics: [rec]
summary: 'Lecture 7. Carries marks on both past papers.'
---

Formally: X customers, S items, a utility function **u : X × S → R** mapping pairs to ratings. The utility matrix is **sparse** — most people have rated almost nothing — and that sparsity is what every method is fighting.

Three approaches: **content-based**, **collaborative filtering**, and latent-factor. The exam has asked for the first two.

### Content-based

Recommend items similar to items this same customer rated highly. It uses **item features** and never looks at another user.

:::paper
1. **Item profiles** — a feature vector per item (actors, director, genre; for text, the high-TF-IDF words).
2. **User profile** — the (weighted) average of the profiles of the items that user rated.
3. **Predict** with cosine similarity between the user profile and each item profile.
4. **Recommend** the highest-scoring items the user has not already seen.
:::

```text
u(x, i) = cos(x, i) = (x · i) / ( ‖x‖ · ‖i‖ )
```

- **x**: the user profile vector
- **i**: an item profile vector
- **x · i**: dot product
- **‖x‖**: length (norm) of x

**Boolean profile** (Lecture 7's own example): user watched 5 movies, 2 with actor A and 3 with actor B ⇒ weight of A = 2/5 = 0.4, weight of B = 3/5 = 0.6. Just counts over the total.

**Star ratings**: first **subtract the user's mean rating**, so that a low rating becomes negative evidence. A's movies rated 3 and 5 with mean 3 ⇒ normalised 0 and +2 ⇒ weight (0+2)/2 = 1. B's rated 1, 2, 4 ⇒ normalised −2, −1, +1 ⇒ weight −2/3.

### Collaborative filtering

Consider user x. Find the set **N** of other users whose ratings are similar to x's. Estimate x's rating from the users in N. No item features at all — it works on any kind of item.

```text
sim(x, y) = Σ_(s∈S_(xy)) (rₓₛ − r̄ₓ)(r_(ys) − r̄_y) / √[ Σ (rₓₛ − r̄ₓ)² · Σ (r_(ys) − r̄_y)² ]
```

- **S\_(xy)**: the items rated by **both** x and y
- **rₓₛ**: user x's rating of item s
- **r̄ₓ**: user x's average rating
- ****: This is Pearson correlation — and **centred cosine is Pearson**, which is why the lecture uses the two words interchangeably.

:::note
**Why centring matters, in one line.** Plain cosine treats a *missing* rating as a zero, i.e. as active dislike, which pushes the vectors apart and understates similarity. Jaccard is worse still: it throws the rating values away entirely. Subtract each user's mean and positive now means "liked more than they usually do".
:::

```text
rₓᵢ = Σ_(y∈N) s_(xy) · r_(yi) / Σ_(y∈N) s_(xy)
```

- **N**: the k users most similar to x who have rated item i
- **s\_(xy)**: shorthand for sim(x, y)
- **rₓᵢ**: the predicted rating of item i for user x

**Item-item** flips it: for item i, find similar *items* and predict from this user's ratings of those. Same similarity metrics, same prediction form.

:::note
**Item-item usually beats user-user in practice** — the lecture's reason: *items are simpler, users are complex and have multiple tastes.* A film is reliably one thing; a person is several.
:::

### Pros and cons — the table both papers want

|   | Content-based | Collaborative filtering |
|---|---|---|
| **Needs other users?** | No — no cold-start or sparsity problem | Yes — needs enough users to find a match |
| **New item** | Fine — profile comes from features, so no first-rater problem | Fails — cannot recommend an unrated item |
| **New user** | Fails — no rated items means no profile | Fails — cold start |
| **Unique tastes** | Handles them | Popularity bias — pushes popular items |
| **Feature engineering** | Hard, and domain-specific (images, music) | None needed — works for any kind of item |
| **Explanations** | Yes — name the features that caused it | Not naturally |
| **Main failure** | **Overspecialisation** — never recommends outside the profile; can't use other users' quality judgements | **Sparsity** — hard to find users who rated the same items |

:::note
**"Which method covers its cons?"** They are complements, and the lecture's answer is **hybrid methods**: implement two or more recommenders and combine the predictions, e.g. with a linear model. Add content-based item profiles to fix CF's new-item problem, and demographics to fix the new-user problem.
:::

### Evaluating recommenders

```text
RMSE = √( Σₓᵢ ( rₓᵢ − r*ₓᵢ )² / n )
```

- **rₓᵢ**: predicted rating
- **r\*ₓᵢ**: the true rating

But the lecture warns that narrow accuracy misses the point: we only care about predicting **high** ratings, and RMSE penalises a method that gets those right but the rest wrong. Alternatives: **precision at top k**, rank correlation (Spearman), coverage, ROC.
