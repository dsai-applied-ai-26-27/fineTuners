---
title: 'Lᵖ spaces'
number: 3
topics: [measure, functional]
summary: From the integrable functions to the spaces Lᵖ, the p-norm and the essential supremum, conjugate exponents, Hölder's and Minkowski's inequalities, why functions equal almost everywhere are identified to make the p-norm a norm, which functions belong to which Lᵖ, the inclusion on a finite measure space, and convergence in Lᵖ, including why mean squared error is the L² distance.
takeaways:
  - '$\|f\|_p = \left(\int \lvert f \rvert^p \, d\mu\right)^{1/p}$, and $L^p(\mu)$ is the set of measurable $f$ with $\|f\|_p < \infty$. $\|f\|_\infty$ is the essential supremum, the smallest bound on $\lvert f \rvert$ outside a null set.'
  - 'Hölder: $\|fg\|_1 \le \|f\|_p \|g\|_q$ for conjugate exponents $\frac1p + \frac1q = 1$ (including $1$ and $\infty$). With $p = q = 2$ it is Cauchy-Schwarz.'
  - 'Minkowski, $\|f + g\|_p \le \|f\|_p + \|g\|_p$ for $p \ge 1$, is the triangle inequality. For $0 < p < 1$ it fails, so the course uses $p \ge 1$.'
  - '$\|\cdot\|_p$ is only a seminorm: $\|f\|_p = 0$ means $f = 0$ almost everywhere. Identifying functions equal almost everywhere makes $L^p$ a normed space.'
  - 'Membership depends on $p$: $x^{-a}$ is in $L^p$ near $0$ iff $ap < 1$ and near $\infty$ iff $ap > 1$, so neither $L^p \subset L^q$ nor $L^q \subset L^p$ holds in general. If $\mu(X) < \infty$ and $p < q$, then $L^q \subset L^p$ and $\|f\|_p \le \mu(X)^{(q-p)/(pq)}\|f\|_q$.'
  - '$f_n \to f$ in $L^p$ means $\|f_n - f\|_p \to 0$. Mean squared error is $\|f_n - f\|_2^2$ for the measure that gives each data point mass $1/N$, so "MSE tends to 0" is convergence in $L^2$.'
sources:
  - lectures/Lecture 3 part 1.pdf
---

## Where this fits

Lecture 2 ended with the integral and the functions that have a finite one. This lecture
gives that set a name, $L^1$, and generalises it to $L^p$ for every exponent. The spaces
$L^p$ are where measure theory meets functional analysis: they are the first examples of
normed spaces of functions, and $L^2$ is where "mean squared error" lives. The notes are by
Ilhama Beganović, from Axler chapters 3 and 7 (numbers 3.x and 7.x) and Folland chapter 6
(numbers 6.x). This is part 1; the lecture continues.

Functions take values in $\mathbf{F}$, which is $\mathbf{R}$ or $\mathbf{C}$; read it as
$\mathbf{R}$ throughout.

## From L¹ to Lᵖ

A measurable $f$ has a finite integral exactly when $\int \lvert f \rvert \, d\mu < \infty$
(lecture 2).

:::definition L¹-norm and L¹(μ) (3.40)
For $\mathcal{S}$-measurable $f : X \to [-\infty, \infty]$, $\|f\|_1 = \int \lvert f \rvert \, d\mu$,
and

$$L^1(\mu) = \{ f : X \to \mathbf{R} \text{ measurable} : \|f\|_1 < \infty \}.$$
:::

:::definition Norm
A function $\|\cdot\| : V \to [0, \infty)$ on a vector space $V$ over $\mathbf{F}$ with, for all
$f, g \in V$ and $\lambda \in \mathbf{F}$:

- **definiteness:** $\|f\| = 0$ if and only if $f = 0$;
- **homogeneity:** $\|\lambda f\| = \lvert \lambda \rvert \|f\|$;
- **triangle inequality:** $\|f + g\| \le \|f\| + \|g\|$.

Examples: $\lvert x \rvert$ on $\mathbf{R}$, the Euclidean length on $\mathbf{R}^n$.
:::

:::theorem Properties of the L¹-norm (3.43)
For $f, g \in L^1(\mu)$: $\|f\|_1 \ge 0$; $\|f\|_1 = 0$ iff $f(x) = 0$ for **almost every** $x$;
$\|cf\|_1 = \lvert c \rvert \|f\|_1$; $\|f + g\|_1 \le \|f\|_1 + \|g\|_1$.
:::

Homogeneity and the triangle inequality hold, but **definiteness fails**: for a non-empty
$E$ with $\mu(E) = 0$, $\|\chi_E\|_1 = 0$ although $\chi_E \ne 0$. Axler: "$\|\cdot\|_1$ might
not be a genuine norm". The repair comes below.

:::proof Why $\|f\|_1 = 0$ exactly when $f = 0$ almost everywhere
Not in the notes. If $f = 0$ outside a null set, $\int \lvert f \rvert = 0$, because a null
set cannot change an integral ([lecture 2](lecture:02-the-lebesgue-integral#almost-every)).
Conversely, if $\int \lvert f \rvert = 0$, let $E_n = \{\lvert f \rvert > \frac1n\}$. Then
$\frac1n\chi_{E_n} \le \lvert f \rvert$, so $\frac1n\mu(E_n) \le 0$ and $\mu(E_n) = 0$. The
set where $f \ne 0$ is $\bigcup_n E_n$, a countable union of null sets, hence null (2.58).
:::

Nothing forces the exponent 1. Errors are often measured by their **square**, as in the mean
squared error of a regression model, which is the exponent 2.

:::definition p-norm and Lᵖ(μ) (7.1, 7.3)
For $0 < p < \infty$ and measurable $f : X \to \mathbf{F}$,

$$\|f\|_p = \left( \int \lvert f \rvert^p \, d\mu \right)^{1/p}, \qquad L^p(\mu) = \{ f \text{ measurable} : \|f\|_p < \infty \}.$$
:::

- The outer power $1/p$ is there so that $\|\lambda f\|_p = \lvert \lambda \rvert \|f\|_p$.
- $\|f\|_p$ does not change if $f$ changes on a set of measure 0.
- $L^p(\mu)$ is a vector space (Axler 7.5): scalar multiples by homogeneity, sums by
  integrating $\lvert f + g \rvert^p \le 2^p(\lvert f \rvert^p + \lvert g \rvert^p)$.
- For $0 < p < 1$ the triangle inequality **fails** (Folland, p. 182), so from here on
  $p \ge 1$.

:::example The triangle inequality fails for p = 1/2
Not in the notes. With Lebesgue measure, $f = \chi_{[0,1]}$ and $g = \chi_{[1,2]}$ have
$\|f\|_{1/2} = \|g\|_{1/2} = 1$, but $\|f + g\|_{1/2} = \left(\int_0^2 1 \, dx\right)^2 = 4 > 2$.
:::

## The essential supremum and L^∞

:::definition Essential supremum (L^∞)
$$\|f\|_\infty = \inf\{ a \ge 0 : \mu(\{x : \lvert f(x) \rvert > a\}) = 0 \},$$
with $\inf\varnothing = \infty$. The infimum is attained, so $\lvert f \rvert \le \|f\|_\infty$
almost everywhere. $L^\infty(\mu)$ is the set of measurable $f$ with $\|f\|_\infty < \infty$.
:::

$\|f\|_\infty$ is the smallest value $\sup\lvert f \rvert$ can be made by changing $f$ on a set
of measure 0.

:::proof Why the infimum is attained
Not in the notes. Let $s = \|f\|_\infty < \infty$. For each $n$ some $a < s + \frac1n$ has
$\mu(\{\lvert f \rvert > a\}) = 0$, so $\{\lvert f \rvert > s + \frac1n\}$ is null. Then
$\{\lvert f \rvert > s\} = \bigcup_n \{\lvert f \rvert > s + \frac1n\}$ is a countable union
of null sets, hence null.
:::

:::example A spike that does not count
On $[0,1]$ with Lebesgue measure, let $f(x) = x$ for $x \ne \frac12$ and $f(\frac12) = 100$.
Then $\sup\lvert f \rvert = 100$, but $\{x : \lvert f(x) \rvert > t\}$ has measure 0 for every
$t \ge 1$, so $\|f\|_\infty = 1$.
:::

## Hölder's and Minkowski's inequalities

:::definition Conjugate exponents
For $1 < p < \infty$, $q = \dfrac{p}{p - 1}$ is the number with $\dfrac1p + \dfrac1q = 1$.
$1$ and $\infty$ are conjugate to each other ($1^{-1} + \infty^{-1} = 1$). Examples: 2 is
conjugate to 2, and 4 to $\frac43$.
:::

:::theorem Hölder's inequality (6.2)
For $1 < p < \infty$ with conjugate $q$, and measurable $f, g$:

$$\|fg\|_1 \le \|f\|_p\,\|g\|_q .$$

So $f \in L^p$, $g \in L^q$ imply $fg \in L^1$. Equality holds iff
$\alpha\lvert f \rvert^p = \beta\lvert g \rvert^q$ a.e. for constants $\alpha, \beta$ with
$\alpha\beta \ne 0$.
:::

:::proof
The notes refer to Folland (p. 182); this is that proof, not written out in the notes.
It rests on **Young's inequality**: for $a, b \ge 0$,
$ab \le \frac{a^p}{p} + \frac{b^q}{q}$. (For $a, b > 0$, concavity of $\log$ with weights
$\frac1p + \frac1q = 1$ gives
$\log\big(\frac1p a^p + \frac1q b^q\big) \ge \frac1p \log a^p + \frac1q \log b^q = \log(ab)$.)

If $\|f\|_p = 0$ or $\|g\|_q = 0$, then $fg = 0$ almost everywhere and both sides are $0$.
If either norm is $\infty$, there is nothing to prove. Otherwise put
$F = \lvert f \rvert/\|f\|_p$ and $G = \lvert g \rvert/\|g\|_q$, so that
$\int F^p = \int G^q = 1$. Young's inequality at each point, integrated, gives

$$\int FG \, d\mu \le \frac1p \int F^p \, d\mu + \frac1q \int G^q \, d\mu = \frac1p + \frac1q = 1,$$

which is $\int \lvert fg \rvert \, d\mu \le \|f\|_p\,\|g\|_q$.
:::

The endpoint $p = 1$, $q = \infty$ also holds:
$\|fg\|_1 \le \|f\|_1\|g\|_\infty$, by integrating $\lvert fg \rvert \le \|g\|_\infty\lvert f \rvert$,
true a.e.

:::theorem Minkowski's inequality (6.5)
For $1 \le p < \infty$ and $f, g \in L^p$: $\|f + g\|_p \le \|f\|_p + \|g\|_p$.
:::

:::proof
Obvious for $p = 1$ or if $f + g = 0$ a.e. Otherwise

$$\lvert f + g \rvert^p \le (\lvert f \rvert + \lvert g \rvert)\,\lvert f + g \rvert^{p-1}.$$

Apply Hölder to each term, using $(p - 1)q = p$:

$$\int \lvert f + g \rvert^p \le \|f\|_p \big\| \lvert f + g \rvert^{p-1} \big\|_q + \|g\|_p \big\| \lvert f + g \rvert^{p-1} \big\|_q = (\|f\|_p + \|g\|_p)\left( \int \lvert f + g \rvert^p \right)^{1/q}.$$

Divide by $\left(\int \lvert f + g \rvert^p\right)^{1/q}$, positive (since $f + g$ is not $0$
almost everywhere) and finite (since $L^p$ is a vector space): since $1 - \frac1q = \frac1p$,
$\|f + g\|_p \le \|f\|_p + \|g\|_p$.
:::

For $p = \infty$ the triangle inequality also holds:
$\lvert f + g \rvert \le \lvert f \rvert + \lvert g \rvert \le \|f\|_\infty + \|g\|_\infty$ a.e.
(Folland 6.8b).

:::tip The one move in the proof
Split one factor off $\lvert f + g \rvert^p$, bound it by $\lvert f \rvert + \lvert g \rvert$,
and let Hölder take care of the remaining power $p - 1$, whose conjugate norm is again a
power of $\int \lvert f + g \rvert^p$. Then divide.
:::

## Making the p-norm a norm

By Minkowski and homogeneity, $\|\cdot\|_p$ is a **seminorm** on $L^p$: everything except
definiteness, since $\|f\|_p = 0$ only says $f = 0$ almost everywhere.

**The fix:** regard two functions as the same element of $L^p$ when they are **equal almost
everywhere**. Formally an element of $L^p$ is the class of all functions agreeing a.e. with
a given one, and addition and scalar multiplication work through representatives (Axler 7.15
to 7.17). In practice we keep writing functions and remember that a.e.-equal ones are
equal. This is harmless because $\|f\|_p$ ignores null sets. **With this convention
$\|\cdot\|_p$ is a norm and $L^p$ is a normed vector space for $1 \le p < \infty$.**

## Which functions belong to Lᵖ?

:::example Membership depends on p
With Lebesgue measure $\lambda$ on $(0, \infty)$:

**(a)** $f(x) = x^{-1/3}\chi_{(0,1)}(x)$ is in $L^1$ but not in $L^3$.

Truncate: $f_n = x^{-1/3}\chi_{[1/n, 1)}$ is measurable, $0 \le f_n \le f_{n+1}$, and
$f_n \to f$ pointwise, so by monotone convergence (3.11) and 3.34 on the bounded piece,

$$\|f\|_1 = \lim_{n\to\infty} \int_{1/n}^{1} x^{-1/3} dx = \lim_{n\to\infty} \frac32\left(1 - n^{-2/3}\right) = \frac32 < \infty .$$

But $\lvert f \rvert^3 = x^{-1}\chi_{(0,1)}$, and the same truncation gives
$\lim_n \int_{1/n}^1 x^{-1} dx = \lim_n \ln n = \infty$, so $f \notin L^3$.

**(b)** $g(x) = x^{-1}\chi_{(1,\infty)}(x)$ is in $L^2$ but not in $L^1$.

Truncate at infinity with $\chi_{(1,n)}\lvert g \rvert^p$:
$\int \lvert g \rvert^2 = \lim_n \left(1 - \frac1n\right) = 1$, so $\|g\|_2 = 1$; and
$\int \lvert g \rvert = \lim_n \ln n = \infty$.
:::

**Neither** $L^p \subset L^q$ nor $L^q \subset L^p$ holds in general: (a) is in $L^1$ and not
$L^3$; (b) is in $L^2$ and not $L^1$. The general rule, from the supplementary exercise:

:::theorem Powers of x
For $a > 0$ and $1 \le p < \infty$ (in fact any $p > 0$):

$$x^{-a}\chi_{(0,1)} \in L^p \iff ap < 1, \qquad x^{-a}\chi_{(1,\infty)} \in L^p \iff ap > 1 .$$
:::

:::proof
Put $s = ap$, so $\lvert f \rvert^p = x^{-s}$. Near 0, truncating to $[1/n, 1)$:
$\int_{1/n}^1 x^{-s} dx$ tends to $\frac{1}{1-s}$ if $s < 1$ and to $\infty$ if $s \ge 1$ ($\ln n$
for $s = 1$). Near $\infty$, truncating to $(1, n)$: $\int_1^n x^{-s} dx$ tends to
$\frac{1}{s-1}$ if $s > 1$ and to $\infty$ if $s \le 1$.
:::

:::recall Remember which way the inequality goes
**Near 0 large powers hurt** (a spike gets worse when raised to a high power): need
$ap < 1$. **Near infinity large powers help** (a small tail gets smaller): need $ap > 1$. At
$ap = 1$ both fail, because $\int dx/x$ diverges at both ends.
:::

On a space of **finite measure** a larger exponent is the stronger condition:

:::theorem Lq ⊂ Lp on a finite measure space (7.10)
If $\mu(X) < \infty$ and $0 < p < q < \infty$, then for all $f \in L^q(\mu)$

$$\|f\|_p \le \mu(X)^{(q-p)/(pq)}\,\|f\|_q, \qquad \text{so } L^q(\mu) \subset L^p(\mu).$$
:::

:::proof
Let $r = q/p > 1$; its conjugate is $r' = \frac{q}{q - p}$. Hölder with exponents $r, r'$,
applied to $\lvert f \rvert^p$ and the constant function 1:

$$\int \lvert f \rvert^p \, d\mu \le \left( \int \lvert f \rvert^{pr} d\mu \right)^{1/r}\left( \int 1 \, d\mu \right)^{1/r'} = \mu(X)^{(q-p)/q}\left( \int \lvert f \rvert^q d\mu \right)^{p/q}.$$

Raise both sides to the power $1/p$.
:::

On $[0,1]$, $\mu([0,1]) = 1$, so $\|f\|_p \le \|f\|_q$ and $L^q([0,1]) \subset L^p([0,1])$ for
$p < q$. ($L^p(E)$ means $L^p$ of Lebesgue measure restricted to the measurable subsets of
$E$.)

:::pitfall The inclusion needs finite measure
On $(0,\infty)$ the function $g$ of (b) is in $L^2$ but not $L^1$: the tail is the problem,
and only a finite total measure removes it.
:::

## Convergence in Lᵖ

:::definition Convergence in Lᵖ
For $1 \le p < \infty$ and $f_n, f \in L^p$: $f_n \to f$ in $L^p$ if
$\lim_{n\to\infty} \|f_n - f\|_p = 0$. For $p = 1$ this is
$\int \lvert f_n - f \rvert \, d\mu \to 0$.
:::

### Mean squared error is an L² distance

For a target $f$, models $f_n$ and data points $x_1, \dots, x_N$,

$$\mathrm{MSE}_n = \frac1N\sum_{i=1}^{N} \big(f_n(x_i) - f(x_i)\big)^2 .$$

Let $\mu$ give each data point mass $1/N$: $\mu(A) = \frac1N\#\{i : x_i \in A\}$. Then
$\int h \, d\mu = \frac1N\sum_i h(x_i)$ for every $h$, so

$$\mathrm{MSE}_n = \int \lvert f_n - f \rvert^2 \, d\mu = \|f_n - f\|_2^2 .$$

If the inputs fill an interval $[a,b]$ instead, the sum becomes
$\frac{1}{b-a}\int_a^b (f_n - f)^2 dx$, again $\|f_n - f\|_2^2$ for Lebesgue measure normalised
by $b - a$. **One formula, $\int \lvert f_n - f \rvert^2 d\mu$, covers both; only the measure
changes.** Since $\|f_n - f\|_2^2 \to 0$ iff $\|f_n - f\|_2 \to 0$, "the MSE tends to 0" is
exactly convergence in $L^2$, also called **convergence in mean square**.

:::example Products converge in L¹
If $f_n \to f$ in $L^2$ and $g \in L^2$, then $f_n g \to fg$ in $L^1$.

$(2, 2)$ are conjugate, so by Hölder $f_n g, fg \in L^1$, and

$$\int \lvert f_n g - fg \rvert \, d\mu = \int \lvert g \rvert\,\lvert f_n - f \rvert \, d\mu \le \|g\|_2\,\|f_n - f\|_2 \to 0 .$$
:::

:::example Convergence in one Lᵖ but not another
Not in the notes. With Lebesgue measure, $f_n = \sqrt{n}\,\chi_{(0,1/n)}$ has
$\|f_n\|_1 = \frac{1}{\sqrt n} \to 0$, so $f_n \to 0$ in $L^1$; but $\|f_n\|_2 = 1$ for all
$n$, so $f_n \not\to 0$ in $L^2$. And $x^n$ on $[0,1]$ has $\|x^n\|_2 = \frac{1}{\sqrt{2n+1}} \to 0$
but $\|x^n\|_\infty = 1$: convergence in $L^2$, not in $L^\infty$.
:::

:::theorem Truncation converges in L¹ (supplementary exercise)
For real $f \in L^1(\lambda)$ on $\mathbf{R}$: $\lim_{n\to\infty} \|f - f\chi_{[-n,n]}\|_1 = 0$.
:::

:::proof
$h_n = \lvert f - f\chi_{[-n,n]} \rvert = \lvert f \rvert\chi_{\mathbf{R}\setminus[-n,n]}$ is
measurable with $0 \le h_n \le \lvert f \rvert$, and $h_n(x) = 0$ once $n \ge \lvert x \rvert$, so
$h_n \to 0$ pointwise. Dominated convergence with $g = \lvert f \rvert$ gives
$\int h_n \to 0$.
:::

## Looking ahead

- **Functional analysis:** $L^p$ is complete, a **Banach space** (Folland 6.6), and $L^2$
  carries the inner product $\langle f, g \rangle = \int f\bar g \, d\mu$, making it a
  **Hilbert space**. Hölder with $p = q = 2$ is the **Cauchy-Schwarz inequality**
  $\int \lvert fg \rvert \le \|f\|_2\|g\|_2$.
- **Advanced probability:** a probability space is a measure space with $\mu(X) = 1$. A
  random variable is in $L^p$ iff $\mathbb{E}\lvert X \rvert^p < \infty$, with
  $\|X\|_p = (\mathbb{E}\lvert X \rvert^p)^{1/p}$. By 7.10, $L^2 \subset L^1$: a **finite second
  moment implies a finite first absolute moment**.

## What an exam wants

:::paper Decide whether f ∈ Lᵖ
1. Write $\int \lvert f \rvert^p \, d\mu$; it is defined because the integrand is $\ge 0$.
2. Truncate where $f$ is unbounded or the domain is infinite; check the monotone convergence
   hypotheses (measurable, increasing, converging).
3. Compute the truncated integral as a Riemann integral (3.34) and take the limit.
4. Conclude $f \in L^p$ (finite) or $f \notin L^p$ (infinite). The power rule $ap < 1$ /
   $ap > 1$ is a check, not a substitute for the computation.
:::

:::paper Use Hölder
Name the conjugate pair, check it ($\frac1p + \frac1q = 1$), say which function plays $f$
and which $g$ (often one is the constant 1, as in 7.10), and write the inequality with both
norms.
:::

## Where next

- Drill: [](deck:lp-spaces), and the proofs: [](deck:lp-spaces-proofs).
- Which space contains which, and which convergence implies which:
  [](guide:counterexamples).
- Practice: [](problems:lp-spaces-practice).
- Definitions: [the glossary](glossary); formulas: [the sheet](formulas).
- Before this: [](lecture:02-the-lebesgue-integral).
