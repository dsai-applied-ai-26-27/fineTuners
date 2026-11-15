---
title: 'Dynamic programming'
number: 7
topics: [dp]
summary: What dynamic programming is, why naive recursion on climbing stairs is exponential, the two properties a DP problem needs, states, transitions and base cases, memoization against tabulation, and three classic problems worked through, coin change, longest increasing subsequence and 0/1 knapsack.
takeaways:
  - DP solves a problem from subproblems and stores each subproblem's answer so it is never computed twice, trading memory for time.
  - It needs overlapping subproblems (the same subproblem recurs) and optimal substructure (an optimal solution is built from optimal solutions of subproblems).
  - 'Every DP is four decisions: the state, the transition (recurrence), the base cases, and the evaluation order, top-down with memoization or bottom-up with a table.'
  - 'Climbing stairs: $\text{ways}(n) = \text{ways}(n-1) + \text{ways}(n-2)$, Fibonacci, $O(n)$ with DP instead of exponential.'
  - 'Coin change counts with $dp[i][j] = dp[i-1][j] + dp[i][j - c_i]$; LIS uses $dp[i] = \max(dp[j] + 1)$ over $j < i$ with $a[j] < a[i]$ in $O(n^2)$; 0/1 knapsack uses $dp[i][w] = \max(dp[i-1][w],\ dp[i-1][w - w_i] + v_i)$.'
sources:
  - misc/ADS REVISION.docx
---

## What DP is about

**Dynamic programming** solves a complex problem by breaking it into simpler subproblems and
**reusing** their solutions instead of recomputing them. Many problems that look exponential
become polynomial once the repeated work is found and stored. DP is not one algorithm but a
**paradigm**, like divide and conquer or greedy; what sets it apart is that its subproblems
**overlap**.

## The motivating example: climbing stairs

A staircase has $n$ steps and each move climbs 1 or 2 steps. How many distinct ways reach the
top? Let $\text{ways}(n)$ be that number. Any way to reach step $n$ comes from step $n - 1$ (a
one-step move) or step $n - 2$ (a two-step move), so

$$\text{ways}(n) = \text{ways}(n-1) + \text{ways}(n-2), \qquad \text{ways}(0) = 1,\ \text{ways}(1) = 1$$

(or $\text{ways}(1) = 1$, $\text{ways}(2) = 2$, depending on indexing). This is the
**Fibonacci** recurrence.

### Why naive recursion is exponential

The recursion branches into two calls at almost every level, and the same values,
$\text{ways}(3)$, $\text{ways}(4)$, …, are recomputed in many branches. The number of calls
grows exponentially: $\text{ways}(50)$ would take billions. The cause is **overlapping
subproblems**: the recursion tree contains many identical subtrees.

## When DP applies

1. **Overlapping subproblems.** The same subproblems come up repeatedly in a recursive
   solution ($\text{ways}(k)$ for the same $k$, many times).
2. **Optimal substructure.** An optimal solution is built from optimal solutions to
   subproblems ($\text{ways}(n)$ depends only on $\text{ways}(n-1)$ and $\text{ways}(n-2)$).

A **simple state** helps: here the answer for step $i$ depends only on $i$, a one-dimensional
state.

**The core idea: never solve the same subproblem twice.** Store each result and reuse it.

## Top-down against bottom-up

| | Top-down (memoization) | Bottom-up (tabulation) |
|---|---|---|
| How | Recursive; before computing, check whether the result is stored; otherwise compute, store, return | Start from the base cases and fill a table for increasing sizes |
| Climbing stairs | Exponential becomes $O(n)$ | Compute $\text{ways}(0), \text{ways}(1), \dots, \text{ways}(n)$ in order |
| Pros | Keeps the natural recursive structure | Easier to analyse, predictable memory, no recursion stack |

Both compute the same states, in a different order.

## States, transitions, base cases

- A **state** is the minimal information that fully describes a subproblem: enough to decide
  the next transitions without the full history. For climbing stairs, $dp[i]$ = number of ways
  to reach step $i$.
- A **transition** computes a state from smaller states: the recurrence.
- **Base cases** are the smallest states, known directly; they anchor the table. Wrong or
  missing base cases are among the most common DP bugs.

## Coin change: counting the ways

Given coin denominations (each usable any number of times) and a target $S$, how many ways
form $S$, order not mattering?

**State:** $dp[i][j]$ = number of ways to form sum $j$ using the first $i$ coins.

**Transition:** either exclude coin $i$, or include it (if $c_i \le j$):

$$dp[i][j] = dp[i-1][j] + dp[i][j - c_i].$$

The second term stays in row $i$ because coin $i$ may be used again.

**Base cases:** $dp[i][0] = 1$ (one way to make 0: use no coins); $dp[0][j] = 0$ for $j > 0$.
Fill row by row; the answer is $dp[n][S]$.

:::example Coins 1, 2, 3 and S = 5
| Coins used, sum → | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| none | 1 | 0 | 0 | 0 | 0 | 0 |
| {1} | 1 | 1 | 1 | 1 | 1 | 1 |
| {1, 2} | 1 | 1 | 2 | 2 | 3 | 3 |
| {1, 2, 3} | 1 | 1 | 2 | 3 | 4 | **5** |

For example $dp[3][5] = dp[2][5] + dp[3][2] = 3 + 2 = 5$. The five ways: 1+1+1+1+1, 2+1+1+1,
2+2+1, 3+1+1, 3+2.
:::

## Longest increasing subsequence (LIS)

The length of the longest strictly increasing subsequence of an array; the elements need
**not** be consecutive.

**State:** $dp[i]$ = length of the LIS **ending at index $i$**. **Base case:** $dp[i] = 1$ for
all $i$ (one element is increasing). **Transition:**

$$dp[i] = \max\big(dp[j] + 1\big) \quad \text{over } j < i \text{ with } a[j] < a[i].$$

**Answer:** $\max_i dp[i]$. Time $O(n^2)$: each state looks at all earlier ones (DP on
sequences).

:::example arr = [3, 10, 2, 1, 20]
$dp = [1, 2, 1, 1, 3]$: 10 extends 3; 2 and 1 extend nothing; 20 extends 3, 10 to length 3.
The answer is **3** (3, 10, 20).
:::

## 0/1 knapsack

Items with weights and values, a knapsack of capacity $W$; maximise total value without
exceeding $W$, taking each item **whole or not at all**. An **optimisation** DP.

**State:** $dp[i][w]$ = maximum value using the first $i$ items with capacity $w$.
**Transition:** skip item $i$, or take it if $w \ge w_i$:

$$dp[i][w] = \max\big(dp[i-1][w],\ dp[i-1][w - w_i] + v_i\big).$$

**Base cases:** $dp[0][w] = 0$ (no items), $dp[i][0] = 0$ (no capacity). Fill row by row; the
answer is $dp[n][W]$.

:::example W = 5, values [1, 2, 3], weights [4, 5, 1]
| Items, capacity → | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| none | 0 | 0 | 0 | 0 | 0 | 0 |
| item 1 (w 4, v 1) | 0 | 0 | 0 | 0 | 1 | 1 |
| item 2 (w 5, v 2) | 0 | 0 | 0 | 0 | 1 | 2 |
| item 3 (w 1, v 3) | 0 | 3 | 3 | 3 | 3 | **4** |

The last cell: $\max(dp[2][5],\ dp[2][4] + 3) = \max(2, 1 + 3) = 4$, taking items 1 and 3
(weight 5, value 4).
:::

## Recognising a DP problem

A good candidate if a naive recursion repeats work, decisions depend on results for smaller
instances, and the solution can be described by a few parameters (the state). Typical
families: **counting**, **sequences**, **grids**, **subsets and knapsack**.

:::paper The recipe
1. Define the state.
2. Define the transitions.
3. Define the base cases.
4. Choose top-down or bottom-up order.

Done right, DP turns exponential brute force into polynomial time.
:::

## Where next

- Drill: [](deck:dynamic-programming).
- Next lecture: [](guide:08-metaheuristics-and-genetic-algorithms).
