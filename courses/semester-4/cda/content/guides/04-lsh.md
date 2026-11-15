---
title: 'Similarity, MinHash, LSH'
number: 4
topics: [lsh]
summary: 'Lectures 4–5. On neither past paper: read last.'
---

:::warning
This appears on **neither** final paper; it was most likely examined at the midterm. Kept here for completeness and because Jaccard turns up inside the recommender question. Read it once; don't drill it.
:::

```text
J(A, B) = |A ∩ B| / |A ∪ B|
```

- **A, B**: sets — of shingles, of liked items
- ****: Range \[0, 1]. Ignores 0–0 matches, so it suits **sparse, asymmetric** binary data. SMC counts 0–0 matches and suits symmetric binary data.

**Three steps to find similar documents:** **Shingling** (turn documents into sets — D1 = "abcab" gives 2-shingles \{ab, bc, ca}) → **MinHashing** (turn big sets into short signatures preserving Jaccard) → **LSH** (hash signatures so only similar pairs are likely to collide). Output: **candidate pairs**.

```text
Pr[ hₘᵢₙ(A) = hₘᵢₙ(B) ] = J(A, B)
```

```text
P(candidate) = 1 − (1 − s^r)^b, n = b·r, threshold t ≈ (1/b)^(1/r)
```

- **s**: true Jaccard similarity
- **b**: number of bands
- **r**: rows per band
- **n**: signature length

Two items are a candidate pair if their signatures match in **all r rows of at least one band**. More bands → higher **recall**; more rows per band → higher **precision**.

Why any of it: with N users there are **N(N−1)/2** pairs — 10,000 users is 49,995,000 comparisons, a million users is 5 × 10¹¹.

| Metric | Use for |
|---|---|
| **Jaccard** | sets of shingles — plagiarism detection |
| **Euclidean** | continuous numeric features — square footage, bedrooms, lot size |
| **Cosine** | directional alignment of dense embeddings; rating patterns where volume shouldn't matter |
| **Mahalanobis** | correlated features, outlier detection, BFR's acceptance test |

**Metric properties:** positive definiteness d(p,q) ≥ 0 and = 0 only if p = q; symmetry d(p,q) = d(q,p); triangle inequality d(p,r) ≤ d(p,q) + d(q,r).
