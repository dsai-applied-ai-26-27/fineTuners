---
title: 'Framing a problem and a first look at the data'
number: 1
topics: [framing]
summary: 'What supervised learning is, features and targets, the first four pandas calls, L1 and L2 loss, empirical risk minimisation, and how to split the data.'
---

Part 1 of 12 of the course notes, from the 2025-26 exam kit (lectures 1 to 7, labs 1 to 10). Each section pairs an exam-ready code pattern with the theory that justifies it. Arguments are tagged **ritual** (always the same), **structural** (forced by the data or the task) or **dial** (a real hyperparameter); the full list is in [](guide:parameter-reference).

## Supervised learning: experience, task, performance

A program **learns from experience E** on a **task T**, measured by **performance P**. This whole course is **supervised learning**: learning the functional relationship between features x and a target y, assuming the data is i.i.d. from an unknown data-generating process.

## Features, target, regression or classification

**Features (x)** describe the object; **target (y)** is what you predict. Numerical target ⇒ **regression** (length of hospital stay). Categorical target ⇒ **classification** (risk category). Categorical *features* must be encoded: one-hot makes k dummies, dummy encoding makes k−1 to remove redundancy.

## First look at a DataFrame

Always the same four questions before modelling: what shape and type is it, what does a row look like, what is the spread, and how imbalanced are the categories. `df.iloc[n]` slices by position, `df.loc["a"]` by label.

```python
df.info()          # shape, dtypes, non-null counts -> where the holes are
df.head(5)         # first n rows
df.describe()      # mean, std, min, max, 25/50/75%
df["ocean_proximity"].value_counts()   # how frequent is each category
df.sample(frac=1)  # shuffle 100% of the rows
```

## L1 and L2 loss

**L1 (absolute) loss $\lvert y - f(x) \rvert$**: robust to outliers, but not differentiable at zero, so it needs numerical optimisation. **L2 (squared) loss $(y - f(x))^2$**: convex and differentiable, gives the closed-form OLS estimator — but squaring means one outlier carries enormous weight and drags the model. Same trade-off reappears as MSE vs MAE at evaluation time.

## Theoretical risk and empirical risk minimisation

**Theoretical risk** = expected loss over the true distribution — unknowable, because the distribution is unknown. So we do **Empirical Risk Minimisation**: minimise the average loss over the observed training data, and accept that training error is optimistically biased.

## Train/test split, plain and stratified

**Why it is representative:** `split.split(X, y)` looks at y (or the stratification column) and draws the test indices so that each category appears in the test set in the same proportion as in the full dataset. A plain random split only guarantees that *on average*; with a rare category or a small test set, one draw can be badly skewed. The loop runs once because `n_splits=1`, and it yields index arrays, which is why you subset with `.iloc[]`.

```python
from sklearn.model_selection import train_test_split, StratifiedShuffleSplit

# plain random split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# stratified: preserves the class / category proportions
split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_index, test_index in split.split(X, y):
    X_train = X.iloc[train_index]
    X_test  = X.iloc[test_index]
```

| Argument | Kind | What it does |
|---|---|---|
| `n_splits=1` | structural | One split, not k folds — this is a train/test split, not cross-validation. |
| `test_size=0.2` | dial | The 80/20 convention. Smaller test set = noisier estimate; smaller train set = pessimistically biased model. |
| `random_state=42` | ritual | Reproducibility. Every randomised function in sklearn takes it; in this course it is always 42. |

## Remember it

The same sections as scenes along a route: [](palace:01-front-door). The code is drilled in [the decks](cards).
