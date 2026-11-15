---
title: 'Linear regression and gradient descent'
number: 3
topics: [linear]
summary: 'The normal equation and the three kinds of gradient descent written by hand, polynomial regression, and reading learning curves for bias and variance.'
---

Part 3 of 12 of the course notes, from the 2025-26 exam kit (lectures 1 to 7, labs 1 to 10). Each section pairs an exam-ready code pattern with the theory that justifies it. Arguments are tagged **ritual** (always the same), **structural** (forced by the data or the task) or **dial** (a real hyperparameter); the full list is in [](guide:parameter-reference).

## The design matrix and the bias column

The **design matrix** trick: prepend a column of 1s so the intercept $\theta_0$ becomes just another weight and the model is a single dot product $X\theta$. **Interpretability** of linear models: increasing feature $x_j$ by one unit changes the prediction by exactly $\theta_j$.

```python
X_b = np.c_[np.ones((100, 1)), X]   # add x0 = 1 to each instance
```

## The normal equation

The **Normal Equation** $\theta = (X^\top X)^{-1} X^\top y$ is the **analytical / closed-form** optimiser for L2 loss. Exact and fast on small data, impractical on massive data (inverting $X^\top X$ scales badly in the number of features). The alternative is **numerical / iterative** optimisation — gradient descent — which is compulsory when no closed form exists at all: neural networks, L1 regression, logistic regression.

```python
theta_best = np.linalg.inv(X_b.T.dot(X_b)).dot(X_b.T).dot(y)

# equivalent, numerically safer (SVD / pseudoinverse)
theta_best_svd, residuals, rank, s = np.linalg.lstsq(X_b, y, rcond=1e-6)
```

## LinearRegression and the estimator API

Every estimator in sklearn is the same three lines: construct with hyperparameters, `fit(X, y)`, `predict(X)`. Learned attributes always end in an underscore. If you know this shape, the only thing you ever have to recall for a new model is the constructor line.

```python
from sklearn.linear_model import LinearRegression
lin_reg = LinearRegression()
lin_reg.fit(X, y)
lin_reg.intercept_, lin_reg.coef_
y_pred = lin_reg.predict(X_new)
```

## Batch gradient descent

**Batch gradient descent** uses the whole training set for every step. It moves in the direction of steepest descent (the negative gradient) until it reaches a stationary point. Convex L2 loss ⇒ that point is the global minimum.

```python
eta = 0.1            # learning rate
n_iterations = 1000
m = 100

theta = np.random.randn(2, 1)          # random initialization

for iteration in range(n_iterations):
    gradients = 2/m * X_b.T.dot(X_b.dot(theta) - y)
    theta = theta - eta * gradients
```

| Argument | Kind | What it does |
|---|---|---|
| `eta = 0.1` | dial | The learning rate α. Too high and it overshoots and diverges; too low and it converges uselessly slowly. |
| `2/m` | structural | The 2 comes from differentiating the square; the /m averages over ALL m instances — that is what makes it 'batch'. |

## Stochastic gradient descent and the learning schedule

**Why single instances:** each step costs O(1) instead of O(m), so it handles huge datasets and can escape local minima by bouncing. The price is that it never settles — it keeps jittering around the optimum. **That is what the schedule fixes:** η starts large (fast progress, still able to jump out of bad regions) and decays towards zero (small final steps, so the parameters can come to rest). It is simulated annealing: hot then cold. Fix η constant and you get a model that orbits the answer forever.

```python
n_epochs = 50
t0, t1 = 5, 50          # learning schedule hyperparameters

def learning_schedule(t):
    return t0 / (t + t1)

theta = np.random.randn(2, 1)

for epoch in range(n_epochs):
    for i in range(m):
        random_index = np.random.randint(m)
        xi = X_b[random_index:random_index+1]
        yi = y[random_index:random_index+1]
        gradients = 2 * xi.T.dot(xi.dot(theta) - yi)
        eta = learning_schedule(epoch * m + i)
        theta = theta - eta * gradients
```

| Argument | Kind | What it does |
|---|---|---|
| `t0, t1 = 5, 50` | dial | Numerator and offset of the decay. Larger t1 = slower cooling. Mini-batch in the same lab uses 200, 1000. |
| `random_index` | structural | One instance drawn at random per step — that is the definition of stochastic. |
| `gradients = 2 * ...` | structural | No /m here. You are averaging over exactly one instance, so there is nothing to divide by. |
| `xi = X_b[i:i+1]` | structural | Slice, not index — keeps it a (1, n) 2-D array so the matrix algebra still works. |

## Mini-batch gradient descent

**Mini-batch GD**: the divisor always matches how many instances the gradient was computed on — `2/m` for batch, `2` for one instance, `2/minibatch_size` here. Reshuffling each epoch stops the model seeing the same batch composition twice.

```python
n_iterations = 50
minibatch_size = 20

t0, t1 = 200, 1000
t = 0
for epoch in range(n_iterations):
    shuffled_indices = np.random.permutation(m)
    X_b_shuffled = X_b[shuffled_indices]
    y_shuffled = y[shuffled_indices]
    for i in range(0, m, minibatch_size):
        t += 1
        xi = X_b_shuffled[i:i+minibatch_size]
        yi = y_shuffled[i:i+minibatch_size]
        gradients = 2/minibatch_size * xi.T.dot(xi.dot(theta) - yi)
        eta = learning_schedule(t)
        theta = theta - eta * gradients
```

## Polynomial regression

A model is **linear if it is linear in the parameters θ**, even when it is nonlinear in the variables. Each θ must appear as a plain multiplier — not in an exponent, a denominator, or inside a sine. **Basis functions** (x², sin x, log x) buy flexibility for free under that definition. The risks are **overfitting** and **Runge's phenomenon** — high-degree polynomials oscillate wildly near the edges of the data.

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

poly_pipeline = Pipeline([
    ("poly_features", PolynomialFeatures(degree=2, include_bias=False)),
    ("std_scaler", StandardScaler()),
    ("lin_reg", LinearRegression()),
])
poly_pipeline.fit(X_train, y_train)
```

| Argument | Kind | What it does |
|---|---|---|
| `degree=2` | dial | How much flexibility. Raise it and you fit wilder curves — and overfit. Lab 4 goes to 90 and 300 to show it breaking. |
| `include_bias=False` | structural | Do NOT add the column of 1s — LinearRegression already fits its own intercept, and StandardScaler would choke on a constant column (zero variance). |

## Learning curves, bias and variance

**Learning curves** = error vs training-set size. **Both curves high and close** ⇒ underfitting / high **bias**: the model is too simple, more data will not help. **Large persistent gap** ⇒ overfitting / high **variance**: it fits noise; more data or more regularisation will help. Increasing complexity makes test error trace a **U**; the sweet spot is the bottom.

```python
def plot_learning_curves(model, X, y):
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=10)
    train_errors, val_errors = [], []
    for m in range(1, len(X_train) + 1):
        model.fit(X_train[:m], y_train[:m])
        train_errors.append(mean_squared_error(y_train[:m], model.predict(X_train[:m])))
        val_errors.append(mean_squared_error(y_val, model.predict(X_val)))
```

## Remember it

The same sections as scenes along a route: [](palace:03-kitchen). The code is drilled in [the decks](cards).
