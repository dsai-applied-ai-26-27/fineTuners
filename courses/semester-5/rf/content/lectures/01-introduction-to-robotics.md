---
title: Introduction to robotics
number: 1
topics: [intro]
summary: The vocabulary of the whole course. What a robot and a manipulator are, the parts of a robotic system, degrees of freedom, joints and common arm structures, reference frames, a first look at kinematics, workspace and singularities on a planar two-link arm, and how programming, robot characteristics and AI fit in.
takeaways:
  - A robot is a programmable physical machine that acts through actuators and a control system. The course's technical focus is the robotic manipulator, a chain of links and joints that positions and orients a tool.
  - A rigid body has 3 degrees of freedom in a plane and 6 in space. A configuration $\boldsymbol{q}$ lists the joint coordinates; a pose is position together with orientation.
  - Joint strings read from base to tool name the classic structures, which are Cartesian PPP, cylindrical RPP, spherical RRP, SCARA and anthropomorphic RRR.
  - For the planar 2R arm, $x = l_1 \cos q_1 + l_2 \cos(q_1 + q_2)$ and $y = l_1 \sin q_1 + l_2 \sin(q_1 + q_2)$. One position can have two configurations, elbow up and elbow down.
  - At a singularity the Jacobian loses rank and some instantaneous tool-velocity direction disappears. The fully extended 2R arm cannot move its tip along the arm.
  - Accuracy is closeness to the intended pose, repeatability is closeness among repeated attempts. A robot can be repeatable and still inaccurate.
sources:
  - lectures/Lecture 1.pdf
  - lectures/Lecture 1 (revised 2026-10-11).pdf
  - lectures/Lecture 1 (revised 2026-10-20).pdf
---

## Where this fits

Lecture 1 builds intuition and vocabulary before any detailed model. The principal reading
is chapter 1 of Niku, with additions from Siciliano et al., Spong et al. and Lačević et al.
The equations are previews: each returns in a later lecture with a full derivation. The
course's technical focus is **exclusively on robotic manipulators**; mobile and other
robots appear for context (p. 1).

The running example: ask a robot to pick up a cup and put it on a tray. Where is the cup?
How should it be grasped? Can the arm reach it without hitting the table? How hard should
the gripper close? What if the cup moves? Robotics is what connects those questions into
physical action.

## What is a robot?

:::definition Robot
A programmable physical machine that uses actuators and a control system to perform actions
in its environment. Its actions may follow a stored program, respond to sensor information,
or be guided by a human operator.
:::

A robot need not look human or use AI: a factory arm repeating a programmed movement
qualifies. What separates it from a manually operated crane is that it executes a sequence
without a person commanding every movement, and **reprogrammability**: the same mechanism
can do a different job without being rebuilt.

:::definition Robotic manipulator
A mechanism of connected bodies, called **links**, and **joints**, which allows a tool or
object to be positioned and oriented.
:::

Figure 1 of the notes labels the parts of a manipulator: base, joints with their actuators,
links, wrist, end effector (a gripper) with its tool center point, sensors, and off the arm
the controller with its software and the power supply.

Four neighbouring terms (section 1):

| Term | Meaning | Example |
|---|---|---|
| Robotics | The study and practice of designing, building, programming, controlling and applying robots | Combines mechanics, electronics, computer science and mathematics |
| Automation | The broader use of machines and control systems to do tasks with reduced human intervention | A thermostat: automatic, but not a robot |
| Robotic system | The robot plus the equipment that makes its task possible | Tools, cameras, fixtures, conveyors, protective equipment |
| Autonomy | The ability to perform a task without continuous human direction | A delivery robot needs more of it than a factory arm fed parts in known positions |

## Classification and history

There is no single classification (section 2). Robots can be sorted by

- **form:** manipulators, mobile robots, humanoids;
- **application:** industrial, medical, domestic, exploration;
- **actuation:** electric, hydraulic, pneumatic;
- **control:** teleoperated, programmed, sensor-adaptive, autonomous.

By mechanical arrangement: a **serial robot** is an open chain of links from base to tool,
like shoulder to hand. A **parallel robot** connects a moving platform to the base through
several chains, forming closed loops. A **mobile robot** moves its base through the
environment, and an arm on such a base is a **mobile manipulator**.

"Articulated" has two meanings. Broadly, articulated robots are rigid bodies connected into
chains or branching trees. In industrial usage an *articulated arm* is narrower: an arm
built mainly from rotary joints, arranged like a human arm. Examples of manipulators in the
notes: KUKA LBR iiwa (7 DoF), Universal Robots UR3 (6 DoF), ABB IRB 120 (6 DoF).

**Mobile robots** come as wheeled (well suited to prepared floors), legged (better on uneven
terrain, harder to coordinate) and flying (quadrotors, fixed-wing aircraft); underwater
robots show the list is not complete. For an omnidirectional planar base the base pose is
$(x_b, y_b, \theta_b)$: two position coordinates and a heading angle.

### Historical milestones

| Period | Milestone |
|---|---|
| Early automata | Mechanical figures reproduced movements long before electronic control |
| 1920 to 1921 | Karel Čapek's play *R.U.R.* published (1920) and performed (1921). Josef Čapek suggested "robot", from *robota*, associated with compulsory labor |
| 1950s to 1961 | Numerical control, computing and manipulators converged. General Motors used Unimate in industrial production in 1961 |
| 1966 to 1972 | SRI's Shakey combined sensing, reasoning and mobile action, linking robotics with AI |
| 1970s to 1990s | Industrial arms became widespread in welding, material handling, painting and assembly; later expansion to mobile, exploration, medical and service robots |
| 1990s to 2010s | Collaborative robotics: lightweight arms, force sensing, compliance and safety functions let robots and people share workspaces |
| 2010s to 2020s | Computer vision, machine learning, deep learning and reinforcement learning improved perception, grasping, navigation and decision making |
| 2020s onward | AI-enabled robots combine vision, language, reasoning and action through foundation models and vision-language-action models |

Niku's historical schemes (JIRA's six classes, the AFR scheme) run from manual handling
through fixed and variable sequences, playback and numerical control to intelligent robots.
They show that the meaning of "robot" has moved with the technology. More autonomy is not
always better: a simple programmed robot can be the right answer to a well-defined task.

## Benefits and limitations

In a suitable application robots give **consistent motion**, higher productivity and less
human exposure to hazardous or strenuous work, without fatigue (section 3).

The advantages need a complete system. The robot has to be integrated with tools and
surroundings, programmed, maintained and checked, and it rests on assumptions: if a part
shifts in its fixture or a sensor misreports, a sequence that used to work fails.
Components wear, sensors drift, faults occur.

:::note Easy for people, hard for machines
A rigid part in a fixed holder has a predictable shape and position. A shirt changes shape
whenever it is touched. Folding unfamiliar clothing can need more perception and adaptation
than repeatedly positioning a much heavier metal part.
:::

## Components of a robotic system

Follow the information and the energy through the cup example: a camera locates the cup,
software chooses an approach, motors move the arm, sensors report whether the motion
happened (section 4).

| Component | Role |
|---|---|
| Mechanical structure | Links connected by joints, on a base. Link dimensions and joint arrangement fix the basic movement capabilities |
| End effector | The device that does the task: gripper, suction cup, welding torch, screwdriver, probe. The **tool center point (TCP)** is a chosen point, often the tool tip, whose motion is specified |
| Actuators and drives | Actuators turn supplied energy into motion or force. Drivers regulate the power; transmissions (gears, screws) connect actuator motion to joint motion |
| Sensors | **Proprioceptive** (internal) sensors measure the robot's own state: joint position, motor current. **Exteroceptive** (external) sensors measure the environment or the interaction: cameras, range, touch, force. An encoder reports rotation or displacement |
| Controller | Computes actuator commands so the actual behaviour follows the desired one, regulating position, velocity, force or torque by feedback |
| Processor and software | Run perception, planning, control and task logic, and coordinate the robot with tools, sensors and other machines |

Plus a power supply, communication between the devices, and supporting and protective
equipment.

### Arm, wrist and tool

In a conventional six-axis industrial arm the first three joints mainly **position the
wrist** and the last three mainly **orient the tool**. The split is cleanest with a
**spherical wrist**, whose three rotation axes meet in one point. The wrist's mounting
flange carries the end effector, so changing the tool changes the relation between flange
and TCP.

:::pitfall Wrist center is not TCP
When the tool tip is offset from the wrist center, rotating the wrist also moves the tip.
Turning a long screwdriver moves its tip unless the rest of the arm compensates.
Controlling the wrist center and controlling the TCP are related but different tasks.
:::

### Choosing an actuator

| Drive | Useful properties | Design considerations |
|---|---|---|
| Electric | Convenient electronic control of motor motion with drives and feedback | Torque limits, heating, gearing, and backlash (play in a transmission) |
| Hydraulic | Pressurised liquid generates large forces and torques in compact actuators | Pumps, valves, hoses, noise, leakage, maintenance |
| Pneumatic | Compressed air suits simple rapid motions such as opening and closing a gripper | Air supply and conditioning; compressibility complicates precise positioning and stiffness |

A **servo system** uses feedback to regulate motion. A **stepper motor** advances through
commanded increments, but can miss steps under excessive load unless that is detected and
corrected. Force or torque, speed, precision and operating conditions are weighed together:
a large payload alone does not decide the technology.

### Feedback control

Real motion differs from desired motion because of loading, friction and disturbances.
Feedback control compares the measurement with a reference and adjusts the command. For a
joint with desired coordinate $q_d(t)$ and measured coordinate $q(t)$ at time $t$, the
position error is

$$e(t) = q_d(t) - q(t) .$$

With a desired angle of $30^\circ$ and a measured angle of $27^\circ$ the error is
$3^\circ$. The simplest rule is proportional,

$$u(t) = K_p\, e(t) ,$$

where $u$ is the actuator command and the gain $K_p$ sets how strongly the controller
reacts. A larger gain is not automatically better: the system may overshoot or oscillate.
Real controllers also account for velocity, gravity and other effects. Holding a loaded arm
still can need non-zero torque although the desired velocity is zero.

The loop of figure 4: task or motion reference → feedback controller → drives and actuators
→ robot and environment → sensors and state estimation → back to the controller.

## Degrees of freedom, configuration and pose

:::definition Degree of freedom (DoF)
An independent freedom of motion. The DoF count is the number of independent continuous
variables needed to describe a configuration locally. "Independent" means not determined by
the others through a mechanical constraint.
:::

- A point needs 2 coordinates in a plane and 3 in space.
- A rigid body in a plane has **3 DoF**: two translations and one rotation.
- A rigid body in space has **6 DoF**: three translations and three rotations.

A book sliding on a table can move forward, move sideways and turn: three planar freedoms.
Lifted and tilted, it needs three position and three orientation variables.

The **configuration** specifies the arrangement of the links. For a serial arm with $n$
independent one-DoF joints,

$$\boldsymbol{q} = \begin{bmatrix} q_1 & q_2 & \cdots & q_n \end{bmatrix}^\top ,$$

a column vector of joint coordinates: an angle for each revolute joint, a displacement for
each prismatic joint.

The tool's **position** says where a chosen point is; its **orientation** says how the tool
is turned; together they are its **pose**. A cup put in the right place upside down has the
right position and the wrong orientation. A tool pose does not always fix the
configuration, since the arm may reach the same pose with different elbow positions.

Six suitably arranged joints commonly allow control of a general spatial pose, but do not
guarantee every pose: joint limits, collisions and **singular configurations** restrict
motion.

:::definition Redundancy
A robot is **redundant for a task** when it has more independent joint variables than the
task requires. A seven-axis arm can often change its elbow posture while holding its tool
pose, to avoid an obstacle or a joint limit. Redundancy depends on the task: placing a
point on a table needs fewer quantities than a full spatial pose.
:::

**Counting convention.** Arm DoF are quoted separately from gripper motion. A joint only
ever commanded to two end positions still has one mechanical DoF. Closed loops and
mechanical coupling can make the number of joints differ from the number of independent
coordinates, so counting visible joints is not always enough.

## Robot joints

A joint connects neighbouring links, permitting some relative motions and blocking others.
Its geometry is separate from its actuator: a rotary motor can drive a linear slide through
a screw (section 6).

| Joint | DoF | Permitted relative motion |
|---|---|---|
| Revolute (R) | 1 | Rotation about one axis, $q_i = \theta_i$. A door on its hinge |
| Prismatic (P) | 1 | Translation along one axis, $q_i = d_i$. A drawer on its guides |
| Cylindrical | 2 | Independent translation along and rotation about the same axis |
| Universal | 2 | Two rotations about intersecting axes |
| Spherical | 3 | Rotation about a common center |
| Helical | 1 | Rotation and translation coupled by the screw geometry |

Revolute and prismatic joints build most serial manipulators; the others appear in
mechanisms such as parallel robots. In calculations angles are in radians and lengths in
consistent units.

:::example Why a screw has one DoF
A helical joint rotates and translates, but the translation is determined by the angle. If
$h$ is the **lead**, the distance advanced in one full revolution, then

$$d = \frac{h\,\theta}{2\pi} .$$

Only one coordinate is independent. With $h = 5$ mm and a quarter turn, $\theta = \pi/2$,
the advance is $d = 5 \cdot \tfrac{1}{4} = 1.25$ mm. (The numbers are not from the notes.)
:::

Some books write T for a translational joint. The notes use P, so TTT, RTT and RRT there
are PPP, RPP and RRP here.

## Coordinates and common configurations

Joint coordinates describe the mechanism; tasks are described by where the tool should be.
The same point can be written in three coordinate systems (section 7).

**Cartesian:** $(x, y, z)$.

**Cylindrical:** radius $r$, angle $\theta$ about the vertical axis, height $z$:

$$x = r \cos\theta, \qquad y = r \sin\theta .$$

**Spherical:** distance $\rho$ from the origin, elevation $\alpha$ measured from the
horizontal plane, azimuth $\theta$ about the vertical axis:

$$x = \rho \cos\alpha \cos\theta, \qquad y = \rho \cos\alpha \sin\theta, \qquad z = \rho \sin\alpha .$$

Other angle conventions exist, so always state the one in use.

The **workspace** is the region the end effector can reach. Its shape and size follow from
link dimensions, joint types and joint limits. The type and order of the three positioning
joints, read from base to tool, give the classic structures:

| Structure | Joints | Workspace | Good at | Watch out for |
|---|---|---|---|---|
| Cartesian | PPP, mutually perpendicular | A box | Joint displacements are the Cartesian coordinates, so straight lines are easy; high stiffness; uniform resolution (gantries) | Orientation needs an extra mechanism; access directions depend on layout |
| Cylindrical | typically RPP | A cylindrical shell or sector | Turn, choose a height, extend: reaching into horizontal cavities, handling, machine tending | The same angular error gives a larger position error far from the axis; extension reduces stiffness |
| Spherical (polar) | RRP | Roughly a spherical shell sector | Two rotations pick a direction, the slide a distance; can reach near the floor | More complex; lower stiffness; radial extension magnifies angular error |
| SCARA | RRP with parallel axes, often RRPR | A ring-shaped region extended vertically | Compliant in the horizontal plane, stiff vertically: vertical insertion and assembly | Controls $(x, y, z, \phi)$ only; cannot tilt the tool freely |
| Anthropomorphic | RRR: base, shoulder, elbow | Roughly part of a sphere | Large workspace for its footprint; many postures; with a wrist, many approach directions (welding) | No joint maps to one Cartesian coordinate, so a straight line needs coordinated joints; accuracy and stiffness depend on posture |

SCARA stands for Selective Compliance Assembly Robot Arm. In the anthropomorphic arm the
first axis is typically perpendicular to the other two, which are parallel. A joint string
names joint *types* only; axis directions and link dimensions are needed to define an
actual mechanism. These are geometric tendencies, not performance specifications:
calibration, transmission errors, loading and construction matter too.

:::recall Which structure would you choose to press small pins vertically into a board, and why?
A SCARA. It is compliant in the horizontal plane, which lets the pin find the hole, and
stiff in the vertical direction, which is the direction of insertion.
:::

## Reference frames

A coordinate system says *how* a point is described. A **reference frame**, an origin with
a set of axes, says *where* the description is anchored and how its axes point. A camera
reports the cup relative to itself; the arm controller needs it relative to the robot base.
A **coordinate transformation** relates the two. The cup has not moved, but its numbers
change with the frame.

| Frame | Attached to |
|---|---|
| World $\{W\}$ | The workcell or environment; fixed |
| Base $\{B\}$ | The robot base. May coincide with the world frame; moves with the base on a mobile robot |
| Tool $\{T\}$ | The tool, often with its origin at the TCP. Its axes turn as the tool turns |
| Workpiece $\{O\}$, sensor $\{C\}$ | An object, a camera or another device. Calibration establishes their relation to the others |

"Move 10 mm along world $x$" uses a fixed direction. "Move 10 mm along tool $z$" uses the
tool's current direction, which is what a screwdriver needs when the screw is inclined.

**Joint mode** (the book's "joint reference frame") commands changes in individual joint
coordinates and is not a Cartesian frame at all: "increase joint 2 by $5^\circ$" generally
moves the TCP along an arc.

## Kinematics, workspace and motion

**Forward kinematics** computes the tool pose from the joint coordinates and the geometry:
if the joints have these values, where is the tool? **Inverse kinematics** asks the
reverse: which joint values give this pose? There may be no solution, several, or a
continuous family.

### The planar 2R arm

Two revolute joints in a plane. Link lengths $l_1$ and $l_2$; $q_1$ is measured
counterclockwise from the base $x$ axis and $q_2$ counterclockwise relative to link 1, so
link 2 makes the angle $q_1 + q_2$ with the base axis. Adding the horizontal and vertical
contributions of the two links:

$$\begin{aligned} x &= l_1 \cos q_1 + l_2 \cos(q_1 + q_2), \\ y &= l_1 \sin q_1 + l_2 \sin(q_1 + q_2), \\ \phi &= q_1 + q_2 . \end{aligned}$$

Here $\phi$ is the orientation of link 2, with the tool aligned to it. Three quantities
$(x, y, \phi)$ depend on only two joint angles, so they cannot all be prescribed
independently.

:::example One target, two configurations
Let $l_1 = l_2 = 1$ m and ask only for the TCP position $(x, y) = (1, 1)$ m.

| Configuration | $q_1$ | $q_2$ | $\phi$ | Picture |
|---|---|---|---|---|
| Elbow down | $0^\circ$ | $90^\circ$ | $90^\circ$ | Link 1 points right, link 2 points up |
| Elbow up | $90^\circ$ | $-90^\circ$ | $0^\circ$ | Link 1 points up, link 2 points right |

Check the first: $x = \cos 0^\circ + \cos 90^\circ = 1$ and
$y = \sin 0^\circ + \sin 90^\circ = 1$. Check the second:
$x = \cos 90^\circ + \cos 0^\circ = 1$ and $y = \sin 90^\circ + \sin 0^\circ = 1$.

Same point, different tool orientation and different space occupied by the arm. An
obstacle may block one solution and leave the other. Position alone does not fix the
posture or the full tool pose.
:::

### Workspace, configuration space, path and trajectory

The **reachable workspace** is every tool position attainable by at least one admissible
configuration. The **dexterous workspace** is the set of positions where every required
tool orientation is attainable (classically, every orientation). A point can be reachable
without allowing the approach direction a task needs.

For an ideal planar 2R arm, with unrestricted joints and no collisions, the distance from
base to TCP satisfies

$$\lvert l_1 - l_2 \rvert \le \sqrt{x^2 + y^2} \le l_1 + l_2 .$$

The outer bound is the fully stretched arm, the inner bound the arm folded back on itself.
The positional workspace is an annulus, or a full disk when $l_1 = l_2$. Real joint limits
and collisions remove parts of it.

**Configuration space** describes the robot by all its independent configuration variables.
For the 2R arm each point $(q_1, q_2)$ is a whole posture, and two different points can give
the same TCP position, as elbow up and elbow down do.

A **path** is a geometric route, such as $\boldsymbol{q}(s)$ for $s \in [0, 1]$, where $s$
is progress and not time. A **trajectory** adds timing: $\boldsymbol{q}(t)$ with its
velocities and accelerations. Carrying a full cup slowly or quickly along the same route is
one path and two trajectories. Motion planning chooses the route, trajectory generation
assigns the timing, feedback control tries to follow it.

:::pitfall A clear TCP path is not a collision-free motion
Obstacle avoidance has to account for every link. The tool can pass well clear of an
object that the elbow or forearm hits.
:::

## From models to control

A **mathematical model** holds the relations needed to predict and control behaviour:
geometric parameters (link lengths, joint-axis locations), dynamic parameters (masses,
centers of mass, moments of inertia) for links and payload, and models of actuators,
transmissions and sensors. The parameters have to be measured or estimated (section 10).

**Kinematics** describes motion without the forces that cause it. **Differential
kinematics** is about velocities. For a spatial tool

$$\begin{bmatrix} \boldsymbol{v} \\ \boldsymbol{\omega} \end{bmatrix} = \boldsymbol{J}(\boldsymbol{q})\, \dot{\boldsymbol{q}} ,$$

where $\dot{\boldsymbol{q}}$ holds the joint velocities (the dot is a time derivative),
$\boldsymbol{v}$ is the linear velocity of the TCP and $\boldsymbol{\omega}$ the angular
velocity of the tool. $\boldsymbol{J}$ is the **geometric Jacobian**. Each column is the
contribution of one joint's motion to the tool velocity, so the relation changes with
posture. Its derivation comes in a later lecture.

### A first look at singularities

:::definition Kinematic singularity
A configuration where the Jacobian for the selected task loses rank relative to its
maximum, which reduces the number of independent task-velocity directions available.
:::

Take the 2R arm with TCP position as the task. Differentiating the position equations with
respect to time gives

$$\begin{aligned} \dot x &= -l_1 \sin q_1\, \dot q_1 - l_2 \sin(q_1 + q_2)\,(\dot q_1 + \dot q_2), \\ \dot y &= \phantom{-} l_1 \cos q_1\, \dot q_1 + l_2 \cos(q_1 + q_2)\,(\dot q_1 + \dot q_2) . \end{aligned}$$

(The notes give only the result at one posture; this general form is the step in between.)
With the arm stretched along $+x$, so $q_1 = q_2 = 0$, every sine vanishes and every cosine
is $1$:

$$\dot x = 0, \qquad \dot y = (l_1 + l_2)\, \dot q_1 + l_2\, \dot q_2 .$$

Both joints can turn, yet neither produces any instantaneous TCP velocity along $x$. The
arm still has two joint DoF, but its positional Jacobian has one independent output
direction instead of two. Bending the arm through a *finite* angle does bring the tip
inward: the restriction is on instantaneous velocity at that posture and not a permanently
blocked direction.

Near a singularity a modest tool speed in the poorly available direction can demand large
joint speeds. **Manipulability** describes how posture affects the conversion of joint
velocities into tool velocities; Siciliano et al. picture it with velocity ellipsoids.
Reaching a point and moving well near that point are different requirements.

### Forces and motion

**Statics** is force and torque balance in equilibrium. **Dynamics** relates forces and
torques to motion, including acceleration, and accounts for inertia, gravity and the
interaction between moving links. Moving one joint changes the loads on the others, so a
manipulator is a **coupled system**. Holding a cup farther from the base raises the torque
at a supporting joint, and accelerating it raises it further. An arm that can
geometrically reach a point may be unable to carry the load there at the requested speed.

### Free motion and contact

In **free motion** the tool touches nothing and the controller can track a position
trajectory. In **contact motion** (polishing, insertion) the surface constrains movement
and produces contact forces, and a large position correction into a rigid surface produces
a large force.

- **Force control** regulates an interaction force.
- **Impedance control** shapes the relation between motion and interaction force so that
  the robot behaves with a chosen compliance and damping, like a spring (controlled
  yielding) with a damper (resists motion, reduces oscillation).
- **Decentralized control** uses individual joint loops. **Centralized control** considers
  the joints together and can compensate for their coupling.

The last pair says how control is organised; position, force and impedance say what
behaviour is wanted.

## Programming modes and languages

Niku's four ways of specifying robot behaviour (section 11):

1. **Physical setup:** switches, stops or sequence hardware determine the motions.
2. **Teach pendant:** an operator moves the robot, stores positions or poses, then adds
   motion and task instructions.
3. **Continuous lead-through:** guided motion is sampled and recorded for playback.
4. **Software programming:** instructions specify motions, conditions, tool actions and
   interaction with other devices.

| Pair | First | Second |
|---|---|---|
| Offline and online | **Offline:** prepared on a model or simulation, which must agree well enough with the real installation | **Online:** involves the real robot or its controller. Nothing to do with the Internet |
| Point-to-point and continuous path | **Point-to-point:** only the endpoints matter, the controller interpolates (spot welding, pick and place) | **Continuous path:** the route is constrained too (seam welding, painting, adhesive dispensing) |
| Absolute and relative | **Absolute:** a destination, such as a stored tray pose | **Relative:** an increment from a reference state, such as 10 mm further along the tool axis |

A straight line in joint coordinates is generally *not* a straight TCP path. Robot
languages differ by manufacturer (Niku uses V+ and AML); higher-level programs in Python or
C++ organise reusable skills while lower levels generate actuator commands.

A robot program combines movement instructions with decisions about the state of the task.
The notes' illustrative pseudocode, which is not executable vendor code:

```python
move_to(pre_pick_pose)
open_gripper()
move_linear(pick_pose)
close_gripper()

if grasp_confirmed():
    move_linear(pre_pick_pose)
    move_to(pre_place_pose)
    move_linear(place_pose)
    open_gripper()
    move_linear(pre_place_pose)
else:
    stop_task_and_request_recovery()
```

`pre_pick_pose` and `pre_place_pose` are approach poses with clearance. The grasp check
stands for real sensing: closing the gripper is not assumed to succeed.

## Robot characteristics

Specifications must be read against the actual task (section 12).

| Characteristic | Meaning |
|---|---|
| Payload | Rated load under stated conditions, normally tool **plus** carried object. Center of mass, inertia and motion matter, not mass alone |
| Reach | How far the robot can extend. Says nothing about attainable orientations or collision-free approach |
| Accuracy | How close an achieved pose is to the intended pose |
| Repeatability | How closely repeated executions reproduce the same pose under stated conditions |
| Resolution | The smallest increment represented, measured or commanded by a subsystem. A small increment does not guarantee accurate motion |
| Speed, acceleration, stiffness | Motion limits affect cycle time and loads. Stiffness is resistance to deformation; compliance is the tendency to deform under load |
| Orientation capability, environment | Joint arrangement and limits decide attainable orientations. Temperature, dust, moisture and cleanliness affect suitability |

:::example Repeatable but inaccurate
The target is 100.00 mm. Three measurements give 100.38, 100.40 and 100.42 mm.

- Mean: $100.40$ mm, so the mean error is $+0.40$ mm. That is the accuracy problem.
- Range: $100.42 - 100.38 = 0.04$ mm. That is the repeatability, and it is good.

The robot is consistent but biased. (Three samples illustrate the idea; they are not a
formal specification test.)
:::

Repeatability is what matters when a task was taught on the installation itself and
conditions stay stable. Accuracy matters when targets come from CAD, vision or external
measurement. **Calibration** estimates and corrects model or measurement parameters so the
descriptions agree. The notes say "repeatability" where others say "precision", to keep it
apart from accuracy and resolution.

## Applications

- **Manufacturing:** machine loading, pick and place, palletizing, welding, painting,
  assembly, drilling, polishing, inspection. Repeated cycles and controlled fixtures suit
  automation.
- **Medical and assistive:** instrument positioning, clinician-guided manipulation,
  rehabilitation. "Robotic" does not mean independent of the clinician: the da Vinci system
  is surgeon-controlled.
- **Exploration and hazardous work:** planetary, underwater, contaminated areas, disaster
  assessment. Communication delays make local autonomy valuable.
- **Service and agriculture:** cleaning, delivery, harvesting, crop inspection, in less
  predictable surroundings.

Palletizing and pin insertion show how priorities differ. The first is about moving loads
efficiently within limits. The second adds orientation, tight tolerances, contact forces
and misalignment, so tool, fixture and compliance matter as much as the arm.

A **structured environment** is arranged so that object locations and access routes are
known or controlled. Siciliano et al. use **advanced robotics** for robots with substantial
autonomy in environments whose geometry and physical properties are not fully known
beforehand. Two groups:

- **Field robots** work outside controlled settings, often where people cannot or should
  not go. Sojourner explored about 250 m² of Mars in 1997; Stanley drove the 132-mile 2005
  DARPA Grand Challenge course autonomously.
- **Service robots** assist people outside manufacturing: Cycab (urban transport), Rhino
  (museum guide), Roomba (floor cleaning), da Vinci (surgery), ASIMO and AIBO (humanoid and
  entertainment).

Industrial examples to recognise, not memorise: PUMA 560, FANUC S-420S, ABB IRB 7600,
Motoman UP20M, Mitsubishi PA-10.

## Robotics and artificial intelligence

**AI** covers computational methods for perception, reasoning, planning and learning.
**Machine learning** is the part of AI that builds models or policies from data. AI can
live entirely in software and robots can work without ML (section 14).

| Term | Meaning |
|---|---|
| Policy | A map from available information to an action, for example from an image and an instruction to the next movement command |
| Imitation learning | Learns behaviour from demonstrations |
| Reinforcement learning | Improves a policy through interaction and rewards; a reward says which outcomes training should favour |
| Generalization | Performance in situations different from those met in training |
| Sim-to-real gap | The difference between simulated and real conditions; a simulated grasp can succeed where the real, more slippery object slips |
| Training and inference | Training adjusts a model's parameters. Inference uses a trained model to produce an output |

SayCan connects language-based task suggestions with estimates of which robot skills can
succeed. RT-2 studies models that go from images and language instructions to robot
actions.

For "put the red cup in the tray", a language model can interpret the request and a vision
model can find the cup. The system still has to relate coordinates, select a feasible
grasp, avoid collisions, generate a movement and confirm the result. The fundamentals of
this course stay necessary when a learned model takes part in the decision.

:::recall A trained network receives a new camera image and predicts a grasp. Is the robot learning?
Not necessarily. That is inference: an already trained model producing an output. Learning
online would require the model's parameters to change as a result of the new experience.
:::

## People and robots

**Human-robot interaction** is about communication and coordination between people and
robots; **collaboration** is cooperation on a shared task. A robot designed for
collaborative use is a **cobot**.

:::warning A cobot does not make an application safe
Safety depends on the complete application: tool, carried object, surroundings and motion.
A soft object and a sharp tool are different hazards on the same arm. Protective approaches
include guarding, monitored stopping, speed and separation control, and limited contact
forces, chosen through an application-specific risk assessment. An emergency stop alone is
not a complete protective design.
:::

Robotics can reduce strenuous work and create technical roles, and it can change or
displace jobs. Responsible design considers training, accessibility, privacy,
accountability, energy use and maintenance. Asimov's laws are fiction and a discussion
starter, not engineering safety specifications.

## What an exam wants

The notes end with 21 discussion questions (section 16). Three recurring shapes:

:::paper Distinguish two terms
Give each definition in one sentence, then one example that separates them. For accuracy
against repeatability: "Accuracy is how close an achieved pose is to the intended pose.
Repeatability is how closely repeated executions reproduce the same pose. Measurements of
100.38, 100.40 and 100.42 mm for a 100.00 mm target are repeatable (range 0.04 mm) but
inaccurate (mean error +0.40 mm)."
:::

:::paper Why does a fully extended 2R arm lose a direction but not a DoF?
At $q_1 = q_2 = 0$ the velocity equations give $\dot x = 0$ and
$\dot y = (l_1 + l_2)\dot q_1 + l_2 \dot q_2$. Both joints still move, so there are two
joint DoF, but no joint velocity produces instantaneous TCP motion along $x$. The
positional Jacobian has rank 1 instead of 2: a singularity. A finite bend still moves the
tip inward.
:::

:::paper Why can a reachable position still be infeasible?
Reachable means some admissible configuration puts the TCP there. The task may also need a
tool orientation that is not attainable at that point (it is outside the dexterous
workspace), or every route to it may make some link, not necessarily the tool, collide.
:::

## Where next

- Drill: [](deck:introduction).
- Compute: [](problems:introduction-practice).
- Definitions: [the glossary](glossary). Equations: [the formula sheet](formulas).
- Organisation and grading: [](guide:course-map).
