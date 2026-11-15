---
title: 'Labs: how they run, how they are graded, what to hand in'
topics: [matlab]
summary: The laboratory work policy and the lab report template in one page. The timeline of a session, the Lab Preparation and its 50% rule, what the report must contain, and a submission checklist.
takeaways:
  - Ten lab exercises of 2 points each make 20 points. Every exercise is 1 point of Lab Preparation plus 1 point of Lab Report.
  - The Lab Preparation happens once, at the start of the session, individually and without AI tools. It cannot be repeated or submitted later, whatever the reason.
  - Scoring under 50% on the preparation, or missing it, caps the report of that exercise at half its points.
  - 'The report and all MATLAB and Simulink files go to C3 as one zip within 7 days, named `DynamicModelingAndSimulation_NameSurname_Index_LEX.zip`. Late means 0 for the report.'
  - Plots are made in MATLAB from exported signals, with labelled axes. Screenshots of Scope windows are not accepted.
sources:
  - labs/DSAI_DMS_LabPolicy (1).pdf
  - labs/Lab_Report_Template_Word.docx
  - labs/Lab_Report_Template_LaTeX (1).zip
---

## At a glance

| | |
|---|---|
| Lab exercises | 10, in two sets worth 10 points each |
| Points | 2 per exercise, 20 in total |
| Split | 1 point Lab Preparation, 1 point Lab Report |
| Tools | MATLAB and Simulink |
| Report deadline | 7 days after the session, on C3 |
| Preparation | Only in the session, individual, no AI tools |

## How a session runs

1. **Minute 5:** the Lab Preparation starts, five minutes after the beginning of the
   session, and lasts a strictly limited time. Arriving late gives no extra time.
2. **Instructions:** when the preparation is over, the teaching assistant explains the
   current exercise.
3. **Practical work** in MATLAB and Simulink, in the session and, if needed, on your own
   afterwards.
4. **Within 7 days:** the Lab Report with its MATLAB and Simulink files is submitted on C3.

## The Lab Preparation

Its purpose is to get you ready for the practical work, not only to assess you. **It does
not cover the lab exercise itself**: it covers the fundamental concepts the exercise
needs. Prepare for it and the practical work becomes much easier.

It takes one of two forms:

- a **C3 quiz** with true/false, multiple-choice or matching questions;
- a **short practical task**, solved individually and submitted within the given time.

It is completed and submitted in the same session and cannot be done later.

:::warning Individual, and no AI tools
AI tools, copying, communicating with others or any other cheating during the Lab
Preparation is strictly prohibited. A student caught cheating is removed from the session
at once, may not continue the practical work, may not submit the report, may not repeat
any part later, and gets **0 points for the entire exercise**.
:::

Practise the question format with [](problems:lab-preparation-practice) and the
fundamentals with [](deck:matlab-basics).

## The 50% rule

The preparation is half of each exercise, and it also sets the ceiling for the other half.

| Preparation score | Most the report can earn | Best total for the exercise |
|---|---|---|
| 0.5 to 1.0 of 1.0 | 1.0 | preparation + 1.0 |
| below 0.5 | 0.5 | preparation + 0.5 |
| not taken (0) | 0.5 | 0.5 |

:::example The policy's own numbers
A student scores $0.4$ of $1.0$ on the preparation. That is below the threshold, so the
report is capped at $0.5$. The best possible total is $0.4 + 0.5 = 0.9$ of $2.0$.

A student misses the session. The preparation is $0$ and cannot be made up; the report,
if submitted on time, can earn at most $0.5$. Best total: $0.5$ of $2.0$.
:::

So a weak preparation costs twice: its own points, and up to half a point of the report.

## The Lab Report

Use the report template published on C3 (Word or LaTeX). It is graded on

- the correctness and completeness of the solution;
- the quality of the presented results: clear, properly labelled figures;
- the quality of the comments and explanations of the results.

The submitted files **must run without errors and reproduce the results in the report**.

### What goes in each section

| Section of the template | What to write |
|---|---|
| 1. Solution approach | How you arrived at the solutions. If a task was already worked out in the handout, describe only what is specific to your solution: no need to rederive. For a task assigned for independent work, the **full derivation of the equations** belongs here |
| 2. Block diagram of the system in MATLAB/Simulink | The Simulink model, one per task, clearly marked with its task |
| 3. Simulation results | The plots, each group with the parameter values used |
| 4. Appendix | The list of what is submitted with the report |

### Rules for the Simulink model

- Neat and easy to read: blocks arranged clearly, signal lines crossing at right angles.
- **Label all parameters (gains)** and the important model variables, such as the outputs
  of summing junctions and integrators.
- Keep the models for different tasks separate and say which belongs to which task.

### Rules for the plots

- For each group of plots, that is each simulation run, **state the parameter values**
  used in the model.
- **Export all signals to the MATLAB workspace and plot them there**, then insert the
  plots into the report.
- Label the variable on each axis, with time $t$ on the horizontal axis.
- Make sure the signals are not truncated, for instance by the Scope's default limit on
  the number of stored data points.
- If an approximate model was used, for example a linearised one, show the original and
  the approximate signals **on the same plot**, with a zoomed-in view so the quality of
  the approximation can be judged.

:::pitfall Scope screenshots
Do **not** insert screenshots of Scope windows. The template says so in bold. Plot from
the workspace instead.
:::

## Submission checklist

- [ ] The report as PDF.
- [ ] Its source document (`.doc`, `.docx` or `.tex`) with all figures used.
- [ ] Every MATLAB file (`.m`, `.mlx`) and Simulink model (`.slx`) used, each clearly
      marked with the task or part of a task it belongs to.
- [ ] The files run without errors and reproduce the report's results.
- [ ] Everything in **one** `.zip`, named
      `DynamicModelingAndSimulation_NameSurname_Index_LEX.zip`, with `X` the exercise
      number. The policy's example: `DynamicModelingAndSimulation_ElmaKandic_20000_LE1.zip`.
- [ ] Uploaded to C3 within 7 days of the session.

:::note Two file names in the material
The policy asks for `DynamicModelingAndSimulation_NameSurname_Index_LEX.zip` and warns
that submissions not following it "may not be recognized by the automated processing".
The appendix of the report template says `FirstnameLastname_LEX`. They disagree; this page
follows the policy, because it is the one tied to automated processing. Ask the teaching
assistant if in doubt.
:::

A report not submitted by the deadline is **not graded**: 0 points for the report
component. The report must be your own individual work. If copying is suspected the
teaching assistant may ask you to explain the submitted work, and both those who copy and
those who share their work get 0 points for the report.

## If you cannot attend

- Tell the person responsible for your lab group **in advance**, before the session.
- The preparation is held only at the start of the scheduled session. Absent means 0 for
  it: no replacement and no extra attempt, **regardless of the reason**.
- You may still do the exercise on your own and submit the report by the regular deadline,
  for at most half of the report points.

## Distance learning students

The same structure and the same grading apply.

1. **Lab Preparation** at the start of the online session, under supervision, with
   **screen sharing and camera on**. Any suspicion of unauthorised help scores it 0,
   without prior warning.
2. **Instructions** by the teaching assistant. This part of the meeting is recorded, so it
   can be watched again.
3. **Practical work and report**, submitted on C3 within 7 days with the same naming.

The policy closes with a line from the teaching team: "In engineering, work is not
complete until it can be explained, defended, and trusted."
