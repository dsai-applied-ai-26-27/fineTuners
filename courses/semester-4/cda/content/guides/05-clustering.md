---
title: 'Clustering — k-means, BFR, CURE'
number: 5
topics: [clustering]
summary: 'Lecture 6. Carries marks on both past papers.'
---

Three algorithms in one family. **k-means** is the base; **BFR** extends it to data too big for memory; **CURE** extends it to clusters that aren't blobs. The exam asks you to place them against each other, so learn the *differences*, not three separate descriptions.

### k-means

Assumes a Euclidean space. Pick k; initialise k centroids; assign every point to the nearest centroid; recompute each centroid as the mean of its members; repeat until nothing moves.

```text
inertia = Σ_(i=1..k) Σ_(x ∈ Cᵢ) ‖x − μᵢ‖²
```

- **k**: number of clusters, chosen in advance
- **Cᵢ**: the set of points assigned to cluster i
- **μᵢ**: the centroid of cluster i — the mean of its points, an artificial point that need not be in the data
- **‖·‖**: Euclidean norm, so ‖x − μ‖² is the squared distance

The lecture's initialisation trick: pick one point at random, then each next point *as far as possible* from those already chosen.

### Centroid vs clustroid

In a **non-Euclidean** space there is no "average of two points", so you cannot form a centroid. Instead you use a **clustroid**: an *actual data point* chosen as closest to all the others — smallest maximum distance, smallest average distance, or smallest sum of squared distances. **Centroid = artificial and averaged; clustroid = real and chosen.** That one sentence is the whole mark.

### BFR

Bradley–Fayyad–Reina: k-means for disk-resident data. Points are read **one memory-load at a time** and then thrown away, replaced by summary statistics.

:::note
**The assumption that decides every BFR question:** clusters are normally distributed about a centroid, with standard deviations that may differ per dimension — so clusters look like **axis-aligned ellipses**. An ellipse at an angle is not allowed, and neither is anything non-convex.
:::

Three sets of points are tracked:

| Set | What is in it | Stored as |
|---|---|---|
| **DS** — Discard set | points close enough to a centroid to be summarised | statistics only; the points are discarded |
| **CS** — Compression set | groups of points close to each other but not to any centroid | summarised, but not assigned to a cluster |
| **RS** — Retained set | isolated points waiting to join a compression set | the actual points, in memory |

```text
summary = (N, SUM, SUMSQ) — 2d + 1 numbers for a cluster of any size
```

- **N**: number of points in the set
- **SUMᵢ**: sum of the i-th coordinate over those points
- **SUMSQᵢ**: sum of the *squares* of the i-th coordinate
- **d**: number of dimensions

```text
centroidᵢ = SUMᵢ / N varianceᵢ = SUMSQᵢ/N − (SUMᵢ/N)²
```

:::note
Why this representation and not a covariance matrix? Because dropping the axis-aligned assumption would mean storing a full **d × d** matrix per cluster instead of a d-vector — the lecture's words: *"which is too big!"* The cheap summary **is** the assumption.
:::

A new point joins a cluster if its **Mahalanobis distance** to that centroid is below a threshold:

```text
d(x, c) = √( Σ_(i=1..d) ( (xᵢ − cᵢ) / σᵢ )² )
```

- **xᵢ**: the point's i-th coordinate
- **cᵢ**: the centroid's i-th coordinate
- **σᵢ**: the cluster's standard deviation in dimension i, from the summary above
- **yᵢ**: shorthand for (xᵢ − cᵢ)/σᵢ — "how many σ away along dimension i"

For a normally distributed cluster in d dimensions, 1 standard deviation after transformation corresponds to a Mahalanobis distance of **√d**, and the lecture's acceptance rule is **d \< 2 standard deviations**.

Two CS sets are merged when the **variance of the combined set** is below a threshold — computable instantly from N, SUM and SUMSQ, since summaries simply add.

### CURE

Clustering Using REpresentatives. Still Euclidean, but a cluster is described by **several representative points** instead of one centroid — so a cluster can take any shape. **Two passes.**

:::paper
**CURE — 2 passes.**

**Pass 1** (on a sample that fits in memory):

1. Take a random sample of points that fits in main memory.
2. Cluster the sample **hierarchically** — repeatedly group nearest points/clusters.
3. For each cluster pick a sample of representative points, **as dispersed as possible**.
4. Move each representative **20% toward the centroid** of its cluster.

**Pass 2:** rescan the whole dataset; for each point p, find the **closest representative** and assign p to that representative's cluster.
:::

### The comparison they ask for

|   | k-means | BFR | CURE |
|---|---|---|---|
| **Cluster represented by** | one centroid | one centroid + per-dimension σ, as (N, SUM, SUMSQ) | a set of representative points |
| **Cluster shapes allowed** | convex blobs | axis-aligned ellipses (normal in each dim) | **any shape** |
| **Fits in memory?** | must | no — one memory-load at a time | no — samples, then rescans |
| **Passes** | iterates to convergence | one pass over the data | **2** |
| **Distance used to assign** | Euclidean | **Mahalanobis** vs a threshold | Euclidean to nearest representative |

:::warning
**The trap in "is BFR suitable for this data".** The answer is never about how many clusters there are or how much data there is. It is about **shape**: could an axis-aligned ellipse drawn round each group contain mostly its own points and little else? Crescents, rings, spirals, tilted cigars — no. Round, separated blobs — yes.
:::
