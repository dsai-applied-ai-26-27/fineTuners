---
title: 'Ensembles & error decomposition'
number: 7
topics: [ens]
summary: 'Lecture 3 pt 3. Carries marks on both past papers.'
---

An ensemble is **a set of predictors whose individual decisions are combined in some way** to classify new examples. Generate multiple classifiers; each votes.

### Error decomposition — asked on both papers

:::paper
**Error = bias² + variance + noise**

bias² = Eₓ\[ (h\*(x) − E\_D\[y(x;D)])² ] — how far the *average* prediction is from the truth

variance = E\_(D,x)\[ (y(x;D) − E\_D\[y(x;D)])² ] — how much the prediction moves when the training set changes

noise = E\_(D,x,t)\[ (t − h\*(x))² ] — irreducible; no algorithm can beat it
:::

- **t**: the true target value
- **D**: a training set, drawn at random
- **y(x; D)**: the prediction of the model trained on D
- **h\*(x) = E\[t | x]**: the **Bayes-optimal** predictor — the best any model could do

The derivation is the same trick twice: add and subtract a term, expand the square, and the cross-term vanishes because its expectation is zero. First insert ±h\*(x) to split off the noise; then insert ±E\_D\[y] to split the remainder into bias² and variance. High variance is the signature of overfitting.

### The two strategies

|   | Bagging | Boosting |
|---|---|---|
| **Training** | **Parallel** — each learner independently | **Sequential** — each learner focuses on the previous ones' mistakes |
| **Data per learner** | a bootstrap sample: sample **with replacement**, same size as the original | same data, with example **weights** updated each round |
| **Combination** | plain average / majority vote | **weighted** vote — better learners get larger α |
| **Reduces** | **variance** | **bias** |
| **Does not reduce** | bias — and correlation between classifiers remains | variance — overfitting risk |
| **Robustness** | more robust to errors and outliers | sensitive — outliers get up-weighted every round |
| **Examples** | Random Forest, bagged trees | AdaBoost, Gradient Boosting, XGBoost |

A third strategy in the skripta: **stacking** — combining *heterogeneous* classifiers with a meta-model. And a fourth training mode: **mixture of experts**, parallel training with an objective that encourages division of labour.

### "Compute the error decomposition for an ensemble"

```text
Var( (1/m) Σᵢ xᵢ ) = σ²/m (independent learners)
```

```text
Var( (1/m) Σᵢ xᵢ ) = (1 − ρ)σ²/m + ρσ² (correlation ρ)
```

- **m**: number of base learners
- **σ²**: variance of a single learner
- **ρ**: pairwise correlation between learners

Averaging divides variance by m — but only if the learners are independent, and bootstrap samples overlap heavily, so they are not. As m → ∞ the variance floors at **ρσ²**. **The bias does not move at all**, which is exactly why bagging cannot fix underfitting.

### Random Forest, AdaBoost, OOB

**Random Forest** = decision trees + bagging + one more trick: each split considers only a **random subset of features**. That extra randomisation exists to drive ρ down, because bagging alone leaves the trees correlated. Trees are the natural base learner because they overfit easily (plenty of variance to remove) and are fast at inference.

```text
H(x) = sign( Σₘ αₘ hₘ(x) ), αₘ = ½ ln( (1 − εₘ) / εₘ )
```

- **hₘ**: the weak classifier trained in round m
- **εₘ**: its **weighted** error rate
- **αₘ**: its coefficient — small error gives large α, so better learners count more

```text
D⁽ⁿ⁾ₘ₊₁ = D⁽ⁿ⁾ₘ · exp( −t⁽ⁿ⁾ αₘ hₘ(x⁽ⁿ⁾) )
```

**Out-of-bag estimation**: each example is left out of about **1/e ≈ 37%** of the bags. Predict each training example using only the trees that never saw it and you get a free test-error estimate — OOB reduces the need for a separate validation set.
