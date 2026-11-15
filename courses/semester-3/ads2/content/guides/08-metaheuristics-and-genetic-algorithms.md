---
title: 'Metaheuristics and genetic algorithms'
number: 8
topics: [metaheuristics]
summary: Why optimisation needs more than exhaustive search and classical methods, local against global optima, heuristics, local search and hill climbing, simulated annealing, exploration against exploitation, what metaheuristics are and how they are built, the No Free Lunch theorem, benchmark functions, and genetic algorithms with selection, crossover and mutation.
takeaways:
  - Exhaustive search explodes combinatorially (TSP, vehicle routing) and gradient methods need smooth landscapes, so in practice a good solution found quickly beats a perfect one found never.
  - Hill climbing always moves to a better neighbour and stops at the first local optimum. Simulated annealing sometimes accepts worse moves, with a probability controlled by a falling temperature.
  - Every metaheuristic balances exploration (new regions) and exploitation (refining good ones); single-solution methods improve one candidate, population-based methods many.
  - 'No Free Lunch: no optimisation algorithm is best on all problems, so algorithms are chosen per problem and compared on benchmark functions (Sphere, Rosenbrock, Rastrigin, Ackley, Griewank, Schwefel) over many runs.'
  - A genetic algorithm evaluates fitness, selects parents (tournament, roulette wheel, rank), recombines them by crossover (one-point, two-point, uniform, arithmetic) and mutates the offspring, generation after generation.
sources:
  - misc/ADS REVISION.docx
---

## Why metaheuristics

**Optimisation** is finding the best solution by some objective (distance, cost, time, error,
energy) under constraints: scheduling, routing, design, planning, resource allocation, machine
learning.

**Exhaustive search** (try every solution) fails at once: the number of solutions grows
combinatorially. The **travelling salesman problem** explodes even for moderately many
locations; the **vehicle routing problem**, several vehicles with capacities and time windows,
is worse. Companies still need good routes quickly.

**Classical methods struggle.** Exact algorithms need too much time or memory. Gradient methods
assume smooth, continuous objectives, but real ones are often **rugged, noisy, discontinuous or
deceptive**. Deterministic searches explore little of the space and get stuck.

So the realistic goal is often a **suboptimal** solution that meets all constraints and is good
enough, found fast. Metaheuristics trade guaranteed optimality for **robustness, flexibility and
scalability**.

## Local and global optima

A **local optimum** is better than all its neighbours but worse than the **global optimum**.
Methods that accept only improving moves get trapped in local optima; escaping needs a way to
accept temporary worsening or to jump elsewhere. This is the main reason metaheuristics use
**randomness**.

## Heuristics, local search, hill climbing

- A **heuristic** is a rule that gives a reasonably good solution quickly, without guarantees.
  **Greedy** algorithms (always take the locally best option) are the classic case: fast, sometimes
  optimal, often poor globally.
- **Local search** improves one solution by small changes: look at its **neighbourhood**, move to
  a better neighbour if there is one, stop when there is none (a local optimum). It explores only a
  small region.
- **Hill climbing** is greedy local search: always move to a strictly better neighbour. Very fast,
  but on a multimodal landscape it almost always stops at the **first local optimum**; plateaus,
  shoulders and flat regions make it worse.

## Simulated annealing

Local search that sometimes **accepts a worse solution**, with a probability set by a
**temperature**. Hot: almost random, wide exploration. As the temperature falls, it becomes
increasingly greedy. This lets it escape local optima early and settle later; the **temperature
schedule** largely decides how well it works.

## Exploration against exploitation

- **Exploitation:** refine and improve promising regions.
- **Exploration:** visit new regions so as not to converge too early.

Pure exploitation ends in local optima; pure exploration wastes time. **How a metaheuristic
balances the two is what distinguishes it.**

## What metaheuristics are

**High-level optimisation frameworks** that guide lower-level heuristics. They need no gradients
or other mathematical properties of the objective; they use structured randomness, adaptive rules
and flexible operators to explore complex landscapes. The aim is high-quality solutions on hard
problems, not guaranteed optimality.

| Kind | Works on | Examples |
|---|---|---|
| Single-solution | One candidate, improved by stochastic moves | Simulated annealing, tabu search, iterated local search |
| Population-based | Many candidates at once; stronger global search and information sharing | Genetic algorithms, particle swarm optimisation |

**General structure:** (1) generate an initial solution or population; (2) evaluate it with the
objective; (3) modify solutions with operators; (4) accept or reject changes by some rule;
(5) repeat until a stopping condition.

### Designing one

| Element | What to decide |
|---|---|
| **Representation** | How a solution is encoded: binary vector, real vector, permutation, set. It decides which operators apply; a poor encoding makes search inefficient |
| **Initialisation** | Random (uniform, to avoid early bias) or heuristic (start in a reasonable region), balancing diversity and baseline quality |
| **Objective / fitness** | Maps a solution to a score; evaluated very often, so it must be fast. It *is* the landscape: noise, discontinuities and flat regions shape the search |
| **Operators** | **Mutation** (small random changes, neighbour moves), **crossover** (combine parts of two or more solutions), **movement rules** (positions and velocities in swarm methods) |
| **Exploration-exploitation balance** | A clear mechanism for both |
| **Parameters** | Population size, mutation rate, crossover probability, PSO coefficients, annealing schedule; fixed or adaptive (self-adapting often helps) |
| **Stopping criteria** | Maximum evaluations or iterations, no improvement for a while, a time limit |

**Strengths and limits.** They work on complex, noisy, discontinuous objectives, are flexible
and robust, and escape local minima. But they guarantee no global optimum, often need many
evaluations, and are sensitive to parameters.

## The No Free Lunch theorem

**No optimisation algorithm is best for all problems**: an algorithm that does well on some
problems must do worse on others. So the choice must be **problem-specific**, benchmarking on
varied functions is essential, and hybrid or adaptive methods often beat pure ones.

## Benchmark functions

Good benchmarks test **multimodality** (many local optima), **deceptiveness** (local optima far
from the global one), **scalability** (behaviour as the dimension grows), **noise sensitivity**
and **landscape shape** (ruggedness, flat regions, narrow valleys).

| Function | Landscape | What it tests |
|---|---|---|
| **Sphere** | Simple convex bowl, minimum at the centre, nothing deceptive | Pure exploitation, speed of convergence |
| **Rosenbrock** | A narrow curved valley; gradients mislead | Following a narrow curved path; exploitation under awkward geometry |
| **Rastrigin** | A regular grid of many local minima on a bowl | Escaping local optima (the source repeats Rosenbrock's description here; this row is the standard one) |
| **Ackley** | Flat near the centre, ring-shaped patterns, many small local minima | Global exploration and stability; the balance of the two |
| **Griewank** | Smooth and oscillating components; many local minima, less regular than Rastrigin | Robustness and large-scale behaviour |
| **Schwefel** | Global minimum far from the origin; local minima pull algorithms away | Aggressive global exploration; exposes premature convergence |

**How they are used in research:** run each algorithm on several functions, in several
dimensions (10, 30, 50, 100), **many times**; report best, worst, mean and standard deviation;
look at convergence curves and evaluation counts; compare with statistical tests.

## Evolutionary algorithms and genetic algorithms

**Evolutionary algorithms** imitate natural evolution: a **population** evolves over
generations by selection, crossover and mutation, so better solutions become more frequent.

**Genetic algorithms (GAs)** are the best known. Solutions are **chromosomes**; **fitness**
sets the chance of being selected; **crossover** recombines parents; **mutation** keeps
diversity. Crossover is the main operator, mutation prevents stagnation, and **selection
pressure** must be tuned: too high loses diversity, too low converges slowly.

**Workflow:** initialise a population → evaluate fitness → select parents → crossover and
mutation → replace part of the population → repeat until the stopping condition.

| Selection | |
|---|---|
| Tournament | Pick a few at random, keep the best: robust and simple |
| Roulette wheel | Probability proportional to fitness: biased by absolute fitness values |
| Rank | Probability by rank: more stable when fitness gaps are large |

| Crossover | |
|---|---|
| One-point | Cut both parents at one position and swap the tails |
| Two-point | Swap the middle segment |
| Uniform | Take each gene independently from parent A or B |
| Arithmetic / blend | For real values: weighted averages or intervals of the parents' genes |

**Mutation** maintains diversity, prevents premature convergence, and brings in genetic material
crossover cannot produce.

| Parameter | Effect |
|---|---|
| Population size | Small converges faster but risks stagnation |
| Mutation rate | Too low loses diversity; too high becomes random search |
| Crossover rate | How strongly information is mixed |
| Elite count | The best individuals survive unchanged |

**Strengths:** global exploration, flexible representations, easy to parallelise.
**Weaknesses:** slow convergence, parameter sensitivity, and they often need hybridisation with
local search for strong exploitation.

## Where next

- Swarm and other nature-inspired methods: [](guide:09-swarm-intelligence).
- Drill: [](deck:metaheuristics).
