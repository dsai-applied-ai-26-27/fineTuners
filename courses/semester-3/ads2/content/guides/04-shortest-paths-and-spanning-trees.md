---
title: 'Shortest paths and minimum spanning trees'
number: 4
topics: [graph-algorithms]
summary: The families of graph algorithms, the rule for choosing a shortest-path algorithm, Dijkstra and Bellman-Ford with negative cycles, minimum spanning trees with Prim and Kruskal, NP-hard graph problems and the move to heuristics.
takeaways:
  - 'Unweighted: BFS. Non-negative weights: Dijkstra. Negative weights: Bellman-Ford. All pairs: Floyd-Warshall.'
  - Dijkstra repeatedly finalises the closest unfinished vertex and relaxes its edges; once a vertex is finalised its distance is final. $O((V + E)\log V)$ with a priority queue, $O(V^2)$ with a matrix.
  - Bellman-Ford relaxes every edge $V - 1$ times, because a shortest path has at most $V - 1$ edges; one more round that still improves something reveals a negative cycle. $O(VE)$.
  - An MST of a connected weighted graph has $V - 1$ edges. Prim grows one tree by the lightest edge leaving it (dense graphs); Kruskal adds the lightest edge that joins two components, with Union-Find (sparse graphs, $O(E \log E)$).
  - Clique, colouring, Hamiltonian cycle and TSP are NP-hard, which is where heuristics take over.
sources:
  - misc/ADS REVISION.docx
---

## The families of graph algorithms

Graph algorithms are grouped by the question they answer:

- **Traversal and search** visits or discovers vertices (BFS, DFS, IDS, bidirectional, UCS,
  greedy, A*: [](guide:03-graphs-and-graph-search)).
- **Shortest paths** finds minimum-cost paths in weighted graphs.
- **Minimum spanning trees** connects all vertices at minimum total weight without cycles.
- **Connectivity** analyses structure: components, articulation points, bridges, robustness.
- **Topological ordering** linearises a DAG respecting dependencies (scheduling, compiling,
  prerequisites).
- **Flow and matching** moves resources through networks and pairs elements optimally; some of
  these problems are NP-hard.

## Shortest paths

What is the minimum cost to get from one vertex to another? The answer depends on the
weights:

| Weights | Algorithm |
|---|---|
| None (unweighted) | BFS |
| Non-negative | Dijkstra |
| Negative allowed | Bellman-Ford |
| All pairs of vertices | Floyd-Warshall |

### Dijkstra's algorithm

Single-source shortest paths when **all weights are non-negative**. Greedy: always expand the
vertex with the **smallest known distance so far**.

1. Distance 0 for the source, $\infty$ for everything else.
2. Repeatedly take the unfinished vertex with the smallest tentative distance and mark it
   final.
3. **Relax** its outgoing edges: if going through it gives a neighbour a shorter path, update
   the neighbour.

**Invariant:** once a vertex is finalised, its shortest distance is guaranteed. (A negative
edge would break this: a later path could still undercut a finalised vertex.)

- Complete and optimal for non-negative weights; directed or undirected graphs.
- Time $O((V + E)\log V)$ with a priority queue, $O(V^2)$ with an adjacency matrix.
- Uses: GPS navigation, network routing, logistics, game pathfinding.

### Bellman-Ford

Single-source shortest paths **with negative weights allowed**. Instead of choosing vertices
greedily, relax **all edges**, repeatedly.

**Key insight:** a shortest path has at most $V - 1$ edges, so after $V - 1$ rounds of
relaxing every edge all shortest paths are found, unless there is a negative cycle.

**Negative cycles.** A cycle with negative total weight can be traversed again and again,
lowering the cost forever, so no shortest path exists. Bellman-Ford detects it with **one
extra round**: if any distance still improves, a negative cycle exists.

- Always terminates; optimal if there are no negative cycles; detects them if there are.
- Time $O(V \cdot E)$, slower than Dijkstra.
- Uses: financial arbitrage detection, the RIP routing protocol, systems with penalties or
  refunds.

## Minimum spanning trees

For a **connected weighted graph**, an MST connects all vertices, has no cycles, and has the
minimum possible total weight. It has exactly $V - 1$ edges.

### Prim's algorithm

Start at any vertex and **grow one tree**, repeatedly adding the **lightest edge** that
connects the tree to a vertex not yet in it: always the cheapest safe edge.

- Complete (for a connected graph) and optimal.
- Time $O((V + E)\log V)$ with a priority queue, $O(V^2)$ with an adjacency matrix.
- Well suited to **dense** graphs.
- Uses: network infrastructure, electrical grids, road networks, clustering.

### Kruskal's algorithm

Consider edges **globally**: sort them by weight, start with every vertex as its own
component, and add each edge if it **joins two different components** (does not form a
cycle). Stop at $V - 1$ edges. A **disjoint-set (Union-Find)** structure detects cycles
efficiently.

- Complete and optimal.
- Time $O(E \log E)$, dominated by sorting.
- Efficient on **sparse** graphs; works naturally on an edge list.
- Uses: network design, image segmentation, clustering, distributed systems.

| | Prim | Kruskal |
|---|---|---|
| Grows | One connected tree | A forest of components that merge |
| Picks | Lightest edge leaving the tree | Lightest edge overall that joins two components |
| Needs | A priority queue | Sorted edges and Union-Find |
| Best on | Dense graphs | Sparse graphs |

Both give a minimum spanning tree.

## The limits of graph algorithms

Some graph problems have no known efficient algorithm: **clique detection, graph colouring,
Hamiltonian cycles, the travelling salesman problem**. They are **NP-hard**.

When exact methods are too slow, **heuristics** trade guaranteed optimality for speed and
guide search towards promising regions: greedy algorithms, A* with a heuristic, genetic
algorithms, simulated annealing ([](guide:08-metaheuristics-and-genetic-algorithms)).

## From graphs to trees

Many graph algorithms build trees implicitly: BFS a breadth-first tree, DFS a depth-first
tree, Prim a minimum spanning tree. Trees give structure, hierarchy and fast search, which is
where the course goes next ([](guide:05-balanced-search-trees)).

:::tip What to know about each algorithm
The guide's own advice: knowing **why** an algorithm works, **when** it applies and **what
guarantees** it gives matters more than memorising its steps.
:::

## Where next

- Drill: [](deck:graphs).
- Formulas and complexities: [the sheet](formulas).
