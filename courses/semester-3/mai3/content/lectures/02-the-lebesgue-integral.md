---
title: The Lebesgue integral
number: 2
topics: [measure]
summary: Measurable functions again with their proofs, simple functions and how they approximate, the integral of a non-negative function as a supremum of lower Lebesgue sums, integrals of characteristic and simple functions, the integral of a real-valued function through its positive and negative parts, almost every, and the three convergence theorems (monotone, dominated, bounded), with the tutorial's four worked computations.
takeaways:
  - The integral of a non-negative measurable $f$ is the supremum of the lower Lebesgue sums $\sum_j \mu(A_j) \inf_{A_j} f$ over all finite partitions of $X$ into measurable sets.
  - The integral of $\chi_E$ is $\mu(E)$, and the integral of a non-negative simple function $\sum c_k \chi_{E_k}$ is $\sum c_k \mu(E_k)$. So $\int \chi_{\mathbf{Q}} \, d\lambda = 0$, where the Riemann integral was undefined.
  - A real-valued $f$ is split as $f = f^+ - f^-$, and $\int f \, d\mu = \int f^+ \, d\mu - \int f^- \, d\mu$ whenever at least one of the two is finite.
  - 'Monotone convergence: for $0 \le f_1 \le f_2 \le \dots$ with limit $f$, $\int f_k \to \int f$. Dominated convergence: if $f_k \to f$ almost everywhere and $\lvert f_k \rvert \le g$ with $\int g < \infty$, then $\int f_k \to \int f$. Bounded convergence is the special case $\mu(X) < \infty$ and $g$ a constant.'
  - To compute an integral over an unbounded set or of an unbounded function, cut it off with $\chi_{[1/n,1]}$ or $\chi_{[0,n)}$, use the Riemann integral on the bounded piece (3.34), and pass to the limit with monotone convergence.
sources:
  - lectures/Lecture 2 part1.pdf
  - lectures/Lecture 2 part2 (tutorial).pdf
---

## Where this fits

Lecture 1 built the three objects the integral needs: σ-algebras, measures and measurable
functions. This lecture defines the integral itself, shows that it fixes the three
problems of the Riemann integral named at the start of lecture 1, and proves nothing
twice: two convergence theorems do the heavy lifting.

The material comes in two parts, both by Ilhama Beganović and extracted from Axler,
*Measure, Integration & Real Analysis*: **part 1** (the lecture, chapters 2 and 3) and
**part 2** (the tutorial, sections 3A and 3B: the convergence theorems again, results
"not in the lecture", and four worked examples). Numbers in brackets are Axler's, as in
the notes. $\lambda$ is Lebesgue measure on $\mathbf{R}$.

## Measurable functions, with the proofs

Part 1 opens by repeating the end of lecture 1, this time with proofs.

:::definition Measurable function (2.35)
Let $(X, \mathcal{S})$ be a measurable space. $f : X \to \mathbf{R}$ is
**$\mathcal{S}$-measurable** if $f^{-1}(B) \in \mathcal{S}$ for every Borel set
$B \subset \mathbf{R}$.
:::

:::example Measurability depends on the σ-algebra (2.36)
- If $\mathcal{S} = \{\varnothing, X\}$, only the constant functions are
  $\mathcal{S}$-measurable.
- If $\mathcal{S}$ is the set of all subsets of $X$, every function is.
- If $\mathcal{S} = \{\varnothing, (-\infty, 0), [0, \infty), \mathbf{R}\}$, then
  $f : \mathbf{R} \to \mathbf{R}$ is $\mathcal{S}$-measurable exactly when $f$ is constant
  on $(-\infty, 0)$ and constant on $[0, \infty)$.
:::

:::recall Why must $f$ be constant on $[0,\infty)$ in the third case?
Suppose $f$ takes two values $s < t$ on $[0, \infty)$. Then $f^{-1}((s, \infty))$
contains a point of $[0,\infty)$ but not all of it, and no set in $\mathcal{S}$ does
that. The same argument works on $(-\infty, 0)$. Conversely, if $f$ is constant on both
pieces, every inverse image is a union of whole pieces, so it is in $\mathcal{S}$.
:::

Checking every Borel set is never necessary:

:::theorem Condition for measurability (2.39)
If $f^{-1}((a, \infty)) \in \mathcal{S}$ for every $a \in \mathbf{R}$, then $f$ is
$\mathcal{S}$-measurable.
:::

:::theorem Continuous functions are Borel measurable (2.40, 2.41)
$f : X \to \mathbf{R}$ with $X \subset \mathbf{R}$ is **Borel measurable** if $f^{-1}(B)$
is Borel for every Borel $B$. Every continuous real function on a Borel subset of
$\mathbf{R}$ is Borel measurable.
:::

:::proof
Not in the notes; this is the standard argument. Let $f : B \to \mathbf{R}$ be continuous
and fix $a \in \mathbf{R}$. For each $x$ with $f(x) > a$, continuity gives $\delta_x > 0$
such that $f(y) > a$ for all $y \in B \cap (x - \delta_x, x + \delta_x)$. Hence
$f^{-1}((a, \infty)) = B \cap G$, where $G$ is the union of these intervals. $G$ is open,
so $B \cap G$ is Borel, and 2.39 finishes the proof.
:::

So polynomials, $\sin$, $\cos$, $\exp$ and everything continuous from calculus are
measurable for free: continuity is a far stronger condition than measurability.

:::theorem Composition (2.44)
If $f : X \to \mathbf{R}$ is $\mathcal{S}$-measurable and $g$ is a real Borel measurable
function defined on a set containing the range of $f$, then $g \circ f$ is
$\mathcal{S}$-measurable.
:::

:::proof
Let $B \subset \mathbf{R}$ be Borel. Then $(g \circ f)^{-1}(B) = f^{-1}\big(g^{-1}(B)\big)$.
$g^{-1}(B)$ is Borel because $g$ is Borel measurable, and $f^{-1}$ of a Borel set is in
$\mathcal{S}$ because $f$ is $\mathcal{S}$-measurable.
:::

:::example Four measurable functions for free (2.45)
If $f$ is $\mathcal{S}$-measurable, so are $-f$, $\tfrac12 f$, $\lvert f \rvert$ and
$f^2$: each is $g \circ f$ with the continuous $g(x) = -x$, $\tfrac12 x$, $\lvert x \rvert$,
$x^2$.
:::

:::theorem Algebraic operations (2.46)
If $f, g$ are $\mathcal{S}$-measurable, so are $f + g$, $f - g$ and $fg$, and $f/g$ when
$g(x) \ne 0$ for all $x$.
:::

:::proof
Not in the notes; the standard argument puts a rational in between. For $a \in \mathbf{R}$,

$$(f + g)^{-1}\big((a, \infty)\big) = \bigcup_{r \in \mathbf{Q}} \Big( f^{-1}\big((r, \infty)\big) \cap g^{-1}\big((a - r, \infty)\big) \Big).$$

If $f(x) + g(x) > a$, a rational $r$ with $a - g(x) < r < f(x)$ puts $x$ in the right
side; conversely $f(x) > r$ and $g(x) > a - r$ add up to $f(x) + g(x) > a$. The union is
countable, so $f + g$ is measurable by 2.39. Then $f - g = f + (-g)$,
$fg = \frac12\big((f+g)^2 - f^2 - g^2\big)$ and $f/g = f \cdot (h \circ g)$ with the
continuous $h(t) = 1/t$ on $\mathbf{R} \setminus \{0\}$ are measurable by 2.44 and 2.45.
:::

:::theorem Pointwise limits (2.48)
If $f_1, f_2, \dots$ are $\mathcal{S}$-measurable and $f(x) = \lim_{k\to\infty} f_k(x)$
exists for every $x \in X$, then $f$ is $\mathcal{S}$-measurable.
:::

:::proof
By 2.39 it is enough to show, for each $a \in \mathbf{R}$,

$$f^{-1}\big((a, \infty)\big) = \bigcup_{j=1}^{\infty} \bigcup_{m=1}^{\infty} \bigcap_{k=m}^{\infty} f_k^{-1}\Big(\big(a + \tfrac{1}{j}, \infty\big)\Big),$$

because the right side is built from sets in $\mathcal{S}$ by countable unions and
intersections.

**Left in right.** If $f(x) > a$, choose $j$ with $f(x) > a + \frac1j$. Since
$f_k(x) \to f(x)$, there is $m$ with $f_k(x) > a + \frac1j$ for all $k \ge m$. So $x$ is
in the right side.

**Right in left.** If $f_k(x) > a + \frac1j$ for all $k \ge m$, letting $k \to \infty$
gives $f(x) \ge a + \frac1j > a$.
:::

:::tip Reading the triple union-intersection
$\bigcup_j \bigcup_m \bigcap_{k \ge m}$ says, word for word: "for some margin $\frac1j$,
from some index $m$ on, every $f_k(x)$ is above $a$ by that margin". The margin is what
makes the strict inequality survive the limit: without it, $f_k(x) > a$ for all $k$
only gives $f(x) \ge a$.
:::

## Simple functions

:::definition Characteristic function
For $E \subset X$, the **characteristic function** (or indicator) of $E$ is
$\chi_E(x) = 1$ if $x \in E$ and $0$ otherwise. It is $\mathcal{S}$-measurable if and
only if $E \in \mathcal{S}$.
:::

The "if and only if" is quick: $\chi_E^{-1}(B)$ is one of $\varnothing$, $E$,
$X \setminus E$, $X$, depending on which of $0$ and $1$ lie in $B$.

:::definition Simple function (2.88)
A function is **simple** if it takes only finitely many values. With distinct non-zero
values $c_1, \dots, c_n$,

$$f = c_1 \chi_{E_1} + \dots + c_n \chi_{E_n}, \qquad E_k = f^{-1}(\{c_k\}),$$

and $f$ is $\mathcal{S}$-measurable if and only if $E_1, \dots, E_n \in \mathcal{S}$.
:::

:::example Rewriting a simple function with disjoint sets
On $\mathbf{R}$ with the Borel sets, $f = 3\chi_{[0,2)} + \chi_{[1,4)}$ overlaps on
$[1,2)$. It equals $3$ on $[0,1)$, $4$ on $[1,2)$, $1$ on $[2,4)$ and $0$ elsewhere, so

$$f = 3\chi_{[0,1)} + 4\chi_{[1,2)} + 1\chi_{[2,4)},$$

with disjoint Borel sets: $f$ is simple and measurable. The disjoint form is the one the
integral formula 3.7 below uses.
:::

:::theorem Approximation by simple functions
For each measurable $f : A \to [0, +\infty)$ with $A \subset X$ there are measurable
simple functions $f_n : A \to [0, +\infty)$ with

$$0 \le f_1 \le f_2 \le \dots \le f \qquad \text{and} \qquad \lim_{n\to\infty} f_n(x) = f(x) \ \text{ for every } x \in A .$$

If $f$ is bounded, the convergence is uniform on $A$.
:::

The notes' figure shows the construction on $f(x) = x^2$, $x \in [0,1]$:

$$f_k = \frac{\lfloor 2^k f \rfloor}{2^k} .$$

$f_k$ rounds $f$ **down** to the grid $0, 2^{-k}, 2 \cdot 2^{-k}, \dots$, so it takes
finitely many values on a bounded $f$, sits below $f$, and grows as the grid refines.
Since rounding down loses less than one grid step, $0 \le f - f_k < 2^{-k}$ everywhere,
which is the uniform convergence. (For an unbounded $f$, Axler (2.89) also caps $f_k$ at
the value $k$, so that it still takes finitely many values; the notes do not show this.)

## The integral of a non-negative function

:::definition $\mathcal{S}$-partition (3.1)
A finite collection $A_1, \dots, A_m$ of **disjoint** sets in $\mathcal{S}$ with
$A_1 \cup \dots \cup A_m = X$.
:::

:::definition Lower Lebesgue sum (3.2)
For a measure space $(X, \mathcal{S}, \mu)$, a measurable $f : X \to [0, \infty]$ and an
$\mathcal{S}$-partition $P = A_1, \dots, A_m$:

$$\mathcal{L}(f, P) = \sum_{j=1}^{m} \mu(A_j) \inf_{A_j} f .$$
:::

Compare the lower Riemann sum: there, the pieces are intervals and their size is length.
Here the pieces are any measurable sets and their size is $\mu$.

:::definition Integral of a non-negative function (3.3)
$$\int f \, d\mu = \sup \big\{ \mathcal{L}(f, P) : P \text{ is an } \mathcal{S}\text{-partition of } X \big\}.$$
:::

Two things are wanted from an integral: $\int \chi_E \, d\mu = \mu(E)$ and additivity.
The definition gives both, though the second is not obvious.

:::theorem Integral of a characteristic function (3.4)
For $E \in \mathcal{S}$: $\displaystyle \int \chi_E \, d\mu = \mu(E)$.
:::

:::proof
**$\ge$.** The partition $E, X \setminus E$ gives
$\mathcal{L}(\chi_E, P) = \mu(E) \cdot 1 + \mu(X \setminus E) \cdot 0 = \mu(E)$.

**$\le$.** For any partition $A_1, \dots, A_m$, $\inf_{A_j} \chi_E$ is $1$ if
$A_j \subset E$ and $0$ otherwise. So

$$\mathcal{L}(\chi_E, P) = \sum_{\{j : A_j \subset E\}} \mu(A_j) = \mu\Big( \bigcup_{\{j : A_j \subset E\}} A_j \Big) \le \mu(E),$$

using additivity on the disjoint $A_j$ and then monotonicity.
:::

:::example The rationals, at last (3.5)
$\int \chi_{\mathbf{Q}} \, d\lambda = \lambda(\mathbf{Q}) = 0$, and
$\int \chi_{[0,1] \setminus \mathbf{Q}} \, d\lambda = \lambda([0,1] \setminus \mathbf{Q}) = 1$.
The first was not Riemann integrable on $[0,1]$; the second has lower Riemann integral
$0$, which is not what anyone wants. **The first deficiency from lecture 1 is fixed.**
:::

:::theorem Integral of a simple function (3.7)
If $E_1, \dots, E_n \in \mathcal{S}$ are **disjoint** and $c_1, \dots, c_n \in [0, \infty]$,

$$\int \Big( \sum_{k=1}^{n} c_k \chi_{E_k} \Big) d\mu = \sum_{k=1}^{n} c_k \, \mu(E_k).$$
:::

:::proof
Adding $E_{n+1} = X \setminus (E_1 \cup \dots \cup E_n)$ with $c_{n+1} = 0$ changes
nothing, so assume $E_1, \dots, E_n$ is a partition of $X$.

**$\ge$.** With $P = E_1, \dots, E_n$ itself, $\mathcal{L} = \sum_k c_k \mu(E_k)$.

**$\le$.** Let $A_1, \dots, A_m$ be any partition. On $A_j$ the function takes the values
$c_i$ for those $i$ with $A_j \cap E_i \ne \varnothing$, so its infimum there is the
smallest such $c_i$. Split each $A_j$ along the $E_k$:

$$\mathcal{L} = \sum_{j=1}^{m} \mu(A_j) \min_{\{i : A_j \cap E_i \ne \varnothing\}} c_i = \sum_{j=1}^{m} \sum_{k=1}^{n} \mu(A_j \cap E_k) \min_{\{i : A_j \cap E_i \ne \varnothing\}} c_i \le \sum_{j=1}^{m} \sum_{k=1}^{n} \mu(A_j \cap E_k)\, c_k = \sum_{k=1}^{n} c_k \, \mu(E_k).$$

The inequality holds term by term: if $\mu(A_j \cap E_k) > 0$, then
$A_j \cap E_k \ne \varnothing$, so $c_k$ is among the values the minimum is taken over.
:::

:::pitfall Use the disjoint form
$\int (3\chi_{[0,2)} + \chi_{[1,4)}) \, d\lambda$ is $3 \cdot 1 + 4 \cdot 1 + 1 \cdot 2 = 9$
from the disjoint form. Here $3 \cdot 2 + 1 \cdot 3$ gives $9$ as well, but only because
additivity (3.16 below) holds; 3.7 as stated needs disjoint sets.
:::

:::theorem Order preserving (3.8)
If $0 \le f \le g$ are measurable, then $\int f \, d\mu \le \int g \, d\mu$.
:::

:::proof
For any partition, $\inf_{A_j} f \le \inf_{A_j} g$ on every piece, so
$\mathcal{L}(f, P) \le \mathcal{L}(g, P)$. Take suprema.
:::

:::theorem Additivity (3.16)
For measurable $f, g : X \to [0, \infty]$:
$\displaystyle \int (f + g) \, d\mu = \int f \, d\mu + \int g \, d\mu$.
:::

The notes state 3.16 without proof (Axler proves it with the Monotone Convergence
Theorem and simple functions).

:::proof
Not in the notes; Axler's route, using the Monotone Convergence Theorem of the next
section. **Simple functions first.** Write $f = \sum_i a_i \chi_{E_i}$ and
$g = \sum_j b_j \chi_{F_j}$ over partitions of $X$. Then
$f + g = \sum_{i,j} (a_i + b_j)\chi_{E_i \cap F_j}$ over the common refinement, and 3.7
with finite additivity of $\mu$ gives

$$\int (f + g) \, d\mu = \sum_{i,j} (a_i + b_j)\,\mu(E_i \cap F_j) = \sum_i a_i \mu(E_i) + \sum_j b_j \mu(F_j) .$$

**Then monotone limits.** Take simple measurable $f_k \uparrow f$ and $g_k \uparrow g$
(the approximation theorem above). Then $f_k + g_k$ is simple and increases to $f + g$,
and monotone convergence, used three times, gives
$\int (f + g) = \lim_k \big(\int f_k + \int g_k\big) = \int f + \int g$.
:::

:::example Where the lower Riemann integral fails
Let $f = \chi_{\mathbf{Q} \cap [0,1]}$ and $g = \chi_{[0,1] \setminus \mathbf{Q}}$. The lower
Riemann integrals are $L(f, [0,1]) = 0$ and $L(g, [0,1]) = 0$, but $f + g = 1$ on
$[0,1]$, so $L(f+g, [0,1]) = 1 \ne 0 + 0$. With Lebesgue measure,
$\int f = 0$, $\int g = 1$, $\int (f+g) = 1$: additivity holds.
:::

## The Monotone Convergence Theorem

:::theorem Monotone Convergence Theorem (3.11)
Let $(X, \mathcal{S}, \mu)$ be a measure space and $0 \le f_1 \le f_2 \le \dots$ an
increasing sequence of $\mathcal{S}$-measurable functions, with $f(x) = \lim_k f_k(x)$
(possibly $\infty$). Then

$$\lim_{k \to \infty} \int f_k \, d\mu = \int f \, d\mu .$$
:::

Two hypotheses, both essential: **non-negative** and **increasing**. Nothing about
boundedness or finiteness: both sides may be $\infty$. **The third deficiency from lecture
1 (limits) is fixed** for increasing sequences.

:::proof
Not in the notes, which state 3.11 without proof; this is the argument of Axler's proof.
$f$ is measurable by 2.48. Since $f_k \le f_{k+1} \le f$, the integrals $\int f_k$
increase and stay below $\int f$ (3.8), so $\lim_k \int f_k \le \int f$.

For the other inequality, fix a partition $A_1, \dots, A_m$ and, for each $j$ with
$\inf_{A_j} f > 0$, a number $0 < c_j < \inf_{A_j} f$. Let
$E_{j,k} = \{x \in A_j : f_k(x) > c_j\}$. These sets increase with $k$, and their union is
$A_j$, because $f_k(x) \to f(x) > c_j$; so $\mu(E_{j,k}) \to \mu(A_j)$ by 2.59. Since
$f_k \ge \sum_j c_j \chi_{E_{j,k}}$, 3.8 and 3.7 give
$\int f_k \ge \sum_j c_j \, \mu(E_{j,k})$. Let $k \to \infty$, then let each $c_j$ rise to
$\inf_{A_j} f$:

$$\lim_{k \to \infty} \int f_k \, d\mu \ge \sum_{j=1}^{m} \mu(A_j) \inf_{A_j} f = \mathcal{L}(f, P) .$$

The supremum over all partitions $P$ is $\int f \, d\mu$.
:::

## Integrating real-valued functions

:::definition Positive and negative parts (3.17)
For $f : X \to [-\infty, \infty]$,

$$f^+(x) = \begin{cases} f(x) & f(x) \ge 0 \\ 0 & f(x) < 0 \end{cases} \qquad f^-(x) = \begin{cases} 0 & f(x) \ge 0 \\ -f(x) & f(x) < 0 \end{cases}$$

Both are non-negative, $f = f^+ - f^-$ and $\lvert f \rvert = f^+ + f^-$.
:::

:::definition Integral of a real-valued function (3.18)
If $f$ is measurable and **at least one** of $\int f^+ \, d\mu$ and $\int f^- \, d\mu$ is
finite,

$$\int f \, d\mu = \int f^+ \, d\mu - \int f^- \, d\mu .$$

If $f \ge 0$ this agrees with 3.3, since then $f^+ = f$ and $f^- = 0$.
:::

:::example Defined and undefined
- $f = \chi_{[0,\infty)}$: $\int f^+ \, d\lambda = \infty$ and $\int f^- \, d\lambda = 0$, so
  $\int f \, d\lambda = \infty - 0 = \infty$. **Defined**, and infinite.
- $f = 1$ on $[0, \infty)$, $-1$ on $(-\infty, 0)$: both parts integrate to $\infty$, and
  $\infty - \infty$ has no value. **Not defined.**
:::

:::note Integrable
The tutorial adds: $\int \lvert f \rvert \, d\mu < \infty$ is equivalent to both
$\int f^+ \, d\mu$ and $\int f^- \, d\mu$ being finite, because
$\lvert f \rvert = f^+ + f^-$. Such an $f$ is what "Lebesgue integrable" means in the
tutorial's remark below: an integral that exists **and** is finite.
:::

## Almost every

:::definition Almost every (3.27)
A set $E \in \mathcal{S}$ contains **$\mu$-almost every** element of $X$ if
$\mu(X \setminus E) = 0$. A property holds almost everywhere (a.e.) if it holds outside a
set of measure zero.
:::

Almost every real number is irrational, because $\lambda(\mathbf{Q}) = 0$. A set of
measure zero cannot change an integral, which is why the Dominated Convergence Theorem
only asks for things to hold almost everywhere.

:::proof Why a null set cannot change an integral
Not in the notes. Let $\mu(N) = 0$ and $f \ge 0$ be measurable. In any partition, a piece
inside $N$ has measure $0$, and a piece not inside $N$ contains a point where
$f\chi_N = 0$. Either way its term in the lower sum is $0$, so
$\int f\chi_N \, d\mu = 0$. If $f = g$ outside $N$, additivity gives
$\int f = \int f\chi_{X \setminus N} + 0 = \int g\chi_{X \setminus N} + 0 = \int g$.
:::

## The Dominated and Bounded Convergence Theorems

In general $f_k \to f$ pointwise does **not** give $\int f_k \to \int f$. Monotone
convergence is one way out, but it needs non-negative increasing sequences. The grand
result drops both and asks only for one integrable function above every $\lvert f_k \rvert$:

:::theorem Dominated Convergence Theorem (3.31)
Let $(X, \mathcal{S}, \mu)$ be a measure space, $f$ and $f_1, f_2, \dots$ measurable from
$X$ to $[-\infty, \infty]$ with $f_k(x) \to f(x)$ for almost every $x$. If there is a
measurable $g : X \to [0, \infty]$ with

$$\int g \, d\mu < \infty \qquad \text{and} \qquad \lvert f_k(x) \rvert \le g(x) \ \text{ for every } k \text{ and almost every } x,$$

then $\displaystyle \lim_{k \to \infty} \int f_k \, d\mu = \int f \, d\mu$.
:::

:::proof
Not in the notes, which state 3.31 without proof. The standard textbook proof goes
through **Fatou's lemma**, itself not part of the course: for measurable $g_k \ge 0$,
$\int \liminf_k g_k \le \liminf_k \int g_k$. (Apply monotone convergence to the increasing
$h_k = \inf_{j \ge k} g_j$, and note $\int h_k \le \int g_j$ for every $j \ge k$.)

Changing everything on a null set changes no integral, so assume $f_k \to f$ and
$\lvert f_k \rvert \le g$ everywhere. Then $\lvert f \rvert \le g$, all the functions are
integrable, and $g + f_k$ and $g - f_k$ are non-negative. Fatou applied to both gives

$$\int g + \int f \le \int g + \liminf_{k} \int f_k, \qquad \int g - \int f \le \int g - \limsup_{k} \int f_k .$$

Cancel the **finite** number $\int g$: $\limsup_k \int f_k \le \int f \le \liminf_k \int f_k$,
so the limit exists and equals $\int f$. This is the one place where $\int g < \infty$ is
used.
:::

:::theorem Bounded Convergence Theorem (3.26)
Let $\mu(X) < \infty$ and let $f_k \to f$ pointwise on $X$, with $f : X \to \mathbf{R}$.
If there is a constant $c$ with $\lvert f_k(x) \rvert \le c$ for all $k$ and $x$, then
$\displaystyle \lim_{k \to \infty} \int f_k \, d\mu = \int f \, d\mu$.
:::

It is the Dominated Convergence Theorem with $g = c$: then
$\int g \, d\mu = c\,\mu(X) < \infty$.

| Theorem | Sign | Shape of the sequence | What bounds it | Measure of $X$ |
|---|---|---|---|---|
| Monotone (3.11) | $f_k \ge 0$ | Increasing | Nothing needed | Any |
| Dominated (3.31) | Any | Any, converging a.e. | One $g$ with $\int g < \infty$ | Any |
| Bounded (3.26) | Any | Any, converging pointwise | A constant $c$ | Finite |

:::pitfall Three sequences where the limit does not pass through the integral
These are not in the notes; they show which hypothesis each theorem needs.

- **Escaping height:** $f_n = n\chi_{(0,1/n)}$. $f_n \to 0$ everywhere, but
  $\int f_n \, d\lambda = 1$ for every $n$. Not increasing (MCT fails), not bounded by a
  constant (BCT fails), and any $g \ge$ all $f_n$ is at least about $\frac{1}{2x}$ near
  $0$, which is not integrable (DCT fails).
- **Escaping to infinity:** $f_n = \chi_{[n, n+1]}$. $f_n \to 0$ everywhere,
  $\int f_n \, d\lambda = 1$. Bounded by $1$, but $\lambda(\mathbf{R}) = \infty$, so BCT does
  not apply.
- **Spreading out:** $f_n = \frac1n \chi_{[0,n]}$, last year's homework problem
  ([](problems:convergence-theorems#ct-p1)). Converges to $0$ uniformly, yet
  $\int f_n \, d\lambda = 1$.
:::

## Results the tutorial adds

Part 2 lists results "not in the lecture" that the examples rely on.

:::theorem Homogeneity, additivity, order, absolute value (3.20 to 3.23)
For a measure space $(X, \mathcal{S}, \mu)$:

- **3.20** If $\int f \, d\mu$ is defined and $c \in \mathbf{R}$:
  $\int cf \, d\mu = c \int f \, d\mu$.
- **3.21** If $\int \lvert f \rvert \, d\mu < \infty$ and $\int \lvert g \rvert \, d\mu < \infty$:
  $\int (f+g) \, d\mu = \int f \, d\mu + \int g \, d\mu$.
- **3.22** If $\int f$ and $\int g$ are defined and $f \le g$:
  $\int f \, d\mu \le \int g \, d\mu$.
- **3.23** If $\int f \, d\mu$ is defined:
  $\big\lvert \int f \, d\mu \big\rvert \le \int \lvert f \rvert \, d\mu$.
:::

:::definition Integration on a subset (3.24)
For $E \in \mathcal{S}$: $\displaystyle \int_E f \, d\mu = \int \chi_E f \, d\mu$, when the
right side is defined.
:::

:::theorem Bounding an integral (3.25)
If $\int_E f \, d\mu$ is defined, then
$\big\lvert \int_E f \, d\mu \big\rvert \le \mu(E) \sup_E \lvert f \rvert$.
:::

:::proof
Not in the notes. By 3.23, $\big\lvert \int \chi_E f \big\rvert \le \int \chi_E \lvert f \rvert$.
Pointwise $\chi_E \lvert f \rvert \le (\sup_E \lvert f \rvert)\,\chi_E$, whose integral is
$\mu(E) \sup_E \lvert f \rvert$ by 3.7. Order (3.8) joins the two.
:::

:::theorem Riemann integrable ⇔ continuous almost everywhere (3.34)
Let $a < b$ and $f : [a, b] \to \mathbf{R}$ be **bounded**. Then $f$ is Riemann integrable
if and only if

$$\big\lvert \{ x \in [a,b] : f \text{ is not continuous at } x \} \big\rvert = 0 .$$

If so, $f$ is Lebesgue measurable and $\displaystyle \int_a^b f = \int_{[a,b]} f \, d\lambda$:
the Riemann and Lebesgue integrals agree.
:::

3.34 is the bridge that lets you **compute**: on a bounded interval, a bounded continuous
function's Lebesgue integral is the calculus integral. Everything unbounded is handled by
cutting off and taking a limit.

## The four worked examples

### Example 1: an unbounded function

$$\int_{(0,1]} \frac{1}{\sqrt{x}} \, d\lambda(x) .$$

$f(x) = x^{-1/2}$ is unbounded near $0$, so 3.34 does not apply directly. Step away from
$0$: $f_n = f \chi_{[1/n, 1]}$.

1. **Monotone convergence applies.** $f$ is continuous, hence Borel measurable (2.41), so
   each $f_n$ is measurable. $0 \le f_1 \le f_2 \le \dots$ because $f \ge 0$ and the
   intervals $[1/n, 1]$ grow. Each $x \in (0,1]$ lies in $[1/n, 1]$ for all large $n$, so
   $f_n(x) = f(x)$ eventually: $f_n \to f$ pointwise. By 3.11,
   $\int_{(0,1]} f \, d\lambda = \lim_n \int_{(0,1]} f_n \, d\lambda$.
2. **Each $f_n$ by Riemann.** $\int_{(0,1]} f_n \, d\lambda = \int_{[1/n,1]} f \, d\lambda$,
   and on $[1/n,1]$ the function is continuous and bounded (by $\sqrt n$), so by 3.34
   $$\int_{[1/n,1]} x^{-1/2} \, d\lambda = \int_{1/n}^{1} x^{-1/2} \, dx = \Big[ 2\sqrt{x} \Big]_{1/n}^{1} = 2 - \frac{2}{\sqrt{n}} .$$
3. **The limit.** $\displaystyle \int_{(0,1]} \frac{d\lambda(x)}{\sqrt{x}} = \lim_{n\to\infty} \Big( 2 - \frac{2}{\sqrt n} \Big) = 2$.

**The second deficiency from lecture 1 (unbounded functions) is fixed.**

### Example 2: an unbounded domain

$$\int_{[0,\infty)} x e^{-x} \, d\lambda(x) .$$

$f(x) = xe^{-x} \ge 0$ on $[0, \infty)$ (both factors are non-negative). Cut off the
domain: $f_n = f \chi_{[0,n)}$.

1. **Monotone convergence applies.** $f$ is continuous and $[0,n)$ is Borel, so $f_n$ is
   measurable; $0 \le f_1 \le f_2 \le \dots$; and $f_n(x) = f(x)$ once $n > x$. By 3.11,
   $\int_{[0,\infty)} f \, d\lambda = \lim_n \int f_n \, d\lambda$.
2. **Each $f_n$ by Riemann.** $f$ is continuous and bounded on $[0,n]$
   ($0 \le f \le 1/e$), so 3.34 applies. The single point $n$ has measure $0$, so $[0,n)$
   and $[0,n]$ give the same integral. By parts,
   $$\int_0^n x e^{-x} \, dx = \Big[ -(x+1) e^{-x} \Big]_0^n = 1 - (n+1)e^{-n} .$$
3. **The limit.** $(n+1)e^{-n} \to 0$, so the integral is $1$.

:::warning Improper Riemann integrals are not always Lebesgue integrals
In examples 1 and 2 the improper Riemann integral is the same limit, so the two agree. Not
always: $\int_0^\infty \frac{\sin x}{x} \, dx$ exists as an improper Riemann integral, but
$\frac{\sin x}{x}$ is **not** Lebesgue integrable on $[0, \infty)$. (The reason, not given
in the notes: $\int_0^\infty \frac{\lvert \sin x \rvert}{x} \, dx = \infty$, so both
$\int f^+$ and $\int f^-$ are infinite.)
:::

### Example 3: dominated convergence

$$\lim_{n\to\infty} \int_{(0,\infty)} \frac{n \sin(x/n)}{x(1+x^2)} \, d\lambda(x) .$$

$f_n(x) = \dfrac{n\sin(x/n)}{x(1+x^2)}$ changes sign, so the Monotone Convergence Theorem
is out. Each $f_n$ is continuous on $(0,\infty)$, hence measurable.

1. **Pointwise limit.** For fixed $x > 0$ put $t = x/n \to 0$. Then
   $\dfrac{n \sin(x/n)}{x} = \dfrac{\sin t}{t} \to 1$, so
   $f_n(x) \to f(x) = \dfrac{1}{1+x^2}$.
2. **Dominating function.** $\lvert \sin t \rvert \le \lvert t \rvert$ for every real
   $t$, so $\lvert n \sin(x/n) \rvert \le n \cdot \frac{x}{n} = x$ and
   $$\lvert f_n(x) \rvert \le \frac{x}{x(1+x^2)} = \frac{1}{1+x^2} =: g(x) .$$
   $g$ is integrable: as in example 2 (monotone convergence with $g\chi_{(0,n)}$ and
   3.34), $\int_{(0,\infty)} g \, d\lambda = \lim_n \arctan n = \frac{\pi}{2} < \infty$.
3. **Apply 3.31.**
   $$\lim_{n\to\infty} \int_{(0,\infty)} f_n \, d\lambda = \int_{(0,\infty)} \frac{d\lambda(x)}{1+x^2} = \frac{\pi}{2} .$$

### Example 4: bounded convergence

$$\lim_{n\to\infty} \int_{[0,1]} \Big( 1 + \frac{x}{n} \Big)^{-n} d\lambda(x)$$

on $[0,1]$ with the Borel sets and $\lambda$. Each $f_n$ is continuous, hence measurable.

1. **Finite measure.** $\lambda([0,1]) = 1 < \infty$.
2. **Pointwise limit.** $(1 + \frac{x}{n})^n \to e^x$, so $f_n(x) \to e^{-x}$.
3. **Uniform bound.** $1 + \frac{x}{n} \ge 1$ on $[0,1]$, so $0 < f_n(x) \le 1$: take
   $c = 1$.
4. **Apply 3.26**, then 3.34 for the continuous bounded limit:
   $$\lim_{n\to\infty} \int_{[0,1]} f_n \, d\lambda = \int_0^1 e^{-x} \, dx = 1 - e^{-1} .$$

## What an exam wants

:::paper Compute a Lebesgue integral of something unbounded
1. Write $f_n = f\chi_{E_n}$ with $E_n$ growing to the domain ($[1/n, 1]$, $[0, n)$, …)
   on which $f$ is bounded and continuous.
2. Check the three hypotheses of 3.11 **in words**: $f_n$ measurable (continuous, 2.41),
   $0 \le f_1 \le f_2 \le \dots$, and $f_n \to f$ pointwise.
3. Compute $\int f_n$ as a Riemann integral, citing 3.34 (bounded, continuous, bounded
   interval).
4. Take the limit.
:::

:::paper Compute a limit of integrals
1. Find the pointwise limit $f$ (a substitution like $t = x/n$, or a known limit like
   $(1 + x/n)^n \to e^x$).
2. **Pick the theorem by the hypotheses you can show:**
   - $f_k \ge 0$ and increasing → monotone (3.11);
   - $\mu(X) < \infty$ and $\lvert f_k \rvert \le c$ → bounded (3.26);
   - otherwise find $g$ with $\lvert f_k \rvert \le g$ for all $k$ and $\int g < \infty$ →
     dominated (3.31). Standard tools: $\lvert \sin t \rvert \le \lvert t \rvert$,
     $\lvert \sin t \rvert \le 1$, $(1 + x/n)^n \ge$ a binomial term.
3. Prove the bound holds **for every $k$** (not just large $k$, or say "for $k \ge 2$" and
   drop finitely many terms).
4. Compute $\int f$.
:::

:::paper Show the limit does not pass through the integral
Compute $\int f_n$ and $\int f$ and show they differ. Then name the hypothesis that fails
for **each** theorem the examiner might expect: not increasing (MCT), no integrable
dominating function (DCT), $\mu(X) = \infty$ or no constant bound (BCT).
:::

## Where next

- Drill: [](deck:lebesgue-integral), and every proof above one step at a time:
  [](deck:lebesgue-integral-proofs).
- Method: [](guide:computing-integrals) for every computation of this kind, and
  [](guide:counterexamples) for limits that do not pass through the integral.
- Practice: [](problems:convergence-theorems): last year's homework problems on the
  convergence theorems, and new computations in the style of the tutorial.
- Definitions in one place: [the glossary](glossary). Formulas: [the sheet](formulas).
- Lecture 1 for σ-algebras and measures: [](lecture:01-sigma-algebras-and-measures).
