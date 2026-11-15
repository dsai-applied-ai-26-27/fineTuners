---
title: 'Preprocessing pipelines'
number: 2
topics: [preprocessing]
summary: 'Imputing, scaling and encoding, chaining them with Pipeline and ColumnTransformer, the fit and transform rule that prevents leakage, and grid search.'
---

Part 2 of 12 of the course notes, from the 2025-26 exam kit (lectures 1 to 7, labs 1 to 10). Each section pairs an exam-ready code pattern with the theory that justifies it. Arguments are tagged **ritual** (always the same), **structural** (forced by the data or the task) or **dial** (a real hyperparameter); the full list is in [](guide:parameter-reference).

## Imputing missing values

Imputation only works on numbers, which is exactly why the numerical and categorical columns get separate branches downstream.

```python
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy="median")
```

| Argument | Kind | What it does |
|---|---|---|
| `strategy="median"` | dial | Median over mean because it is robust to outliers and skew. Options: mean, median, most_frequent, constant. |

## Standardising features

Subtract mean, divide by std → zero mean, unit variance. **Essential** for anything distance-based or gradient-based: k-NN, SVM, PCA, gradient descent, neural nets. **Irrelevant** for decision trees and random forests, which only compare thresholds within a feature.

```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)   # learn mean/std AND transform
X_test_scaled  = scaler.transform(X_test)        # reuse the learned mean/std
```

## One-hot and dummy encoding

One-hot creates **k dummy columns** for k categories. **Dummy encoding** creates k−1 and treats the omitted one as the reference, removing the redundancy (the k columns always sum to 1, so one is linearly dependent on the others).

```python
from sklearn.preprocessing import OneHotEncoder
cat_encoder = OneHotEncoder()
```

## Pipeline and ColumnTransformer

**Pipeline** chains steps *vertically* on the same columns — output of one feeds the next, and every step but the last must be a transformer. **ColumnTransformer** works *horizontally* — different transformers on different column subsets, results concatenated side by side. Both expose fit/transform, so a pipeline can sit inside a ColumnTransformer and vice versa.

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

num_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("std_scaler", StandardScaler()),
])

full_pipeline = ColumnTransformer([
    ("num", num_pipeline, num_attribs),
    ("cat", OneHotEncoder(), cat_attribs),
])

X_prepared = full_pipeline.fit_transform(X)
```

| Argument | Kind | What it does |
|---|---|---|
| `("name", transformer, columns)` | structural | Every ColumnTransformer entry is a 3-tuple; every Pipeline step is a 2-tuple. The names are yours and only matter for grid search ("num__imputer__strategy"). |

## fit, transform and data leakage

**fit** learns parameters (means, stds, categories, components). **transform** applies them. Calling `fit` or `fit_transform` on the test set is **data leakage** — the test estimate becomes optimistic. Models use `fit` / `predict`; transformers use `fit` / `transform`. That is the entire sklearn API.

```python
scaler.fit_transform(X_train)   # LEARN the statistics, then apply them
scaler.transform(X_test)        # APPLY the already-learned statistics

# same convention for anything with parameters
pca = PCA(n_components=0.95)
X_train_reduced = pca.fit_transform(X_train)
X_test_reduced  = pca.transform(X_test)
```

## Grid search

Grid search is exhaustive; `RandomizedSearchCV` samples instead, which is better when the grid is large. After fitting, `best_params_` holds the winning dict, `best_estimator_` the model already refitted on the whole training set.

```python
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier

param_grid = {"max_leaf_nodes": list(range(2, 100)),
              "min_samples_split": [2, 3, 4]}

grid_search = GridSearchCV(DecisionTreeClassifier(random_state=42),
                           param_grid, cv=3)
grid_search.fit(X_train, y_train)

print(grid_search.best_params_)
best = grid_search.best_estimator_
```

| Argument | Kind | What it does |
|---|---|---|
| `param_grid = {...}` | structural | A dict of parameter name → list of values. Every combination is tried, so cost is the product of the list lengths times cv. |
| `cv=3` | dial | Folds of cross-validation per candidate. More folds = more reliable, linearly more expensive. |

## Remember it

The same sections as scenes along a route: [](palace:02-hallway). The code is drilled in [the decks](cards).
