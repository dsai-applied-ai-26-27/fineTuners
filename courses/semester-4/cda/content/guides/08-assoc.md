---
title: 'Frequent itemsets & association rules'
number: 8
topics: [assoc]
summary: 'Lecture 8. Carries marks on both past papers.'
---

The market-basket model: a large set of **items**, a large set of **baskets**, each basket a small subset of items. You want rules of the form "people who bought \{x, y, z} tend to buy \{v, w}".

### The three definitions

```text
support(I) = number of baskets containing every item in I
```

- **I**: an itemset
- **s**: the support threshold; itemsets with support ≥ s are **frequent**

```text
conf(I → j) = support(I ∪ {j}) / support(I)
```

- **I → j**: a rule: a basket containing all of I is likely to contain j
- **conf**: the conditional probability of j given I, in \[0, 1]

```text
Interest(I → j) = conf(I → j) − Pr[j]
```

- **Pr\[j]**: the fraction of *all* baskets containing j
- ****: Interesting rules have high positive *or negative* interest — the lecture's rule of thumb is above 0.5

:::note
**Why Interest exists.** "X → milk" has high confidence for almost any X, because milk is bought constantly. Subtracting the base rate Pr\[j] strips that out. A rule with 0.8 confidence on an item that appears in 75% of baskets is telling you nothing.
:::

### Monotonicity — the idea the whole topic rests on

:::paper
If an itemset I appears at least s times, then **so does every subset of I**.

Contrapositive, which is the usable form: if item i is not frequent, then **no** itemset containing i can be frequent — so it never needs counting.
:::

### A-Priori

One pass per itemset size. Pass 1 counts individual items and keeps those with count ≥ s. Pass 2 counts **only** pairs whose both members were frequent in pass 1. In general, Cₖ (candidates of size k) is built from Lₖ₋₁, then a pass counts them to give Lₖ.

:::note
**Cost model.** The lecture measures cost in **passes over the data**, because the data is disk-resident and disk I/O dominates. The binding constraint within a pass is **main memory for counters**. Every algorithm in this topic is a trick to reduce one of those two.
:::

The naïve alternative fails on arithmetic: 10⁵ items gives 10⁵(10⁵−1)/2 ≈ 5 × 10⁹ pairs, at 4 bytes each that is **20 GB** of counters. Counting pairs is the bottleneck, because frequent pairs are common while frequent triples are rare.

| Storing pair counts | Cost | Better when |
|---|---|---|
| Triangular matrix (count \{i,j} only for i\<j) | 4 bytes per *possible* pair | most possible pairs actually occur |
| Table of triples \[i, j, c] | 12 bytes per *occurring* pair | fewer than 1/3 of possible pairs occur |

### PCY — and what it fixes

Park–Chen–Yu starts from an observation about waste: **in pass 1 of A-Priori most of main memory is idle**, because you only store one counter per item — yet pass 2 is the step that runs out of memory.

:::paper
**PCY pass 1:** count each item *and*, for each pair of items in each basket, hash the pair to a bucket and add 1 to that bucket's count. Keep only bucket counts, never the pairs.

**Between passes:** replace each bucket count with one bit — 1 if the count ≥ s, else 0. This is the bitmap.

**PCY pass 2:** count the pair \{i, j} only if **(1)** i and j are both frequent items **and (2)** \{i, j} hashes to a bucket whose bit is 1.

**Why it is valid:** a bucket with total count below s cannot contain any frequent pair, so every pair hashing there is safely eliminated. The converse fails — a bucket can be frequent without containing any frequent pair — so PCY produces **false positives but never false negatives**.
:::

:::warning
**One detail that is often asked:** on PCY's second pass you **cannot** use the triangular-matrix method — the surviving candidate pairs are scattered, not a dense triangle — so you need a table of (item, item, count) triples. Because triples cost 12 bytes against the matrix's 4, the hash table must eliminate roughly **2/3** of candidate pairs just for PCY to break even with A-Priori.
:::

| Refinement | Idea | Passes |
|---|---|---|
| **Multistage** | after PCY pass 1, **rehash** with a second, independent hash function only those pairs that already qualify. Fewer pairs contribute, so fewer false positives. Must check **both** bitmaps on the final pass. | 3 |
| **Multihash** | several independent hash tables in a *single* first pass. Risk: halving the buckets doubles the average count, so buckets may all reach s. | 2 |
| **SON** | process the file in memory-sized chunks, find frequent itemsets in each; anything frequent in *any* chunk is a candidate; second pass counts candidates over everything. An itemset cannot be frequent overall unless it is frequent in at least one chunk. Distributes trivially. | 2 |
| **Random sampling** | run A-Priori in memory on a sample with a proportionally lowered threshold. Fast, but misses itemsets frequent overall yet not in the sample. | 1–2 |
