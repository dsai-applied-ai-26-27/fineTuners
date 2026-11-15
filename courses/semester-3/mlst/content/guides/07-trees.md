---
title: 'Decision trees (CART)'
number: 7
topics: [trees]
summary: 'How a tree is fitted by greedy search, the splitting criteria, and the two ways to stop it overfitting.'
---

Part 7 of 12 of the course notes, from the 2025-26 exam kit (lectures 1 to 7, labs 1 to 10). Each section pairs an exam-ready code pattern with the theory that justifies it. Arguments are tagged **ritual** (always the same), **structural** (forced by the data or the task) or **dial** (a real hyperparameter); the full list is in [](guide:parameter-reference).

## What a CART tree is

**CART** partitions the feature space into **rectangular regions** by recursive **binary splits**, and predicts a constant in each leaf. Root → internal nodes → terminal nodes. `predict_proba` returns the proportion of each class among the training instances in that leaf.

```python
from sklearn.tree import DecisionTreeClassifier, export_graphviz
tree_clf = DecisionTreeClassifier(max_depth=2, random_state=42)
tree_clf.fit(X, y)
tree_clf.predict_proba([[5, 1.5]])   # class fractions inside the leaf
```

## Fitting by recursive greedy search

**Fitting = recursive greedy search.** At each node the algorithm exhaustively searches all features and all split points and takes the one that minimises the empirical risk (impurity) of the resulting children. Greedy means locally optimal, not globally optimal — the tree it finds is usually not the best possible tree.

## Splitting criteria

**Regression:** minimise total squared error / variance in the children. **Classification:** minimise **Gini impurity** (equivalent to the Brier score) or **entropy** (equivalent to log loss). Gini is slightly faster and usually gives near-identical trees.

```python
DecisionTreeRegressor(max_depth=3, random_state=0)   # criterion: squared_error
DecisionTreeClassifier(criterion="gini")             # or "entropy"
```

## Stopping criteria (pre-pruning)

An unrestricted tree grows until every leaf contains a single observation — the archetype of overfitting. **Stopping criteria** (pre-pruning) limit depth, leaves, or samples per node.

```python
DecisionTreeClassifier(max_depth=3,
                       max_leaf_nodes=16,
                       min_samples_split=4,
                       min_samples_leaf=10,
                       random_state=42)
```

| Argument | Kind | What it does |
|---|---|---|
| `max_depth` | dial | Longest question chain. Lower = simpler = more bias, less variance. |
| `max_leaf_nodes` | dial | Cap on the number of terminal regions. |
| `min_samples_split` | dial | A node must hold at least this many samples to be allowed to split. |
| `min_samples_leaf` | dial | Every leaf must keep at least this many samples. Raising ANY `min_*` or lowering any `max_*` regularises the tree. |

## Cost-complexity pruning

**Post-pruning / cost-complexity pruning (CCP)**: grow a large tree, then remove the branches whose contribution does not justify their complexity, controlled by a regularisation parameter α. Trees are easy to interpret but **unstable** — a small change in the data can produce a very different tree, which is exactly the weakness ensembles fix.

```python
path = tree.cost_complexity_pruning_path(X_train, y_train)
clf = DecisionTreeClassifier(ccp_alpha=0.01, random_state=42)
```

| Argument | Kind | What it does |
|---|---|---|
| `ccp_alpha` | dial | Complexity penalty. α=0 means no pruning; raising it prunes more aggressively. |

## Remember it

The same sections as scenes along a route: [](palace:07-home-office). The code is drilled in [the decks](cards).
