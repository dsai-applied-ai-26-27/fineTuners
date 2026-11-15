---
title: 'Social graphs, power laws and epidemic spread'
number: 10
topics: [social-graphs]
summary: Social networks as directed or undirected graphs, why their structure breaks the assumptions of classical algorithm analysis, the small world (six degrees, Milgram, Bacon and Erdős numbers), sparsity and clustering, rich-get-richer link formation, power-law degree distributions and scale-free networks, and epidemic spread with its threshold.
takeaways:
  - A social graph has people as nodes and relationships as edges; undirected for mutual ties (friendship), directed for asymmetric ones (following, citing).
  - Social graphs are huge but sparse, decentralised and highly clustered, and they are small worlds, with average path lengths of around six even among billions of people.
  - 'Links form by local rules (friends of friends, visibility, popularity), giving rich-get-richer dynamics and a power-law degree distribution $p(x) = c\,x^{-\alpha}$: a straight line of slope $-\alpha$ on a log-log plot.'
  - Scale-free means no typical degree, so averages mislead, workloads are unbalanced and average-case analysis can be wrong.
  - Epidemics spread like a probabilistic BFS. Random graphs have a clear epidemic threshold; in scale-free networks the hubs push it to essentially zero, so even weak spreading persists.
sources:
  - misc/ADS REVISION.docx
---

## Social networks as graphs

Facebook, Instagram, TikTok, LinkedIn: in computer science a social network is a **graph**,
**nodes** for people or entities and **edges** for relationships or interactions. That lets
graph algorithms analyse relationships, information flow, influence and spreading.

Unlike most graphs in algorithms courses, social graphs are **built by human behaviour**, not
designed, which makes them irregular, dynamic and hard to model.

- **Undirected** when the tie is mutual: Facebook friendship, actors in the same film.
- **Directed** when it is not: following on Twitter or Instagram, citing a paper.

They are among the **largest graphs ever built**, billions of users and connections, and they
change constantly. At that scale even simple algorithms behave unexpectedly.

### Why the structure matters

Algorithm analysis often assumes a fixed, well-behaved graph: uniform degrees, balanced work per
node, meaningful averages. Social graphs break those assumptions; their **structure is part of
the input**, and misreading it gives wrong conclusions about performance.

## The small world

**The small-world phenomenon:** even in huge networks, distances are surprisingly short. Studied
since the 1960s.

- **Six degrees of separation:** any two people are linked by a chain of about six
  acquaintances. Two properties: **small average path length** despite enormous size, and **high
  reachability**.
- **Milgram's experiment** (late 1960s): letters forwarded only through personal contacts reached
  a target with about **six intermediaries** on average. Real networks are **navigable**: short
  paths can be found without global knowledge.
- **Kevin Bacon numbers:** actors linked by shared films; almost all have a Bacon number of 4 or
  less. **Erdős numbers:** researchers linked by co-authorship; most are below 6.
- **Online:** studies of Facebook, hundreds of millions of users and tens of billions of
  friendships, found most pairs within a handful of steps. Small worlds are a fundamental
  property, not an artefact.

## Key properties

| Property | Meaning |
|---|---|
| Large but **sparse** | Each node connects to a tiny fraction of the others |
| **Decentralised** | No controlling node |
| **Highly clustered** | Friends of friends tend to know each other |

These set social graphs apart from classical random graphs.

**How links form.** Not at random but by **local rules**: people connect to friends of friends,
visibility matters, popular people attract more connections. That gives **rich-get-richer**
dynamics: well-connected nodes get even more connected.

**Network inequality.** Most users have very few connections; a few have enormous numbers. The
inequality is structural, and it shapes how the network behaves.

## Power laws and scale-free networks

The degree distribution often follows a **power law**: the probability that a node has degree
$x$ is

$$p(x) = \frac{c}{x^{\alpha}} = c\,x^{-\alpha}, \qquad \log p(x) = \log c - \alpha \log x,$$

so on a **log-log plot** it is a straight line with slope $-\alpha$ (the power-law exponent).

- There is **no typical node**.
- **Extreme values dominate** the system.
- **Averages are misleading.**

Such networks are **scale-free**: there is no characteristic scale of degree, and the
distribution looks the same if you zoom in or out. That self-similarity distinguishes it from a
normal distribution.

**Power laws everywhere:** web links, citations, city sizes, wealth; **Zipf's law** and the
**Pareto distribution** are classic examples. Extreme inequality is the norm.

**Why they break classical assumptions:** degrees are not uniform, the average degree is not
representative, workload is very unbalanced, and average-case analysis can mislead. The same
algorithm can behave very differently on a social graph than on a random graph.

## Epidemic spread

Spreading of diseases, information, rumours or behaviour is a **graph process**: nodes are
**susceptible**, **infected** or **recovered**, and infected nodes can infect their neighbours.
It resembles a **BFS with probabilities**, where structure decides how far and how fast it goes.

**Epidemic threshold:** a minimum spreading strength below which an outbreak dies out and above
which it spreads widely.

| | Random networks | Scale-free networks |
|---|---|---|
| Degrees | Similar | Very unequal; hubs |
| Spread | Fairly uniform | Dominated by hubs |
| Threshold | Clear, positive | **Effectively zero** |

**"The threshold goes to zero"** means even very weak spreading can persist: epidemics start
easily and are hard to stop, because the structure amplifies them.

**Real consequences.** Misinformation spreads faster than true information because networks
amplify extreme nodes. In COVID-19 most infected people infected nobody, while a few
**super-spreaders** caused most transmissions.

:::paper The takeaway
Real graphs are not random. Social networks are huge yet distances are short, connectivity is very
unequal, and a few nodes dominate. Average-case assumptions fail, the same algorithm behaves
differently depending on the structure, and epidemic spread is a general graph process. In one
line: **social networks are scale-free small-world graphs, and their power-law degrees change
how algorithms and spreading behave.**
:::

## Where next

- Drill: [](deck:networks).
- Graphs of documents: [](guide:11-document-graphs).
