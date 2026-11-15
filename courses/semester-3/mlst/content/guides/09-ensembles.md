---
title: 'Ensembles'
number: 9
topics: [ensembles]
summary: 'Voting, bagging and pasting, out-of-bag evaluation, random forests and feature importance, AdaBoost, and gradient boosting with early stopping.'
---

Part 9 of 12 of the course notes, from the 2025-26 exam kit (lectures 1 to 7, labs 1 to 10). Each section pairs an exam-ready code pattern with the theory that justifies it. Arguments are tagged **ritual** (always the same), **structural** (forced by the data or the task) or **dial** (a real hyperparameter); the full list is in [](guide:parameter-reference).

## Voting classifiers

An ensemble beats its members when the members are **diverse** — they must make *different* mistakes. Using structurally different algorithms is one way to get that diversity; resampling the data is the other.

```python
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

log_clf = LogisticRegression(solver="lbfgs", random_state=42)
rnd_clf = RandomForestClassifier(n_estimators=100, random_state=42)
svm_clf = SVC(probability=True, random_state=42)

voting_clf = VotingClassifier(
    estimators=[("lr", log_clf), ("rf", rnd_clf), ("svc", svm_clf)],
    voting="soft")
voting_clf.fit(X_train, y_train)
```

| Argument | Kind | What it does |
|---|---|---|
| `estimators=[("lr", clf), ...]` | structural | A list of (name, estimator) tuples. The names are arbitrary labels. |
| `voting="soft"` | structural | Average of predict_proba. "hard" is a majority vote on labels. Soft usually wins because it weights confident votes more. |
| `probability=True` | structural | Mandatory on SVC for soft voting — otherwise it has no predict_proba and the fit fails. |

## Bagging and pasting

**Bagging (bootstrap aggregating)** trains the same algorithm on many resampled versions of the training set and aggregates (majority vote / average). It reduces **variance** without increasing bias — perfect for unstable, high-variance learners like fully grown trees.

```python
from sklearn.ensemble import BaggingClassifier
bag_clf = BaggingClassifier(
    DecisionTreeClassifier(), n_estimators=500,
    max_samples=100, bootstrap=True, random_state=42)
bag_clf.fit(X_train, y_train)
```

| Argument | Kind | What it does |
|---|---|---|
| `n_estimators=500` | dial | How many trees. More is generally better and only costs time; it does not overfit. |
| `max_samples=100` | dial | Size of each bootstrap sample (int = count, float = fraction). |
| `bootstrap=True` | structural | True = BAGGING, sampling WITH replacement. False = PASTING, without replacement. That single boolean is the whole difference. |

## Out-of-bag evaluation

Each bootstrap sample uses about **63.2%** of the unique instances, so roughly **37%** are **out-of-bag** for that predictor and can score it without a separate validation set.

```python
bag_clf = BaggingClassifier(
    DecisionTreeClassifier(), n_estimators=500,
    bootstrap=True, oob_score=True, random_state=40)
bag_clf.fit(X_train, y_train)
bag_clf.oob_score_
bag_clf.oob_decision_function_
```

| Argument | Kind | What it does |
|---|---|---|
| `oob_score=True` | structural | Turns on the free evaluation. Only meaningful with bootstrap=True — pasting leaves nothing out. |

## Random forests

**Random Forest = bagging + random feature subsets at each split.** Individual trees are unstable and overfit; averaging many **decorrelated** trees produces a far more accurate and stable model. Divide and conquer: extra randomness is injected on purpose to make the errors independent.

```python
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
rnd_clf = RandomForestClassifier(n_estimators=500, max_leaf_nodes=16, random_state=42)
rnd_clf.fit(X_train, y_train)

# exactly equivalent:
bag_clf = BaggingClassifier(
    DecisionTreeClassifier(max_features="sqrt", max_leaf_nodes=16),
    n_estimators=500, random_state=42)
```

| Argument | Kind | What it does |
|---|---|---|
| `max_features="sqrt"` | dial | The mtry hyperparameter: how many features each split may consider. This is what decorrelates the trees; it is built into RandomForest. |
| `max_leaf_nodes=16` | dial | Regularises each individual tree. |

## Feature importance

Random Forests trade a little interpretability back: **MDI (mean decrease in impurity)** measures how much each feature reduced impurity across all trees during training. **PFI (permutation feature importance)** measures the drop in performance when a feature's values are randomly shuffled — slower, model-agnostic, and generally more trustworthy.

```python
for name, score in zip(iris["feature_names"], rnd_clf.feature_importances_):
    print(name, score)
```

## AdaBoost

**Boosting** trains predictors **sequentially**, each correcting its predecessor. AdaBoost does it by **reweighting the instances** that were misclassified. Because it is sequential it cannot be parallelised, unlike bagging.

```python
from sklearn.ensemble import AdaBoostClassifier
ada_clf = AdaBoostClassifier(
    DecisionTreeClassifier(max_depth=1), n_estimators=200,
    algorithm="SAMME.R", learning_rate=0.5, random_state=42)
ada_clf.fit(X_train, y_train)
```

| Argument | Kind | What it does |
|---|---|---|
| `DecisionTreeClassifier(max_depth=1)` | structural | A decision stump — the canonical weak learner for AdaBoost. |
| `learning_rate=0.5` | dial | Shrinks each predictor's contribution. Lower needs more estimators but generalises better. |
| `algorithm="SAMME.R"` | ritual | The probability-based variant, the default. Treat as boilerplate. |

## Gradient boosting

**Gradient Boosting** fits each new predictor to the **residual errors** of the ensemble so far, instead of reweighting instances as AdaBoost does. That is the exam-relevant difference between the two boosting methods.

```python
from sklearn.ensemble import GradientBoostingRegressor
gbrt = GradientBoostingRegressor(max_depth=2, n_estimators=3,
                                 learning_rate=1.0, random_state=42)
gbrt.fit(X, y)

gbrt_slow = GradientBoostingRegressor(max_depth=2, n_estimators=200,
                                      learning_rate=0.1, random_state=42)
```

| Argument | Kind | What it does |
|---|---|---|
| `max_depth=2` | dial | Keeps each tree weak. Boosting wants shallow trees; depth 2–3 is typical. |
| `learning_rate` | dial | Shrinkage. LOW learning_rate + MANY estimators generalises better — the classic boosting trade-off. |
| `n_estimators` | dial | Number of sequential trees. Unlike bagging, too many DOES overfit here — hence early stopping. |

## Early stopping for gradient boosting

```python
gbrt = GradientBoostingRegressor(max_depth=2, n_estimators=120, random_state=42)
gbrt.fit(X_train, y_train)

errors = [mean_squared_error(y_val, y_pred)
          for y_pred in gbrt.staged_predict(X_val)]
bst_n_estimators = np.argmin(errors) + 1

gbrt_best = GradientBoostingRegressor(max_depth=2,
                                      n_estimators=bst_n_estimators,
                                      random_state=42)
gbrt_best.fit(X_train, y_train)
```

| Argument | Kind | What it does |
|---|---|---|
| `staged_predict(X_val)` | structural | A generator yielding the ensemble's prediction after each successive tree — 120 sets of predictions from one fit. |
| `np.argmin(errors) + 1` | structural | +1 because index 0 corresponds to an ensemble of ONE tree. |

Two ways to early-stop a GBRT. **(a) Train big, then look back** with `staged_predict` — simple, costs one full fit. **(b) Grow incrementally with `warm_start=True`** and break when validation error has risen five times in a row:

```python
gbrt = GradientBoostingRegressor(max_depth=2, warm_start=True, random_state=42)

min_val_error = float("inf")
error_going_up = 0
for n_estimators in range(1, 120):
    gbrt.n_estimators = n_estimators
    gbrt.fit(X_train, y_train)
    val_error = mean_squared_error(y_val, gbrt.predict(X_val))
    if val_error < min_val_error:
        min_val_error = val_error
        error_going_up = 0
    else:
        error_going_up += 1
        if error_going_up == 5:
            break   # early stopping
```

## Remember it

The same sections as scenes along a route: [](palace:09-balcony). The code is drilled in [the decks](cards).
