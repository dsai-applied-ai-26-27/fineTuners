---
title: 'Balanced search trees'
number: 5
topics: [balanced-trees]
summary: Trees and their vocabulary, binary trees and the three depth-first traversals, binary search trees and why they degrade, and four ways to keep a search tree shallow, AVL trees, red-black trees, splay trees and treaps, with rotations and a comparison.
takeaways:
  - A tree is a connected acyclic graph, so there is exactly one path between any two nodes. Depth is the distance from the root; height is the longest distance down to a leaf.
  - In-order traversal of a BST lists the keys in sorted order. A BST's operations cost $O(h)$, which is $O(\log n)$ when balanced and $O(n)$ when sorted input turns it into a list.
  - AVL trees keep the heights of every node's subtrees within 1 of each other, by rotations; fastest searches, more expensive updates.
  - Red-black trees colour nodes so that every path from a node down to its leaves has the same number of black nodes and no red node has a red child; the longest path is at most twice the shortest, with fewer rotations than AVL.
  - Splay trees move every accessed node to the root (zig, zig-zig, zig-zag), giving amortised $O(\log n)$. Treaps are BSTs by key and heaps by a random priority, giving expected height $O(\log n)$.
sources:
  - misc/ADS REVISION.docx
---

## Why trees

Graphs model general networks; many problems need **hierarchy, order and fast search**,
which trees give: file systems, organisation charts, expression trees, search structures.
Many graph algorithms already build trees (BFS and DFS trees, MSTs).

## Trees and their vocabulary

A **tree** is a connected graph with no cycles, so there is **exactly one path** between any
two nodes.

- The **root** is the unique top node. Every other node has exactly one **parent** and zero
  or more **children**. A node without children is a **leaf**.
- The **depth** of a node is the number of edges from the root to it.
- The **height** of a node is the longest distance from it to a leaf in its subtree; the
  height of the tree is that of the root.
- A **subtree** is a node with all its descendants, and is itself a tree.

Trees are everywhere: directory trees, decision trees and random forests, syntax trees in
compilers, tries for routing and address lookup, and search trees.

## Binary trees and traversals

A **binary tree** gives each node at most two children, left and right.

| Traversal | Order | Useful for |
|---|---|---|
| Preorder | Node, left, right | Serialising a tree, rebuilding it from the root |
| Inorder | Left, node, right | **In a BST, lists the keys in sorted order** |
| Postorder | Left, right, node | Children before parent: deleting a tree, evaluating expressions |

## Binary search trees

Every key in the left subtree is smaller than the node, every key in the right subtree larger.

- **Search** compares with the node and goes left or right.
- **Insert** follows the search path to an empty position.
- **Delete** has three cases: a leaf (remove it), one child (splice it out), two children
  (replace with the in-order successor or predecessor).

All three cost $O(h)$. **Balanced**, $h = O(\log n)$. **Worst case**, for example inserting
already sorted keys, the tree degenerates into a linked list with $h = n$, and every
operation is $O(n)$. That is what self-balancing trees fix: they restructure after updates so
the height stays near $\log n$ **in the worst case**, not just on average.

## Rotations

A **rotation** is a local restructuring that **keeps the BST order** (the in-order sequence of
keys does not change) while changing the shape. **Single rotations** (left or right) fix
simple imbalances; **double rotations** (left-right or right-left) fix zig-zag shaped ones.

## AVL trees

The first self-balancing BST (Adelson-Velsky and Landis, 1962). **Balance condition:** at
every node, the heights of the left and right subtrees differ by **at most 1**. An insertion
or deletion that breaks it is repaired by rotations.

- Search, insert and delete all $O(\log n)$, with near-optimal height.
- Updates may need several rotations, so they cost more than in looser trees.
- Best when **searches dominate**.

## Red-black trees

Relax the balance for cheaper updates. Each node is **red or black**:

1. Every node is red or black.
2. The root is black.
3. No two adjacent red nodes (a red node has black children).
4. Every path from a node to any of its descendant leaves has the **same number of black
   nodes**.
5. The leaves are the null pointers, and they count as black.

Together these make the **longest root-to-leaf path at most twice the shortest**, so the
height is $O(\log n)$.

**Insertion.** Insert as in a BST and colour the new node **red**, then fix any violation:

| Case | Situation | Fix |
|---|---|---|
| 1 | Parent is black | Nothing to do |
| 2 | Parent red, **uncle red** | Recolour parent and uncle black, grandparent red; continue upward from the grandparent |
| 3 | Parent red, **uncle black or null** | A single or double rotation, then recolour |

**Deletion.** Delete as in a BST. If the removed node (or its replacement child) was red, the
tree stays valid; removing a **black** node can leave one path a black node short, which a
fix-up repairs by recolouring and rotations driven by the sibling's colour. Search is plain
BST search.

Red-black trees need **fewer rotations than AVL trees** and give predictable performance.
They are used in Java's `TreeMap`, C++'s `std::map` and the Linux kernel.

:::recall Why is a new node coloured red rather than black?
A red node does not change the number of black nodes on any path, so rule 4 stays true; only
rule 3 (no red parent with a red child) can break, and that is local to fix.
:::

## Splay trees

A **self-adjusting** BST. It does not keep balance at all times; instead, after every access it
**splays** the accessed node to the root. Frequently used nodes end up near the top, exploiting
locality of reference.

Splaying looks at the node, its parent and grandparent and applies one of:

- **zig**: the parent is the root, one rotation;
- **zig-zig** (or zag-zag): node and parent are both left (or both right) children, two
  rotations in the same direction;
- **zig-zag** (or zag-zig): one left and one right, two rotations in opposite directions;

repeating until the node is the root.

A single operation can take $O(n)$, but any sequence of operations runs in **amortised
$O(\log n)$** each. Simpler than AVL or red-black trees and adaptive, but with no per-operation
guarantee.

## Treaps

A **tree + heap**. Every node has a **key** (in BST order) and a **random priority** (in heap
order). The random priorities make the expected height $O(\log n)$.

- **Insert** as in a BST by key, then rotate the node up until the heap property on priorities
  holds.
- **Delete** by rotating the node down until it is a leaf, then removing it.
- **Search** is plain BST search.

Easy to implement (no balance factors, no colours) and fast in practice; the worst case is still
linear, but the expected case is logarithmic.

## Comparing balanced trees

| Tree | Balance | Cost | Strength | Weakness |
|---|---|---|---|---|
| AVL | Strict, height difference $\le 1$ | $O(\log n)$ | Fastest lookups | Costly rotations on update |
| Red-black | Loose, longest path $\le$ 2 × shortest | $O(\log n)$ | Fewer rotations, fast updates | Slightly slower lookups |
| Splay | Self-adjusting | Amortised $O(\log n)$ | Exploits locality | No worst-case guarantee per operation |
| Treap | Random priorities | Expected $O(\log n)$ | Simple | Depends on randomness |

The goal is always the same, keep the tree shallow, and the right choice depends on the
workload: read-heavy, update-heavy, repeated access, or simplicity.

## Where next

- Trees for disks, strings, space and ranges: [](guide:06-b-trees-and-specialised-trees).
- Drill: [](deck:search-trees).
