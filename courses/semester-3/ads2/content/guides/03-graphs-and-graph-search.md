---
title: 'Graphs and graph search'
number: 3
topics: [graph-search]
summary: The vocabulary of graphs (edges and graph types, degree, paths and cycles, sparsity, connectivity, trees, forests and spanning trees, weights), the families of graph problems, and seven search algorithms, BFS, DFS, iterative deepening, bidirectional search, uniform cost search, greedy best-first and A*, with when to use each.
takeaways:
  - A graph is $G = (V, E)$. An adjacency matrix takes $O(V^2)$ space whatever the number of edges; an adjacency list takes $O(V + E)$, far better for the sparse graphs of real life.
  - A tree is a connected acyclic undirected graph, and a tree on $n$ vertices has exactly $n - 1$ edges. A spanning tree uses all vertices of a connected graph and $n - 1$ edges.
  - BFS (a queue) is complete and optimal in unweighted graphs; DFS (a stack or recursion) is not optimal. Both run in $O(V + E)$ time and $O(V)$ space.
  - Iterative deepening repeats depth-limited DFS, getting BFS's optimality with DFS's $O(bd)$ memory. Bidirectional search cuts $O(b^d)$ to $O(b^{d/2})$.
  - Uniform cost search expands the cheapest path so far (Dijkstra is a variant); greedy best-first follows the heuristic $h(n)$ alone; A* uses $f(n) = g(n) + h(n)$ and is optimal when $h$ never overestimates.
sources:
  - misc/ADS REVISION.docx
---

## Why graphs

A graph models **things** and the **relationships** between them: cities and roads, people
and friendships, computers and cables, web pages and links, tasks and prerequisites. Modelling
means choosing what becomes a vertex and what becomes an edge.

## Definitions

$$G = (V, E)$$

$V$ is the set of **vertices**, $E$ a collection of pairs of vertices called **edges**. In
the data-structures view, vertices and edges are positions that store elements: names,
weights, attributes.

- **Directed** edges have a direction (a one-way street, a hyperlink); **undirected** edges
  do not (a two-way road). A directed graph has only directed edges, an undirected graph only
  undirected ones.
- The **endpoints** of an edge are the two vertices it connects. An edge is **incident** on
  its endpoints; two vertices are **adjacent** if an edge joins them.
- The **degree** of a vertex is the number of incident edges (in a directed graph,
  in-degree and out-degree).
- **Parallel edges** join the same pair of vertices; a **self-loop** joins a vertex to
  itself. Both matter: Karger's contraction removes self-loops, and parallel edges change cut
  sizes.
- A **path** alternates vertices and edges, each edge joining its neighbours in the
  sequence; a **simple path** repeats no vertex or edge. A **cycle** is a path that returns to
  its start; a **simple cycle** repeats nothing except the start.

### Sparse graphs and representation

A graph is **sparse** when it has far fewer edges than possible. Most real graphs are (social
networks, road networks).

| Representation | Space | Good for |
|---|---|---|
| Adjacency matrix | $O(V^2)$, whatever $E$ is | Fast edge lookup in dense graphs |
| Adjacency list | $O(V + E)$ | Sparse graphs, which is most of them |

### Connectivity and trees

- $S$ is a **subgraph** of $G$ if its vertices and edges are subsets of $G$'s.
- $G$ is **connected** if there is a path between every pair of vertices. Otherwise it splits
  into **connected components**, which is why traversals restart for each component.
- A **tree** is a connected undirected graph with no cycles. A tree on $n$ vertices has
  exactly $n - 1$ edges.
- A **forest** has no cycles but need not be connected: a collection of trees.
- A **spanning tree** of a connected graph contains all its vertices and is a tree, so it has
  $n - 1$ edges. Minimum spanning trees (Prim, Kruskal) build on this.
- In a **weighted graph** each edge carries a weight or cost: distance, time, price,
  capacity.

## Which problems graphs solve

| Family | Algorithms | Example problem |
|---|---|---|
| Traversal and search | BFS, DFS, iterative deepening, bidirectional | Everyone reachable from an account in a social network |
| Shortest paths | Dijkstra, Bellman-Ford, Floyd-Warshall, A* | Fastest route from Sarajevo to Vienna |
| Minimum spanning trees | Prim, Kruskal | An electricity grid connecting all cities at least cable cost |
| Connectivity and components | Union-Find, Tarjan, Kosaraju, bridges, articulation points | Which parts of the Internet stay connected if a data centre fails |
| Topological ordering | On DAGs | The order to take courses given prerequisites |
| Flow and matching | | Assigning applicants to jobs for maximum suitability |

Harder problems such as enumerating paths or the travelling salesman need specialised or
heuristic methods.

## Graph search

There is no single best traversal. The choice depends on whether you need optimality,
completeness, low memory, weights or heuristics.

### Breadth-first search (BFS)

Visit the start, then all vertices at distance 1, then distance 2, and so on. A **queue**
makes vertices discovered earlier get expanded first.

- **Complete**: finds every reachable vertex.
- **Optimal in unweighted graphs**: the first time a vertex is reached is by a fewest-edges
  path.
- Time $O(V + E)$, space $O(V)$ (the visited set and the queue).

Uses: shortest paths in unweighted graphs, connectivity and components, bipartiteness,
mazes.

### Depth-first search (DFS)

Go as deep as possible along a branch, backtrack at a dead end, continue until every
reachable vertex is visited. Recursive (the call stack) or iterative (an explicit stack).

- **Complete** on finite graphs, but it can get stuck in deep or infinite ones (more of an
  issue in AI state spaces).
- **Not optimal**: no shortest-path guarantee.
- Time $O(V + E)$, space $O(V)$ in the worst case.

Uses: cycle detection, components, topological sorting of DAGs, reachability, mazes and
state-space exploration.

### Iterative deepening search (IDS)

Run **depth-limited DFS** with limit 0, then 1, then 2, and so on until the goal is found.

- **Complete** if the branching factor is finite; **optimal** in edges (it finds the
  shallowest solution, like BFS).
- Time $O(b^d)$, space $O(bd)$, where $b$ is the branching factor and $d$ the depth of the
  shallowest solution.

The repeated shallow levels cost little because most nodes are at the deepest level. Uses:
huge or infinite graphs where BFS runs out of memory, puzzles (8-puzzle, Rubik's cube), game
trees, planning.

### Bidirectional search (BDS)

Search forward from the start and backward from the goal at once; stop when the frontiers
meet and join the two half-paths. With BFS on both sides it is **complete** and
**optimal** (in edges) on finite graphs.

$$\text{Time} = O\!\left(b^{d/2}\right), \qquad \text{Space} = O\!\left(b^{d/2}\right)$$

instead of $O(b^d)$ for one BFS: two frontiers of depth $d/2$. Uses: navigation, puzzles,
routing, peer-to-peer search, whenever start and goal are both known.

### Uniform cost search (UCS)

For **weighted** graphs. Expand the vertex with the **lowest path cost so far**, $g(n)$,
from a priority queue, and relax its neighbours.

- **Complete and optimal** if all edge costs are non-negative.
- Time $O(E \log V)$, space $O(V)$ with a priority queue.
- **Dijkstra's algorithm is a variant of UCS**, computing shortest paths from a source to all
  vertices.

### Greedy best-first search

An **informed** search: expand the vertex with the smallest **heuristic** $h(n)$, an estimate
of the distance to the goal, ignoring the cost so far. Fast, but **neither complete nor
optimal**: it can get stuck, or follow a path that looks good locally and is worse globally.
Uses: game pathfinding and robot navigation where speed matters more than guarantees.

### A*

Combines UCS and greedy search:

$$f(n) = g(n) + h(n),$$

cost so far plus estimated cost to go. Expand the smallest $f(n)$.

- **Complete** with a finite branching factor and non-negative costs.
- **Optimal** if $h$ is **admissible**: it never overestimates the true cost to the goal.
- Time up to $O(E \log V)$ depending on the heuristic; memory is its weak point, since it
  keeps many generated nodes.

Uses: navigation, robotics, autonomous driving, games, logistics, scheduling.

:::recall Why does an overestimating heuristic break A*'s optimality?
If $h$ overestimates on the optimal path, its nodes get too large an $f$, and A* can reach the
goal through a worse path first and stop there.
:::

## Choosing a search algorithm

| Algorithm | Strategy | Optimal? | Weights? | Heuristic? | Use when |
|---|---|---|---|---|---|
| BFS | Level by level | Yes (unweighted) | No | No | Shortest path in an unweighted graph |
| DFS | Deep, then backtrack | No | No | No | Exploring structure, cycles, generating paths |
| Iterative deepening | DFS with a growing depth limit | Yes | No | No | Memory is short but completeness is needed |
| Bidirectional | From start and goal at once | Yes | No | No | Both ends known, to cut search time |
| Uniform cost | Cheapest path so far | Yes | Yes | No | Costs differ and you need the optimum |
| Greedy best-first | Seems closest to goal | No | Yes | Only $h$ | A fast approximate answer |
| A* | Cost so far plus estimate | Yes (admissible $h$) | Yes | $g + h$ | A good heuristic, speed and optimality |

## Where next

- Shortest paths and spanning trees in detail: [](guide:04-shortest-paths-and-spanning-trees).
- Drill: [](deck:graphs).
