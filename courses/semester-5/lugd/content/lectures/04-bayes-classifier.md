---
title: 'The Bayes classifier: the "perfect" classifier and its error'
number: 4
topics: [classification]
summary: Why every method's test error has a floor, the Bayes classifier that picks the most probable class, the Bayes error rate as the classification version of the irreducible error, why the classifier is theory rather than a method you can use, and KNN as a real classifier measured against it.
takeaways:
  - 'Expected test MSE splits into variance, squared bias and the irreducible error $\mathrm{Var}(\varepsilon)$. A method that knew the true $f$ would still have test MSE $\mathrm{Var}(\varepsilon)$: that is the floor.'
  - The Bayes classifier assigns $x_0$ to the class $j$ with the largest $\Pr(Y = j \mid X = x_0)$. With two classes it predicts class 1 when that probability is above $0.5$; the points where it is exactly $0.5$ form the Bayes decision boundary.
  - The Bayes error rate is $1 - E\big[\max_j \Pr(Y = j \mid X)\big]$, at a single point $\min(p, 1-p)$ for two classes. It is the lowest test error any classifier can reach, and it is above zero whenever the classes overlap.
  - The Bayes classifier needs the true conditional probabilities, which only the population has. It cannot be built from real data; it is the benchmark every sample-based method approximates. It is not Naive Bayes.
  - KNN estimates the class probabilities from the $K$ nearest training points. $K = 1$ overfits (training error 0, high test error), a very large $K$ underfits, and the test error is U-shaped in $1/K$, never below the Bayes error.
sources:
  - lectures/Bayes Classifier.pdf
---

## Where this fits

A short sheet from the lecturer on assessing model accuracy, following *An Introduction to
Statistical Learning* (ISL), Chapter 2, §2.2.2 and §2.2.3. It follows
[](lecture:03-collaborative-filtering-ii), which treats CF as k-nearest-neighbour
classification and quotes Cover and Hart's bound against the Bayes error: a recommender
that predicts "relevant or not" is a classifier, and its error has the same floor. The practice test for the first
test asks about it ([](problems:practice-test-1)).

## Starting point: test error has a floor

Even a method with no bias and no variance makes errors on new data. The expected test MSE
at a point $x_0$ splits into three non-negative parts (ISL §2.2.2):

$$E\big(y_0 - \hat f(x_0)\big)^2 = \mathrm{Var}\big(\hat f(x_0)\big) + \big[\mathrm{Bias}\big(\hat f(x_0)\big)\big]^2 + \mathrm{Var}(\varepsilon)$$

- **Variance:** how much the estimate changes when it is trained on a different training
  set. More flexible methods have higher variance.
- **Bias:** the error from approximating a complicated reality with a simpler model. More
  flexible methods have lower bias.
- **$\mathrm{Var}(\varepsilon)$, the irreducible error:** noise in $y$ that is not a
  function of $x$, so no estimate of $f$ can predict it.

A method that recovered the true $f$ exactly would have zero bias and zero variance, and
its test MSE would still be $\mathrm{Var}(\varepsilon)$. In the sheet's simulated example
the squared bias falls and the variance rises as flexibility grows, and their sum plus the
irreducible error never drops below a dashed line at $\mathrm{Var}(\varepsilon)$.

The Bayes classifier is the classification version of this ideal method, and the Bayes
error rate is the classification version of the floor.

## From MSE to error rate

In classification $y$ is a class label, so instead of squaring errors we count mistakes.
The **training error rate** is the fraction of training observations the classifier gets
wrong:

$$\frac{1}{n} \sum_{i=1}^{n} I(y_i \neq \hat y_i)$$

$I(\cdot)$ is an indicator: 1 for a mistake, 0 for a correct prediction. The **test error
rate** is the same average, $\mathrm{Ave}\big(I(y_0 \neq \hat y_0)\big)$, over test
observations not used in training.

As in regression, the test error is the one that matters: KNN with $K = 1$ has zero
training error and can still do badly on new data.

## The Bayes classifier: pick the most probable class

The Bayes classifier assigns each observation to the class that is most probable given its
predictor values:

$$\hat y_0 = \arg\max_j \Pr(Y = j \mid X = x_0)$$

- **Two classes:** predict class 1 if $\Pr(Y = 1 \mid X = x_0) > 0.5$, and class 2
  otherwise.
- **Bayes decision boundary:** the points where that probability is exactly $0.5$.
  Observations on one side are assigned to one class, those on the other side to the other.
- **What it needs:** the true conditional distribution of $Y$ given $X$. It is not learned
  from a training set; it is defined by the population itself. That is why the sheet's
  figures use simulated data, where the true probabilities are known.

## Why it is "perfect", and why the quotes

On average no classifier has a lower test error rate than the Bayes classifier. At any
point $x_0$ any other rule sometimes picks a less probable class, which can only add
mistakes. In bias-variance terms it uses the true probabilities, so nothing is estimated:

- **no bias**, because no simplified model form stands between it and reality;
- **no variance**, because it does not depend on a particular training set.

Only the irreducible part of the error is left. The quotes are there for two reasons:

1. **It is not error-free.** Where the classes overlap, the most probable class is still
   wrong some of the time.
2. **It cannot be built for real data.** We never know $\Pr(Y = j \mid X)$, so the Bayes
   classifier is an "unattainable gold standard" that other methods are compared against.

:::note A caution on the theory
For 0-1 error (right or wrong) the test error does not split exactly into variance plus
squared bias plus $\mathrm{Var}(\varepsilon)$. The same logic still holds: every
classifier's error has a part no method can remove, plus extra error from fitting too
rigidly (bias) or too flexibly (variance).
:::

## Theory, not a method you can choose

"Best classifier" does not mean "the classifier you should use". The Bayes classifier is
defined on the **population**, while every classifier we can build works from a **sample**.

| What we know | Population (theory) | Sample (practice) |
|---|---|---|
| Data | The true $\Pr(Y = j \mid X)$ | $n$ labelled observations |
| Classifier | Bayes classifier | KNN, logistic regression, Naive Bayes, … |
| Probabilities | Exact | Estimated, with bias and variance |
| Test error | Bayes error rate (the floor) | Bayes error rate + estimation error |
| Can we compute it? | Only for simulated data | Yes |

So "use the Bayes classifier" is never an option on real data. Every practical classifier
approximates it from a sample, and the Bayes error tells us how close any of them could
get, not which one to pick.

:::warning Two common confusions
- **It is not Naive Bayes.** Naive Bayes is a sample-based method: it estimates the
  probabilities from training data while assuming the features are independent. When that
  assumption is wrong it can be far from the Bayes classifier.
- **Knowing the best rule exists does not tell you which method wins.** With a small
  sample a simple method can approximate the Bayes classifier better than a very flexible
  one, because the flexible one has high variance.
:::

## The Bayes error rate

The Bayes error rate is the test error of the Bayes classifier, the lowest error any
classifier can achieve. At a single point it is $1 - \max_j \Pr(Y = j \mid X = x_0)$;
averaged over all $X$ it is

$$\text{Bayes error rate} = 1 - E\Big[\max_j \Pr(Y = j \mid X)\Big].$$

With two classes and $p = \Pr(Y = 1 \mid X = x_0)$, the error at that point is
$\min(p, 1 - p)$.

**Worked example.** 100 test observations share the same $x_0$, and $p = 0.7$: 70 belong to
class 1 and 30 to class 2. Every rule must treat them alike, because they look identical.

| Rule at $x_0$ | Mistakes out of 100 | Error rate |
|---|---|---|
| Always predict class 1 (Bayes) | 30 | 0.30 |
| Always predict class 2 | 70 | 0.70 |
| Predict class 1 at random with probability 0.7 | 42 | 0.42 |

The random rule is wrong on class-1 points with probability $0.3$ and on class-2 points with
probability $0.7$: $70 \cdot 0.3 + 30 \cdot 0.7 = 21 + 21 = 42$. The Bayes rule is best, yet
its 30 mistakes cannot be removed: those observations look exactly like the 70 others.

**Why it is above zero.** The classes overlap in the population, so
$\max_j \Pr(Y = j \mid X = x_0) < 1$ for some $x_0$. In the sheet's two-class simulation the
Bayes error rate is $0.136$: even the perfect classifier misclassifies about 14% of test
observations. With one feature and two overlapping class densities, the Bayes error is the
area under the lower curve on each side of the boundary ($0.18$ in the sheet's example). It
is zero only when the classes never overlap.

## Regression and classification: the same floor

| | Regression | Classification |
|---|---|---|
| Accuracy measure | Test MSE | Test error rate |
| Ideal method | The true $f$ | The Bayes classifier |
| Irreducible error | $\mathrm{Var}(\varepsilon)$ | Bayes error rate |
| Where it comes from | Noise in $Y$ that $X$ does not explain | Overlap between classes at the same $X$ |
| Extra error of a real method | $\mathrm{Bias}^2$ + variance | Error from estimating $\Pr(Y = j \mid X)$ badly |

Any real classifier's test error is the Bayes error plus some extra error. The
bias-variance trade-off is about making that extra part as small as possible.

## Real classifiers against the benchmark: KNN

KNN copies the Bayes rule but uses estimated probabilities instead of true ones. It takes
the $K$ training points nearest to $x_0$ (the set $N_0$) and estimates each class
probability as their share of that class:

$$\widehat{\Pr}(Y = j \mid X = x_0) = \frac{1}{K} \sum_{i \in N_0} I(y_i = j)$$

It then picks the class with the highest estimate. How good those estimates are depends on
$K$. On the sheet's simulated data, where the Bayes error is $0.136$:

| $K$ | Flexibility | Bias | Variance | Training error | Test error | Above Bayes |
|---|---|---|---|---|---|---|
| 1 | Very high | Low | Very high | 0.000 | 0.203 | +0.067 |
| 30 | Moderate | Low | Low | 0.145 | 0.154 | +0.018 |
| 100 | Low | High | Low | 0.355 | 0.345 | +0.209 |

- **$K = 1$** draws a wiggly boundary that follows the noise. Training error 0, test error
  high: overfitting.
- **$K = 100$** draws a nearly straight boundary that cannot follow the true one:
  underfitting.
- **$K = 30$** gives a boundary close to the Bayes boundary and comes within $0.018$ of the
  best possible error.

Plotted against $1/K$ (larger means more flexible), the test error traces a U-shape with
its minimum near $K = 30$ and never drops below the Bayes error. The training error keeps
falling and can go below the Bayes error. That is a warning sign, not an achievement: no
classifier can beat the Bayes error on new data.

:::tip The 1-NN limit
With unlimited training data the nearest neighbour of $x_0$ is effectively at $x_0$, so
1-NN predicts a random label drawn with the true probabilities there. With two classes its
error at $x_0$ is then $p(1-p) + (1-p)p = 2p(1-p)$, against the Bayes error $\min(p, 1-p)$.
For $p = 0.65$: Bayes $0.35$, 1-NN $0.455$. This is the same reasoning as the random rule
in the worked example (there $2 \cdot 0.7 \cdot 0.3 = 0.42$), and it is the classic result
that 1-NN's asymptotic error is at most twice the Bayes error.
:::

## Check your understanding

The sheet ends with five questions.

1. **In a two-class problem, $\Pr(Y = 1 \mid X = x_0) = 0.55$. What does the Bayes
   classifier predict at $x_0$, and what is its error there?** Class 1, because
   $0.55 > 0.5$. Its error at $x_0$ is $\min(0.55, 0.45) = 0.45$: close to a coin toss,
   because the classes overlap almost evenly there.
2. **If the Bayes classifier is the best possible, why do we need KNN or any other
   method?** Because it needs the true $\Pr(Y = j \mid X)$, which we never have for real
   data. Every real method estimates those probabilities from a sample.
3. **A classifier has a training error of $0.05$ on data whose Bayes error is $0.13$. What
   does this tell you?** That it is overfitting: no classifier can have a test error below
   $0.13$, so a training error far below it means the model has learned the noise of the
   training set. Its test error will be at least $0.13$, and probably well above.
4. **When is the Bayes error rate exactly zero?** Only when the classes never overlap:
   for every $x$ one class has probability 1, so the most probable class is always right.
5. **Which part of the test error can more training data reduce, and which part can it
   not?** More data reduces the estimation error, mainly the variance, by bringing the
   estimated probabilities closer to the true ones. It cannot reduce the Bayes error, which
   comes from the overlap of the classes in the population.

## Where next

- Drill: [](deck:bayes-classifier).
- Practice for the first test: [](problems:practice-test-1).
- Terms and formulas: [the glossary](glossary), [the formula sheet](formulas).
