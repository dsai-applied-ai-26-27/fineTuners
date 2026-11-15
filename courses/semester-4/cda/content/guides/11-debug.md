---
title: 'Code debugging — the flaw catalogue'
number: 11
topics: [debug]
summary: 'Both papers, Q8. Carries marks on both past papers.'
---

:::warning
**Negative marking: −0.2 per incorrect error detection.** The exam-prep document is explicit: *"Students should not write random lists of possible errors. Incorrect additional claims will be penalized."* There are typically **one, two or three** intended issues. Write what you are sure of; if you want to mention a suspicion, make it conditional ("*if* the segments share a patient id, then…") rather than asserting it.
:::

The exam-prep document also names the four things to produce, in order: **(1)** identify the problem, **(2)** explain why it is a problem, **(3)** propose a corrected workflow, **(4)** write corrected code or pseudocode.

### The six flaws that actually recur

| Flaw | Why it is wrong | Fix |
|---|---|---|
| **1. Random split on grouped data** | Segments from the same patient / sensor / user land in both train and test, so the model learns the *source* rather than the class. Test score is optimistic. | `GroupShuffleSplit` / `StratifiedGroupKFold` on the patient or record id |
| **2. Accuracy on imbalanced data** | 95% of transactions valid ⇒ predicting "valid" always scores 95% and catches no fraud. Accuracy hides the failure that matters. | Confusion matrix + **recall** if false negatives are costly, **F1** if not; PR-AUC for imbalanced data |
| **3. Any `.fit()` before the split** | Scaling, imputation, **feature selection**, PCA, **SMOTE** — all leak the test set. Feature selection is the worst: the selector has seen the test *labels*. | Split first; fit on train only; put everything in a `Pipeline` so leakage is structurally impossible inside CV |
| **4. Global forward-fill** | `df.ffill()` across a frame holding many patients/sensors carries the last value of one into the first rows of the next. Backward fill is worse — it imports the future. | `df.sort_values([id, time])` then `df.groupby(id)[col].ffill()` |
| **5. Unscaled features into a distance method** | k-means, kNN, PCA are distance-based. Variables with large ranges dominate, and the clusters reflect scale rather than behaviour. | `StandardScaler`; log-transform skewed financial variables first |
| **6. Combining scores on different scales** | `0.5*rating + 0.5*similarity` with rating on 0–5 and similarity on 0–1: the rating dominates despite the equal weights, so α does not mean what it appears to. | Min-max both to \[0, 1] *before* combining |

:::note
**Two more that the 26.8 paper's own answer key names, which are worth knowing by name:** a **wrong join** (wrong key, or a join that silently duplicates/drops rows — always check the row count before and after), and **dropping a whole feature because it has missing values** when the missingness is itself the signal (the key's example: an `urgent` flag, where "rare but meaningful" is the point). Also: where the data is a time series, the split must be **temporal**, not grouped and not random.
:::

### The checklist to run over any snippet

| Ask | Red flag |
|---|---|
| Is the split first? | any `.fit()` or `fit_transform()` on the full X |
| Does the data have groups? | repeated ids + plain `train_test_split` |
| Is it a time series? | random split instead of chronological; any backward fill |
| Are the classes balanced? | accuracy quoted alone; no `stratify=y` |
| Are the features on one scale? | distance-based model with no scaler; scores of different ranges added |
| Was SMOTE or feature selection used? | fitted outside the pipeline / before the split |
| Are there duplicates? | no `drop_duplicates()` before splitting |
| Does the join behave? | row count changes unexpectedly after `merge`; duplicate or mistyped keys |
| Is an id column still in X? | `CUST_ID`, index, or a raw timestamp used as a feature |

```python
from sklearn.model_selection import StratifiedGroupKFold, GroupShuffleSplit
from sklearn.pipeline import Pipeline

gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
tr, te = next(gss.split(X, y, groups=df["patient_id"]))

pipe = Pipeline([("impute", SimpleImputer(strategy="median")),
                 ("scale",  StandardScaler()),
                 ("select", SelectKBest(f_classif, k=10)),
                 ("clf",    RandomForestClassifier(random_state=42))])
pipe.fit(X.iloc[tr], y.iloc[tr])          # every step fitted on TRAIN only
```
