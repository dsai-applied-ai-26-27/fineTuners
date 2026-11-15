---
title: 'The six data-mining tasks'
number: 1
topics: [tasks]
summary: 'Lecture 1.'
---

:::warning
**Negatively marked: −0.2 per wrong answer.** On a four-option MCQ, guessing has negative expected value. If you cannot eliminate to one, skip.
:::

:::paper
Three questions, in order:

**1.** Is there a label / known target? No → clustering, association rules, anomaly detection, or summarization.

**2.** If yes: is the target a **category** (classification) or a **number** (regression)?

**3.** If no label: groups of records (clustering) · co-occurring items (association rules) · rare deviant records (anomaly detection) · a compressed human-readable description (summarization)?
:::

| Task | Giveaway wording | Course algorithm |
|---|---|---|
| **Classification** | "spam or not spam", "malignant or benign", "approved or rejected", "will the customer churn" | decision tree, Naïve Bayes, Random Forest |
| **Regression** | "estimate the price", "predict the exact number of", "how many minutes/days" | regression models |
| **Clustering** | "discover similar profiles", "segment", "group users by similar habits" | k-means, BFR, CURE |
| **Association rules** | "often bought together", "customers who buy X often buy Y" | A-Priori, PCY |
| **Anomaly detection** | "unusual transactions", "sudden unusually high", "detecting bots / fake reviews" | IQR, z-score |
| **Summarization** | "executive dashboard", "concise trends", "annual recap" | aggregation, data cubes |

:::note
**The two pairs that catch people.** **Clustering vs classification**: if the groups are given in advance it's classification; if you have to interpret the groups afterwards it's clustering. **Association rules vs recommendation**: "bread and milk are often bought together" is a statement about *items* with no user — association rules. "Viewers who watched this also watched…" the lectures place under recommender systems.
:::

### Process models

**KDD**: Selection → Pre-processing → Transformation → Data mining → Interpretation & evaluation. **CRISP-DM**: Business understanding → Data understanding → Data preparation → Modeling → Evaluation → Deployment.

KDD is a research-oriented view emphasising selection, transformation and pattern extraction, treating data mining as one phase of a broader discovery pipeline. CRISP-DM is a project-oriented framework for real deployments — it starts from business understanding and ends at deployment, which is why industry uses it: it connects analytics to operations.

**The 5 V's:** Volume (algorithms must be near-linear — O(n), O(n log n)) · Velocity (minimise latency; batch vs stream) · Variety (integrating modalities; explainability) · Veracity (trustworthiness; garbage in, garbage out) · Value (not all data is valuable).
