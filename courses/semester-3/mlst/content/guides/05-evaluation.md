---
title: 'Evaluation, metrics and resampling'
number: 5
topics: [evaluation]
summary: 'Confusion matrix, precision and recall, thresholds, ROC and PR curves, cross-validation, the bootstrap, and regression metrics.'
---

Part 5 of 12 of the course notes, from the 2025-26 exam kit (lectures 1 to 7, labs 1 to 10). Each section pairs an exam-ready code pattern with the theory that justifies it. Arguments are tagged **ritual** (always the same), **structural** (forced by the data or the task) or **dial** (a real hyperparameter); the full list is in [](guide:parameter-reference).

## Confusion matrix from cross-validated predictions

**cross_val_predict returns predictions** (one clean out-of-fold prediction per training instance), whereas **cross_val_score returns scores** (one number per fold). You need predictions to build a confusion matrix. Layout: rows = actual, columns = predicted, so [[TN, FP], [FN, TP]].

```python
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix, precision_score, recall_score

y_train_pred = cross_val_predict(sgd_clf, X_train, y_train, cv=3)

print(confusion_matrix(y_train, y_train_pred))
print(precision_score(y_train, y_train_pred))
print(recall_score(y_train, y_train_pred))
```

| Argument | Kind | What it does |
|---|---|---|
| `cv=3` | dial | Number of folds. Each prediction comes from a model that never saw that instance. |

## Precision, recall and F1

**Precision = TP / (TP + FP)** — trustworthiness of a positive prediction. **Recall (sensitivity, TPR) = TP / (TP + FN)** — coverage of the actual positives. **F1 = harmonic mean**, which punishes imbalance between them far harder than an average would. Which one you optimise is a business decision: a spam filter wants precision, a cancer screen wants recall.

## Moving the decision threshold

Classifiers output **hard labels, probabilities, or scores**. Continuous outputs are preferred — more informative and easier to optimise. A threshold c turns them into labels: typically **0.5 for probabilities, 0 for scores**. `np.argmax(boolean_array)` returns the first True, which is the idiom for 'the first threshold that reaches this precision'.

```python
y_scores = sgd_clf.decision_function([some_digit])
y_some_digit_pred = (y_scores > 8000)

# get out-of-fold scores, not labels, to sweep the threshold
y_scores = cross_val_predict(sgd_clf, X_train, y_train_5, cv=3,
                             method="decision_function")

from sklearn.metrics import precision_recall_curve
precisions, recalls, thresholds = precision_recall_curve(y_train_5, y_scores)

# smallest threshold that reaches 90% precision
threshold_90 = thresholds[np.argmax(precisions >= 0.90)]
y_train_pred_90 = (y_scores >= threshold_90)
```

| Argument | Kind | What it does |
|---|---|---|
| `method="decision_function"` | structural | Ask for raw scores instead of hard labels. Use method="predict_proba" for models that give probabilities (RandomForest, Naive Bayes) and take column [:, 1]. |

## ROC and precision-recall curves

**ROC** plots TPR against FPR across all thresholds; **AUC** = 1.0 perfect, 0.5 random. A model 'dominates' another if its curve is above everywhere. **PR curves are superior for heavily imbalanced data** precisely because they ignore true negatives: an ROC curve can look excellent purely because a huge majority of negatives are handled correctly, while the PR curve exposes that performance on the rare positive class is poor.

```python
from sklearn.metrics import roc_curve, roc_auc_score
fpr, tpr, thresholds = roc_curve(y_train_5, y_scores)
roc_auc_score(y_train_5, y_scores)
```

## The accuracy paradox and imbalanced costs

**Accuracy paradox**: with a rare positive class, always predicting negative scores brilliantly on accuracy and is useless. **Imbalanced costs**: a false negative (sick patient sent home) is usually far more damaging than a false positive. Hence confusion matrix, precision/recall, F1 and PR curves instead of accuracy.

## k-fold cross-validation

**k-fold CV**: split into k folds, train on k−1, test on the held-out one, rotate, average. **Stratified** CV keeps each fold's class distribution equal to the whole dataset's — critical for imbalanced classes. A single train/test split has **high pessimistic bias** if the training part is too small, and **high variance** if the test part is too small; resampling fixes both.

```python
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.base import clone

cross_val_score(sgd_clf, X_train, y_train_5, cv=3, scoring="accuracy")

skfolds = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
for train_index, test_index in skfolds.split(X_train, y_train_5):
    clone_clf = clone(sgd_clf)          # fresh, UNTRAINED copy each fold
    clone_clf.fit(X_train[train_index], y_train_5[train_index])
    y_pred = clone_clf.predict(X_train[test_index])
```

| Argument | Kind | What it does |
|---|---|---|
| `n_splits=3` | dial | Number of folds. k=10 is the common default — it balances bias and variance of the estimate. |
| `shuffle=True` | dial | Shuffle before splitting, in case the data arrived sorted by class or time. |
| `clone(model)` | structural | Returns an untrained copy with the same hyperparameters, so fold 2 has not already seen fold 1's data. |

## Bootstrap, subsampling and leave-one-object-out

**Bootstrap**: sample n instances *with replacement*. On average about **63.2%** of the unique instances appear; the remaining ~36.8% are **out-of-bag** and can serve as a test set for free. **Subsampling / Monte-Carlo CV**: randomly re-split train/test 50–200 times and average the errors. **Leave-One-Object-Out CV**: when several observations come from the same object (multiple scans of one patient, several clips of one speaker), the i.i.d. assumption fails — splitting them across train and test lets the model memorise object-specific quirks and leak. LOOO-CV keeps every observation of an object entirely on one side of the split.

## Bias, variance, inner and outer loss

**Bias / underfitting**: model too simple, misses the real pattern, high error on *both* training and test. **Variance / overfitting**: model too flexible, fits noise, very low training error but high test error. Test error against complexity is a **U**; the sweet spot balances the two. Also note **inner vs outer loss**: the inner loss is what training optimises (log loss, MSE) because it is differentiable; the outer loss is what you actually care about (cost-sensitive accuracy, F1) and may not be differentiable at all.

## Regression metrics

**MSE/RMSE**: common, heavily influenced by outliers (it is the L2 loss again). **MAE**: more robust and more intuitive — average error in the target's own units. **Spearman's ρ**: correlation of ranks, so it measures any monotonic relationship, is invariant to monotone transformations and extremely robust to extreme values. Naming convention: `*_error` means lower is better, `*_score` means higher is better, and both take `(y_true, y_pred)` in that order.

```python
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred)
accuracy = accuracy_score(y_test, y_pred)
```

## Remember it

The same sections as scenes along a route: [](palace:05-bathroom). The code is drilled in [the decks](cards).
