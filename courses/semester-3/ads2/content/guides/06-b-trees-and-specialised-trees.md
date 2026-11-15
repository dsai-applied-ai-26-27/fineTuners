---
title: 'B-trees and specialised trees'
number: 6
topics: [multiway-trees]
summary: Why binary trees are slow on disk, multiway B-trees with their structural rules, search and node splitting, B+ trees and why databases use them, and the specialised trees for strings (tries, suffix trees), points (KD trees) and ranges (segment trees), with a comparison table of every tree in the course.
takeaways:
  - On disk the bottleneck is page reads, not comparisons. A B-tree packs many keys into one node the size of a disk page, so the tree is only a few levels deep.
  - 'A B-tree of order $m$: at most $m$ children and $m - 1$ keys per node; every internal node except the root at least $\lceil m/2 \rceil$ children ($\lceil m/2 \rceil - 1$ keys); the root at least two children unless it is a leaf; all leaves on the same level.'
  - Insertion goes into a leaf; a full node splits and promotes its middle key. Only a root split makes the tree taller.
  - A B+ tree keeps all records in the leaves and links the leaves left to right, which makes range queries a single descent plus a scan. PostgreSQL, MySQL InnoDB and SQLite use B+ trees.
  - A trie searches in time proportional to the query length; a suffix tree finds a pattern of length $m$ in $O(m)$; a KD tree splits by a different coordinate at each level; a segment tree answers range queries and updates in $O(\log n)$.
sources:
  - misc/ADS REVISION.docx
---

## Why binary trees are not enough

BSTs, AVL, red-black and splay trees and treaps assume nodes live in **memory**, where
following a pointer is cheap. Databases and file systems keep data on **disk or SSD**, where an
access is orders of magnitude slower than RAM. The bottleneck becomes **disk I/O**: a binary
tree stores one key per node, so every pointer jump may load a new disk page.

**The idea of multiway trees:** store **many keys in one node**, sized to fit a disk page. One
read brings in a whole range of keys, the comparisons inside the page are fast, and the tree
becomes very shallow.

## B-trees

A **multiway, balanced search tree** for large data on secondary storage. Nodes hold many sorted
keys and many children, and **all leaves are at the same depth**.

A node with $k$ children stores exactly $k - 1$ keys, which act as **separators** for the
ranges of its child subtrees.

**Rules for a B-tree of order $m$:**

| Rule | |
|---|---|
| Children per node | At most $m$ |
| Children per internal node (not the root) | At least $\lceil m/2 \rceil$ |
| Root | At least 2 children, unless it is a leaf |
| Keys per node | At most $m - 1$; at least $\lceil m/2 \rceil - 1$ except the root |
| Leaves | All on the same level |

These guarantee a logarithmic height and balance.

**Why it is fast on disk.** Reading a whole page costs little more than reading part of it, so
one read brings in dozens or hundreds of keys and child pointers. Fewer pointer jumps, a tiny
height: often **2 to 4 levels** even for billions of records.

**Search.** From the root, compare the key with the keys in the node to find its range, follow
that child, and repeat down to a leaf. Most work is done **inside** nodes, not across pages.

**Insertion.** Always into a leaf, in sorted position. If the leaf is full it **splits**:

1. The keys are divided into two nodes.
2. The **middle key moves up** to the parent.
3. The two halves become children of the parent.

If the parent overflows, the split propagates upward. If the **root** splits, a new root is
created and the height grows by one: the **only** way a B-tree gets taller, which is why it
stays shallow.

## B+ trees

A refinement for **range queries and scans**:

- **all data records live in the leaves**;
- internal nodes hold only keys and pointers (a guide for the search);
- the **leaves are linked** left to right.

For `SELECT * FROM table WHERE key BETWEEN 100 AND 200`: find the first key of the range with
one descent, then **follow the leaf links** to collect the rest in order. In a plain B-tree the
range can be spread over internal and leaf nodes and need repeated traversals. This is why
**most databases use B+ trees**: PostgreSQL, MySQL (InnoDB), SQLite, and many file systems.

**Height in practice.** Branching factors of 100 to 1000 mean:

| Height | Keys reachable (order of magnitude) |
|---|---|
| 1 | Hundreds |
| 2 | Tens of thousands |
| 3 | Millions |
| 4 | Billions |

So even very large tables have B+ tree height 2 to 4: a handful of disk reads per query.

## Specialised trees

Not every search problem is numeric keys on disk.

### Tries (prefix trees)

Store strings character by character: each edge is a character and each node a **prefix**. A
search costs time proportional to the **length of the query**, not the number of stored strings.
Words with a common prefix share a branch, so prefix queries are very fast. Uses: autocomplete,
spell checking, dictionaries, IP routing (longest prefix match).

### Suffix trees

A **compressed trie of all suffixes** of a string. Once built, finding a pattern of length $m$
takes $O(m)$, whatever the length of the text. Construction is complex and memory-heavy, the
queries extremely fast. Uses: text indexing, pattern matching, DNA sequence analysis.

### KD trees

Store points in $k$-dimensional space, splitting by a **different coordinate at each level**:
in 2-D, level 0 by $x$, level 1 by $y$, level 2 by $x$ again. Built by taking the **median** of
the active coordinate at each level. Good for nearest-neighbour and spatial queries in low
dimensions; they degrade in high dimensions (the **curse of dimensionality**).

### Segment trees

Each node covers a **segment of an array** and stores an aggregate of it (sum, minimum, maximum,
count). Build $O(n)$, range query $O(\log n)$, update $O(\log n)$. Common in competitive
programming and interval problems.

## Every tree of the course

| Tree | Purpose | Stores | Balance / height | Search, insert, delete | Strength | Weakness | Typical use |
|---|---|---|---|---|---|---|---|
| Binary tree | Hierarchy | Anything | Not ordered | Varies | Simple | No fast search | Expression and parse trees |
| BST | Ordered search | Keys | Unbalanced | $O(h)$ | Simple, sorted traversal | Degrades to $O(n)$ | Basic dictionaries |
| AVL | Fast search | Keys | Strict | $O(\log n)$ | Very fast lookup | Costly rotations | Read-heavy systems |
| Red-black | Balanced search | Keys and colour | Loose | $O(\log n)$ | Fewer rotations | Lookup slightly slower than AVL | `TreeMap`, `std::map` |
| Splay | Adaptive access | Keys | Self-adjusting | Amortised $O(\log n)$ | Exploits locality | No worst-case guarantee | Caches, repeated access |
| Treap | Randomised balance | Keys and priority | Expected balanced | Expected $O(\log n)$ | Simple | Depends on randomness | Competitive programming |
| B-tree | Disk search | Keys and children | Perfectly balanced | $O(\log n)$ disk reads | Very shallow | Complex | Database indexes |
| B+ tree | Disk and ranges | Keys inside, records in leaves | Perfectly balanced | $O(\log n)$ disk reads | Fast range scans | Slightly more space | Databases, file systems |
| Trie | Prefix search | Characters | Height = key length | $O(m)$ | Fast prefix queries | Memory-heavy | Autocomplete |
| Suffix tree | Substring search | All suffixes | Height = string length | $O(m)$ | Very fast substring queries | Complex, large | Text indexing, bioinformatics |
| KD tree | Spatial search | $k$-D points | Balanced (static) | Average $O(\log n)$ | Nearest neighbours | Poor in high dimensions | GIS, robotics |
| Segment tree | Range queries | Aggregates | Balanced | $O(\log n)$ | Fast queries and updates | Extra memory | Range sum, min, max |

There is **no universal tree**: each one is designed for one class of search problems.

## Where next

- Drill: [](deck:search-trees).
- Next lecture: [](guide:07-dynamic-programming).
