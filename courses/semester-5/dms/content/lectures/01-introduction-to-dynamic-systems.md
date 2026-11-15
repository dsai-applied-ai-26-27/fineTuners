---
title: Introduction to dynamic systems
number: 1
topics: [dynamic-systems]
summary: What a system is and what makes it dynamic, the roles of inputs, states, outputs, parameters and disturbances, initial conditions and equilibrium, the ways dynamic systems are classified, the three mathematical descriptions (differential equation, state space, transfer function), the time and frequency viewpoints, and the workflow from a real problem to a validated simulation.
takeaways:
  - A system is dynamic when its present behaviour depends on its past, not only on the current input. That memory comes from internal storage of energy, mass, information or another quantity.
  - The state is the minimum internal information that, together with the future inputs, determines the future. It is not necessarily measured; the output is what the model exposes.
  - At an equilibrium $(x_e, u_e)$ of $\dot x = f(x, u)$, $f(x_e, u_e) = 0$ and the state stays constant while the input does.
  - Classification pairs (continuous/discrete, linear/nonlinear, time-invariant/varying, deterministic/stochastic, SISO/MIMO, autonomous/forced, causal/noncausal, lumped/distributed) can all apply to one system at once.
  - A mass-spring-damper $m\ddot x + c\dot x + kx = F$ can be written as a differential equation, as two first-order state equations, or as $G(s) = \dfrac{1}{ms^2 + cs + k}$, which assumes zero initial conditions and hides the state.
  - Verification asks whether the equations and code are implemented correctly; validation asks whether the model is adequate for its purpose.
sources:
  - lectures/DMS_Lecture_01_Introduction_to_Dynamic_Systems.pdf
---

## Where this fits

The first lecture of Dynamic Modeling and Simulation (Assist. Prof. Dr. Adnan Osmanović,
with teaching assistant Elma Kandić-Brdar) sets up the vocabulary for the whole course.
Derivations and numerical methods are postponed to later lectures. The course is 5 ECTS,
50 hours: 30 of lectures and 20 of exercises (slide 2).

The course has three verbs (slide 3):

| Model | Simulate | Analyze |
|---|---|---|
| Translate physical or conceptual knowledge into equations; identify states, inputs, outputs, parameters and assumptions; decide the level of detail | Compute behaviour over time with numerical tools such as MATLAB/Simulink; explore scenarios that are costly to test physically | Interpret transient and steady-state behaviour; compare predictions with measurements; support design decisions |

"A simulation is only as meaningful as the model and assumptions behind it."

## Why model dynamic systems

Many quantities change with time: temperature, speed, voltage, population, inventory,
pressure, concentration. Experiments on the real system may be expensive, slow, unsafe, or
impossible during early design. A model lets you ask "what if?" first, and simulation shows
the **transient** behaviour that a steady-state calculation hides.

Typical questions a model answers: how fast does the system respond? Will it oscillate? Is
it stable? How sensitive is it to its parameters? What happens under disturbances?

## Systems and their boundary

:::definition System
A collection of interacting components that transforms inputs and internal conditions into
observable outputs according to physical, logical or empirical relationships (slide 7).
:::

The **boundary** is chosen by the modeller. It separates what the model includes from its
environment; whatever crosses it becomes an input, an output or a disturbance. What is an
input in one model may be an internal variable in another. There is usually no unique
correct boundary, only one appropriate for the question asked, and moving it changes the
model's structure and complexity.

Complex systems are often built from **subsystems** (an actuator, a process, a sensor)
connected by flows of energy, matter or information. Decomposition makes models easier to
validate and reuse, and each subsystem may have its own physical domain or time scale. But
the whole is not always obvious from the parts: **coupling and feedback can create new
dynamic behaviour**, and interfaces must say which variables are exchanged.

## What makes a system dynamic

A system is **dynamic** when its current behaviour depends on how it has evolved over time,
not only on the current input (slide 10). Its key characteristics:

- **internal storage** of energy, mass, information or another quantity;
- dependence on **initial conditions**;
- **transient** behaviour before a steady condition is reached;
- **memory** of previous inputs or states;
- evolution described by **differential or difference equations**.

| Storage element | What it stores |
|---|---|
| Capacitor | Electrical energy |
| Rotating mass | Kinetic energy |
| Water tank | Mass |
| Thermal body | Thermal energy |
| Bank account | Accumulated balance |

### Static against dynamic

| Static | Dynamic |
|---|---|
| $y(t) = K\,u(t)$ | $\tau \dot y(t) + y(t) = K\,u(t)$ |
| Output fixed by the current input | Output evolves over time |
| No state variable | An initial condition is needed |
| No memory | A characteristic time scale $\tau$ |
| An ideal gain | Past conditions influence the present |

"Dynamic behaviour is fundamentally connected to storage and memory."

## The variables of a model

| Variable | Meaning | Room temperature example |
|---|---|---|
| Input $u(t)$ | Quantity intentionally applied | Heater power |
| State $x(t)$ | Minimum internal information needed to predict future behaviour | Room and wall temperature |
| Output $y(t)$ | Observed quantity or variable of interest | Measured air temperature |
| Parameter $p$ | Model property treated as fixed during one simulation | Thermal resistance, heat capacity |
| Disturbance $d(t)$ | External influence not commanded by the modeller | Outdoor temperature, an opened window |
| Initial condition | State value at the start of the simulation | $T(0) = 18\,^\circ\mathrm{C}$ |

The same physical quantity can play different roles depending on the objective and the
boundary. A general description ties them together:

$$\dot x(t) = f\big(x(t), u(t), d(t), p\big), \qquad y(t) = h\big(x(t), u(t), d(t), p\big).$$

A **control input** can be manipulated deliberately; a **disturbance** affects the system
but is not under direct control; a **parameter** is constant, or slowly varying, during one
simulation.

## State and memory

:::definition State
The state summarises the information from the past that is necessary to determine the
future evolution of the system once the future inputs are known (slide 14). In state form,

$$\dot x(t) = f\big(x(t), u(t), t\big), \qquad y(t) = g\big(x(t), u(t), t\big).$$
:::

- $x(t)$ is generally a **vector**: several stored quantities may be needed.
- The state is **not necessarily measured**.
- Choosing states is a modelling decision, but physical storage variables (charge, velocity,
  level, temperature) are natural choices.
- For a dynamic system, knowing only the current input is not enough: the current state
  matters too.

:::pitfall State and output are not synonyms
The **state** is the internal information needed to predict the future; the **output** is
what the model exposes for observation, analysis or control, through a measurement relation
$y = h(x, u)$. A system can have several internal states and one measured output, and
different sensors give different outputs without changing the physical system.
:::

The **state equation** describes how internal variables evolve; the **output equation**
describes how states and inputs become measurable outputs. This input-state-output view
handles many inputs, many outputs and nonlinear models alike.

## Initial conditions

For the autonomous first-order system $\dot x(t) = -a\,x(t)$ with $a > 0$, the solution is

$$x(t) = x(0)\,e^{-at}.$$

The equation is the same for $x(0) = 1, 2, 3$, but the trajectories differ: the future also
depends on the initial state. **Initial conditions summarise the relevant effect of the
system's past at $t = 0$.**

## Equilibrium and operating point

:::definition Equilibrium
For $\dot x = f(x, u)$, an equilibrium point $(x_e, u_e)$ satisfies

$$f(x_e, u_e) = 0 .$$

There the state stays constant as long as the input and external conditions stay
unchanged.
:::

| Mechanical | Thermal | Fluid |
|---|---|---|
| A mass at rest when the net force is zero | Room temperature constant when supplied and lost heat balance | Tank level constant when inflow equals outflow |

Many systems operate near a chosen **operating point**, and later lectures approximate
nonlinear models by linear ones around it.

## Dynamic systems everywhere

| Engineering | Natural sciences | Socio-economic |
|---|---|---|
| Circuits, electric machines, vehicles and robots, power systems, thermal processes | Population dynamics, epidemics, chemical reactions, physiology, ecology | Inventory and supply chains, financial balances, traffic flow, demand response, resource allocation |

The mathematics is often the same even when the physical interpretation is completely
different.

## Feedback

- **Open loop:** the input acts on the system, but the output does not modify the input.
- **Closed loop:** the current or past output influences future evolution through a
  feedback path (a decision or controller compares a reference $r(t)$ with $y(t)$).

**Negative feedback** counteracts deviations and promotes regulation; **positive feedback**
reinforces change and can produce growth or instability. Feedback returns later as the
foundation of control.

## Classifying dynamic systems

A single system can belong to several categories at once. Classification points to suitable
assumptions, analysis tools and simulation methods.

| Pair | First | Second |
|---|---|---|
| Continuous / discrete time | $\dot x(t) = f(x(t), u(t), t)$, time varies continuously; physical processes (motor speed, temperature, voltage) | $x[k+1] = F(x[k], u[k], k)$, updated at instants $k$; sampled data, digital controllers, a monthly balance |
| Linear / nonlinear | Obeys superposition: if $u_1 \to y_1$ and $u_2 \to y_2$ then $a u_1 + b u_2 \to a y_1 + b y_2$; e.g. $\dot x = Ax + Bu$ | Superposition fails; e.g. the pendulum $\dot\theta = \omega$, $\dot\omega = -\frac{g}{\ell}\sin\theta + u$ |
| Time-invariant / time-varying | Rules do not change with time: $\dot x = Ax + Bu$ with constant $A, B$; a shifted input gives a shifted response | $\dot x = A(t)x + B(t)u$; parameters change with scheduling, ageing, motion; the response depends on when the input is applied |
| Deterministic / stochastic | Given inputs, parameters and initial conditions, a unique trajectory $x(t) = \phi(t, x_0, u, p)$; e.g. an ideal RLC circuit | Random variables or processes included explicitly, $\dot x = f(x, u) + w(t)$ with noise $w$; e.g. demand forecasting, noisy sensors |
| SISO / MIMO | One input and one output | Several inputs and/or outputs: $\dot x = Ax + Bu$, $y = Cx + Du$ with vector $u, y$ |
| Autonomous / forced | No external input, $\dot x = f(x)$; driven by the initial state | An external input affects the trajectory |
| Causal / noncausal | Output at $t$ depends only on present and past: $y(t) = S\{u(\tau) : \tau \le t\}$ | Uses future values; possible offline, not in a real-time physical system |
| Lumped / distributed | A finite set of time-dependent variables, ODEs; e.g. RLC circuit, rigid body, a well-mixed room | Depends on time **and** position, PDEs such as $\dfrac{\partial T}{\partial t} = \alpha \dfrac{\partial^2 T}{\partial x^2}$; heat conduction, flexible beams, fluid flow |

:::note Memoryless against dynamic
A **memoryless** relation such as $y(t) = u^2(t)$ uses only the current input. A dynamic
system needs an internal state or the past input history. Memoryless is not the same as
causal: $y(t) = u^2(t)$ is both memoryless and causal, while a causal system may still use
all of its past.
:::

Most physical systems are nonlinear at a sufficiently detailed level; linear models remain
extremely useful near an operating point.

## Three mathematical descriptions

| Differential equation | State space | Transfer function |
|---|---|---|
| Directly expresses physical balances and constitutive laws, e.g. $M\ddot q + C\dot q + Kq = F(t)$ | First-order vector form $\dot x = f(x, u, t)$, $y = g(x, u, t)$ | $G(s) = \dfrac{Y(s)}{U(s)}$, input-output in the Laplace domain |
| Best for deriving models from first principles | Natural for MIMO and nonlinear systems | For LTI systems; frequency analysis and control |

### The mass-spring-damper three ways

**Differential equation.** Newton's second law for a mass $m$ on a spring $k$ and a damper
$c$, driven by a force $F(t)$:

$$m\ddot x(t) + c\dot x(t) + kx(t) = F(t).$$

The mass stores kinetic energy, the spring potential energy, the damper dissipates energy;
$F$ is the input and the displacement $x$ the output.

**State space.** With $x_1 = x$ and $x_2 = \dot x$,

$$\begin{bmatrix} \dot x_1 \\ \dot x_2 \end{bmatrix} = \begin{bmatrix} 0 & 1 \\ -\dfrac{k}{m} & -\dfrac{c}{m} \end{bmatrix} \begin{bmatrix} x_1 \\ x_2 \end{bmatrix} + \begin{bmatrix} 0 \\ \dfrac{1}{m} \end{bmatrix} F(t).$$

One second-order equation becomes two first-order ones, and the state vector shows the
internal condition explicitly.

**Transfer function.** With zero initial conditions, the Laplace transform gives
$(ms^2 + cs + k)X(s) = F(s)$, so

$$G(s) = \frac{X(s)}{F(s)} = \frac{1}{ms^2 + cs + k}.$$

Poles and zeros summarise the dynamics compactly, but **the internal state is not explicit**
in this form, and the initial conditions are assumed zero. That is exactly why Lab 1's
Transfer Fcn block could not take $x(0) = 1$ and the integrator chain could.

## Time domain and frequency domain

**Time domain: how does the system evolve as time passes?** You look at the transient,
the rise and settling, overshoot and oscillation, the steady-state value, and the effect of
initial conditions. Time-domain simulation is usually the first look at a model.

A response is often read as

$$y(t) = y_{tr}(t) + y_{ss}(t),$$

the **transient** part (the transition from the initial condition) plus the **steady-state**
part (long-term behaviour under the input). A good model predicts both how fast the system
changes and where it settles.

**Time scales.** Processes run from milliseconds (power electronics, actuators) through
seconds and minutes (sensors, building temperature) to hours and years (population,
economy). Very fast dynamics may be neglected when only slow behaviour matters, but
ignoring a fast mode is dangerous if it affects stability or peak values. For simulation,
**the time step must be small enough to resolve the fastest dynamics that matter**, and
widely separated time scales are computationally hard. (Lab 1, Task 4 showed what a step
that is too large does.)

**Frequency domain: how does the system respond to sinusoids of different frequencies?**
You look at gain and phase shift against frequency, bandwidth and resonance, filtering, and
robustness. For LTI systems the transfer function bridges the differential equation and the
frequency response.

| | Time domain | Frequency domain |
|---|---|---|
| Independent variable | Time $t$ | Angular frequency $\omega$ |
| Typical signal | Step, impulse, arbitrary waveform | Sinusoidal excitation |
| Typical output | Trajectory $y(t)$ | Magnitude and phase |
| Highlights | Transient and steady state | Bandwidth, resonance, filtering |
| Tools | ODE solver, state trajectory | Transfer function, Bode plot |
| Best for | Simulation and scenarios | LTI analysis and control insight |

Neither is "better": they are complementary.

## An integrative example: room temperature

A room with temperature $T(t)$, heated with power $P_h(t)$ and losing heat through a
thermal resistance $R$ to the outside at $T_o(t)$, with thermal capacitance $C$:

$$C\,\frac{dT}{dt} = P_h(t) - \frac{T(t) - T_o(t)}{R}.$$

| Ingredient | Here |
|---|---|
| State | Room temperature $T(t)$ |
| Control input | Heater power $P_h(t)$ |
| Disturbance | Outside temperature $T_o(t)$ |
| Parameters | $C$ and $R$ |
| Output | Measured room temperature |

The room cannot change temperature instantly because it stores thermal energy; its future
depends on its current temperature, the heat input and the losses.

:::recall What is the time constant of the room, and its equilibrium temperature for constant heating?
Rearranged, $RC\,\dot T + T = T_o + R P_h$: a first-order system with time constant
$\tau = RC$. At equilibrium $\dot T = 0$, so $T_e = T_o + R P_h$. (Worked out here; the
slide stops at the model.)
:::

## From a real problem to a result

Real problem → assumptions and boundary → mathematical model → numerical simulation →
analysis and decision, with a loop back for validation and refinement.

- **Modelling** selects what to represent and what to neglect.
- **Simulation** evaluates the model numerically under specified conditions.
- **Verification**: were the equations and code implemented correctly?
- **Validation**: is the model adequate for its real-world purpose?

Modelling is iterative, not a one-time translation into equations.

## Next lecture and references

Lecture 2: mathematical modelling, physical laws, differential equations, model order,
transfer functions, first modelling examples.

The slides cite MIT OpenCourseWare 6.241J *Dynamic Systems and Control* (lectures 6 and 7),
MIT 2.004 *Systems, Modeling, and Control II* (lectures 1 to 3) and Stanford EE263
*Introduction to Linear Dynamical Systems*.

## Where next

- Drill: [](deck:dynamic-systems).
- Terms in one place: [the glossary](glossary); equations: [the sheet](formulas).
