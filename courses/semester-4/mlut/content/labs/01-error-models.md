---
title: "Lab 1: Covariance, distributions, and error models"
number: 1
topics: [lecture-1]
summary: Use covariance matrices, Gaussian marginals and conditionals, Bayes' theorem, and rolling statistics to diagnose measurement noise.
takeaways:
  - A covariance matrix makes pairwise linear relationships visible numerically and geometrically.
  - Marginal and conditional Gaussian distributions have different means and variances.
  - A mixture density is valid when its component weights are non-negative and sum to one.
  - Rolling spread versus rolling mean distinguishes constant-scale from signal-dependent noise.
sources:
  - 2025-26/lectures/lecture1/lab1/MLUT_Laboratory_Exercise1.pdf
  - 2025-26/lectures/lecture1/lab1/MLUT_lab1.ipynb
  - 2025-26/lectures/lecture1/lab1/dataset_covariance.csv
  - 2025-26/lectures/lecture1/lab1/sensor_data.csv
---

## Goal

This lab applies Lecture 1 to two supplied datasets. The source notebook is a 2025-26 worked solution; the code below keeps its main reasoning while omitting plotting boilerplate that does not change the analysis.

## Task 1: covariance in three dimensions

Load `dataset_covariance.csv`, inspect the three variables, and visualise each pair. Then compute the covariance matrix:

```python
import pandas as pd

df = pd.read_csv("dataset_covariance.csv")
covariance_matrix = df[["x", "y", "z"]].cov()
print(covariance_matrix)
```

Interpret the signs rather than comparing raw magnitudes alone: the worked solution finds that $x$ and $y$ move together, while $x$ and $z$ and $y$ and $z$ move in opposite directions.

For the advanced question $w=x+y-z$, use covariance linearity:

```python
cov_xx = covariance_matrix.loc["x", "x"]
cov_yx = covariance_matrix.loc["y", "x"]
cov_zx = covariance_matrix.loc["z", "x"]
cov_wx = cov_xx + cov_yx - cov_zx
print(cov_wx)
```

Since $\operatorname{Cov}(y,x)>0$ and $\operatorname{Cov}(z,x)<0$, the subtraction of the negative term contributes positively. The conclusion is about covariance with $x$, not a claim that every possible notion of dependence increases.

## Task 2: bivariate Gaussian distributions

Use the supplied mean vector and covariance matrix from the notebook to derive the marginals and conditionals. For a bivariate Gaussian,

$$
p(x)=\mathcal{N}(\mu_x,\sigma_x^2),\qquad
p(y)=\mathcal{N}(\mu_y,\sigma_y^2).
$$

The conditional formulas used in the solution are

$$
p(x\mid y)=\mathcal{N}\left(\mu_x+\frac{\operatorname{Cov}(x,y)}{\sigma_y^2}(y-\mu_y),
\sigma_x^2-\frac{\operatorname{Cov}(x,y)^2}{\sigma_y^2}\right),
$$

with the symmetric expression for $p(y\mid x)$. The conditional variance is smaller than the marginal variance when the covariance is non-zero: observing one variable reduces uncertainty about the other.

## Task 3: a Gaussian mixture and Bayes' theorem

Construct

$$
p(x)=\pi_1\mathcal{N}(x\mid\mu_1,\sigma_1^2)+
\pi_2\mathcal{N}(x\mid\mu_2,\sigma_2^2)
$$

with the notebook's example $\mu_1=-1$, $\sigma_1=0.8$, $\pi_1=0.4$, $\mu_2=2$, $\sigma_2=1.2$, and $\pi_2=0.6$. Check $\pi_1+\pi_2=1$ before plotting, then integrate the mixture over the real line. The total area should be one because each component is a normalised density and the weights sum to one.

For the notebook's Bayes example, the prior is $p(\text{Study})=0.01$, with $p(\text{Pass}\mid\text{Study})=0.95$ and $p(\text{Pass}\mid\text{No Study})=0.05$. Compute the evidence first, then the posterior. The worked result is $p(\text{Study}\mid\text{Pass})\approx0.161$.

## Task 4: identify sensor error models

Load `sensor_data.csv`. It contains temperature, pressure, and vibration readings over 500 time steps while a latent machine load changes. Start with scatter plots, then calculate rolling statistics with a window of 20:

```python
df2 = pd.read_csv("sensor_data.csv")
window_size = 20
for sensor in ["temperature", "pressure", "vibration"]:
    rolling_mean = df2[sensor].rolling(window=window_size).mean()
    rolling_std = df2[sensor].rolling(window=window_size).std()
    # Plot rolling_std against rolling_mean for diagnosis.
```

The solution's diagnosis is:

- **Temperature:** additive; the spread is approximately constant.
- **Pressure:** multiplicative; the spread grows with the signal and the rolling standard deviation trends upward with the rolling mean.
- **Vibration:** mainly additive with occasional extreme outliers.

For pressure, apply a log transform and repeat the rolling diagnostic. If the rising spread becomes approximately flat, that supports the multiplicative interpretation because multiplication becomes addition on the log scale.

## What to hand in

- [ ] Pairwise visualisations and the covariance matrix for `dataset_covariance.csv`.
- [ ] The calculation and interpretation of $\operatorname{Cov}(w,x)$ for $w=x+y-z$.
- [ ] Marginal and conditional Gaussian plots, with the conditional variance explained.
- [ ] A Gaussian-mixture plot and an area check equal to one.
- [ ] A Bayes calculation with the evidence and posterior shown.
- [ ] Sensor diagnoses justified by scatter plots and rolling statistics, including the pressure log-transform check.