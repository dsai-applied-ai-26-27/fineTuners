---
title: 'Model evaluation'
number: 10
topics: [eval]
summary: 'Lecture 10.'
---

### Splitting

**Holdout**: train / validation / test, usually 60/20/20 — but with a million rows a 98/1/1 split is fine, because 1% is still 10,000 rows. The lecture's analogy: study → practice test → refocus → final exam. The model learns on train, you tune against validation, and you touch test **once**.

**k-fold cross-validation**: split into k folds, hold one out, train on k−1, repeat for every fold, average. Use it when data is limited.

**Temporal division** where the data is a time series: train on the earliest period, validate on the next, test on the most recent. Validation and test must come from the same distribution — something that reflects future data.

### Classification metrics

```text
Accuracy = (TP + TN) / (TP + TN + FP + FN)
```

```text
Precision = TP / (TP + FP) — of the positive predictions, how many were right
```

```text
Recall = Sensitivity = TP / (TP + FN) — of the actual positives, how many were found
```

```text
Specificity = TN / (TN + FP)
```

```text
F1 = 2·P·R / (P + R) — the harmonic mean, which punishes extreme values
```

Higher sensitivity ⇒ lower type II error rate. Higher specificity ⇒ lower type I error rate. In medical diagnosis, sensitivity is the ability to correctly identify those *with* the disease, specificity those *without*.

:::note
**Curves.** **Precision–recall** curve: precision against recall as the threshold varies — appropriate for **imbalanced** data. **ROC**: true positive rate against false positive rate — better for **balanced** data. **AUC summarises skill across all thresholds; F1 summarises it at one threshold.**
:::

### Regression metrics

| Metric | Formula | Outlier-sensitive | Use when |
|---|---|---|---|
| **MAE** | (1/n) Σ \|y − ŷ\| | Low | all errors count equally; same units as the target |
| **MSE** | (1/n) Σ (y − ŷ)² | High | large errors are particularly costly; squared units are hard to read |
| **RMSE** | √MSE | High | MSE's penalty but interpretable units — the general default |
| **R²** | 1 − SSᵣₑₛ/SSₜₒₜ | Indirectly | comparing explanatory power; unitless |

Clustering has no ground truth, so its metrics measure self-similarity instead: **silhouette** s = (b − a)/max(a, b) with a the mean distance to points in the same cluster and b to the nearest other cluster; **inertia** (compactness only); Davies-Bouldin (lower better); Calinski-Harabasz (higher better).

:::warning
**One metric does NOT fit all.** That is the lecture's closing line, and it is the sentence that earns the mark on any "which metric" question — followed immediately by *which* one and *why*, in terms of what the errors cost.
:::
