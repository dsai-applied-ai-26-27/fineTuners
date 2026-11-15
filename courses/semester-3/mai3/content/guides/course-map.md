---
title: Course map
summary: How Mathematics for AI III is organised and graded, the units it covers and why each matters for AI, and what last year's five homeworks say about the scope of the semester.
sources:
  - lectures/Course Overview.pdf
  - 2025-26/HW1_Mathematics_for_AI_III.pdf
  - 2025-26/HW2 Measure Theory.pdf
  - 2025-26/HW3_Mathematics_for_AI_III.pdf
  - 2025-26/Homework assignment 4.pdf
  - 2025-26/Homework assignment 5.pdf
  - misc/c3-notes.md
---

## Organisation

From the course overview of 7 October 2026 (slides 2 and 3).

- **Staff:** Assistant Professor Nermin Čović (responsible teacher) and teaching assistant
  Ilhama Beganović. Consultations are by arrangement over email.
- **Hours:** 70 in total, 50 of lectures and 20 of tutorials, at 5 or 6 hours a week.
- **When and where:** Wednesday 15:00 to 18:00 in classroom 2-02 (S-10) and Friday 09:00 to
  12:00 in classroom 2-03 (S-8).
- **Announced on C3:** lectures began on Wednesday 7 October 2026; the Friday lecture of
  16 October started at 10:00 instead of 09:00, and the one of 23 October at 9:30.
- **Delivery:** in class with a two-way live stream. Recordings stay online until the end
  of the semester, and slides and materials are on the courseware page (slide 10).

## Grading

| Component | Points | Notes |
|---|---|---|
| Midterm | 40 | During the semester |
| Final exam | 40 | After 15 weeks. Worth 80 if it also covers the midterm part |
| Four short tests | 20 | Coursework |
| Attendance and activity | up to 5 extra | Lectures and tutorials |

Exams carry 80% of the grade and coursework 20% (slide 11).

| Points | 0 to 54 | 55 to 64 | 65 to 74 | 75 to 84 | 85 to 94 | 95 to 100 |
|---|---|---|---|---|---|---|
| Grade | No pass | 6 | 7 | 8 | 9 | 10 |

:::note What the overview does not say
There are no dates for the midterm or the short tests, no description of the exam format,
and no homework this year: coursework is four short tests instead. Until that is known
there is no exam plan on this site.
:::

## The units

The overview lists two parts (slides 5 and 6). The names in brackets are the topic labels
used on this site.

**Part I.** Use measure theory and functional analysis to give the core objects of machine
learning (expected loss, conditional expectation, kernels) a precise meaning.

1. Basic measure and integration theory ([](topic:measure))
2. Advanced probability ([](topic:probability))
3. Basic functional analysis: vector spaces, normed spaces and Hilbert spaces, and
   convergence in normed spaces ([](topic:functional))
4. Reproducing kernel Hilbert spaces ([](topic:rkhs))

**Part II.** Use those structures to build efficient computational methods for large-scale
data and AI problems.

5. Computation with large matrices ([](topic:matrices))
6. Low-rank methods and compressed sensing ([](topic:lowrank))
7. Optimization, unconstrained and constrained ([](topic:optimization))
8. Double and triple integrals ([](topic:integrals))

## Why this mathematics matters for AI

Slides 7 and 8 give one sentence of motivation per unit. They are worth knowing because
they say what each block of theory is *for*.

**Measure theory answers "what are we minimising?"** Learning minimises the expected loss
under an unknown data distribution $P$:

$$R(f) = \mathbb{E}_P[\ell(f(X), Y)] = \int \ell(f(x), y)\, dP(x, y) .$$

Here $f$ is the predictor, $\ell$ the loss, and the integral is taken with respect to the
measure $P$. The training loss is the same integral with $P$ replaced by the empirical
measure of the observed samples. Integrating against a measure also covers discrete,
continuous, mixed and manifold-valued data with one definition.

**Functional analysis makes prediction a projection.** For $Y \in L^2$, the best prediction
of $Y$ given the information $\mathcal{G}$ is the conditional expectation
$\mathbb{E}[Y \mid \mathcal{G}]$, which is the orthogonal projection of $Y$ onto the
$\mathcal{G}$-measurable functions in $L^2$.

**Kernel methods: why the kernel trick works.** Replacing a dot product by a kernel $k$
means working in a reproducing kernel Hilbert space. By the representer theorem a
minimiser is, under its assumptions, a finite combination of kernel evaluations at the
training points $x_1, \dots, x_n$:

$$f^*(x) = \sum_{i=1}^{n} \alpha_i\, k(x_i, x) .$$

**Optimization explains when and why learning converges.** Convexity, smoothness and
conditioning account for convergence guarantees, step-size choices, slow progress and
failures.

**Large-scale linear algebra makes computation feasible.** Iterative solvers, Krylov
subspaces and low-rank approximations keep large problems inside time and memory limits.

## What last year's homework covered

:::warning Read this as a map, not as a forecast
The five sheets below are from 2025-26, when the course was taught by Senada Kalabušić and
Zenan Šabanac. The staff has changed, the order has changed (last year opened with multiple
integrals; this year's overview puts them last), and this year's coursework is short tests,
not homework. The sheets show how far each unit went. They do not show what will be asked.
:::

| Sheet | Date set | Unit | What was asked |
|---|---|---|---|
| Homework 1 | 15 Oct 2025 | Double and triple integrals | 8 problems. A change of variables to $u = x + y$, $v = x - y$; area between a line and a parabola; volumes by double and by triple integral; surface area of $z = xy$ inside a cylinder; integrals in cylindrical and spherical coordinates |
| Homework 2 | 9 Nov 2025 | Measure theory | 9 problems. Algebras against σ-algebras; generators of the Borel σ-algebra; σ-algebras defined through inverse images; generated σ-algebras; restricting a measure; a limit that does not pass through the integral and why the Monotone Convergence Theorem is not contradicted; two limits of integrals found by domination; integrability of $1/\sqrt{xy}$ on the unit square |
| Homework 3 | 20 Nov 2025 | Functional analysis | 5 problems. Two matrix norms; $C[0,1]$ with the $L^2$ norm is not a Banach space (a Cauchy sequence of continuous functions with a discontinuous limit); a bounded linear operator and its norm; an inner product defined by a positive definite matrix; triangle and Cauchy–Schwarz inequalities in a Hilbert space |
| Homework 4 | 25 Dec 2025 | Functional analysis and RKHS | 6 problems. Bounded linear functionals on $\ell^1$ and on $L^2(0,1)$ with their operator norms; the Riesz representation theorem; closure properties of positive definite kernels (sums, products, limits, exponentials); deciding whether given functions are kernels; a quadratic kernel with an explicit feature map that separates four points; describing its RKHS |
| Homework 5 | 15 Jan 2026 | Large matrices and continuous optimization | 11 problems. Two iterations of Gauss–Seidel; conjugate gradient by hand and its convergence in few steps; a Krylov subspace and the minimal-residual approximation in it; constrained optimisation with equality and inequality constraints; nonlinear conjugate gradient with the Fletcher–Reeves formula and exact line search |

Each sheet was worth 20 points, with single problems worth between 1 and 6.

What stands out:

- **Proof and computation in equal measure.** The measure and functional analysis sheets
  are mostly "show that" and "prove that". The integrals and numerical sheets are
  computations carried out by hand for two iterations.
- **No sheet on advanced probability or on low-rank methods and compressed sensing.** Both
  are units this year, so last year's homework is silent on them.
- **Lectures 1 and 2 cover almost all of homework 2.** Its first five problems need only
  σ-algebras and measures and are written up in
  [](problems:sigma-algebras-and-measures). Problems 6 to 8 need the convergence
  theorems of lecture 2 and are in [](problems:convergence-theorems). Only problem 9, an
  integral over the unit square, waits for integration on product spaces.

## Literature

Lecture and tutorial materials come first. The overview (slide 13) also lists:

- Bauer and Burckel, *Measure and Integration Theory*
- Kreyszig, *Introductory Functional Analysis with Applications*
- Strang, *Introduction to Applied Mathematics*; *Linear Algebra and Learning from Data*;
  *Calculus*; *Linear Algebra and Its Applications*
- Nelson, *Essential Math for AI*
- Vestrup, *The Theory of Measures and Integration*

Lectures 1 to 3 are extracted from Axler, *Measure, Integration & Real Analysis*,
chapters 1 to 3 and 7. Lecture 1 quotes one definition from Folland, *Real Analysis*, and
lecture 3 takes Hölder's and Minkowski's inequalities from Folland's chapter 6. Both books
are on the courseware page under Literature.

## Start here

| Lecture | Notes | Drill | Proofs | Practice |
|---|---|---|---|---|
| 1 | [](lecture:01-sigma-algebras-and-measures) | [](deck:measure-foundations) | [](deck:measure-foundations-proofs) | [](problems:sigma-algebras-and-measures) |
| 2 | [](lecture:02-the-lebesgue-integral) | [](deck:lebesgue-integral) | [](deck:lebesgue-integral-proofs) | [](problems:convergence-theorems) |
| 3 | [](lecture:03-lp-spaces) | [](deck:lp-spaces) | [](deck:lp-spaces-proofs) | [](problems:lp-spaces-practice) |

The guides cut across the lectures:

- [](guide:proof-toolkit): the dozen moves every proof is made of, and an index of every
  proof with its card.
- [](guide:counterexamples): why each hypothesis is there, and which kind of convergence
  implies which.
- [](guide:computing-integrals): the recipes for integrals and limits of integrals, and
  how to find a dominating function.

Every definition of the three lectures is in the [glossary](glossary), and the formulas,
including the three convergence theorems side by side, on [the sheet](formulas). To drill
only the proofs across all lectures, use [the step-by-step cards](cards?filter=steps).
