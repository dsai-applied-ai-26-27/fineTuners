---
title: Fisher's discriminant and PCA
topics: [features]
summary: Two ways to pick a projection direction. One looks for spread, the other for separation. The past paper asked for both, and for the difference.
takeaways:
  - Fisher maximises a **ratio**, projected between-class spread over projected within-class spread. Never either part alone.
  - 'For two classes: $f \propto \Sigma_W^{-1}(\mu_1 - \mu_2)$ with $\Sigma_W = \Sigma_1 + \Sigma_2$.'
  - PCA is unsupervised and keeps variance. Fisher is supervised and keeps separability.
  - The direction of largest variance can be exactly the direction in which the classes overlap.
---

## Extraction and selection

There are two ways to get from $m$ measurements $y$ to $n$ features $x$.

**Extraction** builds new features as combinations, $x = F^\top y$ (or a nonlinear $f(y)$).
It is a continuous matrix problem and usually has an eigenvector solution.

**Selection** keeps a subset of the original measurements, $x = S^\top y$ where each column
of $S$ has a single 1. It is a discrete search over $\binom{m}{n}$ subsets, which is
genuinely harder, and the best single feature need not belong to the best pair.

Prefer selection when measurement cost, original units or interpretability matter. Prefer
extraction when combinations of measurements are meaningful and discrimination matters more
than interpretability.

## Fisher's criterion

Lecture 1 said a good feature makes within-class variability small compared with
between-class variability. Fisher's criterion is that sentence as a formula. For a
projection direction $f$:

$$J(f) = \frac{f^\top \Sigma_T f}{f^\top \Sigma_W f}, \qquad \Sigma_W = \sum_{\kappa=1}^{K} \Sigma_\kappa$$

Here $\Sigma_\kappa$ is the covariance of class $\kappa$, $\Sigma_W$ the within-class scatter
and $\Sigma_T$ the between-class (total) scatter. Read the ratio as *projected between-class
spread divided by projected within-class spread*. The numerator is how far apart the class
means land after projection; the denominator is how wide the classes are once projected.

Both halves matter. A large gap between the means is worthless if the classes are smeared
across it, and a tight projection is worthless if the means coincide.

:::paper
Fisher's criterion finds the direction onto which to project so that the classes are as
separable as possible in one dimension: it pushes the projected class means apart while
keeping each projected class tight.
:::

### The two-class direction

For two classes the maximiser has a closed form.

$$f_{\text{Fisher}} \propto \Sigma_W^{-1}(\mu_1 - \mu_2), \qquad \Sigma_W = \Sigma_1 + \Sigma_2$$

Only the direction matters, so any positive multiple is the same answer. "Simplest integer
form" in an exam means: clear the fraction and divide out any common factor.

The factor $\Sigma_W^{-1}$ is what makes this more than the difference of the means. It
rotates the naive direction $\mu_1 - \mu_2$ away from the directions in which the classes are
already wide.

:::example Fisher's direction from numbers
$\mu_A = (1, 1)^\top$, $\Sigma_A = \begin{pmatrix} 1 & 0 \\ 0 & 2 \end{pmatrix}$ and
$\mu_B = (3, 2)^\top$, $\Sigma_B = \begin{pmatrix} 4 & 2 \\ 2 & 4 \end{pmatrix}$.

$$\Sigma_W = \begin{pmatrix} 5 & 2 \\ 2 & 6 \end{pmatrix}, \qquad \det \Sigma_W = 26, \qquad \Sigma_W^{-1} = \frac{1}{26} \begin{pmatrix} 6 & -2 \\ -2 & 5 \end{pmatrix}$$

$$w \propto \frac{1}{26} \begin{pmatrix} 6 & -2 \\ -2 & 5 \end{pmatrix} \begin{pmatrix} 2 \\ 1 \end{pmatrix} = \frac{1}{26} \begin{pmatrix} 10 \\ 1 \end{pmatrix} \quad\Longrightarrow\quad w = \begin{pmatrix} 10 \\ 1 \end{pmatrix}$$

The mean difference alone is $(2, 1)^\top$. Multiplying by $\Sigma_W^{-1}$ has swung it hard
towards the first axis, because class B is wide and correlated while A is narrow there. The
full step-by-step version is the card [](card:fisher-compute).
:::

### More than two classes

For several Fisher features keep the eigenvectors with the largest eigenvalues of

$$\Sigma_W^{-1} \Sigma_T F = F \Lambda .$$

There are at most $K - 1$ useful directions for $K$ classes.

### Where Fisher fails

:::pitfall
Fisher summarises each class only through its mean and covariance. Two banana-shaped classes
can be perfectly separable by a line in 2-D and still project onto overlapping intervals.
Fisher is not badly optimised there: it maximises its ratio correctly. The ratio is simply
not the right summary of that geometry.
:::

It also needs an invertible $\Sigma_W$.

## PCA

Principal component analysis solves an ordinary eigenproblem on the covariance $\Sigma$ of
the data:

$$\Sigma v_j = \lambda_j v_j, \qquad \lambda_1 \ge \dots \ge \lambda_m, \qquad F = [\,v_1 \;\dots\; v_n\,]$$

Keep the eigenvectors with the largest eigenvalues. They preserve the maximum variance and
minimise the mean squared error of linear reconstruction. Labels are never used.

How much the first $q$ components keep is the cumulative variance

$$v_q = \sum_{j=1}^{q} \lambda_j, \qquad v_m = \operatorname{tr}(\Sigma).$$

Strongly correlated measurements are redundant, so a few components capture nearly
everything. Weakly correlated measurements give a slow, nearly linear cumulative curve.

## PCA or Fisher

| | PCA | Fisher's discriminant |
|---|---|---|
| **Uses labels?** | No, unsupervised | Yes, supervised |
| **Maximises** | Retained variance (minimises reconstruction error) | Between-class over within-class spread |
| **Eigenproblem** | $\Sigma v = \lambda v$ | $\Sigma_W^{-1} \Sigma_T F = F \Lambda$ |
| **Directions available** | Up to $m$ | At most $K - 1$ |
| **Fails when** | The direction of largest variance is where the classes overlap | Classes are not described by mean and covariance, or $\Sigma_W$ is singular |
| **Use it for** | Compression, denoising, visualisation, preprocessing when $m \gg N$ | Discrimination, when labels exist |

:::paper
PCA is unsupervised and maximises retained variance. Fisher is supervised and maximises class
separability. Variance is not class information: the direction of largest variance can be
exactly the direction in which the classes overlap.
:::

PCA is also a preprocessing step *for* Fisher: when the dimension is large relative to the
number of samples, reducing it first makes $\Sigma_W$ invertible.

## Three simpler directions, and how each breaks

1. **Between the means**, $f \propto \mu_1 - \mu_2$. Maximises the gap. Fails when large
   class variance lies along the mean difference.
2. **Most compact within-class**, the eigenvector of $\Sigma_W$ with the smallest eigenvalue.
   Fails when the projected means coincide in that direction.
3. **Largest total variance**, the top eigenvector of $\Sigma_T$, which is PCA. Fails when the
   total spread comes from elongation inside the classes and not from their separation.

Fisher is the principled compromise between 1 and 2.

:::recall Why can a nonlinear feature be needed?
When the class structure is curved or folded (a lower-dimensional **manifold** embedded in
the measurement space), no linear projection preserves the separation. A nonlinear mapping
can unfold it.
:::

## Practise

[](deck:ch5-features) holds the statements and the numeric derivation.
[](problems:fisher-and-boundaries#fb-p1) compares Fisher against the mean-difference
direction with numbers. The past paper asks all of this in
[questions 1 and 2](paper:final/past-paper).
