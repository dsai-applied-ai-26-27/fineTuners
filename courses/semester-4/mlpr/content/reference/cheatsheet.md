---
title: Cheat sheet
summary: Chapters 5 and 6 on one page, for the last read before the exam.
topics: [features, distance]
---

## Fisher

- Criterion $J(f) = \dfrac{f^\top \Sigma_T f}{f^\top \Sigma_W f}$: between over within.
- Two classes: $f \propto \Sigma_W^{-1}(\mu_1 - \mu_2)$, $\Sigma_W = \Sigma_1 + \Sigma_2$.
- Recipe: add, invert, multiply, drop the scalar.
- Project: $\mu_x = f^\top \mu$, $\sigma_x^2 = f^\top \Sigma f$.
- At most $K - 1$ directions. Needs invertible $\Sigma_W$.
- Fails for classes not described by mean and covariance.

## PCA

- $\Sigma v_j = \lambda_j v_j$, keep the largest $\lambda_j$.
- Maximum variance, minimum reconstruction error.
- Unsupervised: variance is not class information.

## PCA or Fisher

| | PCA | Fisher |
|---|---|---|
| Labels | No | Yes |
| Keeps | Variance | Separability |
| Directions | Up to $m$ | At most $K - 1$ |

## Distances

- Minkowski $d_\rho$: $\rho = 1$ diamond, $2$ circle, $\infty$ square.
- Mahalanobis $\sqrt{(x - \mu)^\top \Sigma^{-1} (x - \mu)}$: distance in sigmas.
- A class distance needs a point distance **and** a prototype.
- Prototypes: mean, NN, kNN, furthest neighbour.

## MED boundary

- $2x^\top(\mu_2 - \mu_1) = \lVert \mu_2 \rVert^2 - \lVert \mu_1 \rVert^2$.
- Perpendicular bisector, through the midpoint.
- Straight because $x^\top x$ cancels.
- Not one line if: $K > 2$, prototype is not the mean, metric is not L2, or MMD with unequal
  $\Sigma$.

## Tools

- $\begin{pmatrix} a & b \\ c & d \end{pmatrix}^{-1} = \dfrac{1}{ad - bc} \begin{pmatrix} d & -b \\ -c & a \end{pmatrix}$
- $\begin{pmatrix} a & b \\ b & a \end{pmatrix}$: $\lambda = a \pm b$ along $(1, \pm 1)$.
- Ellipse semi-axis is $\sqrt{\lambda}$, not $\lambda$.

## kNN

- Distances, sort, take $k$, vote.
- $k$ small: noisy. $k$ large: blurred.
- Standardise first. Choose $k$ odd for two classes.
