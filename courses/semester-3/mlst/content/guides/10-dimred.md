---
title: 'Dimensionality reduction'
number: 10
topics: [dimred]
summary: 'The curse of dimensionality, PCA and how many components to keep, incremental and randomized PCA, kernel PCA and LLE.'
---

Part 10 of 12 of the course notes, from the 2025-26 exam kit (lectures 1 to 7, labs 1 to 10). Each section pairs an exam-ready code pattern with the theory that justifies it. Arguments are tagged **ritual** (always the same), **structural** (forced by the data or the task) or **dial** (a real hyperparameter); the full list is in [](guide:parameter-reference).

## The curse of dimensionality

**Curse of dimensionality**: as dimensions grow, points become sparse and all pairwise distances converge, which breaks distance-based methods (k-NN, RBF kernels) and demands exponentially more data. High-dimensional data usually lies near a much lower-dimensional **manifold**, which is what makes reduction possible.

## PCA

**PCA** projects onto the orthogonal axes of **maximum variance**. Each successive component is orthogonal to the previous ones and captures as much of the remaining variance as it can. It is a linear projection, and it requires centred (usually scaled) data.

```python
from sklearn.decomposition import PCA
pca = PCA(n_components=2)
X2D = pca.fit_transform(X)

pca.components_               # the principal axes
pca.explained_variance_ratio_ # fraction of variance kept per axis
```

## Choosing the number of components

Plot cumulative explained variance against the number of components and look for the elbow. `np.argmax(cumsum >= 0.95) + 1` is the index of the first component that crosses the threshold, converted to a count.

```python
pca = PCA()
pca.fit(X_train)
cumsum = np.cumsum(pca.explained_variance_ratio_)
d = np.argmax(cumsum >= 0.95) + 1

# or in one line — let PCA choose d for you
pca = PCA(n_components=0.95)
X_reduced = pca.fit_transform(X_train)
```

| Argument | Kind | What it does |
|---|---|---|
| `n_components=154` | structural | An INT means: give me exactly this many dimensions. |
| `n_components=0.95` | structural | A FLOAT below 1 means: give me however many dimensions preserve this share of the variance. Same argument, completely different meaning — a favourite exam trap. |

## Incremental and randomized PCA

```python
from sklearn.decomposition import IncrementalPCA
inc_pca = IncrementalPCA(n_components=154)
for X_batch in np.array_split(X_train, n_batches):
    inc_pca.partial_fit(X_batch)
X_reduced = inc_pca.transform(X_train)

rnd_pca = PCA(n_components=154, svd_solver="randomized", random_state=42)
```

| Argument | Kind | What it does |
|---|---|---|
| `partial_fit` | structural | Incremental learning — note it is NOT fit; you call it once per batch. |
| `svd_solver="randomized"` | dial | Approximate but much faster SVD when d is far smaller than the number of features. |

## Kernel PCA and LLE

**Kernel PCA** applies the kernel trick to PCA, allowing non-linear projections. **LLE** is **manifold learning**: it preserves local linear relationships between neighbours rather than global distances, which is what actually unrolls a Swiss roll.

```python
from sklearn.decomposition import KernelPCA
from sklearn.manifold import LocallyLinearEmbedding

rbf_pca = KernelPCA(n_components=2, kernel="rbf", gamma=0.04,
                    fit_inverse_transform=True)
X_reduced = rbf_pca.fit_transform(X)

lle = LocallyLinearEmbedding(n_components=2, n_neighbors=10, random_state=42)
X_reduced = lle.fit_transform(X)
```

| Argument | Kind | What it does |
|---|---|---|
| `kernel="rbf"` | dial | Also "linear" (identical to plain PCA), "poly", "sigmoid" (with coef0). |
| `gamma` | dial | Same meaning as in an RBF SVM — the reach of each point's influence. |
| `fit_inverse_transform=True` | structural | Needed to map reduced points back to the original space (for reconstruction error). |
| `n_neighbors=10` | dial | How large a local neighbourhood LLE treats as linear. |

## Remember it

The same sections as scenes along a route: [](palace:10-storage-closet). The code is drilled in [the decks](cards).
