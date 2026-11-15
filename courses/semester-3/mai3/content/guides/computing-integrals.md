---
title: Computing integrals and limits of integrals
topics: [measure]
summary: The recipes behind every computation of lectures 2 and 3, a toolbox of bounds for finding a dominating function, a table of integrals to compare with, and an index of every worked computation.
---

## Short answer

A Lebesgue integral is never computed from its definition. It is reduced to things you
already know how to do: finite sums (simple functions), Riemann integrals (3.34 on a
bounded piece) and limits (the convergence theorems). Each recipe below says what to
write and which hypotheses to show. $\lambda$ is Lebesgue measure.

## Recipe 1: a simple function

1. Rewrite it with **disjoint** sets: $3\chi_{[0,2)} + \chi_{[1,4)} = 3\chi_{[0,1)} + 4\chi_{[1,2)} + 1\chi_{[2,4)}$.
2. Apply 3.7: $\int \sum_k c_k \chi_{E_k} \, d\mu = \sum_k c_k \mu(E_k)$, here $3 + 4 + 2 = 9$.

Sets of measure $0$ drop out: $\int (\chi_{\mathbf{Q} \cap [0,5]} + 2\chi_{[0,1]}) \, d\lambda = 0 + 2 = 2$.

## Recipe 2: bounded, continuous, on a bounded interval

By 3.34, a **bounded** $f$ on $[a,b]$ whose discontinuities form a null set has
$\int_{[a,b]} f \, d\lambda = \int_a^b f(x) \, dx$. Continuous and bounded is the usual
case. Endpoints never matter: $[a,b]$, $[a,b)$ and $(a,b)$ differ by a null set.

## Recipe 3: an unbounded function or an unbounded domain

The integrand must be $\ge 0$ (for $\lvert f \rvert^p$ it always is).

1. **Cut off** where the trouble is: $f_n = f\chi_{[1/n, 1]}$ near a spike at $0$,
   $f_n = f\chi_{[0, n)}$ for a tail.
2. **Monotone convergence, all three hypotheses in words:** $f_n$ is measurable ($f$ is
   continuous, the interval is Borel); $0 \le f_1 \le f_2 \le \dots$ (the intervals grow and
   $f \ge 0$); $f_n \to f$ pointwise (each $x$ is inside the interval from some $n$ on).
3. **Compute $\int f_n$ with recipe 2.**
4. **Take the limit.** A finite limit means $f$ is integrable; $\infty$ means it is not.

Worked: tutorial examples [1](lecture:02-the-lebesgue-integral#example-1-an-unbounded-function)
and [2](lecture:02-the-lebesgue-integral#example-2-an-unbounded-domain),
[the cut-off](card:leb-cutoff), [an unbounded domain](card:leb-unbounded-domain).

## Recipe 4: a limit of integrals

1. **Find the pointwise limit** $f$. Useful facts: $\frac{\sin t}{t} \to 1$ as $t \to 0$
   (put $t = x/n$); $(1 + \frac{x}{n})^n \to e^x$; $te^{-t} \to 0$ as $t \to \infty$.
2. **Choose the theorem by what you can show:**

| You can show | Theorem | Then |
|---|---|---|
| $0 \le f_1 \le f_2 \le \dots$ | Monotone (3.11) | $\lim \int f_k = \int f$, possibly $\infty$ |
| $\mu(X) < \infty$ and $\lvert f_k \rvert \le c$ for a constant | Bounded (3.26) | the same |
| $\lvert f_k \rvert \le g$ for **all** $k$, with $\int g < \infty$ | Dominated (3.31) | the same |
| None of these | Compute $\int f_k$ directly, or suspect a counterexample | see [](guide:counterexamples) |

3. **Prove the bound for every $k$**, or say "for $k \ge 2$" and drop finitely many terms:
   a limit does not see them.
4. **Compute $\int f$** with recipes 1 to 3.

Check monotonicity at one point before you rely on it. $nxe^{-nx}$, $x^n$ and
$(1 + x/n)^{-n}$ are **not** increasing in $n$.

## Finding a dominating function

| Bound | When it helps | Used in |
|---|---|---|
| $\lvert \sin t \rvert \le \lvert t \rvert$, so $\lvert n \sin(x/n) \rvert \le x$ | $\sin$ of something small, multiplied by something large | [tutorial example 3](lecture:02-the-lebesgue-integral#example-3-dominated-convergence) |
| $\lvert \sin t \rvert \le 1$, $\lvert \cos t \rvert \le 1$ | An oscillating factor next to an integrable one | [](problems:convergence-theorems#ct-p7) |
| $\dfrac{t}{1 + t^\alpha} \le 1$ for $t \ge 0$, $\alpha > 1$ | $t = nx$ in numerator and denominator | [](problems:convergence-theorems#ct-p2) |
| $te^{-t} \le e^{-1}$ for $t \ge 0$ | $nxe^{-nx}$: the peak moves but does not grow | [](problems:convergence-theorems#ct-p14) |
| $\big(1 + \frac{x}{n}\big)^n \ge \binom{n}{2}\frac{x^2}{n^2} \ge \frac{x^2}{4}$ for $n \ge 2$, $x \ge 0$ | $(1 + \frac{x}{n})^{-n} \le \frac{4}{x^2}$ on $[1,\infty)$ | [](problems:convergence-theorems#ct-p3) |
| $\big(1 + \frac{x}{n}\big)^n \ge \big(1 + \frac{x}{2}\big)^2$ for $n \ge 2$, $x \ge 0$ | $(1 + \frac{x}{n})^{-n}$ on all of $(0,\infty)$, including near $0$ | [](problems:convergence-theorems#ct-p7) |
| $\big(1 + \frac{x}{n}\big)^{-n} \le 1$ for $x \ge 0$ | On a set of finite measure: bounded convergence | [tutorial example 4](lecture:02-the-lebesgue-integral#example-4-bounded-convergence) |

:::pitfall $e^{-x}$ is not a roof for $(1 + x/n)^{-n}$
$\ln(1 + t) \le t$ gives $(1 + \frac{x}{n})^n \le e^x$, so $(1 + \frac{x}{n})^{-n} \ge e^{-x}$:
the limit sits **below** every term. A dominating function has to lie above all of
them, which is why the binomial bounds are used.
:::

A dominating function is only useful if you can show it is integrable. Compare it with
the table below; each entry is a cut-off and a Riemann integral (recipe 3).

| Function | Domain | Integral |
|---|---|---|
| $x^{-a}$ | $(0,1)$ | $\frac{1}{1-a}$ if $a < 1$, $\infty$ if $a \ge 1$ |
| $x^{-a}$ | $(1,\infty)$ | $\frac{1}{a-1}$ if $a > 1$, $\infty$ if $a \le 1$ |
| $\frac{1}{1+x^2}$ | $(0,\infty)$ | $\frac{\pi}{2}$ |
| $\big(1 + \frac{x}{2}\big)^{-2}$ | $(0,\infty)$ | $2$ |
| $\frac{4}{x^2}$ | $[1,\infty)$ | $4$ |
| $x^k e^{-x}$ | $[0,\infty)$ | $k!$ ($1$ for $k = 1$, $2$ for $k = 2$) |

## Recipe 5: is $f$ in $L^p$? What is $\|f\|_p$?

1. Write $\int \lvert f \rvert^p \, d\mu$. It is defined, because the integrand is
   $\ge 0$.
2. Recipe 3 on $\lvert f \rvert^p$: cut off, monotone convergence, Riemann, limit.
3. Finite means $f \in L^p$, and $\|f\|_p$ is that number to the power $\frac1p$.

Check with the power rule ($x^{-a}$ is in $L^p$ near $0$ iff $ap < 1$, near $\infty$ iff
$ap > 1$), but write the computation: the rule is a check, not a proof. For indicators
$\|\chi_E\|_p = \mu(E)^{1/p}$. For $\|f\|_\infty$, ignore what happens on null sets: find
the smallest $a$ with $\mu(\{\lvert f \rvert > a\}) = 0$.

## Every worked computation

| What | Where |
|---|---|
| $\int_{(0,1]} x^{-1/2} = 2$, $\int_{[0,\infty)} xe^{-x} = 1$ | Tutorial [examples 1 and 2](lecture:02-the-lebesgue-integral#the-four-worked-examples) |
| $\lim \int \frac{n\sin(x/n)}{x(1+x^2)} = \frac\pi2$ (dominated) | [Example 3](lecture:02-the-lebesgue-integral#example-3-dominated-convergence) |
| $\lim \int_{[0,1]} (1 + \frac{x}{n})^{-n} = 1 - e^{-1}$ (bounded) | [Example 4](lecture:02-the-lebesgue-integral#example-4-bounded-convergence), [the card](card:leb-bounded-example) |
| A limit that does not pass through the integral | [](problems:convergence-theorems#ct-p1), [](problems:convergence-theorems#ct-p8) |
| Domination by elementary and binomial bounds | [](problems:convergence-theorems#ct-p2), [](problems:convergence-theorems#ct-p3), [](problems:convergence-theorems#ct-p7) |
| Cut-offs: $\int x^{-1/3} = \frac32$, $\int x^2e^{-x} = 2$ | [](problems:convergence-theorems#ct-p4), [](problems:convergence-theorems#ct-p5) |
| Bounded convergence: $x^n$, $nxe^{-nx}$ | [](problems:convergence-theorems#ct-p6), [](problems:convergence-theorems#ct-p14) |
| Lower Lebesgue sums of $x$, simple functions | [](problems:convergence-theorems#ct-p9), [](problems:convergence-theorems#ct-p10) |
| When an integral is defined | [](problems:convergence-theorems#ct-p11), [](problems:convergence-theorems#ct-p12) |
| Membership in $L^p$ | [](problems:lp-spaces-practice#lp-p1), [](problems:lp-spaces-practice#lp-p2) |
| $p$-norms and essential suprema | [](problems:lp-spaces-practice#lp-p6), [](problems:lp-spaces-practice#lp-p7) |
| Hölder and 7.10 with numbers | [](problems:lp-spaces-practice#lp-p8), [](problems:lp-spaces-practice#lp-p9) |
| Convergence in one $L^p$ and not another | [](problems:lp-spaces-practice#lp-p10), [](problems:lp-spaces-practice#lp-p11) |
| Mean squared error as $\Vert f_n - f\Vert _2^2$ | [](problems:lp-spaces-practice#lp-p14) |

## Mistakes that cost marks

- Using 3.34 on an unbounded function or interval. Cut off first.
- Applying monotone convergence to a sequence that decreases somewhere.
- A dominating function that depends on $n$, or one that is not integrable.
- Bounded convergence on a set of infinite measure.
- Writing $\infty - \infty$: if both $\int f^+$ and $\int f^-$ are infinite, the integral
  does not exist.
- Forgetting measurability. One sentence is enough: "continuous, hence Borel
  measurable (2.41)".

Related: [](guide:proof-toolkit), [](guide:counterexamples), the
[formula sheet](formulas).
