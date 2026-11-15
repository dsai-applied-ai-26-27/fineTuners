---
title: 'Regularization and early stopping'
number: 4
topics: [regularization]
summary: 'Ridge, Lasso and Elastic Net, and early stopping with a manual epoch loop around SGDRegressor.'
---

Part 4 of 12 of the course notes, from the 2025-26 exam kit (lectures 1 to 7, labs 1 to 10). Each section pairs an exam-ready code pattern with the theory that justifies it. Arguments are tagged **ritual** (always the same), **structural** (forced by the data or the task) or **dial** (a real hyperparameter); the full list is in [](guide:parameter-reference).

## Ridge regression (L2 penalty)

**Ridge = L2 penalty** $\alpha \sum_j \theta_j^2$. Shrinks coefficients smoothly toward zero but never exactly to zero. Always scale features first — the penalty is on the raw coefficient sizes.

```python
from sklearn.linear_model import Ridge
ridge_reg = Ridge(alpha=1, solver="cholesky", random_state=42)
ridge_reg.fit(X, y)
ridge_reg.predict([[1.5]])

# the SGD equivalent
sgd_reg = SGDRegressor(penalty="l2", max_iter=1000, tol=1e-3, random_state=42)
```

| Argument | Kind | What it does |
|---|---|---|
| `alpha=1` | dial | Regularisation strength. α=0 is plain LinearRegression; large α flattens the model towards a horizontal line (more bias, less variance). |
| `solver="cholesky"` | dial | Closed-form matrix factorisation. "sag" is stochastic average gradient — use it when the data is large. "auto" picks for you. |

## Lasso regression (L1 penalty)

**Lasso = L1 penalty** $\alpha \sum_j \lvert \theta_j \rvert$. Because the L1 ball has corners, the optimum lands on axes and coefficients become **exactly zero** — automatic feature selection. Same non-differentiability at zero as the L1 loss, so it is solved numerically.

```python
from sklearn.linear_model import Lasso
lasso_reg = Lasso(alpha=0.1)
lasso_reg.fit(X, y)
lasso_reg.predict([[1.5]])
```

| Argument | Kind | What it does |
|---|---|---|
| `alpha=0.1` | dial | Same meaning as Ridge, but here raising it kills more coefficients outright. |

## Elastic Net

Elastic Net is the middle ground: it keeps Lasso's feature selection but behaves better when features are correlated (Lasso picks one of a correlated group arbitrarily; Elastic Net shares between them).

```python
from sklearn.linear_model import ElasticNet
elastic_net = ElasticNet(alpha=0.1, l1_ratio=0.5, random_state=42)
elastic_net.fit(X, y)
elastic_net.predict([[1.5]])
```

| Argument | Kind | What it does |
|---|---|---|
| `alpha=0.1` | dial | Total regularisation strength. |
| `l1_ratio=0.5` | dial | The MIX, not the strength. 0 = pure Ridge, 1 = pure Lasso, 0.5 = half and half. |

## Early stopping

**Early stopping**: train, watch validation error fall then rise, and keep the model from the turning point. It regularises without touching the loss function. Note that `clone(model)` (imported in the exam snippet) does the opposite of `deepcopy` — it returns an *untrained* copy with the same hyperparameters, which is what you want inside a cross-validation fold.

```python
from copy import deepcopy
from sklearn.linear_model import SGDRegressor

sgd_reg = SGDRegressor(max_iter=1, tol=-np.infty, warm_start=True,
                       penalty=None, learning_rate="constant", eta0=0.0005)

minimum_val_error = float("inf")
best_epoch = None
best_model = None

for epoch in range(1000):
    sgd_reg.fit(X_train_poly_scaled, y_train)      # continues where it left off
    y_val_predict = sgd_reg.predict(X_val_poly_scaled)
    val_error = mean_squared_error(y_val, y_val_predict)
    if val_error < minimum_val_error:
        minimum_val_error = val_error
        best_epoch = epoch
        best_model = deepcopy(sgd_reg)
```

| Argument | Kind | What it does |
|---|---|---|
| `max_iter=1` | structural | One epoch per .fit() call, so the Python for-loop becomes the epoch counter. Without it, one fit would run 1000 epochs internally and you could not measure in between. |
| `warm_start=True` | structural | Do not reset θ on the next fit — continue from where the last one stopped. Without it every iteration restarts from random and the loop is meaningless. |
| `tol=-np.infty` | structural | Disables sklearn's own stopping rule. Improvement can never be smaller than −∞, so it never quits on its own; YOUR loop decides when to stop. |
| `learning_rate="constant"` | dial | No decay schedule — a fixed step, so errors at different epochs are comparable. |
| `eta0=0.0005` | dial | That fixed step size. Small, so the validation curve is smooth enough to find a clear minimum. |
| `penalty=None` | structural | No L1/L2 term, because early stopping IS the regularisation here. |
| `deepcopy(sgd_reg)` | structural | Snapshot by value. A plain assignment stores a reference to the same object, which keeps training — you would end up with the last model, not the best one. |

## Remember it

The same sections as scenes along a route: [](palace:04-pantry). The code is drilled in [the decks](cards).
