---
title: 'Swarm intelligence and nature-inspired algorithms'
number: 9
topics: [swarm]
summary: A recap of optimisation, single-solution against population-based metaheuristics, swarm intelligence and the families of nature-inspired algorithms, when to use swarm, evolutionary or physical methods, and six algorithms, particle swarm, ant colony, firefly, bat, elephant herding and fireworks, followed by No Free Lunch and hybrids.
takeaways:
  - Swarm intelligence gets complex global behaviour from agents following simple local rules and sharing information (positions, pheromones, fitness), with no global knowledge.
  - Swarm methods suit continuous spaces and fast convergence; evolutionary methods suit discrete or combinatorial problems with complex encodings; physical-process methods like simulated annealing suit simple trajectory search with probabilistic acceptance.
  - 'PSO: $v_i \leftarrow Wv_i + c_1r_1(P_{best,i} - x_i) + c_2r_2(g_{best} - x_i)$, then $x_i \leftarrow x_i + v_i$. ACO: pheromone $\tau_{xy} \leftarrow (1-\rho)\tau_{xy} + \sum_k \Delta\tau^k_{xy}$, with evaporation $\rho$.'
  - Fireflies move towards brighter ones with attraction fading with distance; bats lower loudness and raise pulse rate as they close in, shifting from exploration to exploitation; elephant clans follow a matriarch while the worst males are dispersed; fireworks with good values explode small and dense, poor ones wide.
  - No single method wins everywhere (No Free Lunch), which is why hybrids such as PSO with local search or GA with simulated annealing are popular.
sources:
  - misc/ADS REVISION.docx
---

## Recap

Optimisation looks for the best solution of an objective under constraints, in search spaces
that grow explosively with problem size. Many problems have many **local optima**, and simple
methods that only accept improvements get stuck there. Greedy methods and hill climbing are fast
but stop at the first local optimum. Metaheuristics add **structured randomness**, temporary
worsening moves, population diversity or adaptive behaviour to balance **exploitation** and
**exploration** ([](guide:08-metaheuristics-and-genetic-algorithms)).

They target problems with huge search spaces, non-smooth, noisy or deceptive objectives, many
variables, and constraints that break classical assumptions. They need no gradients or
convexity.

| Single-solution | Population-based |
|---|---|
| Simulated annealing, tabu search, iterated local search | Evolutionary algorithms, swarm intelligence |

## Swarm intelligence

Inspired by **collective behaviour**: bird flocks, fish schools, ant colonies, bee swarms. Each
agent follows **simple local rules** with no global knowledge, yet intelligent global behaviour
emerges. Agents influence each other indirectly through shared information: positions,
pheromones, fitness.

**Strengths:** fast adaptation, strong global exploration, simple intuitive rules, natural
parallelism, which suits continuous, high-dimensional problems.

## Nature-inspired algorithms

They mimic biological, ecological or physical processes (adaptation, cooperation, competition,
self-organisation), need no derivatives, and often do well on **multimodal and noisy**
landscapes.

| Group | Examples |
|---|---|
| Evolutionary processes | Genetic algorithms, differential evolution |
| Collective behaviour | PSO, ACO, bee colony, firefly |
| Physical processes | Simulated annealing, harmony search |

**General structure:** initialise solutions; evaluate them; apply movement or update rules;
optionally let agents communicate; replace or update solutions; stop on a criterion.

**Swarm against evolutionary.** Swarms rely on **cooperation, spatial movement and social
learning**; evolutionary algorithms on **selection, reproduction and mutation**.

| Use | When |
|---|---|
| Swarm intelligence | The space is continuous, fast convergence is needed, position information helps |
| Evolutionary algorithms | The problem is discrete or combinatorial, encodings are complex, diversity across generations matters |
| Physical-process methods | Simple trajectory search is enough, probabilistic acceptance helps escape local optima, evaluations are expensive |

## Particle swarm optimisation (PSO)

Kennedy and Eberhart, 1995, inspired by flocking. Each **particle** is a candidate solution
moving through the space with a **velocity**. It remembers its own best position
($P_{best,i}$), and the swarm shares the best position found by anyone ($g_{best}$).

$$v_i \leftarrow W v_i + c_1 r_1 \big(P_{best,i} - x_i\big) + c_2 r_2 \big(g_{best} - x_i\big), \qquad x_i \leftarrow x_i + v_i$$

$W$ is the **inertia weight**, $c_1, c_2$ the acceleration (learning) coefficients, $r_1, r_2$
random numbers. The three terms: keep going, the **cognitive** pull to your own best, the
**social** pull to the swarm's best.

**Loop:** random initial swarm → fitness → update personal and global bests → update velocities
and positions → repeat until the termination condition.

**Parameters:** inertia weight (exploration against exploitation), learning coefficients
(personal against social), population size (global search), velocity limits (no overshooting).

**Strengths:** simple, fast convergence, few parameters. **Weaknesses:** premature
convergence, parameter sensitivity, poor on discrete problems without modification.

## Ant colony optimisation (ACO)

Dorigo and colleagues, early 1990s, from how ants find short paths with **pheromones**.
Artificial ants build solutions step by step on a graph, choosing the next step
**probabilistically by pheromone intensity**. Good solutions get more pheromone, so they are
chosen more often later; **evaporation** prevents stagnation.

After all ants have built a solution:

$$\tau_{xy} \leftarrow (1 - \rho)\,\tau_{xy} + \sum_k \Delta\tau^k_{xy},$$

$\tau_{xy}$ the pheromone on the transition $x \to y$, $\rho \in (0, 1]$ the **evaporation**
coefficient (small: slow adaptation; large: fast), $\Delta\tau^k_{xy}$ the pheromone deposited by
ant $k$.

**Ant colony system:** initialise; while not done, place each ant on a start node; each ant
repeatedly chooses its next node by the state transition rule and applies a step-by-step
pheromone update until all have built solutions; update the best solution; apply the offline
pheromone update.

**Strengths:** excellent for routing and graph problems, naturally parallel, good balance.
**Weaknesses:** sensitive to $\alpha$, $\beta$ and evaporation, risk of stagnation, less suited
to high-dimensional continuous spaces.

## Firefly algorithm (FA)

Xin-She Yang, 2008. Each firefly is a solution; its **brightness** is the objective value.
Fireflies **move towards brighter ones**, with attractiveness **decreasing with distance**, plus
randomness.

**Pseudocode:** initialise $M$ fireflies; light intensity $I_i = f(x_i)$; for each generation,
for every pair $i, j$, if $I_j > I_i$ move firefly $i$ towards $j$; evaluate, rank, update the
global best $g_*$.

**Parameters:** the **light absorption coefficient** (how fast attraction fades with distance),
the **randomisation factor** (noise against premature convergence), population size (more
exploration, more cost).

**Strengths:** simple movement, good on multimodal landscapes, balanced local and global
search. **Weaknesses:** depends on absorption and randomness settings, slow if randomness is too
high, sensitive to the scale of the space.

## Bat algorithm (BA)

Models **echolocation**. Each bat has a position, velocity, **frequency**, **loudness** and
**pulse rate**. As bats approach good solutions, **loudness decreases and pulse rate increases**,
shifting the search smoothly from exploration to exploitation.

**Loop:** adjust frequencies and update velocities and positions; if a random number exceeds the
pulse rate, generate a local solution around one of the best; also fly randomly; accept a new
solution if a random number is below the loudness and it improves, then **increase the pulse rate
and reduce the loudness**; rank and track the best.

**Parameters:** frequency range (diversity of movement), pulse rate (higher means exploitation),
loudness (falls over time, stabilising the search), population size.

**Strengths:** smooth global-to-local transition, simple rules, often fast on continuous
problems. **Weaknesses:** depends on loudness and pulse scheduling, stagnates if the frequency
range is too small, needs tuning in high dimensions.

## Elephant herding optimisation (EHO)

Inspired by elephant social structure. The population is split into **clans**, each led by its
best member, the **matriarch**.

- **Clan update:** each elephant moves towards its matriarch along a weighted direction, with
  some randomness; females mainly follow the leader.
- **Male dispersion:** the worst-performing males are relocated randomly, preventing stagnation
  and forcing global exploration.

Different clans explore different regions, which keeps diversity. **Parameters:** number of
clans, clan size, the $\alpha$ and $\beta$ factors (how strongly elephants move to the
matriarch), the dispersal factor. **Strengths:** diversity, strong exploration, intuitive rules.
**Weaknesses:** parameter-sensitive, slow without good dispersal control, less studied than
classic swarms.

## Fireworks algorithm (FWA)

Models explosions. Each **firework** is a candidate solution; its explosion produces **sparks**,
new candidates.

- **Better solutions** produce **smaller, denser** explosions (exploitation); **worse ones larger,
  wider** explosions (exploration).
- **Local sparks** land near the firework for fine search; **global sparks** land far away to jump
  to new regions; sparks outside the domain are repaired or discarded.
- Evaluate all sparks, keep the best few, replace weaker fireworks, keep diversity with random
  mutation sparks, and carry the best spark into the next generation.

**Strengths:** good control of exploration and exploitation, adaptive explosions, suits
high-dimensional continuous problems. **Weaknesses:** parameter-sensitive, explosion amplitude
needs tuning, many sparks can be expensive.

## No Free Lunch and hybrids

No optimisation algorithm is universally best. That is why so many metaheuristics exist, why
benchmarking is essential, and why **hybrids** are popular: **PSO + local search**, **GA +
simulated annealing**, **ACO + neighbourhood refinement**. Hybrids improve robustness, reduce
parameter sensitivity and adapt better to complex landscapes.

## The six algorithms side by side

| Algorithm | Inspiration | Solution | Search mechanism | Strengths | Weaknesses | Best for |
|---|---|---|---|---|---|---|
| PSO | Bird flocking, fish schooling | Position in continuous space | Velocity towards personal and global best | Simple, fast, few parameters | Premature convergence, weak diversity | Continuous, real-valued functions |
| ACO | Ant foraging, pheromone trails | Paths or sequences on graphs | Probabilistic construction, pheromone reinforcement | Combinatorial and graph problems | Parameter-sensitive, stagnation | TSP, routing, scheduling, networks |
| Firefly | Firefly light | Position | Attraction to brighter solutions plus randomness | Multimodal landscapes | Parameter-sensitive, slower scaling | Multimodal continuous optimisation |
| Bat | Echolocation | Position, velocity, frequency | Frequency-controlled moves, loudness and pulse | Adaptive exploration to exploitation | Many parameters, less theory | Continuous optimisation, hybrids |
| EHO | Elephant clans | Population split into clans | Clan attraction plus random dispersion | Diversity | Less mature, problem-dependent | Complex multimodal landscapes |
| Fireworks | Firework explosions | Position | Local and global sparks around solutions | Balance of exploration and exploitation | Tuning complexity | High-dimensional continuous optimisation |

## Where next

- Drill: [](deck:metaheuristics).
- Next lecture: [](guide:10-social-graphs-and-epidemics).
