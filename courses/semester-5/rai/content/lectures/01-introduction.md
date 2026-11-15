---
title: Introduction to Responsible AI
number: 1
topics: [foundations, pillars, regulation, practice]
summary: Why AI needs to be built responsibly, a working definition, the six pillars shared by the major frameworks, how the EU AI Act and the NIST and ISO frameworks turn principles into obligations, and what responsible practice looks like across the lifecycle.
takeaways:
  - Responsible AI is designing, building, deploying and governing AI so that its benefits are shared and its harms are anticipated, measured and mitigated, across the whole lifecycle and not only in the model.
  - 'The documented failures (COMPAS, the recruiting tool, Gender Shades, Dutch childcare benefits) were socio-technical: data, objectives, deployment and oversight failed together.'
  - 'Most frameworks share six pillars: fairness, explainability, accountability, privacy and security, robustness and safety, human oversight. They trade off against each other.'
  - Group-fairness metrics such as demographic parity, equal opportunity, equalized odds and predictive parity cannot all hold at once. Choose one consciously and document why.
  - The EU AI Act scales obligations with risk to people, from prohibited uses through high-risk and limited-risk systems down to minimal risk with no new obligations.
  - Responsibility is built in at every lifecycle stage. It is not bolted on at the end, and tools and frameworks do not replace judgement.
sources:
  - lectures/Introduction_to_Responsible_AI.pptx.pdf
---

## Where this fits

This is the opening lecture of the seminar. It gives the vocabulary and the map: four
sections (why, principles, regulation, practice) that the papers presented later in the
semester will fill in. There is no mathematics beyond four probability statements about
fairness.

## How the course runs

The course is a **teaching seminar**: a subject expert meets a small group, about 10 to 20
students, for interactive study, paper presentations and guided discussion (slide 2). The
point is that students become contributors rather than listeners.

| Share | Component | What it involves |
|---|---|---|
| 50% | Homework | Projects in teams of 2 to 3 people |
| 20% | Discussion and activity | Reading and presenting papers. Presenting a paper: 5 points. Reading tests: 5 points |
| 30% | Exam | On selected topics and presentations |

Read each paper before it is presented: that is the entry ticket to the discussion
(slide 3).

**Attendance** (slide 4). Regular students may miss at most 20% of the seminars. Distance
learning students must attend at least 30%, must present a paper in person, and take the
reading test together with the exam.

:::note Two things slide 3 leaves open
The discussion component is 20% but the slide itemises only 5 + 5 points, and it does not
say how the rest is awarded. Under the exam it says the selected topics and presentations
"will be marked", which most likely means they will be pointed out during the semester.
Both are worth asking about.
:::

## Why Responsible AI

AI now shapes high-stakes decisions (slide 7):

| Domain | Typical uses |
|---|---|
| Hiring | CV screening, candidate ranking, video interviews |
| Credit and insurance | Scoring, pricing, fraud flags |
| Healthcare | Triage, imaging support, risk prediction |
| Justice and policing | Risk assessment, face recognition |
| Education | Grading, proctoring, admissions |
| Public services | Benefit eligibility, fraud detection |

When AI informs decisions about people, an error is harm to a person and not just a bug.

### Four documented failures

| Case | Year | What happened |
|---|---|---|
| COMPAS risk scores | 2016 | A ProPublica analysis found that Black defendants who did not reoffend were nearly twice as likely as white defendants to be labelled high risk |
| Recruiting tool | 2018 | Reuters reported that a CV-screening model trained on past hires learned to penalise résumés mentioning "women's". It was abandoned |
| Gender Shades | 2018 | Commercial face analysis had error rates of up to about 35% for darker-skinned women, against under 1% for lighter-skinned men |
| Dutch childcare benefits | 2021 | Algorithmic fraud-risk flags wrongly accused thousands of families; the Dutch government resigned |

The lesson drawn on slide 8: these failures were **socio-technical**. No single bug caused
them. Data, objectives, deployment and oversight each contributed.

:::recall What do the four cases have in common, in one word?
They are socio-technical failures. The cause sits in the combination of data, the objective
the model was given, how it was deployed, and the lack of oversight, not in the model alone.
:::

## A working definition

:::definition Responsible AI (slide 9)
Designing, building, deploying and governing AI so that its benefits are shared and its
harms are anticipated, measured and mitigated.
:::

The slide places **trustworthy AI** at the centre of three properties:

- **Lawful:** complies with regulation such as the GDPR and the EU AI Act.
- **Ethical:** respects rights, fairness and human autonomy.
- **Robust:** technically reliable and socially aware.

The definition covers the whole lifecycle, not only the model.

### Related terms

The terms overlap and are often used loosely. Slide 10 separates them by emphasis:

| Term | Emphasis |
|---|---|
| Responsible AI | Practices and accountability for how AI is built, deployed and used |
| Ethical AI | Moral values and principles that should guide AI: what is right? |
| Trustworthy AI | Properties a system needs to deserve trust: lawful, ethical, robust |
| Human-centred AI | A design approach that keeps human needs, control and wellbeing central |
| Explainable AI (XAI) | Techniques that make model behaviour understandable to people |

Different emphases, same goal: AI that serves people and can be held to account.

## Principles converge

From voluntary declarations to binding law in seven years (slide 12):

| Year | Document | What it is |
|---|---|---|
| 2017 | Asilomar AI Principles | 23 principles for beneficial AI, from researchers |
| 2018 | GDPR and the Montreal Declaration | Data-protection law; a civil-society declaration |
| 2019 | OECD principles and the EU High-Level Expert Group | OECD principles; 7 requirements for trustworthy AI |
| 2021 | UNESCO ethics standard | Adopted by 193 member states |
| 2023 | NIST AI RMF and ISO/IEC 42001 | A risk framework and a management-system standard |
| 2024 | EU AI Act | First comprehensive AI law; in force August 2024 |

Despite different origins the documents agree on a shared core.

## The six pillars

| # | Pillar | In one line |
|---|---|---|
| 1 | Fairness | Avoid unjustified discrimination |
| 2 | Explainability | Understand and communicate how decisions are made |
| 3 | Accountability | Clear responsibility, audit and redress |
| 4 | Privacy and security | Protect data and resist attacks |
| 5 | Robustness and safety | Reliable under real-world conditions |
| 6 | Human oversight | People stay in control |

The pillars are interdependent: improving one can cost another (slide 13). Differential
privacy adds noise, which can lower accuracy; a more complex, more accurate model is harder
to explain. (Those two illustrations are not on the slide.)

### Pillar 1: fairness

Fairness means avoiding unjustified discrimination (slide 14):

- similar people should receive similar treatment;
- outcomes should not systematically disadvantage groups defined by **protected
  attributes**: gender, ethnicity, age, disability;
- fairness is contextual, and no single definition fits every application.

The slide's illustration is a loan approval rate of 62% for group A against 41% for group B.
Fairness is a socio-technical choice: it needs stakeholders, not just a metric.

**Where bias comes from** (slide 15). It can enter at every stage:

| Stage | How bias enters |
|---|---|
| Data | Past discrimination in the records; unrepresentative samples; noisy or biased labels |
| Model | The objective ignores subgroups; proxies such as postcode; optimised for the majority |
| Deployment | A different population than in training; use outside the intended scope; over-trust by users |
| Feedback loop | Predictions shape future data; errors reinforce themselves; hard to notice from inside |

:::pitfall "We removed the protected attribute, so the model is fair"
Removing the attribute is not enough: **proxies** leak it back in. A postcode can stand in
for ethnicity, and the wording of a CV for gender, as in the recruiting tool.
:::

**Measuring fairness** (slide 16). Write $\hat Y$ for the model's prediction, $Y$ for the
true outcome and $A$ for the protected attribute with groups $a$ and $b$. (The slide uses
these symbols without defining them.)

| Metric | Requirement | In words |
|---|---|---|
| Demographic parity | $P(\hat Y = 1 \mid A = a) = P(\hat Y = 1 \mid A = b)$ | Same positive rate in every group |
| Equal opportunity | $P(\hat Y = 1 \mid Y = 1, A = a) = P(\hat Y = 1 \mid Y = 1, A = b)$ | Same true-positive rate for qualified people |
| Equalized odds | Equal TPR and equal FPR across groups | Same error profile for every group |
| Predictive parity | $P(Y = 1 \mid \hat Y = 1, A = a) = P(Y = 1 \mid \hat Y = 1, A = b)$ | A positive prediction means the same in every group |

TPR is the true-positive rate and FPR the false-positive rate. The metrics **cannot all hold
at once**: choose consciously and document why.

:::example Worked numbers (not in the slides)
A loan model is applied to 100 people in each of two groups.

| | Group a | Group b |
|---|---|---|
| Qualified ($Y = 1$) | 50 | 20 |
| Qualified and approved | 40 | 16 |
| Unqualified and approved | 10 | 16 |
| Approved in total | 50 | 32 |

- Positive rate: $50/100 = 0.50$ against $32/100 = 0.32$. Demographic parity **fails**.
- TPR: $40/50 = 0.80$ against $16/20 = 0.80$. Equal opportunity **holds**.
- FPR: $10/50 = 0.20$ against $16/80 = 0.20$. With equal TPR, equalized odds **holds**.
- Precision: $40/50 = 0.80$ against $16/32 = 0.50$. Predictive parity **fails**.

The model makes errors at the same rates in both groups, yet approves group a more often
and an approval is more trustworthy there. The reason is the different share of qualified
people (50% against 20%). This is the conflict the slide's last line refers to; the
references list the papers that prove it (Chouldechova 2017; Kleinberg, Mullainathan and
Raghavan 2017).
:::

### Pillar 2: transparency and explainability

The picture on slide 17 is input, black-box model, prediction, and then an explanation
attached to the prediction. Two routes:

- **Intrinsic:** use interpretable models where possible: linear models, decision trees,
  rule lists.
- **Post-hoc:** explain a complex model afterwards: SHAP, LIME, Grad-CAM, counterfactual
  examples.

The explanation has to fit its audience. Users need actionable reasons, regulators need
evidence, developers need debugging insight. An explanation is only useful if the person
receiving it can act on it.

### Pillar 3: accountability and documentation

Who answers for the system? What is needed (slide 18):

- a named accountable owner for every system;
- audit trails: data sources, versions, decisions;
- redress: people can contest and appeal outcomes;
- independent audits before and after launch.

Three documentation tools make this concrete:

| Document | Records |
|---|---|
| Datasheets for datasets | Origin, collection, intended use, known gaps |
| Model cards | Intended use, metrics per subgroup, limitations |
| Impact assessments and audits | Risks to people, mitigations, sign-off |

If nobody is accountable, the system is not responsible, however good the model.

### Pillar 4: privacy and security

| Privacy | Security |
|---|---|
| Data minimisation and purpose limitation (GDPR) | Adversarial examples: tiny changes flip predictions |
| Differential privacy: calibrated noise protects individuals | Data poisoning: corrupt the training set |
| Federated learning: train without centralising data | Prompt injection in LLM-based applications |
| Threats: membership inference, model inversion, memorised training data | Model theft and unauthorised extraction |

The rule of thumb from slide 19: collect less data, protect what you keep, and assume the
model can be attacked.

### Pillar 5: robustness, safety and reliability

Three ways real conditions differ from the test set (slide 20):

- **Distribution shift:** deployment data differs from training data, through a new
  population, season or sensor.
- **Adversarial and edge cases:** rare inputs or small, targeted changes cause confident
  errors.
- **Uncertainty and fallback:** the remedy side: calibrated confidence, abstention and
  graceful degradation.

Practices: stress testing and red-teaming, continuous monitoring and drift detection,
incident reporting and a rollback plan. Test where the system is most likely to fail, not
only on the average case.

### Pillar 6: human agency and oversight

| Mode | The human's role |
|---|---|
| Human-in-the-loop | A person approves or reviews each decision |
| Human-on-the-loop | A person monitors the system and can intervene |
| Human-in-command | People decide whether and how the system is used at all |

:::warning Automation bias
People over-trust confident output. Meaningful oversight needs time, training, authority
and the ability to say no. A human in the loop is only oversight if they can really
disagree (slide 21).
:::

### Beyond the individual model

Slide 22 widens the view to society and the environment:

- **Energy and resources:** training and serving large models consume significant energy
  and water.
- **Labour:** data labelling and content moderation work; job displacement and change.
- **Information ecosystem:** deepfakes, misinformation and synthetic content at scale.
- **Concentration of power:** compute, data and expertise sit with few organisations.

Responsible AI asks who benefits, who pays, and who is left out.

## Regulation and frameworks

### The EU AI Act: a risk-based approach

Obligations scale with risk to people (slide 24):

| Risk tier | Consequence | Examples |
|---|---|---|
| Unacceptable | Prohibited | Social scoring, manipulation, some biometric uses |
| High | Strict obligations | Hiring, credit, education, policing, infrastructure |
| Limited | Transparency duties | Chatbots and AI-generated content must be disclosed |
| Minimal | No new obligations | Spam filters, video games |

Know which tier a system is in; it decides what must be done.

:::recall A university wants an AI system that ranks applicants for admission. Which tier?
High risk: education is on the high-risk list, so strict obligations apply. A chatbot that
answers applicants' questions would be limited risk and would have to disclose that it is
an AI.
:::

### NIST AI RMF and ISO/IEC 42001

The NIST AI Risk Management Framework has four functions (slide 25). **Govern** spans the
other three: culture, policies, roles and accountability across the organisation.

| Function | What it does |
|---|---|
| Map | Understand context, intended use, stakeholders and potential impacts |
| Measure | Assess, test and track risks with metrics and evaluations |
| Manage | Prioritise and treat risks, respond to incidents, keep improving |

**ISO/IEC 42001 (2023)** is a certifiable AI management-system standard: policies, roles,
risk assessment, improvement.

Frameworks give a repeatable process, not a guarantee of good outcomes.

## Responsible AI in practice

### Checks at every lifecycle stage

| Stage | Checks |
|---|---|
| 1. Problem framing | Is AI needed? Who is affected? |
| 2. Data | Representative? Consent and provenance |
| 3. Modelling | Set objectives and constraints. Prefer the simpler model if performance is equal |
| 4. Evaluation | Metrics per subgroup. Red-teaming |
| 5. Deployment | Human oversight. User information, appeals |
| 6. Monitoring | Drift and incidents. Periodic audit; retire |

Responsibility is built in, not bolted on at the end (slide 27).

### A starter toolkit

Open-source tools named on slide 28:

| Purpose | Tools |
|---|---|
| Fairness | Fairlearn, AI Fairness 360 |
| Explainability | SHAP, LIME, Captum, InterpretML |
| Privacy and robustness | Opacus (differential privacy), Adversarial Robustness Toolbox |
| Documentation | Model Cards Toolkit, Datasheets template |

Tools help to measure and document; they do not replace judgement.

### Impact assessment checklist

Eight questions to ask before deployment (slide 29). No clear answer yet means the system
is not ready to deploy.

1. **Purpose.** What decision does it make or support, and who is affected?
2. **Alternatives.** Is a simpler or non-AI approach sufficient?
3. **Data.** Is the data lawful, representative and documented?
4. **Fairness.** Have we measured performance per subgroup?
5. **Explainability.** Can affected people get a meaningful explanation?
6. **Oversight.** Who can intervene and override, and how?
7. **Safety and security.** What happens when it fails or is attacked?
8. **Redress.** How can a person contest an outcome?

### Case study: an AI hiring tool

| Step | What happened |
|---|---|
| Data | Ten years of résumés, mostly from men |
| Model | Learns that the patterns of past hires predict "success" |
| Outcome | Women's résumés downgraded; tool abandoned |
| Lesson | Audit the data, test by subgroup, keep humans decisive |

What responsible practice would have added: a pre-deployment bias audit, a recruiter who
always decides, and ongoing monitoring of outcomes. The slide's source is Reuters (2018),
and it notes that the company stated the tool was never the sole basis for decisions.

Historical data encodes historical bias; models then scale it (slide 30).

### Open challenges

Where the field is unsettled (slide 31):

- **Trade-offs:** accuracy, fairness, privacy and explainability can pull in different
  directions.
- **Generative AI:** hallucination, provenance, copyright and misuse are hard to evaluate.
- **Measurement:** benchmarks rarely capture real-world harm to real people.
- **Global differences:** values and laws differ across regions and cultures.
- **Supply chains:** who is accountable when models are fine-tuned by third parties?
- **Ethics washing:** principles on paper without practice in the product.

Responsible AI is ongoing work, not a checklist one finishes.

## Questions for the room

The lecture closes with three discussion prompts (slide 33). A seminar grade includes
discussion, so have a position on each.

1. **Which pillar is hardest?** Which of the six would be hardest to achieve in your own
   domain, and why?
2. **Who is accountable?** When an AI-assisted decision harms someone, who should answer
   for it: developer, deployer or user?
3. **Accuracy or fairness?** Would you accept a slightly less accurate model if it were
   measurably fairer? Who decides?

## What an exam wants

The exam is "on selected topics and presentations". From this lecture the natural
questions are definitions, lists with one line each, and applying a framework to a case.

:::paper Define Responsible AI
Responsible AI is designing, building, deploying and governing AI so that its benefits are
shared and its harms are anticipated, measured and mitigated. It covers the whole
lifecycle, and aims at trustworthy AI: lawful, ethical and robust.
:::

:::paper Apply the pillars to a case
Name the case's failure, then walk the pillars that were violated, one sentence each, and
end with what practice would have prevented it. For the hiring tool: the training data
encoded past bias (fairness); nobody audited it before launch (accountability); the remedy
is a bias audit, testing per subgroup and a recruiter who always decides (human oversight).
:::

## Where next

- Drill: [](deck:introduction).
- Definitions: [the glossary](glossary).
- Mnemonics for the lists: [the memory page](memory).
- The slide deck's reference list (slide 34) names the papers behind every case and metric
  here, starting with Angwin et al. (2016), Buolamwini and Gebru (2018), Mitchell et al.
  (2019) and Gebru et al. (2021).
