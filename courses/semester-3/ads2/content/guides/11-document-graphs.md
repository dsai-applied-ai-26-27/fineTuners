---
title: 'Document graphs, ranking and retrieval'
number: 11
topics: [document-graphs]
summary: Modelling a document collection as a graph, what edges mean, building similarity graphs by threshold or k nearest neighbours and why naive construction is quadratic, representation and dynamic updates, bounded and weighted traversal, graph-based importance and PageRank, similarity and semantic search, and retrieval as candidate selection, graph expansion and ranking, as in RAG.
takeaways:
  - Documents become nodes and relationships (similarity, citations, hyperlinks, shared metadata) become edges, directed or undirected, weighted by strength. Similarity graphs are undirected, citation and link graphs directed.
  - Building a similarity graph naively compares all pairs, $O(n^2)$. Thresholding at $\tau$ or keeping each document's $k$ nearest neighbours keeps the graph sparse, at the cost of some global structure.
  - On document graphs traversal is bounded (depth, visited count, edge weight $\ge \tau$) and weight-guided, because the goal is relevant documents, not everything reachable.
  - Importance is recursive and global, since a document is important if important documents point to it. PageRank computes it as the probability a random walker visits a page, iteratively.
  - Similarity gives local relevance, the graph gives global importance; retrieval selects candidates by similarity, expands them through the graph, and ranks the subgraph, producing context for a system such as an LLM in RAG.
sources:
  - misc/ADS REVISION.docx
---

## Why document graphs

Classic search treats each document alone: compare the query with every document, return the
matches. But documents are **related**: they cite and link to each other, discuss similar
topics, share authors, tags or venues. Modelling those relations lets algorithms use them for
search, ranking and analysis.

## The model

$$G = (V, E)$$

Each **vertex is a document**, each **edge a relationship**. Search stops being pure text
matching and becomes a **graph problem**: traverse to related documents, compute connectivity,
and above all compute **importance** from the global structure.

Graphs help in three ways: they make relationships **explicit** instead of hiding them in feature
vectors or keywords; they capture **global structure** visible only across the whole network;
and they let classical algorithms (traversal, shortest paths, centrality, clustering) apply.

### What an edge means

An edge $(u, v)$ exists when a relationship holds: **content similarity, citation, hyperlink,
shared metadata or topic**. The meaning is **problem-dependent** (academic search, web search,
recommendations). In a weighted graph $w(u, v)$ is the **strength** of the relationship.

| Graph | Direction | Typically |
|---|---|---|
| Similarity graph | Undirected (similarity is symmetric) | Weighted |
| Citation or hyperlink graph | Directed | Weighted or not, depending on the task |

Document graphs are stored **sparse**: only the most relevant edges are kept.

## Building the graph

For documents $D = \{d_1, \dots, d_n\}$: every document is a vertex, compute a relation score for
pairs, and add an edge when a condition holds:

- the score is **above a threshold** $\tau$, or
- the document is among the other's **$k$ nearest neighbours** (kNN).

The goal is a graph that is **meaningful but sparse**: dense graphs are expensive and noisy.

**Similarity graphs.** Documents are **vectors**, compared by **cosine similarity** or **dot
product**: add $(u, v)$ if $\text{sim}(u, v) \ge \tau$. Naively this compares **every pair**,
$O(n^2)$, infeasible for large collections.

**kNN graphs** connect each document only to its $k$ most similar ones. That guarantees sparsity
and a controlled number of edges, an **approximation** that may lose some global structure.

**At real scale** there are more problems: huge collections, high-dimensional vectors, long
construction, exploding memory, and $\tau$ or $k$ strongly affect both accuracy and cost. The
tension is **accuracy against time against memory**.

### Representation and change

| | Adjacency matrix | Adjacency list |
|---|---|---|
| Memory | $O(V^2)$, unrealistic for large graphs | Proportional to the edges |
| Edge lookup | Fast | Slower |
| Used | Rarely | **Preferred**: most document graphs are sparse |

Weighted lists store (neighbour, weight) pairs, and weights complicate traversal and ranking.

Collections are **dynamic**: documents are added, removed and edited, so edges must be updated
efficiently, similarities sometimes recomputed, and sparsity maintained. Building the graph is
an **ongoing process**, not a one-time job.

## Traversal with a purpose

BFS and DFS still apply, but traversal is guided by **relevance**, not just reachability: you
stop early, limit depth or cap the number of visited nodes. Constraints include **maximum depth,
maximum visited nodes and a minimum edge weight $\tau$**, so traversal becomes a **bounded
search**: follow only edges with weight $\ge \tau$, or stop after collecting $k$ documents.

Because edges are weighted, a relevance-aware traversal prefers **strong edges** and ignores weak
ones: no longer pure BFS but a heuristic-guided exploration.

**But traversal is not enough.** It answers "which documents can be reached?"; search needs
"which are **important**?". The goal shifts from full exploration to the **best results
quickly**.

## Importance and PageRank

Document graphs drive web search (hyperlinks, PageRank), academic search (citations: "important
papers are cited by important papers", Google Scholar, Semantic Scholar) and recommendation.

**A document is important if it is connected to other important documents.** The definition is
recursive: importance flows through the graph and is a **global** property. **Degree is not
enough**: many weak links need not mean importance, and a few links from important nodes can
matter more.

**Random-walk view.** A random user wanders from document to document along edges; documents
visited more often are more important. Importance becomes the **probability of being visited**.
In PageRank-style algorithms each node passes its importance to its neighbours, and the process
**repeats until the values stabilise**: an iterative algorithm, costlier than BFS or DFS because
it makes many passes over the edges.

| Graph | How importance flows |
|---|---|
| Directed (citations, links) | Along the edge direction |
| Undirected (similarity) | Symmetrically |
| Weighted | Stronger edges pass more |

So the **construction choices** (threshold, weights, sparsity) change the ranking.

### Google PageRank, then and now

In the late 1990s Google's ranking was essentially graph-based: pages as nodes, hyperlinks as
directed edges, "a page is important if important pages link to it". It beat keyword-frequency
engines, which were easy to game, by bringing **global importance, authority propagation and
resistance to keyword spam**. Then **link farms** and artificial links appeared: link structure
alone is not enough. Modern search is **hybrid**: links, content relevance, user intent and
context, freshness, behaviour and machine learning. PageRank is one signal among many, but graph
thinking stays foundational.

## Similarity and semantic search

Similarity is a **number**, not yes or no, used to compare documents, decide relatedness and
create edges. Keywords are not enough, because related documents may share few words, so each
document is mapped to a **vector that represents meaning**: similar documents lie close, others
far. Cosine similarity or the dot product gives the score. Bad similarity makes a bad graph.

**Semantic search** puts queries and documents in the **same vector space** and returns the
documents closest to the query, bridging the vocabulary gap of keyword search. But it scores only
query-document closeness, **not importance**.

**Why similarity alone is not enough:** it is pairwise and local, each comparison independent,
blind to global structure, authority and indirect relevance. Two documents equally similar to a
query cannot be told apart by similarity; the graph supplies the **global tie-breaker**.

## Retrieval as a graph problem

1. **Candidate selection:** take the documents most similar to the query, a small candidate set
   that limits the search and gives **local relevance**.
2. **Graph expansion:** explore their neighbours along edges, limited by depth, edge weight and
   number of visited nodes, giving a **relevant subgraph** rather than the whole graph.
3. **Ranking and output:** rank the subgraph by graph-based importance and pass the ordered set
   on.

Retrieval outputs **context, not answers**: the best supporting documents, which another system
may use to answer.

### LLMs and RAG

**Retrieval-augmented generation:** documents are chunked and stored in a vector store; the user's
question (sometimes rewritten into a standalone question using the chat history) retrieves
relevant chunks; the LLM answers grounded in them. Vector similarity provides the candidates, and
graph structure can improve expansion and ranking.

:::paper The summary
Documents are nodes; similarity defines local relevance; graph structure captures global
importance; retrieval is constrained graph search with ranking; and classical algorithms still
power modern retrieval, alongside embeddings and LLMs.
:::

## Where next

- Drill: [](deck:networks).
- Back to the start: [](guide:01-from-ads1-to-ads2).
