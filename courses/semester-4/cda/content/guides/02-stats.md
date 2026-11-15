---
title: 'Data types → which correlation, and χ²'
number: 2
topics: [stats]
summary: 'Lecture 2. Carries marks on both past papers.'
---

Both papers open Q2 the same way: here is a variable, **what data type is it**, and **which method measures the relationship**. The data type decides everything, so answer in that order and the marks follow.

:::paper
**Both variables numeric (continuous), relationship roughly linear** → **Pearson correlation**.

**At least ordinal, or monotone but not linear, or outlier-heavy** → **Spearman** (Pearson on the ranks).

**Both categorical / nominal** → **χ² test of independence**.

Then justify by the assumption: Pearson needs two continuous numeric variables and only detects *linear* association; Spearman needs rankable values and detects *monotone* association; χ² is non-parametric and works on counts in a contingency table.
:::

| Type | What it is | Example |
|---|---|---|
| **Nominal** | categories with no order | blood type, has-heart-disease (yes/no) |
| **Ordinal** | ordered categories, gaps not meaningful | exercise level low/medium/high, disease stage I/II/III |
| **Interval** | numeric, no true zero | temperature in °C |
| **Ratio** | numeric with a true zero | minutes of exercise per week, income |

:::note
**The exercise-and-heart-disease question.** Heart disease is **nominal** (yes/no) — you cannot rank it, so Spearman is out; it has no numeric scale, so Pearson is out. If exercise is recorded as categories too, it's **χ²**. If exercise is given as a *number* (minutes/week) and disease is still binary, χ² still works after binning, but the cleaner answers are point-biserial correlation or logistic regression — say that in one line and you've shown you understand the principle rather than the recipe.
:::

### χ² — every element defined

```text
χ² = Σᵢ Σⱼ (Oᵢⱼ − Eᵢⱼ)² / Eᵢⱼ
```

- **Oᵢⱼ**: the **observed** count in row i, column j of the contingency table
- **Eᵢⱼ**: the count **expected if the two variables were independent**
- **i, j**: range over the r categories of variable 1 and the c categories of variable 2

```text
Eᵢⱼ = (row totalᵢ × column totalⱼ) / n
```

- **n**: the grand total number of observations

```text
df = (r − 1)(c − 1)
```

- ****: For a 2×2 table df = 1, and the critical value at α = 0.05 is **3.841**

The larger χ², the more likely the variables are related. The cells contributing most are those where observed differs most from expected. **And association is not causation** — the lecture's own example is that the number of hospitals and the number of car thefts in a city are correlated.

The lecture's worked table (n = 1500, expected counts in brackets):

|   | Play chess | Not play chess | Row total |
|---|---|---|---|
| Like science fiction | 250 (90) | 200 (360) | 450 |
| Not like science fiction | 50 (210) | 1000 (840) | 1050 |
| **Column total** | **300** | **1200** | **1500** |

```text
χ² = 160²/90 + 160²/210 + 160²/360 + 160²/840 = 284.44 + 121.90 + 71.11 + 30.48 = 507.93
```

### Pearson

```text
r_(A,B) = Σᵢ (aᵢ − Ā)(bᵢ − B̄) / [ (n − 1) σ_A σ_B ]
```

- **n**: number of tuples
- **aᵢ, bᵢ**: the i-th values of A and B
- **Ā, B̄**: their means
- **σ\_A, σ\_B**: their standard deviations

r > 0 positively correlated; r = 0 no *linear* relationship; r \< 0 negatively correlated. Equivalently: standardise both variables and take the dot product.

:::warning
**When correlation is the wrong tool.** Non-linear relationships — Pearson on a U-shaped relationship returns about 0 even though the variables are perfectly dependent. Also: a single outlier can create or destroy a correlation, so look at the scatter plot first.
:::
