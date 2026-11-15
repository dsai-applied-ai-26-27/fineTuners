---
title: How the proofs are built
topics: [measure]
summary: The dozen moves that every proof of lectures 1 to 3 is made of, each with the results that use it, then an index of every proof with the card that drills it.
---

## Short answer

The proofs of the measure unit are short, and they repeat. About a dozen moves cover all of
them. Learn the moves and most proofs become "which move, applied to what". The cards
that drill each proof are in three decks: [](deck:measure-foundations-proofs),
[](deck:lebesgue-integral-proofs) and [](deck:lp-spaces-proofs).

Proofs marked *not in the notes* are standard proofs of results the notes state without
proof. They are there to make the theory hang together; the ones in the notes come first
when time is short.

## The moves

### 1. Check the axioms one by one; refute with one example

To show a collection is a σ-algebra, check $\varnothing$, complements and countable
unions, each on its own line. To show a function is a measure, check $\mu(\varnothing) = 0$
and countable additivity on a **disjoint** sequence. To show something is **not** a
σ-algebra or a measure, one concrete set or sequence that breaks one condition is the
whole proof.

Used in: the countable-or-co-countable σ-algebra
([card](card:measure-cocountable-sigma-proof)), the finite-or-co-finite sets
([card](card:measure-cofinite-not-sigma)), the 0-or-3 measure
([card](card:measure-cocountable-measure-proof)), the restricted measure
$\mu(A \cap E)$ ([card](card:measure-restriction-proof)).

### 2. De Morgan: trade unions for intersections

$$X \setminus \bigcup_{k} E_k = \bigcap_{k} (X \setminus E_k)$$

Closure under complements and countable unions gives closure under countable
intersections (2.25). Inside a set of finite measure, it turns a decreasing intersection
into an increasing union (2.60).

### 3. Make a sequence disjoint

Countable additivity only speaks about disjoint sets. Replace $E_1, E_2, \dots$ by
$D_k = E_k \setminus (E_1 \cup \dots \cup E_{k-1})$: same union, $D_k \subset E_k$, and
disjoint. For an increasing sequence the $D_k$ are the rings $E_k \setminus E_{k-1}$.

Used in: subadditivity 2.58, increasing unions 2.59, the union of two sets 2.61.

### 4. Inverse images commute with every set operation

$$f^{-1}(Y \setminus E) = X \setminus f^{-1}(E), \qquad f^{-1}\Big(\bigcup_k E_k\Big) = \bigcup_k f^{-1}(E_k), \qquad (g \circ f)^{-1}(B) = f^{-1}\big(g^{-1}(B)\big).$$

So a σ-algebra pulled back or pushed forward along a function is again a σ-algebra
([card](card:measure-pushforward-proof)), a composition of measurable functions is
measurable (2.44), and $\chi_E^{-1}(B)$ is one of four sets
([card](card:leb-chi-measurable-proof)).

### 5. The good sets form a σ-algebra

To prove that **every** set of $\sigma(\mathcal{A})$ has a property, show that (a) the sets
with the property form a σ-algebra and (b) the generators in $\mathcal{A}$ have it. Then
$\sigma(\mathcal{A})$ is inside, because it is the smallest σ-algebra containing
$\mathcal{A}$.

This is the proof of the measurability test 2.39 ([card](card:measure-criterion-proof)):
the sets $B$ with $f^{-1}(B) \in \mathcal{S}$ form a σ-algebra that contains the rays,
hence all Borel sets. The same smallest-σ-algebra argument gives **two inclusions** when
two families generate the same σ-algebra: $\sigma(\mathcal{E}) \subset \mathcal{B}$
because the generators are Borel, and $\mathcal{B} \subset \sigma(\mathcal{E})$ because the
open sets can be built from $\mathcal{E}$ ([card](card:measure-rays-generate-proof)).

### 6. Pay $\varepsilon / 2^k$ for the $k$-th item

Countably many things can each be made small with a finite total budget, because
$\sum_k \varepsilon/2^k = \varepsilon$. That is the proof that a countable set has outer
measure $0$ ([card](card:measure-countable-zero)).

### 7. A margin $\frac1j$ keeps a strict inequality

Limits keep only $\ge$. To keep $>$, leave a margin and take a countable union over it:

$$\{f > a\} = \bigcup_{j} \{f \ge a + \tfrac1j\} \quad\text{and}\quad \{\lvert f \rvert > 0\} = \bigcup_n \{\lvert f \rvert > \tfrac1n\}.$$

Used in: limits of measurable functions 2.48 ([card](card:leb-limit-proof)), the essential
supremum is attained ([card](card:lp-ess-sup-attained-proof)), and $\|f\|_1 = 0$ forces
$f = 0$ almost everywhere ([card](card:lp-l1-zero-proof)).

### 8. Put a rational in between

A condition on a sum, $f(x) + g(x) > a$, becomes a countable union over $r \in \mathbf{Q}$
of conditions on each function: $f(x) > r$ and $g(x) > a - r$. The rationals are dense
(so some $r$ fits) and countable (so the union stays in $\mathcal{S}$). This is 2.46
([card](card:leb-sum-measurable-proof)).

### 9. Squeeze an integral between two inequalities

The integral is a supremum of lower Lebesgue sums. **One** good partition proves $\ge$;
a bound on **every** partition proves $\le$.

Used in: $\int \chi_E = \mu(E)$ ([card](card:leb-chi-integral)), the integral of a simple
function 3.7 ([card](card:leb-simple-integral-proof)), order 3.8
([card](card:leb-order)), and the null-set lemma ([card](card:leb-null-set-proof)).

### 10. Simple functions first, then monotone limits

Prove a statement for simple functions, where the integral is a finite sum. Approximate
a general $f \ge 0$ from below by simple functions ([card](card:leb-dyadic)) and pass to
the limit with the Monotone Convergence Theorem. Real-valued $f$ then follow through
$f = f^+ - f^-$.

Used in: additivity 3.16 ([card](card:leb-additivity-proof)). The Monotone Convergence
Theorem itself ([card](card:leb-mct-proof)) needs only the rule for increasing unions,
2.59, applied to the sets where $f_k$ has climbed above a level.

### 11. One integrable roof

When a limit has to pass through an integral and the sequence is not increasing, find a
single $g$ with $\lvert f_k \rvert \le g$ for all $k$ and $\int g < \infty$: the
Dominated Convergence Theorem. Fatou's lemma, applied to $g + f_k$ and $g - f_k$, proves
it ([card](card:leb-dct-proof)). In lecture 3 the roof is $\lvert f \rvert$ itself
([card](card:lp-truncation-proof)). How to find a roof in practice is in
[](guide:computing-integrals).

### 12. Hölder with a chosen pair

Hölder's inequality is only as good as the two functions you feed it.

| Goal | Feed Hölder | Exponents |
|---|---|---|
| $L^q \subset L^p$ on a finite measure space (7.10) | $\lvert f \rvert^p$ and the constant $1$ | $\frac{q}{p}$ and $\frac{q}{q-p}$ |
| Minkowski (6.5) | $\lvert f \rvert$ and $\lvert f + g \rvert^{p-1}$ | $p$ and $q$, with $(p-1)q = p$ |
| Products converge in $L^1$ | $\lvert g \rvert$ and $\lvert f_n - f \rvert$ | $2$ and $2$ |

Hölder itself is Young's inequality $ab \le \frac{a^p}{p} + \frac{b^q}{q}$ applied to the
functions scaled to norm $1$ ([card](card:lp-young-proof),
[card](card:lp-holder-proof)).

### 13. Cut off, compute, pass to the limit

For an unbounded function or domain: multiply by $\chi_{[1/n,1]}$ or $\chi_{[0,n)}$, check
monotone convergence, compute the bounded piece as a Riemann integral (3.34), take the
limit. The same steps decide whether $f \in L^p$ ([card](card:lp-power-rule-proof)). The
full recipe is in [](guide:computing-integrals).

## Every proof, and its idea

| Result | The idea in one line | Card |
|---|---|---|
| 2.25 $X$, finite unions, intersections, differences | Pad with $\varnothing$; De Morgan | [card](card:measure-sigma-basic-ops-proof) |
| 2.25 countable intersections | De Morgan, complements twice | [card](card:measure-sigma-intersection) |
| 2.24 countable-or-co-countable is a σ-algebra | A complement swaps the cases; a co-countable member makes the union co-countable | [card](card:measure-cocountable-sigma-proof) |
| Finite-or-co-finite is not a σ-algebra | Every other point of a sequence | [card](card:measure-cofinite-not-sigma) |
| Open rays generate $\mathcal{B}$ | Two inclusions; build $(a,b)$ from rays | [card](card:measure-rays-generate-proof) |
| Finite additivity | Pad with empty sets | [card](card:measure-finite-additivity) |
| 2.55 the 0-or-3 measure *(not in the notes)* | Two co-countable sets always meet | [card](card:measure-cocountable-measure-proof) |
| Restricted measure $\mu(A \cap E)$ | Intersection distributes over unions | [card](card:measure-restriction-proof) |
| 2.57 order and difference | $E = D \cup (E \setminus D)$ | [card](card:measure-monotone-difference-proof) |
| 2.58 subadditivity | Make the sets disjoint | [card](card:measure-subadditivity-proof) |
| 2.59 increasing union | Rings, then a telescoping sum | [card](card:measure-increasing-union-proof) |
| 2.60 decreasing intersection | Complements inside $E_1$; finiteness avoids $\infty - \infty$ | [card](card:measure-decreasing-intersection-proof) |
| 2.61 union of two sets | Three disjoint pieces | [card](card:measure-union-proof) |
| 2.4 countable sets are null | $\varepsilon/2^k$ | [card](card:measure-countable-zero) |
| Push-forward σ-algebra | Inverse images commute with set operations | [card](card:measure-pushforward-proof) |
| 2.39 rays suffice | The good sets form a σ-algebra | [card](card:measure-criterion-proof) |
| 2.41 continuous ⇒ Borel measurable *(not in the notes)* | $f^{-1}((a,\infty))$ is $B \cap$ open | [card](card:leb-continuous-borel-proof) |
| 2.44 composition | $(g \circ f)^{-1} = f^{-1} \circ g^{-1}$ | [card](card:leb-composition) |
| 2.46 sums and products *(not in the notes)* | A rational in between; $fg$ from squares | [card](card:leb-sum-measurable-proof) |
| 2.48 pointwise limits | Margin $\frac1j$, from some index on | [card](card:leb-limit-proof) |
| $\chi_E$ measurable iff $E \in \mathcal{S}$ | Four possible inverse images | [card](card:leb-chi-measurable-proof) |
| Approximation by simple functions | Round down to the grid $2^{-k}$ | [card](card:leb-dyadic) |
| 3.4 $\int \chi_E = \mu(E)$ | One partition for $\ge$, every partition for $\le$ | [card](card:leb-chi-integral) |
| 3.7 integral of a simple function | The same squeeze, splitting each piece along the $E_k$ | [card](card:leb-simple-integral-proof) |
| 3.8 order | Compare infima piece by piece | [card](card:leb-order) |
| 3.11 Monotone Convergence *(not in the notes)* | 2.59 on the sets where $f_k > c_j$ | [card](card:leb-mct-proof) |
| 3.16 additivity *(not in the notes)* | Simple functions, then monotone convergence | [card](card:leb-additivity-proof) |
| Null sets do not change integrals *(not in the notes)* | Every lower sum is $0$ | [card](card:leb-null-set-proof) |
| 3.25 bound on $\int_E f$ *(not in the notes)* | $\lvert f \rvert \chi_E \le (\sup_E \lvert f \rvert)\chi_E$ | [card](card:leb-subset-bound-proof) |
| Fatou's lemma *(not in the notes)* | Monotone convergence on $\inf_{j \ge k} g_j$ | [card](card:leb-fatou-proof) |
| 3.31 Dominated Convergence *(not in the notes)* | Fatou on $g + f_k$ and $g - f_k$ | [card](card:leb-dct-proof) |
| 3.43 $\Vert f\Vert _1 = 0$ iff $f = 0$ a.e. *(not in the notes)* | $\frac1n \chi_{\{\lvert f \rvert > 1/n\}} \le \lvert f \rvert$ | [card](card:lp-l1-zero-proof) |
| 7.5 $L^p$ is a vector space | $\lvert f + g \rvert^p \le 2^p(\lvert f \rvert^p + \lvert g \rvert^p)$ | [card](card:lp-vector-space-proof) |
| Essential supremum attained *(not in the notes)* | Margin $\frac1n$, countable union of null sets | [card](card:lp-ess-sup-attained-proof) |
| Young's inequality *(not in the notes)* | $\log$ is concave | [card](card:lp-young-proof) |
| 6.2 Hölder *(not in the notes)* | Normalise, Young, integrate | [card](card:lp-holder-proof) |
| Hölder for $p = 1$, $q = \infty$ | $\lvert g \rvert \le \Vert g\Vert _\infty$ a.e. | [card](card:lp-holder-endpoint-proof) |
| 6.5 Minkowski | Split off one factor, Hölder on the rest, divide | [card](card:lp-minkowski-proof) |
| Triangle inequality for $\Vert \cdot\Vert _\infty$ | Bound outside two null sets | [card](card:lp-minkowski-infty) |
| Powers of $x$ in $L^p$ | Truncate, $s = ap$, compare with $1$ | [card](card:lp-power-rule-proof) |
| 7.10 inclusion on a finite measure space | Hölder against the constant $1$ | [card](card:lp-inclusion-proof) |
| Products converge in $L^1$ | Hölder with $(2,2)$ | [card](card:lp-product) |
| Truncation converges in $L^1$ | Dominated by $\lvert f \rvert$ | [card](card:lp-truncation-proof) |

## Writing a proof in the exam

:::paper How a proof is marked
1. **Say what is to be shown**, in symbols: "Let $E_1, E_2, \dots \in \mathcal{S}$. To show:
   $\bigcap_k E_k \in \mathcal{S}$."
2. **One fact per line, with its reason**: "by closure under complements", "by 2.59",
   "since $\mu(D) < \infty$". The reason is where the marks are.
3. **For a theorem you apply, show each hypothesis** before the conclusion: measurable,
   non-negative, increasing, dominated by an integrable $g$, finite measure.
4. **Close the loop**: end with the statement you set out to prove, and "hence".
:::

:::pitfall Five ways a proof loses marks
- Using additivity on sets that are not disjoint. Make them disjoint first (move 3).
- Subtracting a measure that may be $\infty$. Every $\mu(E \setminus D) = \mu(E) - \mu(D)$
  needs $\mu(D) < \infty$ said aloud.
- Showing only finite unions where countable unions are asked: an algebra is not a
  σ-algebra.
- A dominating function that depends on $n$. The roof must be one $g$ for all $k$.
- Proving one inclusion of a set identity and calling it equality.
:::

Related: [](guide:counterexamples) shows why each hypothesis is there.
