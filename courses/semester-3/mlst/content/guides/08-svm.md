---
title: 'Support vector machines'
number: 8
topics: [svm]
summary: 'Maximum margin and support vectors, soft margin and C, hinge loss, kernels, and SVM regression.'
---

Part 8 of 12 of the course notes, from the 2025-26 exam kit (lectures 1 to 7, labs 1 to 10). Each section pairs an exam-ready code pattern with the theory that justifies it. Arguments are tagged **ritual** (always the same), **structural** (forced by the data or the task) or **dial** (a real hyperparameter); the full list is in [](guide:parameter-reference).

## Maximum margin

**SVM** is a binary linear classifier built on geometry: find the hyperplane that separates the classes with the **maximum margin**. A larger margin is more robust to noise and generalises better.

## Support vectors

**Support vectors** are the instances lying exactly on the margin boundaries. The final solution depends *only* on them, not on the rest of the dataset — which is why SVMs are memory-efficient at prediction time and sensitive to a few critical points.

## Hard and soft margin, and C

A **hard-margin** SVM requires perfect linear separability, which real data rarely offers. **Soft margin** introduces **slack variables ξ** that permit violations, with C controlling the trade-off between maximising the margin and minimising violations.

```python
from sklearn.svm import SVC, LinearSVC
SVC(kernel="linear", C=float("inf"))    # hard margin
SVC(kernel="linear", C=100)             # soft margin
LinearSVC(C=1, loss="hinge", random_state=42)
```

| Argument | Kind | What it does |
|---|---|---|
| `C` | dial | Cost of margin violations. LARGE C = narrow margin, few violations, risk of overfitting. SMALL C = wide margin, more violations, more regularisation. It is the inverse of alpha. |
| `loss="hinge"` | structural | Makes LinearSVC the true SVM loss; its default is squared_hinge. |

## Hinge loss

**Hinge loss**: zero for points correctly classified and outside the margin; grows linearly for points inside the margin or misclassified. So an SVM is just **regularised ERM with hinge loss** — the same machinery as everything else in this course, with a different loss function.

## Kernels and the kernel trick

**The kernel trick**: explicitly computing a high-dimensional feature map is expensive or impossible. A **kernel function** computes the inner product in that space implicitly, using only the original coordinates. **Polynomial kernel** ↔ monomials up to a degree. **RBF/Gaussian** ↔ similarity based on distance, allowing smooth and highly flexible boundaries.

```python
SVC(kernel="poly", degree=3, coef0=1, C=5)
SVC(kernel="poly", degree=10, coef0=100, C=5)
SVC(kernel="rbf", gamma=5, C=0.001)
SVC(kernel="rbf", gamma="scale", probability=True, random_state=42)
```

| Argument | Kind | What it does |
|---|---|---|
| `kernel` | structural | "linear", "poly" (monomials up to a degree), "rbf"/Gaussian (similarity by distance), "sigmoid". |
| `degree` | dial | Polynomial order. Higher = more flexible = more overfitting risk. |
| `coef0` | dial | How much the high-degree terms count relative to the low-degree ones in a polynomial kernel. |
| `gamma` | dial | Reach of a single training point's influence in RBF. LARGE gamma = narrow bell = wiggly, overfit boundary. SMALL gamma = wide bell = smoother. gamma and C both increase complexity: if overfitting, reduce BOTH. |
| `probability=True` | structural | SVC has no predict_proba by default. Required for soft voting in an ensemble; it fits an extra calibration and slows training. |

## SVM regression

**SVR inverts the objective**: classification pushes instances off the street, regression fits as many instances as possible on the street. Adding instances inside the tube does not change the model at all.

```python
from sklearn.svm import LinearSVR, SVR
LinearSVR(epsilon=1.5, random_state=42)
SVR(kernel="poly", degree=2, C=100, epsilon=0.1, gamma="scale")
```

| Argument | Kind | What it does |
|---|---|---|
| `epsilon` | dial | Half-width of the insensitive tube. Errors smaller than ε cost nothing. Larger ε = flatter, simpler model. |
| `C` | dial | In SVR, LARGE C means less regularisation (tighter fit), same direction as in SVC. |

## Remember it

The same sections as scenes along a route: [](palace:08-bedroom). The code is drilled in [the decks](cards).
