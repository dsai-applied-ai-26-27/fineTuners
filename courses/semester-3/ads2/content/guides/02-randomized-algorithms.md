---
title: 'Randomized algorithms'
number: 2
topics: [randomized]
summary: Where computers get randomness from (pseudorandom generators, seeds, entropy), what makes an algorithm randomized, expected running time and linearity of expectation, Las Vegas against Monte Carlo, and four examples, estimating π, randomized quicksort, randomized selection and Karger's min-cut.
takeaways:
  - Computers are deterministic, so they use pseudorandom number generators, which produce a reproducible sequence from a seed. True randomness comes from physical entropy and is used to seed cryptographic generators.
  - 'A linear congruential generator computes $X_{n+1} = (aX_n + c) \bmod m$: fast but statistically weak. The Mersenne Twister has period $2^{19937} - 1$ and is excellent for simulation but not cryptographically secure.'
  - Randomized algorithms are analysed by expected running time, $E[T] = \sum_i P_i T_i$, and linearity of expectation holds even for dependent variables.
  - Las Vegas algorithms are always correct with random running time; Monte Carlo algorithms have bounded running time and may be wrong with small probability.
  - Randomized quicksort and quickselect pick a random pivot, giving expected $O(n \log n)$ and $O(n)$; the worst case stays $O(n^2)$. Karger's min-cut contracts random edges and is repeated to make failure unlikely.
sources:
  - misc/ADS REVISION.docx
---

## Randomness and distributions

A random process has an outcome that cannot be predicted with certainty, although its
behaviour follows a **probability distribution**. Two matter most: the **uniform**
distribution (all outcomes equally likely, which avoids systematic bias in algorithms) and
the **normal** distribution (values cluster around a mean).

## Random numbers on a deterministic machine

Given the same input and program, a computer always produces the same output, so software
alone cannot produce true randomness. It uses **pseudorandom number generators (PRNGs)**:
deterministic algorithms whose output looks random to statistical tests. Every PRNG starts
from a **seed**, and the seed determines the whole sequence.

**True randomness** comes from physical phenomena: radioactive decay, thermal noise, timing
variations in hardware, even mouse movements and keystroke timing. These are collected into
an **entropy pool**; Linux exposes it through `/dev/random` and `/dev/urandom`.

**Why pseudorandom numbers dominate.** Hardware randomness is slow, expensive and needs
special devices. PRNGs are **fast, portable and reproducible**: the same seed reproduces the
same run, which is what debugging and testing need. Even cryptographic systems use
pseudorandom algorithms; what matters is that they are seeded with good entropy.

### How a PRNG works

Start from $X_0$ and apply a deterministic recurrence

$$X_{n+1} = f(X_n).$$

A good sequence looks **uniformly distributed**, its values are statistically
**independent**, and it has a **long period** before it repeats.

| Generator | Rule | Strengths | Weaknesses |
|---|---|---|---|
| Linear congruential (LCG) | $X_{n+1} = (aX_n + c) \bmod m$ | Simple, very fast | Statistically weak, patterns in higher dimensions, predictable |
| Mersenne Twister | State of 624 32-bit integers, mixed by shifts, XOR and masks | Period $2^{19937} - 1$, excellent statistics; Python's and NumPy's default | **Not cryptographically secure**: enough outputs reveal the state |
| CSPRNG | Seeded from system entropy | Infeasible to predict from observed outputs | Slower; used for passwords, keys, tokens (`os.urandom`, `secrets` in Python) |

:::tip The seed
Same seed, same sequence: controlled seeds for simulations and tests, unpredictable seeds
for cryptography.
:::

## Randomized algorithms

A **randomized algorithm** makes random choices while it runs, so it may follow a different
path on each run with the same input. Randomness can affect its running time, its
correctness, or both.

**Why use them.** A deterministic algorithm can be forced into its worst case by a carefully
chosen "unlucky" input. Randomization makes it very unlikely to hit bad cases consistently,
which often gives better average performance, simpler code and fewer special cases.

### Expected running time

The exact running time is random, so we analyse its **expectation**. If execution path $i$
has probability $P_i$ and running time $T_i$,

$$E[T] = \sum_i P_i T_i .$$

**Linearity of expectation** is the key tool:

$$E[X + Y] = E[X] + E[Y],$$

and it holds **whether or not** $X$ and $Y$ are independent.

### Las Vegas against Monte Carlo

| | Correctness | Running time | Example |
|---|---|---|---|
| **Las Vegas** | Always correct | Random | Randomized quicksort, quickselect |
| **Monte Carlo** | May be wrong with small probability | Fixed (bounded) | Estimating $\pi$, Karger's min-cut, Miller-Rabin |

:::recall Which kind is Karger's algorithm, and why?
Monte Carlo: each run takes a fixed amount of work, but the cut it returns is only the
minimum with some probability.
:::

## Four examples

### Estimating π by Monte Carlo

Sample points uniformly in a square containing an inscribed circle. The fraction landing in
the circle approximates the ratio of areas:

$$\frac{A_{\text{circle}}}{A_{\text{square}}} = \frac{N_{\text{circle}}}{N_{\text{total}}} .$$

For a circle of radius $r$ in a square of side $2r$ the ratio is $\frac{\pi r^2}{4r^2} = \frac{\pi}{4}$,
so $\pi \approx 4\,N_{\text{circle}}/N_{\text{total}}$. The estimate converges as the number
of points grows.

### Randomized quicksort

Quicksort's speed depends on the pivot: bad pivots give very unbalanced partitions and the
worst case $O(n^2)$. Choosing the pivot **uniformly at random** makes bad splits very
unlikely, so the **expected** time is $O(n \log n)$, though the worst case is still $O(n^2)$.

### Randomized selection (quickselect)

Finds the $k$-th smallest element of an unsorted array with a random pivot and partitioning,
recursing only into the side that contains position $k$. A **Las Vegas** algorithm:
always correct, expected time $O(n)$, worst case $O(n^2)$.

### Karger's randomized min-cut

A **cut** splits the vertices of an undirected graph into two non-empty sets; its size is the
number of edges between them. The **minimum cut** has the fewest crossing edges.

1. Pick a random edge and **contract** it: merge its two endpoints into one vertex, keeping
   parallel edges and **removing self-loops**.
2. Repeat until two vertices remain.
3. The edges between them form a candidate cut.

One run succeeds only with low probability, but **repeating** the algorithm and keeping the
smallest cut makes the probability of failure fall **exponentially** with the number of
runs.

## Applications

Game development, cryptography (Miller-Rabin primality testing), Monte Carlo simulation,
graph algorithms and machine learning. The recurring lesson: randomness can improve
performance, simplify design and avoid pathological worst cases, and repetition buys
reliability.

## Where next

- Drill: [](deck:randomized-algorithms).
- Graphs, where Karger's contraction lives: [](guide:03-graphs-and-graph-search).
