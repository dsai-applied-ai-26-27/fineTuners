---
title: 'Classification models'
number: 6
topics: [classifiers]
summary: 'Discriminant against generative models, logistic and softmax regression, LDA and QDA, Naive Bayes, k-nearest neighbours, and what makes a classifier linear.'
---

Part 6 of 12 of the course notes, from the 2025-26 exam kit (lectures 1 to 7, labs 1 to 10). Each section pairs an exam-ready code pattern with the theory that justifies it. Arguments are tagged **ritual** (always the same), **structural** (forced by the data or the task) or **dial** (a real hyperparameter); the full list is in [](guide:parameter-reference).

## Discriminant and generative approaches

**Discriminant approach**: optimise the decision boundary directly via a loss function and ERM. Logistic Regression, SVM. **Generative approach**: model the feature distribution of each class separately, then use **Bayes' theorem** to get the posterior. Naive Bayes, LDA/QDA.

## Logistic regression

A **probabilistic discriminant** method for binary classification. The **logistic (sigmoid)** function squashes the linear score into (0,1). Trained by minimising **negative log-likelihood**, also called log loss or cross-entropy. It is still a **linear classifier**: the boundary p=0.5 corresponds to score=0, which is an affine function of the features.

```python
from sklearn.linear_model import LogisticRegression
log_reg = LogisticRegression(solver="lbfgs", random_state=42)
log_reg.fit(X, y)

y_proba = log_reg.predict_proba(X_new)     # probabilities
y_pred  = log_reg.predict(X_new)           # hard labels at p = 0.5
```

| Argument | Kind | What it does |
|---|---|---|
| `solver="lbfgs"` | ritual | The default optimiser. It appears in every logistic regression in this course; treat it as boilerplate. |
| `C` | dial | INVERSE regularisation strength — the opposite direction to alpha. Small C = strong regularisation. |

## Softmax regression

**Softmax regression** generalises logistic regression to multi-class: each class gets a score, and softmax normalises the exponentials so they sum to 1. Alternatives for making a binary model multi-class: `OneVsRestClassifier`, one-vs-one.

```python
softmax_reg = LogisticRegression(multi_class="multinomial", solver="lbfgs",
                                 C=10, random_state=42)
softmax_reg.fit(X, y)
```

| Argument | Kind | What it does |
|---|---|---|
| `multi_class="multinomial"` | structural | True softmax across all classes at once, instead of one-vs-rest binary models. |
| `C=10` | dial | Weak regularisation here (remember: inverse). |

## LDA and QDA

**GDA** assumes each class is multivariate Gaussian. **LDA**: all classes share one covariance matrix ⇒ the quadratic terms cancel ⇒ **linear** boundary. **QDA**: each class keeps its own covariance ⇒ **quadratic, curved** boundary, more parameters, more data needed.

```python
from sklearn.discriminant_analysis import (LinearDiscriminantAnalysis,
                                          QuadraticDiscriminantAnalysis)
lda = LinearDiscriminantAnalysis(store_covariance=True)
qda = QuadraticDiscriminantAnalysis(store_covariance=True)
lda.fit(X, y); qda.fit(X, y)
```

| Argument | Kind | What it does |
|---|---|---|
| `store_covariance=True` | ritual | Keeps the estimated covariance matrices so you can plot the ellipses. Nothing to do with the model's behaviour. |

## Naive Bayes

**Naive Bayes** is generative and assumes **conditional independence of features given the class**. That turns an intractable joint density into a product of one-dimensional ones. Wrong in principle, effective in practice — especially high-dimensional text like spam filtering.

```python
from sklearn.naive_bayes import GaussianNB
nb = GaussianNB()
nb.fit(X_train, y_train)

# text pipeline, as in the SMS spam lecture
from sklearn.feature_extraction.text import TfidfVectorizer
vec = TfidfVectorizer(ngram_range=(1, 2))
X = vec.fit_transform(corpus)
```

## k-nearest neighbours

**k-NN** predicts from the k most similar training points: majority vote for classification, (weighted) average for regression. It is a **lazy, non-parametric, non-linear** method — no training phase, all cost at prediction time. **Feature scaling is mandatory**, because everything is distances.

```python
from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train_scaled, y_train)     # SCALED features
y_pred = knn.predict(X_test_scaled)
```

| Argument | Kind | What it does |
|---|---|---|
| `n_neighbors=5` | dial | Small k = jagged boundary, low bias, HIGH variance (overfit). Large k = smooth, HIGH bias, low variance. |
| `weights="distance"` | dial | Closer neighbours count more (w = 1/d). Default "uniform" treats all k equally; weighted gives smoother transitions and better local detail. |
| `metric` | dial | Euclidean is typical for continuous data; Manhattan and the general Minkowski are alternatives; Gower handles mixed numeric + categorical. |

## Linear and non-linear classifiers

A classifier is **linear** if its decision boundary — the hypersurface where the model is undecided — is an affine linear function of the features. It carves the space into half-spaces. **Linear:** logistic regression, perceptron, linear SVM. **Non-linear:** k-NN, decision trees, RBF-kernel SVM. Applying a sigmoid does not break linearity: what matters is whether the ranking of classes depends on an affine combination of features.

## Remember it

The same sections as scenes along a route: [](palace:06-living-room). The code is drilled in [the decks](cards).
