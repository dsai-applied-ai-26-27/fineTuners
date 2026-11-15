---
title: Distances, prototypes and decision boundaries
topics: [distance]
summary: A distance-based classifier is a point distance plus a class prototype. Which pair you choose decides the shape of the boundary, and whether it is straight.
takeaways:
  - A point-to-class distance needs **both** a point distance and a prototype. Naming one without the other is an incomplete answer.
  - 'MED boundary for two classes: $2x^\top(\mu_2 - \mu_1) = \lVert \mu_2 \rVert^2 - \lVert \mu_1 \rVert^2$, the perpendicular bisector of the means.'
  - It is straight because the $x^\top x$ terms cancel. Say so explicitly; that step earns the mark.
  - Change the number of classes, the prototype or the metric, and it stops being one straight line.
---

## Distance between two points

The Minkowski family, with one parameter $\rho$:

$$d_\rho(x, z) = \Big( \sum_j |x_j - z_j|^\rho \Big)^{1/\rho}$$

| $\rho$ | Name | Unit contour in 2-D | In 3-D | Character |
|---|---|---|---|---|
| 1 | Manhattan | Diamond | Octahedron | Blunts one large discrepancy |
| 2 | Euclidean | Circle | Sphere | Rotationally natural; penalises large deviations quadratically |
| 4 | | Rounded square | Rounded cube | |
| $\infty$ | Maximum coordinate | Square | Cube | Only the worst coordinate counts |

Units and scaling matter for all of them.

**Mahalanobis distance** is the odd one out. It is measured against a class, using that
class's covariance $\Sigma$:

$$d_M(x, \mu) = \sqrt{(x - \mu)^\top \Sigma^{-1} (x - \mu)}$$

It measures displacement in standard-deviation units: it shrinks directions of high variance
and stretches directions of low variance. Its unit contours are exactly the class's own
covariance ellipses.

## From a class to a prototype

A class is many points. To measure the distance from $x$ to a class you must say which point
of the class stands for it.

| Prototype | Behaviour |
|---|---|
| **Mean** | Fixed and fast. Assumes a compact class |
| **Nearest neighbour** | Follows any shape. One outlier or mislabelled point can own a whole region. Expensive |
| **k nearest neighbours** | The compromise. Larger $k$ is more robust and less local; at $k = N$ the local mean becomes the global class mean |
| **Furthest neighbour** | Conservative: a point is close to the class only if it is close even to its furthest member |

:::pitfall
"Nearest neighbour" on its own is not a classifier. One query against one set of points can
give three different answers under L1, L2 and L∞. Always name the point distance as well.
:::

**Point pruning** discards stored points that provably cannot be the nearest. It cuts
computation and is not meant to change the decision.

## MED: minimum Euclidean distance to the mean

Assign $x$ to the class whose mean is nearest. For two classes the boundary is where the two
distances tie. Square both (squaring is monotonic, so the boundary is the same):

$$\lVert x - \mu_1 \rVert^2 = \lVert x - \mu_2 \rVert^2$$

$$x^\top x - 2x^\top \mu_1 + \mu_1^\top \mu_1 = x^\top x - 2x^\top \mu_2 + \mu_2^\top \mu_2$$

The term $x^\top x$ is the same on both sides and cancels:

$$2x^\top(\mu_2 - \mu_1) = \lVert \mu_2 \rVert^2 - \lVert \mu_1 \rVert^2$$

Everything left is linear in $x$. That is a hyperplane: in 2-D, the **perpendicular
bisector** of the segment joining the means, through the midpoint
$\tfrac{1}{2}(\mu_1 + \mu_2)$, with normal vector $\mu_2 - \mu_1$.

:::paper
For two classes, mean prototypes and Euclidean distance the MED boundary is always a straight
line, whatever the covariances, because the quadratic term $x^\top x$ cancels. MED never
looks at the covariances.
:::

:::example
$\mu_A = (1, 1)^\top$, $\mu_B = (3, 2)^\top$. Then $\mu_B - \mu_A = (2, 1)^\top$ and
$\lVert \mu_B \rVert^2 - \lVert \mu_A \rVert^2 = 13 - 2 = 11$, so

$$4x_1 + 2x_2 = 11 \quad\Longleftrightarrow\quad 2x_1 + x_2 = 5.5 .$$

Check: the midpoint $(2, 1.5)$ gives $4 + 1.5 = 5.5$.
:::

## When the boundary is not one straight line

| Classifier | Boundary | Why |
|---|---|---|
| MED, two classes | One straight line (hyperplane) | $x^\top x$ cancels |
| MED, $K > 2$ | Piecewise linear, a Voronoi partition | Pairwise bisectors; only the winning pieces survive |
| MMD, equal $\Sigma$ | Straight | The quadratic terms still cancel |
| MMD, unequal $\Sigma$ | Quadratic, possibly **two** branches | The broader class wins both far tails |
| NN, Euclidean | Piecewise-linear Voronoi edges, possibly disconnected | Every training point owns a cell |
| MED with L1 or L∞ | Piecewise linear, with tie regions | Diamond and square contours |

MMD is the minimum **Mahalanobis** distance classifier. MED and MMD coincide exactly when
every class has the same *spherical* covariance $\Sigma_\kappa = cI$: a common positive scale
cannot change which class is nearest.

:::example Two boundaries from unequal covariances
$\mu_A = (0, 0)^\top$, $\Sigma_A = I$ against $\mu_B = (4, 0)^\top$,
$\Sigma_B = \operatorname{diag}(4, 1)$. Setting the squared Mahalanobis distances equal, the
$x_2^2$ terms cancel but the $x_1^2$ terms do not:

$$x_1^2 = \frac{(x_1 - 4)^2}{4} \quad\Longrightarrow\quad 3x_1^2 + 8x_1 - 16 = 0 \quad\Longrightarrow\quad x_1 = \tfrac{4}{3} \ \text{ or } \ x_1 = -4 .$$

Class A owns only the strip $-4 < x_1 < \tfrac{4}{3}$. The wider class B owns both outer
regions, including the one behind A's own mean. On the same means MED gives the single line
$x_1 = 2$. Worked step by step in [](card:mmd-two-boundaries).
:::

A **Voronoi region** is the set of points closer to one prototype than to any other. With
three class means you draw all three pairwise bisectors, find the point where they meet, and
keep only the three rays leaving it: along the rest of each line a third class is closer.
See [](card:med-three-class).

## Two tools you will need

The inverse of a $2 \times 2$ matrix, used in every Fisher and Mahalanobis question:

$$\begin{pmatrix} a & b \\ c & d \end{pmatrix}^{-1} = \frac{1}{ad - bc} \begin{pmatrix} d & -b \\ -c & a \end{pmatrix}$$

Swap the diagonal, negate the off-diagonal, divide by the determinant.

And a trap: only **monotonic** transformations of a distance preserve the decision. With
$\varphi(d) = (d - 1)^2$, the distances $d_1 = 0.2 < d_2 = 0.8$ become
$\varphi(d_1) = 0.64 > \varphi(d_2) = 0.04$, and the classification flips.

## kNN in code

The past paper asked for the algorithm as two functions. Four steps for one point: distance
to every training point, sort, take the $k$ smallest, majority vote.

```python
import numpy as np
from collections import Counter

def knn_predict_one(x, X_train, y_train, k):
    """Classify one point x by majority vote of its k nearest neighbours."""
    d = np.sqrt(np.sum((np.asarray(X_train) - np.asarray(x)) ** 2, axis=1))
    nearest = np.argsort(d)[:k]
    votes = Counter(np.asarray(y_train)[nearest])
    return votes.most_common(1)[0][0]

def knn_predict(X_test, X_train, y_train, k):
    """Classify every row of X_test."""
    return np.array([knn_predict_one(x, X_train, y_train, k) for x in X_test])
```

:::tip
Say these with the code: squaring is monotonic, so you may rank on squared distance and skip
the square root. Choose $k$ odd for two classes to avoid ties. Standardise the features
first, or the one with the largest units dominates the distance.
:::

## Practise

[](deck:ch6-distance), then [](problems:fisher-and-boundaries#fb-p3) and
[](problems:fisher-and-boundaries#fb-p4). Question 4 of [the past paper](paper:final/past-paper)
is the MED derivation with a sketch.
