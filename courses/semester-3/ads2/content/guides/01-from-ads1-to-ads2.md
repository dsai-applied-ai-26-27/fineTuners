---
title: 'From ADS I to ADS II'
number: 1
topics: [overview]
summary: What Algorithms and Data Structures I covered and is assumed here, the syllabus lecture 1 announced for ADS II, and a map of where each lecture of the 2025-26 run is written up.
takeaways:
  - ADS II assumes ADS I in full, from asymptotic analysis, recursion and the Master Theorem to BSTs, heaps, hashing, sorting, and BFS, DFS and topological sorting.
  - The 2025-26 lectures after the introduction cover randomized algorithms, graph search and graph algorithms, balanced and multiway trees, dynamic programming, metaheuristics, swarm intelligence, social graphs and document graphs.
  - Lecture 1 also listed hashing, distributed hashing and PRAM algorithms; the revision guide this course is written from has no lecture on them.
sources:
  - misc/ADS REVISION.docx
---

These study guides are written from **"ADS REVISION"**, a student's revision guide to the
2025-26 run of the course (lectures 1 to 11). Formulas that were pictures in the original
are written out here, and the worked examples are kept.

## What ADS I covered

Lecture 1 opens with a recap of the first course. Everything here is assumed knowledge.

| Area | What you should still know |
|---|---|
| Algorithms | An algorithm is a finite, well-defined sequence of steps that takes input and produces output in finite time. **Correctness**: right output for every valid input. **Efficiency**: time and space use |
| Asymptotic analysis | Time and space complexity; $O$, $\Omega$, $\Theta$; comparing growth rates; best, average and worst case |
| Recursion | Base cases; divide and conquer; recurrence relations; the **Master Theorem** for divide-and-conquer recurrences |
| Binary search trees | Left subtree smaller, right subtree larger; search, insert, delete by following that rule; in-order traversal gives sorted order; a skewed tree degrades from $O(\log n)$ to $O(n)$ |
| Stacks, queues, deques | Abstract data types; LIFO (push, pop) and FIFO (enqueue, dequeue); linked against array implementations; stacks for expression evaluation, queues for BFS |
| Lists and iterators | Singly and doubly linked lists; cheap insertion and deletion at a known position |
| Trees and AVL | Root, depth, height; pre-, in- and post-order traversals; hierarchies and parsing |
| Priority queues and heaps | Complete binary tree with the heap property; insert and extract-min in $O(\log n)$; heap sort; scheduling and Dijkstra |
| Sorting | Selection, insertion, merge, quick, heap, bucket and radix sort; stability; when to use which |
| Hash tables | Hash functions and collisions; separate chaining against open addressing; load factor and rehashing; expected $O(1)$ operations |
| Graph basics | Adjacency lists and matrices; vertices, edges, degree; directed and undirected graphs |
| Graph traversal | BFS (level by level, a queue, shortest paths in unweighted graphs), DFS (deep first, recursion or a stack), connected components, topological sorting of DAGs |

## The ADS II syllabus announced in lecture 1

1. Randomized algorithms: Monte Carlo and Las Vegas, expected running time, randomized
   quicksort and selection.
2. Search trees: AVL, red-black, splay, B and B+ trees; trees in databases; rotations.
3. Hashing: open addressing and chaining, double hashing and rehashing, perfect and cuckoo
   hashing.
4. Distributed hashing: consistent hashing, distributed hash tables (Chord, Pastry,
   Kademlia).
5. Advanced graph algorithms: weighted, directed and dynamic graphs, shortest paths,
   topological sorting, connectivity and centrality.
6. Social graphs: degree distribution, clustering coefficient, small-world and scale-free
   networks, community detection.
7. Document graphs: TF-IDF and similarity, co-occurrence networks, PageRank and TextRank.
8. Power law and epidemic models: preferential attachment, the Barabási-Albert model, SI, SIR
   and SIS.
9. Evolutionary algorithms: selection, crossover, mutation, fitness.
10. PRAM algorithms: the parallel random access machine (EREW, CREW, CRCW), parallel prefix
    sums, work, depth and speedup.

:::note What the 2025-26 lectures actually covered
The revision guide has eleven lectures. Hashing, distributed hashing and PRAM algorithms do
not appear in it, and dynamic programming and swarm intelligence, which are not on the
announced list, do. Use the lectures below as the scope, and the announced list as a hint of
what may have been mentioned in passing.
:::

## Where each lecture is written up

| Lecture | Guide | Drill |
|---|---|---|
| 2. Randomized algorithms | [](guide:02-randomized-algorithms) | [](deck:randomized-algorithms) |
| 3. Graphs I: definitions and search | [](guide:03-graphs-and-graph-search) | [](deck:graphs) |
| 4. Graphs II: shortest paths and MSTs | [](guide:04-shortest-paths-and-spanning-trees) | [](deck:graphs) |
| 5. Search trees I and II | [](guide:05-balanced-search-trees) | [](deck:search-trees) |
| 6. Search trees III | [](guide:06-b-trees-and-specialised-trees) | [](deck:search-trees) |
| 7. Dynamic programming | [](guide:07-dynamic-programming) | [](deck:dynamic-programming) |
| 8. Metaheuristics I | [](guide:08-metaheuristics-and-genetic-algorithms) | [](deck:metaheuristics) |
| 9. Metaheuristics II | [](guide:09-swarm-intelligence) | [](deck:metaheuristics) |
| 10. Social graphs, power law, epidemics | [](guide:10-social-graphs-and-epidemics) | [](deck:networks) |
| 11. Document graphs | [](guide:11-document-graphs) | [](deck:networks) |

Formulas and complexities in one place: [the sheet](formulas).
