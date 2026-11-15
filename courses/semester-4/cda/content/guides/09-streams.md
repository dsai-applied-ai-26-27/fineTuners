---
title: 'Mining data streams'
number: 9
topics: [streams]
summary: 'Lecture 9. On neither past paper: read last.'
---

:::warning
On **neither** past paper — Lecture 9 was taught last and was not examined in either sitting. Read it after the topics that carry marks. If it does appear, the four algorithms below are the whole lecture.
:::

In a stream, data arrives one element at a time, too fast to store: if it isn't processed immediately it is lost forever. The question is always *how do you compute this with limited memory*.

| Problem | Algorithm | The idea in one line |
|---|---|---|
| Sample a fixed **proportion** | hash the **key** | Don't sample queries, sample **users**: hash each tuple's key into b buckets, keep it if the hash is ≤ a, for an a/b sample. |
| Maintain a fixed-**size** sample s | **Reservoir sampling** | Keep the first s. For the n-th element (n > s), keep it with probability s/n, and if kept, evict one of the s uniformly at random. |
| Is this key in set S? | **Bloom filter** | Hash each member with k functions and set those bits. An item passes only if all k of its bits are 1. **False positives yes, false negatives never.** |
| How many **distinct** elements? | **Flajolet-Martin** | Hash each element; let r(a) be the number of **trailing zeros**; keep R = max r(a). Estimate = **2^R**. |
| Most frequent **recently**? | **Exponentially decaying window** | On each new element multiply all counts by (1 − c), add 1 to the new item's count, and drop counts below ½. |

```text
reservoir: P(element in S after n items) = s / n
```

```text
Bloom false positive rate = (1 − e^(−km/n))ᵏ, optimal k = (n/m)·ln 2
```

- **m**: number of keys in S
- **n**: number of bits in the array B
- **k**: number of hash functions

The lecture's worked case: m = 10⁹ keys in n = 8×10⁹ bits gives 1 − e^(−1/8) = **0.1175** at k = 1, and **0.0489** at k = 2; the optimum is k = 8·ln 2 ≈ **5.54 ≈ 6**, giving 0.0216. For decaying windows, there cannot be more than **2/c** items with weight ≥ ½.
