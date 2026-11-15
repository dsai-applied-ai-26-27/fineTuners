---
title: 'Cleaning, covariance vs correlation, redundancy'
number: 3
topics: [clean]
summary: 'Lecture 2.'
---

### Covariance vs correlation — the 26.8 Q3

```text
Cov(A,B) = E[(A − Ā)(B − B̄)] = E[A·B] − Ā·B̄
```

```text
r_(A,B) = Cov(A,B) / (σ_A σ_B)
```

:::paper
**Covariance** measures only the **direction** of a linear relationship and is **scale-dependent** — change the units and the number changes, so its magnitude means nothing on its own.

**Correlation** is **standardised covariance**: it measures both **strength and direction**, is scale-independent, and always lies in **\[−1, 1]**.

Cov > 0: both tend to be above their means together. Cov \< 0: one above tends to go with the other below. **Cov = 0 does not imply independence** — only under extra assumptions such as multivariate normality.
:::

### Redundant data

The lecture frames redundancy as a **data-integration** problem — it appears when you merge multiple databases. Three forms:

- **Object identification** — the same attribute or object under different names in different databases.
- **Derivable data** — one attribute can be derived from others, e.g. annual revenue when you already store the monthly figures.
- **Redundancy in rows** — duplicate records, usually created by a join on a non-unique key.

**Detection:** redundant attributes can be detected by **correlation analysis** (numeric) and **χ²** (nominal), plus covariance analysis; duplicate rows by `df.duplicated()`. **Treatment:** drop one of a correlated pair, drop duplicates, drop identifiers, or use **PCA / attribute subset selection** when there are many correlated features. Fix it at integration time where you can — careful integration "reduces redundancies and inconsistencies and improves mining speed and quality".

:::note
**Why it matters, in the exam's own terms.** If one concept appears twice as two near-identical columns, a **distance-based** method counts it twice and it dominates the clustering. And duplicates that straddle a train/test split put the same record on both sides — which is Q8's territory.
:::

### Outliers and noise

```text
IQR = Q3 − Q1 fences: [ Q1 − 1.5·IQR , Q3 + 1.5·IQR ]
```

- **Q1, Q3**: 25th and 75th percentiles

**Noise** is random error or variance in a measured variable — faulty instruments, data-entry and transmission problems, technology limits, inconsistent naming. Handled by: moving/rolling window (mean, median); **binning** (sort into bins, then smooth by bin means, medians or boundaries); regression; clustering; combined computer and human inspection.

:::warning
The IQR rule is purely statistical — it cannot tell a data-entry error from a genuine extreme value. **Not every flagged outlier should be removed**, and in anomaly-detection problems the outliers are the thing you're looking for.
:::

### Data reduction

| Strategy | Methods |
|---|---|
| **Dimensionality reduction** | wavelet transforms, **PCA**, feature subset selection / creation |
| **Numerosity reduction** | regression and log-linear models, histograms, clustering, sampling, data cube aggregation |
| **Data compression** | string, audio/video; dimensionality and numerosity reduction |

**PCA** finds a projection capturing the largest variance; numeric data only. Steps: normalise the input; compute k orthonormal principal components; each input is a linear combination of them; components are sorted by decreasing significance; drop the weak ones.
