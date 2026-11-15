---
title: 'Week 2: from an AI idea to an evaluable project'
number: 2
topics: [design]
summary: The eight parts of a complete Applied AI project, the difference between a domain, a problem, an AI task and a technology, how to narrow a broad idea into something that can be evaluated, and what to check about data, baseline and metrics before building anything.
takeaways:
  - 'A project has eight parts: stakeholder, problem, data, AI task, baseline, method, evaluation, risk. The model is one of them.'
  - Start with the problem, and plan the evaluation before the implementation.
  - Domain, problem, AI task, technology and output are five different things. Remove the words AI, machine learning, chatbot and deep learning from a topic and a meaningful problem must remain.
  - A strong topic names the user, the data, the task, the comparison, the metric and the boundary of the study.
  - Data and baseline come before model ambition. Choose the metric by the consequence of an error, and report more than one view.
sources:
  - lectures/Applied_AI_Week_02_Project_Design.pptx
---

## Where this fits

Week 2 is a working session, a "seminar studio": by the end of it each student has an
**initial project concept**, written into a project canvas on Moodle, reviewed by a peer
and pitched. The outcome is "one feasible concept, not a final approved topic" (slide 2).
It is the first deliverable of the seminar schedule in
[](guide:seminar-work-guidelines): a statement of interest or initial topic proposal.

## The anatomy of an Applied AI project

Eight parts, each with one question (slide 3):

| # | Part | The question it answers |
|---|---|---|
| 1 | Stakeholder | Who needs the result? |
| 2 | Problem | What is difficult today? |
| 3 | Data | What evidence is available? |
| 4 | AI task | What output is required? |
| 5 | Baseline | What is the simple comparison? |
| 6 | Method | What approach will be tested? |
| 7 | Evaluation | How will success be measured? |
| 8 | Risk | Where can the system fail? |

Two rules come with it: **a model is one component; the project is the complete chain of
reasoning and evidence**, and **start with the problem, plan evaluation before
implementation**.

## Five things students mix together

| Element | What it is | The slide's example |
|---|---|---|
| Domain | The application context | Education |
| Problem | A real need that exists without AI | Students struggle to find rules in university documents |
| AI task | The technical input-output problem | Information retrieval and question answering |
| Technology | The tools used to implement the task | Sentence embeddings, vector search, a language model |
| Output | What the user receives | An answer with cited sources |

:::tip The topic test
Remove the words *AI*, *machine learning*, *chatbot* and *deep learning* from your topic.
Does a meaningful problem remain? If not, what you have is a technology looking for a
problem.
:::

:::recall "Build a RAG chatbot with vector search." Which of the five elements does this name?
Only the technology, and loosely the AI task. It has no domain, no problem that exists
without AI, and no stated output for a user. It fails the topic test.
:::

## A worked example: the university document assistant

The initial concept, as a question: *can semantic retrieval help students find
source-supported answers in a controlled collection of public university regulations?*

| Part | For this project |
|---|---|
| Stakeholder | Students and student services |
| Input | A question, and public university documents |
| Output | Relevant passages, and an answer with sources |
| AI task | Retrieval; optionally controlled generation |
| Baseline | Keyword or BM25 search |
| Method | Sentence embeddings with vector search |
| Evaluation | Recall@k, answer support, latency |
| Main risk | Unsupported or outdated answers |

"Evidence, not interface polish, determines whether the idea works" (slide 5).

## From a broad idea to an evaluable topic

| Broad idea | Evaluable version |
|---|---|
| Build a chatbot for students | Compare keyword search and semantic retrieval for answering questions from a fixed set of university regulations |
| Use AI to recognize images | Evaluate transfer learning for classifying six categories in a licensed image dataset, including class-level error analysis |
| Predict student success | Compare interpretable classification models for a defined educational outcome using a public dataset and fairness checks |

What changes from left to right: the right-hand version **names the user, data, task,
comparison, metric and boundary of the study** (slide 6). Each one has a comparison built
in ("compare", "evaluate … including error analysis"), which is what makes it evaluable.

## Six project areas

| # | Area | Typical tasks |
|---|---|---|
| 1 | Language and document AI | Search, classification, summarisation, controlled question answering |
| 2 | Computer vision | Classification, detection, segmentation, quality analysis |
| 3 | Predictive analytics | Tabular classification, regression, explainability |
| 4 | Time series and anomalies | Forecasting, unusual-pattern detection, sensor data |
| 5 | Recommendation | Ranking, personalisation, coverage, cold start |
| 6 | AI systems and monitoring | Pipelines, drift, reliability, deployment risks |

You rank your top three. The ranking informs provisional teams; it does not lock the final
topic.

## Technology comes after the task

| For | Tools named on the slide | Used for |
|---|---|---|
| Tabular ML | pandas, scikit-learn, XGBoost | Classification, regression, explainability |
| Language | Hugging Face, sentence-transformers, spaCy | Classification, embeddings, retrieval |
| Computer vision | PyTorch, torchvision, OpenCV | Classification, detection, image processing |
| Time series | pandas, statsmodels, sktime | Forecasting, anomalies, temporal validation |
| Prototype | Jupyter, Streamlit, FastAPI | Analysis, demonstration, simple interfaces |
| Collaboration | Git, GitHub, MLflow or simple experiment logs | Versioning, evidence, reproducibility |

The rule: **use the smallest stack that lets you test the project question reliably**.

## Feasibility: data and baseline before model ambition

**Data check**

- Who created the dataset, and why?
- Can we legally and ethically use it?
- Are labels, fields and units understood?
- Does it represent the intended setting?
- Is the dataset large and complete enough?
- Could leakage make results look better than reality?

**Baseline check**

- What is done today without the proposed model?
- What simple rule or statistical method is reasonable?
- Can a majority, mean, naive, keyword or popularity baseline work?
- How much improvement would justify the extra complexity?
- What cost, latency or maintenance trade-off matters?

:::note Why a baseline, in one line
Not on the slide in these words: a score means nothing alone. "82% accuracy" is good if
always guessing the majority class gets 60% and worthless if it gets 81%.
:::

## Evaluation: match the metric to the consequence of error

| Task | Metrics | The question behind them |
|---|---|---|
| Classification | Precision, recall, F1, confusion matrix | Which mistakes matter most? |
| Regression | MAE, RMSE, error distribution | How costly are large errors? |
| Forecasting | MAE or RMSE with a temporal split and a naive forecast | Does it beat the future-blind baseline? |
| Retrieval | Recall@k, precision@k, source relevance | Are useful passages near the top? |
| Recommendation | Precision@k, coverage, diversity | Is the list useful beyond popular items? |
| Generative output | Correctness, source support, task success | Are claims supported and useful? |

**Report more than one view:** the score, the baseline, error examples and limitations
(slide 10).

## The studio: the project canvas

On Moodle, under "Week 2 - Project Interest and Initial Concept":

1. **Rank project areas:** first, second and third preference.
2. **Draft the concept:** stakeholder, problem, input, output, data, baseline, metric, risk.
3. **Keep the form open:** do not submit before peer review and the final instruction.

Work individually before the peer review.

:::paper The sentence pattern for a concept
"For **[target user]**, we will use **[input data]** to support **[specific task or
decision]** by producing **[output]**. We will compare it with **[baseline]** and evaluate
it using **[metric]**."

Filled in for the worked example: "For students and student services, we will use public
university regulations to support finding the rule that answers a question, by producing
relevant passages and an answer with sources. We will compare it with keyword (BM25)
search and evaluate it using Recall@k and answer support." (The filled-in sentence is
assembled here from slide 5.)
:::

## Peer review and the pitch

**Questions a reviewer asks**

- Is the problem clear after one reading?
- Is the data realistically available?
- Is there a meaningful baseline?
- Can success be measured?
- What is the single most important improvement?

**The lightning pitch answers four**

- Who has the problem?
- What data and output are involved?
- What is the baseline?
- How will you evaluate success?

## Before week 3

- [ ] Revise the canvas after the peer review.
- [ ] Identify one realistic **primary dataset** and one **backup** candidate.
- [ ] Find **two reliable sources**.
- [ ] Explain feasibility in 3 to 5 sentences.
- [ ] Submit the Moodle form only when instructed.

## Where next

- Drill: [](deck:project-design).
- The whole seminar, its criteria and its schedule: [](guide:seminar-work-guidelines) and
  [](exam:seminar).
