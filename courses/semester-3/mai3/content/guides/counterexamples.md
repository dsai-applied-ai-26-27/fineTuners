---
title: Counterexamples to know
topics: [measure]
summary: The standard counterexamples of lectures 1 to 3, sorted by the claim each one breaks, and a table of the four kinds of convergence with what implies what.
---

## Short answer

Every hypothesis in this unit is there because something breaks without it. An exam
asks for that in two forms: "show that the hypothesis cannot be dropped" and "does this
contradict theorem X?". The answer is almost always one of the examples below. Each row
says what the example shows and the one line of computation that proves it. Examples
marked *not in the notes* are standard ones added here.

Notation as in the notes: $\lambda$ is Lebesgue measure on $\mathbf{R}$ and $\chi_E$ the
characteristic function of $E$.

## The Riemann integral

| False claim | Counterexample | Why |
|---|---|---|
| Every bounded function on $[0,1]$ is Riemann integrable | $\chi_{\mathbf{Q} \cap [0,1]}$ (1.14) | Every lower sum is $0$, every upper sum $1$. Its Lebesgue integral is $0$ |
| A bounded pointwise limit of Riemann integrable functions is Riemann integrable | $\chi_{\{r_1, \dots, r_k\}}$, the first $k$ rationals (1.17) | Each has integral $0$; the limit is $\chi_{\mathbf{Q} \cap [0,1]}$ |
| The lower Riemann integral is additive | $\chi_{\mathbf{Q}\cap[0,1]} + \chi_{[0,1]\setminus\mathbf{Q}} = 1$ | Lower integrals $0 + 0$, but the sum has $1$ |
| Every improper Riemann integral is a Lebesgue integral | $\frac{\sin x}{x}$ on $[0,\infty)$ | $\int_0^\infty \frac{\lvert \sin x \rvert}{x} dx = \infty$, so $\int f^+$ and $\int f^-$ are both infinite |

## σ-algebras

| False claim | Counterexample | Why |
|---|---|---|
| Containing $\varnothing$ and $X$ is enough | $\{\varnothing, \{1\}, \{2\}, X\}$ on $X = \{1,2,3\}$ | The complement $\{2,3\}$ of $\{1\}$ is missing |
| An algebra is a σ-algebra | Finite and co-finite subsets of an infinite $X$ ([card](card:measure-cofinite-not-sigma)) | $\{x_2, x_4, \dots\}$ is a countable union of members, but neither it nor its complement is finite |
| A σ-algebra containing all points contains all intervals | Countable-or-co-countable sets of $\mathbf{R}$ | $(0,\infty)$ is uncountable with an uncountable complement |
| Every subset of $\mathbf{R}$ is Borel | A Vitali-type set (Axler 2.18) | Constructed with the axiom of choice; the notes only mention it |
| A dense set has positive measure | $\mathbf{Q}$ | Countable, so $\lambda(\mathbf{Q}) = 0$ ([card](card:measure-countable-zero)) |

## Measures

| False claim | Counterexample | Why |
|---|---|---|
| $\mu(\bigcap_k E_k) = \lim_k \mu(E_k)$ for every decreasing sequence | $E_k = [k, \infty)$ with $\lambda$ | Each has measure $\infty$, the intersection is empty. 2.60 needs $\mu(E_1) < \infty$ |
| $\mu(E \setminus D) = \mu(E) - \mu(D)$ always | $E = \mathbf{R}$, $D = [0,\infty)$ | The right side is $\infty - \infty$; 2.57 needs $\mu(D) < \infty$ |
| Outer measure is a measure on all subsets of $\mathbf{R}$ | The same Vitali-type set | Outer measure is not additive on all subsets; that is why Lebesgue measure lives on the Borel sets |

## A limit and an integral that do not commute

All three sequences converge to $0$ everywhere, and every integral is $1$. They are three
ways for mass to escape.

| Sequence | How the mass escapes | Monotone (3.11) | Bounded (3.26) | Dominated (3.31) |
|---|---|---|---|---|
| $n\chi_{(0,1/n)}$ | Grows taller on a shrinking set | Not increasing | No constant bound, and $\lambda(\mathbf{R}) = \infty$ | Any roof is at least $\frac{1}{2x}$ near $0$, not integrable |
| $\chi_{[n,n+1]}$ | Walks off to infinity | Not increasing | $\lambda(\mathbf{R}) = \infty$ | Any roof is at least $1$ on $[1,\infty)$ |
| $\frac1n\chi_{[0,n]}$ | Spreads out flat, converging **uniformly** | Not increasing | $\lambda(\mathbf{R}) = \infty$ | Any roof is at least about $\frac{1}{x+1}$ |

Cards: [escaping height](card:leb-escaping-height), [escaping to infinity](card:leb-escaping-infinity),
[spreading out](card:leb-spreading). Worked in full:
[](problems:convergence-theorems#ct-p8) and [](problems:convergence-theorems#ct-p1).

:::paper "Does this contradict the Monotone Convergence Theorem?"
No. Name the hypothesis that fails and show it at one point: "$f_1(0) = 1 > \frac12 = f_2(0)$,
so the sequence is not increasing, and the theorem does not apply." Then, for full marks,
say why dominated and bounded convergence fail too.
:::

## Integrals that are not defined

| Function | $\int f^+$ | $\int f^-$ | $\int f$ |
|---|---|---|---|
| $\chi_{[0,\infty)}$ | $\infty$ | $0$ | $\infty$, defined |
| $-\chi_{[0,\infty)}$ | $0$ | $\infty$ | $-\infty$, defined |
| $1$ on $[0,\infty)$, $-1$ on $(-\infty,0)$ | $\infty$ | $\infty$ | not defined |
| $\sin x$ on $\mathbf{R}$ | $\infty$ | $\infty$ | not defined |

Defined means at least one part is finite (3.18); integrable means both are.

## Lᵖ spaces

| False claim | Counterexample | Why |
|---|---|---|
| $\Vert \cdot\Vert _1$ is a norm on functions | $\chi_{\{0\}}$ | $\Vert \chi_{\{0\}}\Vert _1 = 0$ but $\chi_{\{0\}} \ne 0$; definiteness holds only after identifying a.e.-equal functions |
| The triangle inequality holds for $p = \frac12$ | $\chi_{[0,1]}$ and $\chi_{[1,2]}$ | Norms $1$ and $1$, the sum has norm $4$ |
| $\sup \lvert f \rvert = \Vert f\Vert _\infty$ | $f(x) = x$ on $[0,1]$ with $f(\frac12) = 100$ | $\sup = 100$, $\Vert f\Vert _\infty = 1$; and $\Vert \chi_{\mathbf{Q}}\Vert _\infty = 0$ |
| $L^1 \subset L^3$ | $x^{-1/3}\chi_{(0,1)}$ | $\Vert f\Vert _1 = \frac32$; $\lvert f \rvert^3 = \frac1x$ near $0$ |
| $L^2 \subset L^1$ on $(0,\infty)$ | $x^{-1}\chi_{(1,\infty)}$ | $\Vert g\Vert _2 = 1$; $\int_1^\infty \frac{dx}{x} = \infty$. On a finite measure space 7.10 rules this out |
| Equality in Hölder is common | $f = 1$, $g = x$ on $[0,1]$ | $\frac12 < \frac{1}{\sqrt3}$: $\lvert f \rvert^2$ and $\lvert g \rvert^2$ are not proportional |

The rule behind the two inclusion failures: $x^{-a}$ is in $L^p$ near $0$ iff $ap < 1$ and
near $\infty$ iff $ap > 1$ ([card](card:lp-power-rule-proof)).

## Four kinds of convergence

For $f_n \to f$ on a measure space:

- **pointwise**: $f_n(x) \to f(x)$ for every $x$;
- **almost everywhere**: for every $x$ outside a null set;
- **uniformly**: $\sup_x \lvert f_n(x) - f(x) \rvert \to 0$;
- **in $L^p$**: $\|f_n - f\|_p \to 0$.

| | Holds | Fails, and the example |
|---|---|---|
| Uniform ⇒ pointwise ⇒ a.e. | Always | The converses fail: $x^n$ on $[0,1)$ converges pointwise, not uniformly |
| Pointwise ⇒ $L^1$ | With a roof $\lvert f_n \rvert \le g$, $\int g < \infty$: dominated convergence applied to $\lvert f_n - f \rvert \le 2g$ *(a consequence not in the notes)* | $n\chi_{(0,1/n)}$: $\Vert f_n - 0\Vert _1 = 1$ |
| Uniform ⇒ $L^1$ | If $\mu(X) < \infty$: $\Vert f_n - f\Vert _1 \le \mu(X)\sup\lvert f_n - f \rvert$ (3.25) | $\frac1n\chi_{[0,n]}$: uniform, but $\Vert f_n\Vert _1 = 1$ |
| $L^q$ ⇒ $L^p$ for $p < q$ | If $\mu(X) < \infty$, by 7.10 | On an infinite measure space it can fail |
| $L^p$ ⇒ $L^q$ for $p < q$ | Never in general | $\sqrt n\,\chi_{(0,1/n)}$: $\to 0$ in $L^1$, $\Vert f_n\Vert _2 = 1$ |
| $L^2$ ⇒ $L^\infty$ | Never in general | $x^n$ on $[0,1]$: $\Vert x^n\Vert _2 \to 0$, $\Vert x^n\Vert _\infty = 1$ |
| $L^1$ ⇒ pointwise | Never in general *(not in the notes)* | The "typewriter": for $k = 1, 2, \dots$ run $\chi_{[j/2^k,\,(j+1)/2^k]}$ through $j = 0, \dots, 2^k - 1$. The $L^1$ norms $2^{-k}$ tend to $0$, but at every $x \in [0,1)$ the value $1$ comes back in every round, so $f_n(x)$ converges nowhere |

Cards: [L¹ but not L²](card:lp-l1-not-l2), [L² but not L∞](card:lp-l2-not-linf), [spreading out](card:leb-spreading).

Related: [](guide:proof-toolkit) for the proofs these examples guard,
[](guide:computing-integrals) for computing the integrals in the tables.
