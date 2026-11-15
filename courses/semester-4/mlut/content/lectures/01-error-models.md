---
title: Basic probability and error models
number: 1
topics: [lecture-1]
summary: Probability, Gaussian statistics, covariance, and measurement models for reasoning about hidden structure in unlabeled data.
takeaways:
  - Unsupervised learning uses observed data to infer structure or latent variables without target labels.
  - Marginal, conditional, and posterior probabilities answer different questions and are connected by Bayes' theorem.
  - Covariance describes linear co-movement; independence is stronger than zero covariance.
  - Additive noise has roughly constant spread, while multiplicative noise grows with the signal.
  - The conditional model $x = z + \varepsilon$ with $\varepsilon \sim \mathcal{N}(0,\sigma^2)$ gives $p(x \mid z) = \mathcal{N}(z,\sigma^2)$.
sources:
  - 2025-26/lectures/lecture1/MLUT_Lecture1_ErrorModels.pdf
  - 2025-26/lectures/lecture1/Lecture 1.pdf
---

## Where this fits

The lecture starts with the problem that unsupervised learning has inputs but no target labels. A useful model assumes that observed data $x$ was generated from hidden, or latent, variables $z$. Probability and statistics provide the language for describing that relationship; error models describe how measurements depart from the underlying signal. The source material is from the 2025-26 offering.

## Unsupervised learning

Supervised learning receives input-output pairs $(x,y)$ and learns a mapping from input to a known target. Unsupervised learning receives observations without labels and looks for structure already present in them. Typical goals include clustering, dimensionality reduction, anomaly detection, generative modelling, and association rules.

Let a **dataset** be the collection of observations, a **sample** be one observation, and a **feature** be one measurable property of a sample. A latent variable is not observed directly but is inferred from observed variables. For example, customer segments can be latent structure inferred from purchase history and browsing behaviour.

:::recall What is missing in an unsupervised training set?
There is no pre-defined target label. The model must discover structure, such as clusters or a lower-dimensional representation, from the observed inputs.
:::

## Probability for observed and hidden variables

For two events or variables, the joint probability $p(A,B)$ describes their occurrence together. A marginal probability ignores the other variable. For continuous variables, marginalisation integrates it out:

$$
p(z) = \int p(z,y)\,dy.
$$

The conditional probability of $A$ given $B$ is

$$
p(A \mid B) = \frac{p(A,B)}{p(B)},
$$

when $p(B) > 0$. The same identity lets us infer an unobserved state from data. Bayes' theorem is

$$
p(z \mid x) = \frac{p(x \mid z)p(z)}{p(x)}.
$$

Here $p(z \mid x)$ is the posterior, $p(x \mid z)$ the likelihood, $p(z)$ the prior, and $p(x)$ the evidence. The denominator normalises the posterior across possible values of $z$.

### A base-rate example

Suppose a condition has prior probability $0.01$, a positive result has probability $0.95$ when the condition is present, and a false-positive probability of $0.05$ otherwise. Then

$$
p(\text{positive}) = 0.95(0.01) + 0.05(0.99) = 0.059,
$$

and

$$
p(\text{condition}\mid\text{positive}) = \frac{0.95(0.01)}{0.059} \approx 0.161.
$$

The posterior is not $0.95$: the rare prior matters. This is the base-rate effect.

:::recall How do you test event independence?
Check whether $p(A \cap B) = p(A)p(B)$. Equivalently, when $p(B)>0$, check whether $p(A \mid B)=p(A)$.
:::

## Mean, variance, and covariance

For observations $x_1,\ldots,x_N$, the population mean and variance are

$$
\mu = \frac{1}{N}\sum_{i=1}^{N}x_i,\qquad
\sigma^2 = \frac{1}{N}\sum_{i=1}^{N}(x_i-\mu)^2.
$$

The standard deviation is $\sigma = \sqrt{\sigma^2}$. For a sample used to estimate a larger population, the lab notes use $N-1$ in the denominator for the unbiased variance estimate.

For paired observations $(x_i,y_i)$,

$$
\operatorname{Cov}(X,Y) = \frac{1}{N}\sum_{i=1}^{N}(x_i-\mu_x)(y_i-\mu_y).
$$

Positive covariance means the variables tend to increase together; negative covariance means one tends to decrease as the other increases. Approximately zero covariance means no linear relationship, not necessarily independence.

For a vector of variables, covariance is collected in a matrix. For $(x,y,z)$,

$$
\Sigma = \begin{bmatrix}
\operatorname{Var}(x) & \operatorname{Cov}(x,y) & \operatorname{Cov}(x,z)\\
\operatorname{Cov}(y,x) & \operatorname{Var}(y) & \operatorname{Cov}(y,z)\\
\operatorname{Cov}(z,x) & \operatorname{Cov}(z,y) & \operatorname{Var}(z)
\end{bmatrix}.
$$

If $w=x+y-z$, covariance linearity gives

$$
\operatorname{Cov}(w,x)=\operatorname{Var}(x)+\operatorname{Cov}(y,x)-\operatorname{Cov}(z,x).
$$

Thus $\operatorname{Cov}(y,x)>0$ and $\operatorname{Cov}(z,x)<0$ both add positive contributions to the relationship between $w$ and $x$.

:::pitfall Zero covariance is not the same as independence.
Independence implies zero covariance when the expectations exist, but zero covariance can coexist with a nonlinear relationship, such as $Y=X^2$ for a variable symmetric about zero.
:::

## Gaussian distributions and mixtures

The univariate Gaussian density is

$$
p(x;\mu,\sigma^2)=\frac{1}{\sqrt{2\pi\sigma^2}}
\exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right).
$$

The standard-deviation rule gives approximately 68%, 95%, and 99.7% of mass within one, two, and three standard deviations of the mean. The Central Limit Theorem explains why Gaussian noise is a useful approximation when many small independent error sources add together.

The multivariate normal density in $D$ dimensions is

$$
p(\mathbf{x})=\frac{1}{(2\pi)^{D/2}|\Sigma|^{1/2}}
\exp\left(-\frac{1}{2}(\mathbf{x}-\boldsymbol{\mu})^T\Sigma^{-1}(\mathbf{x}-\boldsymbol{\mu})\right).
$$

With spherical covariance $\Sigma=\sigma^2I$, contours are circles. With diagonal covariance, contours are axis-aligned ellipses. With full covariance, off-diagonal terms rotate the ellipses: positive correlation tilts the ridge from bottom-left to top-right, and negative correlation tilts it in the opposite direction.

A mixture of Gaussians combines component densities:

$$
p(x)=\sum_{k=1}^{K}\pi_k\mathcal{N}(x\mid\mu_k,\sigma_k^2),
\qquad \sum_{k=1}^{K}\pi_k=1,\quad \pi_k\geq0.
$$

The weights preserve total area one and the components can create multiple modes.

## Error models

An error model separates the underlying signal from measurement uncertainty. It supports reliability estimates, sensible combination of measurements, outlier detection, and likelihood-based inference.

In the additive model,

$$
y=x+\varepsilon,\qquad \varepsilon\sim\mathcal{N}(0,\sigma^2).
$$

The error spread is approximately constant as the signal changes. GPS and thermometer measurements are examples. In a multiplicative model,

$$
y=x\eta,\qquad \eta\sim\mathcal{N}(1,\sigma_\eta^2).
$$

The mean of $\eta$ is one so the signal is not rescaled on average. The error spread grows with $|x|$; this is appropriate for effects such as percentage sensor error or speckle. A log transform turns a positive multiplicative relationship into an additive one.

| Property | Additive | Multiplicative |
| --- | --- | --- |
| Model | $y=x+\varepsilon$ | $y=x\eta$ |
| Noise scale | Fixed $\sigma$ | Proportional to $|x|$ |
| Visual spread | Roughly constant | Widens as the signal grows |
| Signal-to-noise ratio | $x/\sigma$ changes with $x$ | Approximately constant $1/\sigma_\eta$ |

For the observation model $x=z+\varepsilon$ with Gaussian noise, fixing $z$ shifts the Gaussian but does not change its variance:

$$
p(x\mid z)=\mathcal{N}(x\mid z,\sigma^2).
$$

Rolling means and rolling standard deviations help choose a model from data. A roughly flat rolling standard deviation versus rolling mean suggests additive noise; an increasing trend suggests multiplicative noise.

:::paper Exam wording for the two error models
Additive noise has the form $y=x+\varepsilon$ and has variance independent of the signal magnitude. Multiplicative noise has the form $y=x\eta$ and has a spread that scales with the signal. Therefore constant spread suggests an additive model, while increasing spread suggests a multiplicative model.
:::

## Check your understanding

1. Explain why $p(z\mid x)$ is not the same quantity as $p(x\mid z)$.
2. Given $p(A)=0.4$, $p(B)=0.5$, and $p(A,B)=0.2$, calculate $p(A\mid B)$ and test independence.
3. For $w=x+y-z$, derive $\operatorname{Cov}(w,x)$ and interpret the signs when $x$ and $y$ are positively correlated but $x$ and $z$ are negatively correlated.
4. A sensor's rolling standard deviation increases with its rolling mean. Which error model is the first candidate, and what transformation could make it additive?

The executable applications of these ideas are in [Lab 1](lab:01-error-models), and the key definitions and derivations are in [the Lecture 1 deck](deck:lecture-1-error-models).