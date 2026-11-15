---
title: Course map
summary: How Robotics Fundamentals is organised and graded, the units it covers, the software used in the labs, and the literature.
sources:
  - lectures/Course Overview.pdf
---

## Organisation

From the course overview of 6 October 2026 (slides 2 and 3).

- **Staff:** Assistant Professor Nermin Čović (responsible teacher), Full Professor Bakir
  Lačević (teacher) and teaching assistant Elma Kandić-Brdar. Consultations are by
  arrangement over email.
- **Lectures:** 30 hours, 3 hours a week, Tuesday 12:00 to 15:00 in classroom 2-03 (S-8).
  In class with a two-way live stream; recordings go on the courseware page.
- **Lab exercises:** 10 hours, 2 hours a week for 5 weeks. Three groups, two on site and
  one online for distance learning. Each lab has a 20-minute video introduction.
- **Seminar:** 10 hours of independent or team work on a selected robotics topic.

:::warning Labs are assessed by demonstration
Each student demonstrates and explains their own work in the lab (slides 3 and 7). Being
able to explain the solution counts, not only having one.
:::

## Grading

| Component | Points | Notes |
|---|---|---|
| Midterm | 30 | During the semester |
| Final exam | 30 | After 15 weeks. Worth 60 if it also covers the midterm part |
| Seminar | up to 30 | Oral presentations of seminar work progress during the semester |
| Lab exercises | up to 10 | Oral presentations of assignments; up to 5 extra points |
| Lecture attendance | up to 5 extra | |

Exams carry 60% of the grade, homework and coursework 40% (slide 11). The seminar is worth
as much as an exam, so it deserves the same planning.

| Points | 0 to 54 | 55 to 64 | 65 to 74 | 75 to 84 | 85 to 94 | 95 to 100 |
|---|---|---|---|---|---|---|
| Grade | No pass | 6 | 7 | 8 | 9 | 10 |

:::note What the overview does not say
No dates for the midterm, no exam format, and no list of seminar topics. Until that is
known there is no exam plan on this site.
:::

## The units

The names in brackets are the topic labels used on this site (slides 5 and 6).

**Part I**

1. General introduction to robotics; robotics overview and applications
   ([](topic:intro))
2. Short survey and classification of sensors and actuators ([](topic:sensors))
3. Position and orientation of a rigid body: transformations ([](topic:transformations))
4. Kinematics of robotic manipulators, direct and inverse ([](topic:kinematics))
5. Differential robot kinematics and applications of the Jacobian matrix
   ([](topic:diffkin))

**Part II**

6. Robot trajectory and motion planning ([](topic:planning))
7. Dynamics of robotic manipulators ([](topic:dynamics))
8. Robot control: decentralized, centralized, force and impedance control
   ([](topic:control))
9. Short introduction to AI reasoning in robotics, introduction to probabilistic robotics,
   task planning ([](topic:ai))
10. Robot vision ([](topic:vision))

Lecture 1 already names most of these in passing: the Jacobian, singularities, impedance
control and path against trajectory all appear in [](lecture:01-introduction-to-robotics)
as previews.

## What the course aims at

Five learning outcomes (slides 8 and 9):

| Outcome | Students learn to |
|---|---|
| Modeling | Build mathematical models of robot systems from geometry, kinematics, statics and dynamics, and use them to analyse behaviour |
| Design | Design robot systems for specific tasks, weighing speed, accuracy, payload capacity, sensors and actuators |
| Planning | Plan robot motion, including basic motion planning and obstacle and collision avoidance |
| Control | Apply basic control concepts, including feedback control and trajectory tracking |
| Programming | Program robotic systems in high-level languages such as MATLAB, Python and C++ |

## Software and tools

The labs are about implementation, simulation, visualisation and robot programming
(slide 7), with:

- MATLAB and Simulink
- ROS1 and ROS2
- Gazebo, RViz, MoveIt and BabaCad
- RPMPLv2 and xarm6-etf-lab

A reference list of MATLAB functions is in [](guide:matlab-built-in-functions).

## Literature

Lecture and exercise materials come first. Mandatory books (slide 13):

- Niku, *Introduction to Robotics: Analysis, Control, Applications*, 2nd edition
- Siciliano et al., *Robotics: Modelling, Planning and Control*, 2009
- Spong, Hutchinson and Vidyasagar, *Robot Modeling and Control*, 2nd edition

Additional (slide 14):

- Craig, *Introduction to Robotics: Mechanics and Control*, 4th edition
- Lynch and Park, *Modern Robotics: Mechanics, Planning, and Control*, 2017

## Start here

- [](lecture:01-introduction-to-robotics), with [](deck:introduction) and
  [](problems:introduction-practice)
- [](lecture:02-rigid-body-motions), with [](deck:rigid-body-motions) and
  [](problems:rigid-body-practice)
- [](lecture:03-forward-kinematics), with [](deck:forward-kinematics) and
  [](problems:forward-kinematics-practice)

The four textbooks of the reading list (Niku, Lynch and Park, Spong, Siciliano) are now in
the courseware's Literature folder.
