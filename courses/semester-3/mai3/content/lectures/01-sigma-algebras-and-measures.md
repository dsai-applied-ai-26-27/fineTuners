---
title: σ-algebras, measures and measurable functions
number: 1
topics: [measure]
summary: Why the Riemann integral is not enough, which collections of sets can be given a size (σ-algebras and Borel sets), what a measure is and how it behaves under limits, Lebesgue measure on the real line, and measurable and simple functions.
takeaways:
  - The Riemann integral fails for functions with many discontinuities, for unbounded functions, and under pointwise limits. Measure theory is built to repair all three.
  - A σ-algebra $\mathcal{S}$ on $X$ contains $\varnothing$ and is closed under complements and countable unions. Closure under countable intersections and set differences follows from De Morgan's laws.
  - The Borel σ-algebra is the smallest σ-algebra containing the open subsets of $\mathbf{R}$. Every interval, every single point and every countable set is a Borel set.
  - A measure $\mu$ has $\mu(\varnothing) = 0$ and is countably additive on disjoint sets. Monotonicity, subadditivity and the two limit rules (increasing unions, decreasing intersections) are consequences.
  - Lebesgue measure is outer measure restricted to the Borel sets. An interval with endpoints $a < b$ has measure $b - a$ and every countable set has measure $0$.
  - A function $f$ is $\mathcal{S}$-measurable as soon as $f^{-1}((a, \infty)) \in \mathcal{S}$ for every real $a$. Sums, products, compositions with continuous functions and pointwise limits of measurable functions stay measurable.
sources:
  - lectures/Lecture 1 part 1.pdf
  - lectures/Lecture 1 part 2.pdf
  - lectures/Lecture 1 part 1 (revised 2026-10-14).pdf
  - lectures/Lecture 1 part 2 (revised 2026-10-14).pdf
---

## Where this fits

The first block of the course is measure and integration. This lecture sets up the three
objects everything later is built from: a **σ-algebra** (which sets get a size), a
**measure** (what the size is) and a **measurable function** (what can later be
integrated). The integral itself comes in the following lectures.

The lecture notes come in two parts and are extracted from Axler, *Measure, Integration &
Real Analysis*, chapters 1 and 2. Numbers in brackets such as (2.23) are Axler's numbering,
which the notes keep. The notes write $\mathbf{R}$ for the real numbers, $\mathbf{Z}^+$ for
the positive integers, $\mathcal{S}$ for a σ-algebra and $\subset$ for "is a subset of"
(equality allowed).

## Why the Riemann integral is not enough

The Riemann integral has three deficiencies (part 1, p. 1): it cannot handle functions with
many discontinuities, it cannot handle unbounded functions, and it does not work well with
limits.

:::note Not restated in the notes: lower and upper Riemann sums
For a bounded $f$ on $[a, b]$ and a partition $P$ given by $a = x_0 < x_1 < \dots < x_n = b$,

$$L(f, P, [a,b]) = \sum_{j=1}^{n} (x_j - x_{j-1}) \inf_{[x_{j-1}, x_j]} f, \qquad U(f, P, [a,b]) = \sum_{j=1}^{n} (x_j - x_{j-1}) \sup_{[x_{j-1}, x_j]} f .$$

The lower Riemann integral $L(f, [a,b])$ is the supremum of the lower sums over all
partitions, the upper Riemann integral $U(f, [a,b])$ the infimum of the upper sums. $f$ is
**Riemann integrable** when the two agree. These are the definitions from Axler chapter 1
that the examples below use.
:::

### Issue 1: many discontinuities

:::example A function that is not Riemann integrable (1.14)
Define $f : [0,1] \to \mathbf{R}$ by

$$f(x) = \begin{cases} 1 & \text{if } x \text{ is rational,} \\ 0 & \text{if } x \text{ is irrational.} \end{cases}$$

Every interval $[a, b] \subset [0,1]$ with $a < b$ contains a rational and an irrational
number, so $\inf_{[a,b]} f = 0$ and $\sup_{[a,b]} f = 1$. Every lower sum is therefore $0$
and every upper sum is $1$, so $L(f, [0,1]) = 0 \ne 1 = U(f, [0,1])$ and $f$ is not Riemann
integrable.
:::

This is disturbing because there are far fewer rationals than irrationals: $f$ "should"
have integral $0$. Lebesgue measure will make that precise, since the rationals turn out to
have measure $0$.

### Issue 2: unbounded functions

For $f(x) = 1/\sqrt{x}$ on $(0, 1]$ with $f(0) = 0$ (1.15), the supremum of $f$ on the first
subinterval $[x_0, x_1]$ of any partition is $\infty$, so every upper sum is $\infty$. Yet
the area under the graph should be

$$\lim_{a \downarrow 0} \int_a^1 \frac{1}{\sqrt{x}}\, dx = \lim_{a \downarrow 0} \left( 2 - 2\sqrt{a} \right) = 2 .$$

Calculus patches this by *defining* the integral as that limit (an improper integral). The
patch does not scale. Take a sequence $r_1, r_2, \dots$ listing every rational in $(0,1)$
exactly once, put $f_k(x) = 1/\sqrt{x - r_k}$ for $x > r_k$ and $f_k(x) = 0$ otherwise, and
define $f = \sum_{k=1}^{\infty} f_k / 2^k$ (1.16). Every open subinterval of $[0,1]$
contains some $r_k$, so $f$ is unbounded on every subinterval and no improper-integral trick
can be applied anywhere. Still, the area under each $f_k$ is $2\sqrt{1 - r_k} < 2$, so the
area under $f$ ought to be less than $\sum_k 2/2^k = 2$ rather than undefined.

### Issue 3: limits

With the same kind of enumeration $r_1, r_2, \dots$ of the rationals in $[0,1]$, let $f_k$
be $1$ on $\{r_1, \dots, r_k\}$ and $0$ elsewhere (1.17). Each $f_k$ is Riemann integrable
with $\int_0^1 f_k = 0$, because it differs from the zero function at finitely many points.
But $f_k(x) \to f(x)$ for every $x$, where $f$ is the function of 1.14, which is not Riemann
integrable. So a pointwise limit of Riemann integrable functions, all bounded by $1$, need
not be Riemann integrable.

:::theorem Interchanging the Riemann integral and a limit (1.18)
Let $a < b$ and $M$ be real, and let $f_1, f_2, \dots$ be Riemann integrable functions on
$[a,b]$ with $\lvert f_k(x) \rvert \le M$ for all $k$ and all $x$. Suppose
$f(x) = \lim_{k \to \infty} f_k(x)$ exists for each $x \in [a,b]$. **If $f$ is Riemann
integrable**, then

$$\int_a^b f = \lim_{k \to \infty} \int_a^b f_k .$$
:::

The result has two flaws (part 1, p. 3). The hypothesis that the limit $f$ is Riemann
integrable should follow from the others, and 1.17 shows it does not. And its proof is
harder than it should be; a cleaner proof of a stronger statement comes later with measure
theory.

:::recall Give a sequence of Riemann integrable functions, all bounded by 1, whose pointwise limit is not Riemann integrable.
List the rationals in $[0,1]$ as $r_1, r_2, \dots$ and let $f_k$ be the indicator of
$\{r_1, \dots, r_k\}$. Each $f_k$ has integral $0$, and $f_k \to$ the indicator of the
rationals, whose lower integral is $0$ and upper integral is $1$.
:::

**The plan.** Extend the notion of the length of an interval to a much larger collection of
subsets of $\mathbf{R}$. That gives measures, and then integration with respect to a
measure.

## σ-algebras

One would like to assign a size to *every* subset of $\mathbf{R}$. That requirement cannot
be met together with countable additivity and translation invariance (part 1, p. 3), so the
size is defined only on a well-behaved collection of sets.

:::definition σ-algebra (2.23)
Let $X$ be a set and $\mathcal{S}$ a set of subsets of $X$. Then $\mathcal{S}$ is a
**σ-algebra on $X$** if

- $\varnothing \in \mathcal{S}$;
- if $E \in \mathcal{S}$, then $X \setminus E \in \mathcal{S}$;
- if $E_1, E_2, \dots$ is a sequence of elements of $\mathcal{S}$, then
  $\bigcup_{k=1}^{\infty} E_k \in \mathcal{S}$.
:::

The **power set** $\mathcal{P}(X)$ is the set of all subsets of $X$. A σ-algebra is a
subcollection $\mathcal{S} \subset \mathcal{P}(X)$ that is closed under complements and
countable unions. It need not contain every subset.

:::example A σ-algebra on a finite set
Let $X = \{1, 2, 3\}$, so $\mathcal{P}(X)$ has $2^3 = 8$ elements. The collection
$\mathcal{S} = \{\varnothing, \{1\}, \{2,3\}, X\}$ is a σ-algebra: the complement of
$\{1\}$ is $\{2,3\}$ and the other way round, $\varnothing$ and $X$ are complements of each
other, and any union of members is again a member.

By contrast $\{\varnothing, \{1\}, \{2\}, X\}$ is not: the complement $\{2,3\}$ of $\{1\}$
is missing. (The second collection is not in the notes; it is here to show a failure.)
:::

Three standard examples on any set $X$ (2.24):

- $\{\varnothing, X\}$, the smallest possible;
- $\mathcal{P}(X)$, the largest possible;
- all $E \subset X$ such that $E$ is countable or $X \setminus E$ is countable.

:::theorem σ-algebras are closed under countable intersection (2.25)
Let $\mathcal{S}$ be a σ-algebra on $X$. Then

1. $X \in \mathcal{S}$;
2. if $D, E \in \mathcal{S}$, then $D \cup E$, $D \cap E$ and $D \setminus E$ are in
   $\mathcal{S}$;
3. if $E_1, E_2, \dots \in \mathcal{S}$, then $\bigcap_{k=1}^{\infty} E_k \in \mathcal{S}$.
:::

:::proof
The notes state this without proof; the argument is short.

1. $X = X \setminus \varnothing$, a complement of a member.
2. $D \cup E$ is the union of the sequence $D, E, \varnothing, \varnothing, \dots$. By De
   Morgan, $D \cap E = X \setminus \big( (X \setminus D) \cup (X \setminus E) \big)$. And
   $D \setminus E = D \cap (X \setminus E)$.
3. By De Morgan, $\bigcap_{k} E_k = X \setminus \bigcup_{k} (X \setminus E_k)$: complements,
   a countable union, then a complement again.
:::

The same laws run backwards: a collection that contains $\varnothing$ and is closed under
complements and countable *intersections* is a σ-algebra.

:::definition Measurable space, measurable set (2.26)
A **measurable space** is a pair $(X, \mathcal{S})$ with $\mathcal{S}$ a σ-algebra on $X$.
An element of $\mathcal{S}$ is an **$\mathcal{S}$-measurable set**, or just a measurable
set.
:::

For example, take $X = \mathbf{R}$ and $\mathcal{S}$ the countable-or-co-countable sets. The
rationals $\mathbf{Q}$ are $\mathcal{S}$-measurable (countable). The positive reals are
not: neither they nor their complement is countable.

## The smallest σ-algebra containing a collection

:::theorem Smallest σ-algebra containing a collection of subsets (2.27)
Let $X$ be a set and $\mathcal{A}$ a set of subsets of $X$. The intersection of all
σ-algebras on $X$ that contain $\mathcal{A}$ is a σ-algebra on $X$.
:::

:::proof
There is at least one σ-algebra containing $\mathcal{A}$, namely $\mathcal{P}(X)$, so the
intersection is over a non-empty family. Call it $\mathcal{S}$.

- $\varnothing$ is in each σ-algebra of the family, hence in $\mathcal{S}$.
- If $E \in \mathcal{S}$, then $E$ is in each σ-algebra of the family, so $X \setminus E$ is
  too, hence $X \setminus E \in \mathcal{S}$.
- If $E_1, E_2, \dots \in \mathcal{S}$, each $E_k$ is in each σ-algebra of the family, so
  $\bigcup_k E_k$ is too, hence $\bigcup_k E_k \in \mathcal{S}$.
:::

This intersection is called the **smallest σ-algebra containing $\mathcal{A}$**, or the
σ-algebra *generated* by $\mathcal{A}$, written $\sigma(\mathcal{A})$. "Smallest" is
literal: it is contained in every σ-algebra that contains $\mathcal{A}$.

Examples (2.28):

- $X$ any set, $\mathcal{A} = \{\{x\} : x \in X\}$ (all singletons). Then
  $\sigma(\mathcal{A})$ is the countable-or-co-countable σ-algebra.
- $X = \mathbf{R}$, $\mathcal{A} = \{(0,1), (0,\infty)\}$. Then
  $$\sigma(\mathcal{A}) = \big\{ \varnothing,\ (0,1),\ (0,\infty),\ (-\infty,0] \cup [1,\infty),\ (-\infty,0],\ [1,\infty),\ (-\infty,1),\ \mathbf{R} \big\} .$$

:::example Worked: $X = [0,1]$, $\mathcal{A} = \{(0, \tfrac12), (\tfrac12, 1)\}$
The notes leave this one as an exercise. The two generators are disjoint, and what they
leave uncovered is $R = \{0, \tfrac12, 1\}$. The three sets $(0,\tfrac12)$, $(\tfrac12,1)$
and $R$ are disjoint and cover $X$. Every member of $\sigma(\mathcal{A})$ is a union of
some of these three blocks, and every such union must be a member, so there are $2^3 = 8$:

$$\varnothing,\quad (0,\tfrac12),\quad (\tfrac12,1),\quad \{0,\tfrac12,1\},\quad (0,\tfrac12) \cup (\tfrac12,1),\quad [0,\tfrac12] \cup \{1\},\quad \{0\} \cup [\tfrac12,1],\quad [0,1] .$$
:::

:::tip Finite generated σ-algebras: find the blocks
Not in the notes, but it is how both examples above are computed. When $\mathcal{A}$ is a
finite collection, cut $X$ into the smallest disjoint pieces that the generators and their
complements distinguish. With $m$ non-empty pieces, $\sigma(\mathcal{A})$ consists of all
$2^m$ unions of pieces. For $\{(0,1), (0,\infty)\}$ the pieces are $(-\infty,0]$, $(0,1)$
and $[1,\infty)$, giving the eight sets listed.
:::

## Borel sets

:::definition Borel σ-algebra on $\mathbf{R}$ (2.29)
The smallest σ-algebra on $\mathbf{R}$ containing all open subsets of $\mathbf{R}$ is the
**Borel σ-algebra**. Its elements are the **Borel sets**.
:::

More generally, for a metric or topological space $X$ the σ-algebra generated by the open
sets (equivalently, by the closed sets) is the Borel σ-algebra $\mathcal{B}_X$ (the notes
quote this from Folland, section 1.2).

:::theorem $\mathcal{B}_{\mathbf{R}}$ is generated by each of the following
1. the open intervals $(a, b)$;
2. the closed intervals $[a, b]$;
3. the half-open intervals $(a, b]$, or the half-open intervals $[a, b)$;
4. the open rays $(a, \infty)$, or the open rays $(-\infty, a)$;
5. the closed rays $[a, \infty)$, or the closed rays $(-\infty, a]$.
:::

A subset $U \subset \mathbf{R}$ is **open** if around every point of $U$ some open interval
lies entirely inside $U$. Every open subset of $\mathbf{R}$ is a union of a *sequence* of
open intervals, which is why open intervals alone generate all Borel sets (part 1, p. 6).

### Why every interval is a Borel set

| Interval | Notation | Open or closed | Why it is Borel |
|---|---|---|---|
| Open interval, open ray | $(a,b)$, $(a,\infty)$, $(-\infty,b)$ | open | It is an open set |
| Closed ray | $[a,\infty)$, $(-\infty,b]$ | closed | Complement of an open ray: $[a,\infty) = \mathbf{R} \setminus (-\infty,a)$ |
| Closed interval | $[a,b]$ | closed | Intersection of two closed rays: $[a,\infty) \cap (-\infty,b]$ |
| Single point | $\{a\}$ | closed | $\bigcap_{n=1}^{\infty} \left( a - \tfrac1n,\ a + \tfrac1n \right)$ |
| Half-open | $[a,b)$, $(a,b]$ | neither | $[a,b) = \bigcap_{n=1}^{\infty} \left( a - \tfrac1n,\ b \right)$ and $(a,b] = \bigcap_{n=1}^{\infty} \left( a,\ b + \tfrac1n \right)$ |
| Whole line | $\mathbf{R}$ | both | 2.25, part 1 |

Each row uses only complements and countable unions or intersections of sets already known
to be Borel. Alternatively $[a,b) = [a,b] \setminus \{b\}$ by closure under set difference.

The same argument covers any **countable set**: it is a countable union of single points.
In particular $\mathbf{Q}$ is a Borel set.

:::warning Not every subset of $\mathbf{R}$ is Borel
Non-Borel sets exist, but constructing one needs more than complements and countable
unions. They are rare: essentially every set met in this course is Borel (part 1, p. 7).
:::

:::recall Is the set of irrational numbers in [0, 1] a Borel set?
Yes. $[0,1]$ is Borel (closed interval), $\mathbf{Q}$ is Borel (countable union of points),
and the irrationals in $[0,1]$ are $[0,1] \setminus \mathbf{Q}$. A σ-algebra is closed
under set difference.
:::

## Measures

:::definition Measure (2.54)
Let $\mathcal{S}$ be a σ-algebra on $X$. A **measure** on $(X, \mathcal{S})$ is a function
$\mu : \mathcal{S} \to [0, \infty]$ such that $\mu(\varnothing) = 0$ and

$$\mu\Big( \bigcup_{k=1}^{\infty} E_k \Big) = \sum_{k=1}^{\infty} \mu(E_k)$$

for every *disjoint* sequence $E_1, E_2, \dots$ of sets in $\mathcal{S}$.
:::

The second condition is **countable additivity**; it is what makes the limit theorems
work. It implies *finite* additivity: for disjoint $E_1, \dots, E_n$ apply it to the
sequence $E_1, \dots, E_n, \varnothing, \varnothing, \dots$ and use $\mu(\varnothing) = 0$.
Note that $\infty$ is an allowed value.

Examples (2.55):

- **Counting measure** on $(X, \mathcal{P}(X))$: $\mu(E)$ is the number of elements of $E$
  if $E$ is finite, and $\infty$ otherwise.
- **Dirac measure** $\delta_c$ for a fixed $c \in X$: $\delta_c(E) = 1$ if $c \in E$ and
  $0$ if $c \notin E$.
- On the countable-or-co-countable σ-algebra: $\mu(E) = 0$ if $E$ is countable and
  $\mu(E) = 3$ if $E$ is uncountable.

:::definition Measure space (2.56)
A **measure space** is a triple $(X, \mathcal{S}, \mu)$: a set, a σ-algebra on it, and a
measure on that σ-algebra.
:::

## Properties of measures

Throughout, $(X, \mathcal{S}, \mu)$ is a measure space and all sets are in $\mathcal{S}$.

:::theorem Order and set difference (2.57)
If $D \subset E$, then

1. $\mu(D) \le \mu(E)$;
2. $\mu(E \setminus D) = \mu(E) - \mu(D)$, provided $\mu(D) < \infty$.
:::

:::proof
$E = D \cup (E \setminus D)$ is a disjoint union, so
$\mu(E) = \mu(D) + \mu(E \setminus D) \ge \mu(D)$. If $\mu(D) < \infty$, subtract $\mu(D)$
from both sides. (If $\mu(D) = \infty$ the subtraction would read $\infty - \infty$, which
is why the condition is there.)
:::

:::theorem Countable subadditivity (2.58)
For any sequence $E_1, E_2, \dots$, disjoint or not,

$$\mu\Big( \bigcup_{k=1}^{\infty} E_k \Big) \le \sum_{k=1}^{\infty} \mu(E_k) .$$
:::

:::proof
Not proved in the notes. Make the sets disjoint: put $D_1 = E_1$ and
$D_k = E_k \setminus (E_1 \cup \dots \cup E_{k-1})$. The $D_k$ are disjoint, have the same
union as the $E_k$, and $D_k \subset E_k$. So
$\mu(\bigcup_k E_k) = \sum_k \mu(D_k) \le \sum_k \mu(E_k)$ by countable additivity and
2.57.
:::

:::theorem Measure of an increasing union (2.59)
If $E_1 \subset E_2 \subset \cdots$, then

$$\mu\Big( \bigcup_{k=1}^{\infty} E_k \Big) = \lim_{k \to \infty} \mu(E_k) .$$
:::

:::proof
If some $\mu(E_k) = \infty$ both sides are $\infty$, so assume all are finite. Put
$E_0 = \varnothing$. The rings $E_j \setminus E_{j-1}$ are disjoint and their union is
$\bigcup_k E_k$. Hence

$$\mu\Big( \bigcup_{k=1}^{\infty} E_k \Big) = \sum_{j=1}^{\infty} \mu(E_j \setminus E_{j-1}) = \lim_{k \to \infty} \sum_{j=1}^{k} \big( \mu(E_j) - \mu(E_{j-1}) \big) = \lim_{k \to \infty} \mu(E_k) .$$

The middle step is 2.57; the last is a telescoping sum.
:::

:::theorem Measure of a decreasing intersection (2.60)
If $E_1 \supset E_2 \supset \cdots$ **and $\mu(E_1) < \infty$**, then

$$\mu\Big( \bigcap_{k=1}^{\infty} E_k \Big) = \lim_{k \to \infty} \mu(E_k) .$$
:::

:::proof
By De Morgan, $E_1 \setminus \bigcap_k E_k = \bigcup_k (E_1 \setminus E_k)$, and the sets
$E_1 \setminus E_k$ increase with $k$. By 2.59,
$\mu(E_1 \setminus \bigcap_k E_k) = \lim_k \mu(E_1 \setminus E_k)$. Apply 2.57, part 2, to
both sides (allowed because everything is inside $E_1$, which has finite measure):

$$\mu(E_1) - \mu\Big( \bigcap_{k} E_k \Big) = \mu(E_1) - \lim_{k \to \infty} \mu(E_k) .$$

Cancel the finite number $\mu(E_1)$.
:::

:::pitfall Dropping $\mu(E_1) < \infty$
The notes say the hypothesis "cannot be deleted in general". A standard counterexample,
not in the notes: with Lebesgue measure take $E_k = [k, \infty)$. Each has measure
$\infty$, the sets decrease, and their intersection is empty, with measure $0 \ne \infty$.
:::

:::theorem Measure of a union (2.61)
If $\mu(D \cap E) < \infty$, then $\mu(D \cup E) = \mu(D) + \mu(E) - \mu(D \cap E)$.
:::

:::proof
$D \cup E$ is the disjoint union of $D \setminus (D \cap E)$, $E \setminus (D \cap E)$ and
$D \cap E$. Add the three measures and use 2.57, part 2, on the first two:

$$\mu(D \cup E) = \big( \mu(D) - \mu(D \cap E) \big) + \big( \mu(E) - \mu(D \cap E) \big) + \mu(D \cap E) .$$
:::

## Lebesgue measure

Measures so far are abstract. Now the specific one on $\mathbf{R}$ that extends length.

:::definition Length of an open interval (2.1)
$$\ell(I) = \begin{cases} b - a & \text{if } I = (a, b) \text{ with } a < b, \\ 0 & \text{if } I = \varnothing, \\ \infty & \text{if } I = (-\infty, a),\ (a, \infty) \text{ or } (-\infty, \infty). \end{cases}$$
:::

The size of a set $A \subset \mathbf{R}$ should be at most the total length of any sequence
of open intervals that covers it. Take the best such bound:

:::definition Outer measure (2.2)
$$\lvert A \rvert = \inf \Big\{ \sum_{k=1}^{\infty} \ell(I_k) \ :\ I_1, I_2, \dots \text{ are open intervals with } A \subset \bigcup_{k=1}^{\infty} I_k \Big\} .$$
:::

:::theorem Countable sets have outer measure 0 (2.4)
Every countable subset of $\mathbf{R}$ has outer measure $0$.
:::

:::proof
Let $A = \{a_1, a_2, \dots\}$ and $\varepsilon > 0$. Cover the $k$-th point by

$$I_k = \Big( a_k - \frac{\varepsilon}{2^k},\ a_k + \frac{\varepsilon}{2^k} \Big), \qquad \ell(I_k) = \frac{2\varepsilon}{2^k} .$$

The $I_k$ cover $A$ and $\sum_k \ell(I_k) = 2\varepsilon \sum_k 2^{-k} = 2\varepsilon$, so
$\lvert A \rvert \le 2\varepsilon$. Since $\varepsilon$ was arbitrary,
$\lvert A \rvert = 0$.
:::

In particular $\lvert \mathbf{Q} \rvert = 0$ even though $\mathbf{Q}$ is dense in
$\mathbf{R}$. Size in this sense has nothing to do with density. This is the precise form
of "far fewer rationals" from issue 1.

Outer measure agrees with length on intervals: $\lvert [a, b] \rvert = b - a$ (2.14). But
it is **not** finitely additive on arbitrary subsets, so it is not a measure on
$(\mathbf{R}, \mathcal{P}(\mathbf{R}))$. The fix is to restrict it to the Borel sets. The
proof needs a chain of preliminary results that the notes omit (Axler, section 2D).

:::theorem Outer measure is a measure on the Borel sets (2.68)
Outer measure is a measure on $(\mathbf{R}, \mathcal{B})$, where $\mathcal{B}$ is the
σ-algebra of Borel subsets of $\mathbf{R}$.
:::

:::definition Lebesgue measure (2.69)
**Lebesgue measure** is the measure on $(\mathbf{R}, \mathcal{B})$ that assigns to each
Borel set its outer measure.
:::

So the Lebesgue measure of a set *is* its outer measure; the name is reserved for Borel
sets (and the slightly larger class of Lebesgue measurable sets), where countable
additivity is guaranteed.

:::example Computing Lebesgue measures (part 2, pp. 4 to 5)
- $[a,b]$, $(a,b)$, $[a,b)$ and $(a,b]$ all have measure $b - a$: they differ by at most
  two points, a set of measure $0$.
- A single point and any countable set have measure $0$. So $\mathbf{Q}$ has measure $0$,
  and this is a statement about Lebesgue measure because $\mathbf{Q}$ is Borel.
- $(1,3) \cup (7,10)$ has measure $2 + 3 = 5$ by finite additivity.
- Translation invariance: $\lvert t + A \rvert = \lvert A \rvert$ for every real $t$.
- A Vitali-type construction (Axler 2.18) gives a set that is not Borel; definition 2.69
  assigns it no Lebesgue measure.
:::

:::recall What is the Lebesgue measure of the irrational numbers in [0, 1]?
$1$. The rationals in $[0,1]$ are a countable set of measure $0$, sitting inside $[0,1]$ of
measure $1$, so by 2.57 the difference has measure $1 - 0 = 1$.
:::

## Measurable functions

:::definition Measurable function (2.35)
Let $(X, \mathcal{S})$ be a measurable space. A function $f : X \to \mathbf{R}$ is
**$\mathcal{S}$-measurable** if $f^{-1}(B) \in \mathcal{S}$ for every Borel set
$B \subset \mathbf{R}$.
:::

Here $f^{-1}(B) = \{x \in X : f(x) \in B\}$ is the inverse image; $f$ need not be
invertible. How many functions are measurable depends on how rich $\mathcal{S}$ is (2.36):

- If $\mathcal{S} = \{\varnothing, X\}$, only the constant functions are measurable.
- If $\mathcal{S} = \mathcal{P}(X)$, every function is measurable.
- If $\mathcal{S} = \{\varnothing, (-\infty,0), [0,\infty), \mathbf{R}\}$, then $f$ is
  measurable exactly when it is constant on $(-\infty,0)$ and constant on $[0,\infty)$.

:::note Not in the notes: the same idea on three points
On $X = \{1,2,3\}$ with $\mathcal{S} = \{\varnothing, \{1\}, \{2,3\}, X\}$, a function is
measurable exactly when $f(2) = f(3)$. If $f(2) \ne f(3)$, the inverse image of the single
point $\{f(2)\}$ contains $2$ but not $3$, and no member of $\mathcal{S}$ does that. A
σ-algebra records which points the function is allowed to tell apart.
:::

Checking every Borel set would be hopeless. One family of rays is enough:

:::theorem Condition for a measurable function (2.39)
If $f^{-1}\big( (a, \infty) \big) \in \mathcal{S}$ for all $a \in \mathbf{R}$, then $f$ is
$\mathcal{S}$-measurable.
:::

The reason, which the notes do not spell out: the sets $B$ with $f^{-1}(B) \in \mathcal{S}$
form a σ-algebra on $\mathbf{R}$ (this is [last year's homework problem](problems:sigma-algebras-and-measures#sam-p3)),
it contains the rays $(a, \infty)$, and those rays generate the Borel sets.

:::definition Borel measurable function (2.40)
For $X \subset \mathbf{R}$, a function $f : X \to \mathbf{R}$ is **Borel measurable** if
$f^{-1}(B)$ is a Borel set for every Borel set $B \subset \mathbf{R}$.
:::

:::theorem Every continuous function is Borel measurable (2.41)
Every continuous real-valued function defined on a Borel subset of $\mathbf{R}$ is Borel
measurable.
:::

So polynomials, $\sin$, $\cos$, $\exp$ and everything else from calculus are measurable.
Continuity is far stronger than measurability.

:::theorem Composition of measurable functions (2.44)
Let $f : X \to \mathbf{R}$ be $\mathcal{S}$-measurable and let $g$ be a real-valued Borel
measurable function defined on a subset of $\mathbf{R}$ that contains the range of $f$.
Then $g \circ f$ is $\mathcal{S}$-measurable.
:::

:::proof
For a Borel set $B$, $(g \circ f)^{-1}(B) = f^{-1}\big( g^{-1}(B) \big)$. The inner set
$g^{-1}(B)$ is Borel because $g$ is Borel measurable, so its inverse image under $f$ is in
$\mathcal{S}$ because $f$ is $\mathcal{S}$-measurable.
:::

Consequence (2.45): if $f$ is measurable then so are $-f$, $\tfrac12 f$, $\lvert f \rvert$
and $f^2$, each being $g \circ f$ with the continuous $g(x) = -x$, $\tfrac12 x$,
$\lvert x \rvert$, $x^2$.

:::theorem Algebraic operations (2.46)
If $f, g : X \to \mathbf{R}$ are $\mathcal{S}$-measurable, then so are $f + g$, $f - g$ and
$fg$, and so is $f/g$ when $g(x) \ne 0$ for all $x \in X$.
:::

:::theorem Limit of measurable functions (2.48)
If $f_1, f_2, \dots$ are $\mathcal{S}$-measurable and $f(x) = \lim_{k \to \infty} f_k(x)$
exists for every $x \in X$, then $f$ is $\mathcal{S}$-measurable.
:::

This is exactly what Riemann integrability lacked in 1.17: the measurable functions are
closed under pointwise limits.

## Simple functions

:::definition Simple function (2.88)
A function is **simple** if it takes only finitely many values.
:::

If $f : X \to \mathbf{R}$ is simple with distinct non-zero values $c_1, \dots, c_n$, then

$$f = c_1 \chi_{E_1} + \dots + c_n \chi_{E_n}, \qquad E_k = f^{-1}(\{c_k\}),$$

where $\chi_E$ is the characteristic function of $E$ ($1$ on $E$, $0$ elsewhere; also
written $1_E$ and called the indicator function). $\chi_E$ itself is measurable if and only
if $E \in \mathcal{S}$, and such an $f$ is $\mathcal{S}$-measurable if and only if
$E_1, \dots, E_n \in \mathcal{S}$.

:::example Characteristic and simple functions (revised notes)
On $\mathbf{R}$ with the Borel sets, $\chi_{[1,2]}$ is measurable because $[1,2]$ is Borel.
The function $f = 3\chi_{[0,2)} + \chi_{[1,4)}$ equals $3$ on $[0,1)$, $4$ on $[1,2)$, $1$
on $[2,4)$ and $0$ elsewhere, so it is simple, with
$f = 3\chi_{[0,1)} + 4\chi_{[1,2)} + 1\chi_{[2,4)}$. The sets are disjoint intervals,
hence Borel, so $f$ is measurable.
:::

:::theorem Approximation by simple functions
For each measurable $f : A \to [0, +\infty)$ with $A \subset X$ there is a sequence of
measurable simple functions $f_n : A \to [0, +\infty)$ with

$$0 \le f_1 \le f_2 \le \dots \le f \qquad \text{and} \qquad \lim_{n \to \infty} f_n(x) = f(x) \ \text{ for every } x \in A .$$

If $f$ is bounded, the convergence is uniform on $A$.
:::

The revised notes draw the construction for $f(x) = x^2$ on $[0,1]$:
$f_k = \lfloor 2^k f \rfloor / 2^k$, which rounds $f$ down to multiples of $2^{-k}$. It is
written out in [](lecture:02-the-lebesgue-integral#simple-functions), where these
functions become the first things to integrate.

## What an exam wants

:::paper Show that a collection $\mathcal{S}$ is a σ-algebra
Write the three checks as three labelled lines and finish each with "$\in \mathcal{S}$".

1. $\varnothing \in \mathcal{S}$ because …
2. Let $E \in \mathcal{S}$. Then $X \setminus E$ … hence $X \setminus E \in \mathcal{S}$.
3. Let $E_1, E_2, \dots \in \mathcal{S}$. Then $\bigcup_k E_k$ … hence
   $\bigcup_k E_k \in \mathcal{S}$.

To show a collection is **not** a σ-algebra, exhibit one concrete set (or sequence) that
breaks one condition.
:::

:::paper Show that a set is Borel
Write the set using open intervals (or sets already shown Borel), complements, and
countable unions or intersections, and name the closure property at each step. Example:
$\{a\} = \bigcap_{n} (a - \tfrac1n, a + \tfrac1n)$, a countable intersection of open sets,
so Borel by 2.25.
:::

:::paper State the definition of a measure
Four ingredients, none optional: the domain is a σ-algebra $\mathcal{S}$; values lie in
$[0, \infty]$; $\mu(\varnothing) = 0$; and
$\mu(\bigcup_k E_k) = \sum_k \mu(E_k)$ for every **disjoint** sequence in $\mathcal{S}$.
:::

## Where next

- The integral built on all of this: [](lecture:02-the-lebesgue-integral).
- Drill: [](deck:measure-foundations), and every proof of this lecture:
  [](deck:measure-foundations-proofs).
- How these proofs are put together, move by move: [](guide:proof-toolkit).
- Practice: [](problems:sigma-algebras-and-measures), five problems from last year's
  measure theory homework that need only this lecture.
- Formulas to know cold: the measure section of [the sheet](formulas).
- The shape of the semester: [](guide:course-map).
