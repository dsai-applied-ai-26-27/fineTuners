---
title: 'Rigid-body motions: positions and rotations'
number: 2
topics: [transformations]
summary: How to express a point in different frames, what a rotation matrix is and why its inverse is its transpose, how rotations compose about current and about fixed axes, and three ways to describe an orientation with three numbers.
takeaways:
  - 'The columns of a rotation matrix are the local axes expressed in the global frame, $\boldsymbol{R} = [\boldsymbol{n}\ \boldsymbol{s}\ \boldsymbol{a}]$, and it converts local coordinates to global ones by $\boldsymbol{p}^0 = \boldsymbol{d}^0 + \boldsymbol{R}\boldsymbol{p}^1$.'
  - A rotation matrix is orthogonal with determinant $+1$, so $\boldsymbol{R}^{-1} = \boldsymbol{R}^\top$. It changes direction without scaling or shear.
  - A rotation about a current (body-fixed) axis multiplies on the right. A rotation about a fixed (world) axis multiplies on the left. Swapping the order generally gives a different orientation.
  - 'Intrinsic ZYZ Euler angles give $\boldsymbol{R} = \boldsymbol{R}_z(\phi)\boldsymbol{R}_y(\theta)\boldsymbol{R}_z(\psi)$. Fixed-axis XYZ roll, pitch and yaw give $\boldsymbol{R} = \boldsymbol{R}_z(\gamma)\boldsymbol{R}_y(\beta)\boldsymbol{R}_x(\alpha)$.'
  - Every three-angle description has singular configurations ($\theta = 0$ or $\pi$ for ZYZ, $\beta = \pm 90^\circ$ for RPY) where only a sum or a difference of two angles can be recovered. The orientation itself stays well defined.
  - 'Any rotation is one angle about one axis. The axis satisfies $\boldsymbol{R}\boldsymbol{u} = \boldsymbol{u}$ and the angle is $\vartheta = \arccos\big((\operatorname{tr}\boldsymbol{R} - 1)/2\big)$.'
sources:
  - lectures/Lecture 2.pdf
  - lectures/Lecture 2 (revised 2026-10-13).pdf
  - lectures/Lecture 2 (revised 2026-10-20).pdf
---

## Where this fits

[Lecture 1](lecture:01-introduction-to-robotics) separated a manipulator's configuration
from the position and orientation of its tool, and noted that a camera, a robot base and a
workpiece each use their own frame. This lecture builds the mathematics that connects
those descriptions. It covers positions and rotations; homogeneous transformations and the
Denavit-Hartenberg convention follow in lecture 3. The references are chapter 2 of Spong et
al., chapter 2 of Siciliano et al. and chapter 2 of Niku (p. 2).

The motivating picture: a gripper approaching a cup. Knowing where the gripper is does not
suffice, since its fingers must also be turned so they can grasp. A representation is
needed for both *where* a rigid object is and *how it is oriented*.

:::definition Rigid body
An idealised object whose internal distances stay constant. Motion changes its placement
but does not stretch or bend it. Attaching a frame to a rigid body describes every point
of the body through one position and one orientation.
:::

## Notation and conventions

- All frames are right-handed; all coordinate vectors are columns. Bold symbols are vectors
  and matrices.
- A **superscript** on a coordinate vector names the frame its components are expressed
  in. It is not an exponent: $\boldsymbol{p}^0$ is $P$ in frame $\{0\}$.
- Frame $\{0\}$ is the global frame with origin $O$, axes $x, y, z$ and unit vectors
  $\boldsymbol{i}, \boldsymbol{j}, \boldsymbol{k}$. Frame $\{k\}$ is a local frame with
  origin $O_k$ and axes $x_k, y_k, z_k$.
- The final local frame (the end-effector frame) has axes $\boldsymbol{n}$ (**normal**,
  across the jaws), $\boldsymbol{s}$ (**sliding**) and $\boldsymbol{a}$ (**approach**,
  along the fingers toward the object), with
  $\boldsymbol{n} \times \boldsymbol{s} = \boldsymbol{a}$. Niku writes $\boldsymbol{o}$
  where these notes write $\boldsymbol{s}$.
- Positive angles follow the right-hand rule: thumb along the positive axis, fingers curl
  in the positive direction. Seen from the positive axis looking at the origin, that is
  counterclockwise.

In figure 1 of the notes the gripper hangs over a cup with
$\boldsymbol{n} = \boldsymbol{i}$, $\boldsymbol{s} = -\boldsymbol{j}$ and
$\boldsymbol{a} = -\boldsymbol{k}$: approach straight down.

## Representing positions

A point $P$ is a geometric location; its coordinates depend on the frame. In the global
frame

$$\overrightarrow{OP} = p_x \boldsymbol{i} + p_y \boldsymbol{j} + p_z \boldsymbol{k}, \qquad \boldsymbol{p}^0 = \begin{bmatrix} p_x \\ p_y \\ p_z \end{bmatrix} .$$

Each component is a signed projection onto an axis. Relative to a local frame at $O_1$ the
same point has $\boldsymbol{p}^1 = [p_n\ p_s\ p_a]^\top$, generally different numbers for
the same physical point.

Geometrically $\overrightarrow{OP} = \overrightarrow{OO_1} + \overrightarrow{O_1P}$ always
holds. As *coordinate columns* the sum only works when both are expressed in the same
frame. If the local axes are parallel to the global ones and
$\boldsymbol{d}^0 = [d_x\ d_y\ d_z]^\top$ is the local origin expressed globally, then

$$\boldsymbol{p}^0 = \boldsymbol{d}^0 + \boldsymbol{p}^1, \qquad \boldsymbol{p}^1 = \boldsymbol{p}^0 - \boldsymbol{d}^0 .$$

:::pitfall Adding columns from different frames
$\boldsymbol{p}^0 = \boldsymbol{d}^0 + \boldsymbol{p}^1$ is **not valid** when the local
axes are rotated. The local components must first be converted to global components. That
conversion is the rotation matrix.
:::

## Rotation in the plane

Two frames share an origin in the $xy$ plane. The local frame is turned counterclockwise
by $\theta$, so $\boldsymbol{n}$ makes the angle $\theta$ with $x$ and $\boldsymbol{s}$
sits at $\theta + 90^\circ$. Projecting onto the global axes:

$$\boldsymbol{n} = \begin{bmatrix} \cos\theta \\ \sin\theta \end{bmatrix}, \qquad \boldsymbol{s} = \begin{bmatrix} -\sin\theta \\ \cos\theta \end{bmatrix} .$$

The minus sign is geometry and not convention: the horizontal projection of
$\boldsymbol{s}$ is $-\cos(90^\circ - \theta) = -\sin\theta$.

A point's local coordinates say how far to go along $\boldsymbol{n}$ and $\boldsymbol{s}$:

$$\boldsymbol{p}^0 = p_n \boldsymbol{n} + p_s \boldsymbol{s} = \underbrace{\begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix}}_{\boldsymbol{R}(\theta)} \boldsymbol{p}^1 .$$

The first column is the local $\boldsymbol{n}$ direction expressed globally, the second the
local $\boldsymbol{s}$ direction. **This column reading is the central idea** and carries
over unchanged to three dimensions. Going back is a transpose:

$$\boldsymbol{p}^1 = \boldsymbol{R}^\top(\theta)\, \boldsymbol{p}^0, \qquad \boldsymbol{R}^\top(\theta) = \boldsymbol{R}(-\theta) = \boldsymbol{R}^{-1}(\theta) .$$

:::example A 90° orientation, there and back (examples 1 and 2)
A point one unit along local $\boldsymbol{n}$ has $\boldsymbol{p}^1 = (1, 0)$. With the
local frame turned by $90^\circ$,

$$\boldsymbol{p}^0 = \begin{bmatrix} 0 & -1 \\ 1 & 0 \end{bmatrix} \begin{bmatrix} 1 \\ 0 \end{bmatrix} = \begin{bmatrix} 0 \\ 1 \end{bmatrix} ,$$

so local $\boldsymbol{n}$ points along global $y$, and the second column says local
$\boldsymbol{s}$ points along $-x$. Back again:

$$\boldsymbol{p}^1 = \boldsymbol{R}^\top(90^\circ)\, \boldsymbol{p}^0 = \begin{bmatrix} 0 & 1 \\ -1 & 0 \end{bmatrix} \begin{bmatrix} 0 \\ 1 \end{bmatrix} = \begin{bmatrix} 1 \\ 0 \end{bmatrix} .$$
:::

## Rotation in space

Let $\boldsymbol{n}, \boldsymbol{s}, \boldsymbol{a}$ be the three local unit axes, all
expressed in the global frame. Each component is a signed projection, and the projection of
one unit vector on another is the cosine of the angle between them:

$$n_x = \boldsymbol{i}^\top \boldsymbol{n} = \cos\angle(x, \boldsymbol{n}), \qquad s_y = \boldsymbol{j}^\top \boldsymbol{s} = \cos\angle(y, \boldsymbol{s}), \qquad a_z = \boldsymbol{k}^\top \boldsymbol{a} = \cos\angle(z, \boldsymbol{a}) .$$

That is why a rotation matrix is also called a **direction cosine matrix**.

:::definition Rotation matrix
$$\boldsymbol{R} = \begin{bmatrix} \boldsymbol{n} & \boldsymbol{s} & \boldsymbol{a} \end{bmatrix} = \begin{bmatrix} n_x & s_x & a_x \\ n_y & s_y & a_y \\ n_z & s_z & a_z \end{bmatrix}$$

**Read columns as axes and rows as global components.** The first column says where local
$\boldsymbol{n}$ points. The first row computes the global $x$ component of any local
vector.
:::

With coincident origins, $\boldsymbol{p}^0 = p_n\boldsymbol{n} + p_s\boldsymbol{s} + p_a\boldsymbol{a} = \boldsymbol{R}\boldsymbol{p}^1$.
A rotation matrix holds orientation only. If the origins differ, rotate first and then add
the origin displacement:

$$\boldsymbol{p}^0 = \boldsymbol{d}^0 + \boldsymbol{R}\boldsymbol{p}^1 \qquad \Longleftrightarrow \qquad \boldsymbol{p}^1 = \boldsymbol{R}^\top (\boldsymbol{p}^0 - \boldsymbol{d}^0) .$$

### Properties of a rotation matrix

:::theorem Orthogonality
$$\boldsymbol{R}^\top \boldsymbol{R} = \boldsymbol{I}, \qquad \boldsymbol{R}^{-1} = \boldsymbol{R}^\top .$$
:::

:::proof
The local axes are unit length and mutually perpendicular:
$\boldsymbol{n}^\top\boldsymbol{n} = \boldsymbol{s}^\top\boldsymbol{s} = \boldsymbol{a}^\top\boldsymbol{a} = 1$
and
$\boldsymbol{n}^\top\boldsymbol{s} = \boldsymbol{n}^\top\boldsymbol{a} = \boldsymbol{s}^\top\boldsymbol{a} = 0$.
The $(i, j)$ entry of $\boldsymbol{R}^\top\boldsymbol{R}$ is the dot product of column $i$
with column $j$, so the product collects exactly these nine numbers: ones on the diagonal,
zeros elsewhere.
:::

Orthogonality alone also admits reflections. A right-handed frame needs in addition

$$\boldsymbol{n} \times \boldsymbol{s} = \boldsymbol{a}, \qquad \det(\boldsymbol{R}) = \boldsymbol{n}^\top(\boldsymbol{s} \times \boldsymbol{a}) = 1 .$$

:::definition Special orthogonal group
$$SO(3) = \{\boldsymbol{R} \in \mathbb{R}^{3 \times 3} : \boldsymbol{R}^\top\boldsymbol{R} = \boldsymbol{I},\ \det(\boldsymbol{R}) = 1\}$$

"Group" means that composing or undoing rotations gives another rotation. For now it is
enough to know the two defining checks.
:::

A diagonal matrix with entries $(1, 1, -1)$ has perpendicular unit columns but determinant
$-1$: it reverses handedness and is not a rotation.

Rotations preserve lengths and angles, since for any $\boldsymbol{u}, \boldsymbol{v}$

$$(\boldsymbol{R}\boldsymbol{u})^\top(\boldsymbol{R}\boldsymbol{v}) = \boldsymbol{u}^\top\boldsymbol{R}^\top\boldsymbol{R}\boldsymbol{v} = \boldsymbol{u}^\top\boldsymbol{v}, \qquad \lVert\boldsymbol{R}\boldsymbol{v}\rVert^2 = \lVert\boldsymbol{v}\rVert^2 .$$

Its entries are dimensionless, even when the rotated vector is in metres.

:::recall Is a matrix with perpendicular unit columns always a rotation matrix?
No. It must also have determinant $+1$. With determinant $-1$ it is a reflection, which
turns a right-handed frame into a left-handed one.
:::

### Elementary rotations

Start from aligned, coincident frames and turn about one global axis. Each is a planar
rotation in the plane perpendicular to its axis, with the unchanged axis added.

$$\boldsymbol{R}_z(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{bmatrix}, \quad \boldsymbol{R}_x(\theta) = \begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos\theta & -\sin\theta \\ 0 & \sin\theta & \cos\theta \end{bmatrix}, \quad \boldsymbol{R}_y(\theta) = \begin{bmatrix} \cos\theta & 0 & \sin\theta \\ 0 & 1 & 0 \\ -\sin\theta & 0 & \cos\theta \end{bmatrix}$$

How to rebuild them instead of memorising them:

- about $z$: $\boldsymbol{a}$ stays on $z$; $\boldsymbol{n}$ and $\boldsymbol{s}$ turn in
  the $xy$ plane;
- about $x$: $\boldsymbol{n}$ stays on $x$; $\boldsymbol{s}$ turns from $y$ toward $z$ and
  $\boldsymbol{a}$ from $z$ toward $-y$;
- about $y$: $\boldsymbol{s}$ stays on $y$; $\boldsymbol{a}$ turns from $z$ toward $x$ and
  $\boldsymbol{n}$ from $x$ toward $-z$. That is why the minus sign of
  $\boldsymbol{R}_y$ sits in the bottom-left corner.

Two checks before using one: $\boldsymbol{R}_j(0) = \boldsymbol{I}$ and
$\boldsymbol{R}_j(-\theta) = \boldsymbol{R}_j^\top(\theta)$ for $j \in \{x, y, z\}$.

### Changing coordinates or physically rotating

The same matrix has two readings.

| | What happens | Formula |
|---|---|---|
| **Passive** (coordinate conversion) | The point stays; its coordinates are re-expressed between two frames | $\boldsymbol{p}^0 = \boldsymbol{R}\boldsymbol{p}^1$ |
| **Active** (physical rotation) | The vector turns; the frame stays fixed | $\boldsymbol{v}^0_{\text{after}} = \boldsymbol{R}\,\boldsymbol{v}^0_{\text{before}}$ |

To convert global coordinates into those of the rotated frame use $\boldsymbol{R}^\top$;
to turn a vector actively through the positive angle in global coordinates use
$\boldsymbol{R}$. Always say what moves and which frame expresses each vector.

:::example Actively rotating a vector about global $z$ (example 3)
$\boldsymbol{v}^0_{\text{before}} = [1, 0, 0]^\top$, turned through $45^\circ$ about fixed
$z$:

$$\boldsymbol{v}^0_{\text{after}} = \boldsymbol{R}_z(45^\circ) \begin{bmatrix} 1 \\ 0 \\ 0 \end{bmatrix} = \begin{bmatrix} \tfrac{\sqrt2}{2} \\ \tfrac{\sqrt2}{2} \\ 0 \end{bmatrix} .$$

Length still one, $z$ component still zero, and the vector now makes $45^\circ$ with the
positive $x$ axis.
:::

## Composition of rotations

### Keeping track of frames

Write $\boldsymbol{R}^0_1$ for the orientation of frame $\{1\}$ relative to frame $\{0\}$:
its columns are the axes of $\{1\}$ expressed in $\{0\}$, and it converts components from
$\{1\}$ to $\{0\}$. For free vectors, or with coincident origins,

$$\boldsymbol{v}^0 = \boldsymbol{R}^0_1 \boldsymbol{v}^1, \qquad \boldsymbol{v}^1 = \boldsymbol{R}^1_2 \boldsymbol{v}^2 \qquad \Longrightarrow \qquad \boldsymbol{v}^0 = \boldsymbol{R}^0_1 \boldsymbol{R}^1_2 \boldsymbol{v}^2 = \boldsymbol{R}^0_2 \boldsymbol{v}^2 .$$

Neighbouring indices name the intermediate frame, like cancelling: the lower $1$ meets the
upper $1$. Read the action on a vector from right to left. For $N$ frames

$$\boldsymbol{R}^0_N = \boldsymbol{R}^0_1 \boldsymbol{R}^1_2 \cdots \boldsymbol{R}^{N-1}_N, \qquad \boldsymbol{R}^N_0 = (\boldsymbol{R}^0_N)^\top .$$

### Current axis or fixed axis

Let $\boldsymbol{R}$ be the present orientation of the local frame relative to the global
frame, and add one more rotation.

| Axis of the added rotation | Update | The added matrix is written in |
|---|---|---|
| A **current** (body-fixed, local) axis | $\boldsymbol{R}_{\text{new}} = \boldsymbol{R}\,\boldsymbol{Q}_{\text{local}}$ (postmultiply) | local coordinates |
| A **fixed** (world, global) axis | $\boldsymbol{R}_{\text{new}} = \boldsymbol{Q}_{\text{global}}\,\boldsymbol{R}$ (premultiply) | global coordinates |

The subscripts $x, y, z$ on an elementary matrix mean the first, second and third axis *of
the frame the operation is written in*; they do not automatically mean world axes. Turn an
aligned frame by $\alpha$ about $z$ and then by $\beta$ about an $x$ axis:

$$\boldsymbol{R}_{\text{current}} = \boldsymbol{R}_z(\alpha)\boldsymbol{R}_x(\beta), \qquad \boldsymbol{R}_{\text{fixed}} = \boldsymbol{R}_x(\beta)\boldsymbol{R}_z(\alpha) .$$

The same two elementary matrices appear, but the physical second axis differs: after the
first turn the frame's own $x$ axis no longer coincides with the global $x$ axis.

:::example Why rotation order matters (example 4)
Both angles $90^\circ$:

$$\boldsymbol{R}_z(90^\circ) = \begin{bmatrix} 0 & -1 & 0 \\ 1 & 0 & 0 \\ 0 & 0 & 1 \end{bmatrix}, \qquad \boldsymbol{R}_x(90^\circ) = \begin{bmatrix} 1 & 0 & 0 \\ 0 & 0 & -1 \\ 0 & 1 & 0 \end{bmatrix} .$$

Second turn about the **current** $x$ axis, multiply on the right:

$$\boldsymbol{R}_{\text{current}} = \boldsymbol{R}_z(90^\circ)\boldsymbol{R}_x(90^\circ) = \begin{bmatrix} 0 & 0 & 1 \\ 1 & 0 & 0 \\ 0 & 1 & 0 \end{bmatrix} .$$

Second turn about the **fixed** $x$ axis, multiply on the left:

$$\boldsymbol{R}_{\text{fixed}} = \boldsymbol{R}_x(90^\circ)\boldsymbol{R}_z(90^\circ) = \begin{bmatrix} 0 & -1 & 0 \\ 0 & 0 & -1 \\ 1 & 0 & 0 \end{bmatrix} .$$

Third columns: $\boldsymbol{a}_{\text{current}} = [1, 0, 0]^\top$ and
$\boldsymbol{a}_{\text{fixed}} = [0, -1, 0]^\top$. One tool approaches along global $x$,
the other along $-y$. Spatial rotations are **noncommutative**.
:::

Rotations about the *same* axis are the exception:
$\boldsymbol{R}_z(\alpha)\boldsymbol{R}_z(\beta) = \boldsymbol{R}_z(\alpha + \beta)$, by the
angle-addition identities, and there the order does not matter. Do not extend that planar
intuition to different axes.

### The same rotation in another frame

If $\boldsymbol{Q}_{\text{local}}$ rotates vectors given in local coordinates, then
converting a global vector to local coordinates, rotating, and converting back gives the
global matrix of the same physical rotation:

$$\boldsymbol{Q}_{\text{global}} = \boldsymbol{R}\,\boldsymbol{Q}_{\text{local}}\,\boldsymbol{R}^\top .$$

This is a **similarity transformation**. It makes the two update rules consistent:
$\boldsymbol{Q}_{\text{global}}\boldsymbol{R} = \boldsymbol{R}\boldsymbol{Q}_{\text{local}}\boldsymbol{R}^\top\boldsymbol{R} = \boldsymbol{R}\boldsymbol{Q}_{\text{local}}$.

## Parameterizations of rotations

A rotation matrix has nine entries, but the orthonormality conditions impose six
independent constraints, leaving **three** degrees of freedom. So three parameters suffice
locally, although no three-angle description is globally unique and free of
singularities. For any of them the axis sequence, the angle signs and the fixed or current
interpretation must be stated.

Shorthand: $c_\eta = \cos\eta$ and $s_\eta = \sin\eta$. $\operatorname{atan2}(y, x)$ is the
angle of the planar pair $(x, y)$ in the correct quadrant: **$y$ first, $x$ second**. It is
undefined when both arguments are zero.

### Euler angles (intrinsic ZYZ)

Start aligned with the global frame. Turn by $\phi$ about $z$, then by $\theta$ about the
*current* $y$ axis, then by $\psi$ about the *current* $z$ axis. Each step is about a
current axis, so each factor goes on the right:

$$\boldsymbol{R}_{ZYZ} = \boldsymbol{R}_z(\phi)\boldsymbol{R}_y(\theta)\boldsymbol{R}_z(\psi) = \begin{bmatrix} c_\phi c_\theta c_\psi - s_\phi s_\psi & -c_\phi c_\theta s_\psi - s_\phi c_\psi & c_\phi s_\theta \\ s_\phi c_\theta c_\psi + c_\phi s_\psi & -s_\phi c_\theta s_\psi + c_\phi c_\psi & s_\phi s_\theta \\ -s_\theta c_\psi & s_\theta s_\psi & c_\theta \end{bmatrix} .$$

The third column does not contain $\psi$: the last turn is about the approach axis itself,
so it spins $\boldsymbol{n}$ and $\boldsymbol{s}$ without moving $\boldsymbol{a}$. This is
the parameterization tied to spherical wrists.

**Recovering the angles.** Choose $0 \le \theta \le \pi$, so $\sin\theta \ge 0$. From the
third column, $a_x = c_\phi s_\theta$, $a_y = s_\phi s_\theta$, $a_z = c_\theta$, hence
$a_x^2 + a_y^2 = s_\theta^2$. From the last row, $n_z = -s_\theta c_\psi$ and
$s_z = s_\theta s_\psi$. For $0 < \theta < \pi$:

$$\theta = \operatorname{atan2}\!\Big(\sqrt{a_x^2 + a_y^2},\ a_z\Big), \qquad \phi = \operatorname{atan2}(a_y, a_x), \qquad \psi = \operatorname{atan2}(s_z, -n_z) .$$

The common factor $s_\theta > 0$ does not change a quadrant, which is why it can be dropped
inside each $\operatorname{atan2}$.

:::example An approach axis at 45° in the global $xy$ plane (example 6)
$\phi = 45^\circ$, $\theta = 90^\circ$, $\psi = -30^\circ$:

$$\boldsymbol{R} = \boldsymbol{R}_z(45^\circ)\boldsymbol{R}_y(90^\circ)\boldsymbol{R}_z(-30^\circ) = \begin{bmatrix} \tfrac{\sqrt2}{4} & -\tfrac{\sqrt6}{4} & \tfrac{\sqrt2}{2} \\ -\tfrac{\sqrt2}{4} & \tfrac{\sqrt6}{4} & \tfrac{\sqrt2}{2} \\ -\tfrac{\sqrt3}{2} & -\tfrac12 & 0 \end{bmatrix} .$$

The third column $\boldsymbol{a} = [\tfrac{\sqrt2}{2}, \tfrac{\sqrt2}{2}, 0]^\top$ lies in
the $xy$ plane at $45^\circ$ to $x$. Recovering:

$$\theta = \operatorname{atan2}(1, 0) = 90^\circ, \qquad \phi = \operatorname{atan2}\!\big(\tfrac{\sqrt2}{2}, \tfrac{\sqrt2}{2}\big) = 45^\circ, \qquad \psi = \operatorname{atan2}\!\big(-\tfrac12, \tfrac{\sqrt3}{2}\big) = -30^\circ .$$

The simpler example 5, $(\phi, \theta, \psi) = (0, 90^\circ, 0)$, gives
$\boldsymbol{R} = \boldsymbol{R}_y(90^\circ)$ with $\boldsymbol{a}$ along global $x$.
:::

**Singular configurations.** When $\theta = 0$ the first and third axes coincide and the two
$z$ rotations merge:

$$\boldsymbol{R}_{ZYZ}(\phi, 0, \psi) = \boldsymbol{R}_z(\phi + \psi) .$$

Only the sum is recoverable; a convenient choice is $\phi = 0$,
$\psi = \operatorname{atan2}(n_y, n_x)$. At $\theta = \pi$ only the difference
$\delta = \phi - \psi$ is recoverable, for instance
$\delta = \operatorname{atan2}(-s_x, s_y)$, from

$$\boldsymbol{R}_{ZYZ}(\phi, \pi, \psi) = \begin{bmatrix} -\cos\delta & -\sin\delta & 0 \\ -\sin\delta & \cos\delta & 0 \\ 0 & 0 & -1 \end{bmatrix} .$$

### Roll, pitch, yaw (fixed-axis XYZ)

The names and the sequence differ between books, so three numbers mean nothing without the
convention. In these notes: **roll $\alpha$ about $x$, pitch $\beta$ about $y$, yaw
$\gamma$ about $z$**, applied about the **fixed** axes in the order $x$, then $y$, then
$z$. The aircraft picture behind the names has $x$ forward, $y$ to the left and $z$ up.
Each step is about a fixed axis, so each factor goes on the left:

$$\boldsymbol{R}_{RPY} = \boldsymbol{R}_z(\gamma)\boldsymbol{R}_y(\beta)\boldsymbol{R}_x(\alpha) = \begin{bmatrix} c_\gamma c_\beta & c_\gamma s_\beta s_\alpha - s_\gamma c_\alpha & c_\gamma s_\beta c_\alpha + s_\gamma s_\alpha \\ s_\gamma c_\beta & s_\gamma s_\beta s_\alpha + c_\gamma c_\alpha & s_\gamma s_\beta c_\alpha - c_\gamma s_\alpha \\ -s_\beta & c_\beta s_\alpha & c_\beta c_\alpha \end{bmatrix} .$$

The same matrix comes from the reversed *intrinsic* sequence: yaw about current $z$, pitch
about the new $y$, roll about the new $x$ (intrinsic ZYX). The first column does not depend
on roll.

**Recovering the angles.** Choose $-\pi/2 \le \beta \le \pi/2$, so $\cos\beta \ge 0$. The
first column gives $n_x = c_\gamma c_\beta$, $n_y = s_\gamma c_\beta$, $n_z = -s_\beta$; the
last row gives $s_z = c_\beta s_\alpha$, $a_z = c_\beta c_\alpha$. For
$-\pi/2 < \beta < \pi/2$:

$$\beta = \operatorname{atan2}\!\Big(-n_z,\ \sqrt{n_x^2 + n_y^2}\Big), \qquad \gamma = \operatorname{atan2}(n_y, n_x), \qquad \alpha = \operatorname{atan2}(s_z, a_z) .$$

:::example The same orientation, described by RPY (example 8)
$\alpha = -90^\circ$, $\beta = 60^\circ$, $\gamma = -45^\circ$ gives
$\boldsymbol{R}_z(-45^\circ)\boldsymbol{R}_y(60^\circ)\boldsymbol{R}_x(-90^\circ)$, which
multiplies out to exactly the matrix of the Euler example above. One orientation, two
different angle triples under two conventions. Recovering:

$$\beta = \operatorname{atan2}\!\big(\tfrac{\sqrt3}{2}, \tfrac12\big) = 60^\circ, \qquad \alpha = \operatorname{atan2}\!\big(-\tfrac12, 0\big) = -90^\circ, \qquad \gamma = \operatorname{atan2}\!\big(-\tfrac{\sqrt2}{4}, \tfrac{\sqrt2}{4}\big) = -45^\circ .$$

Example 7 is the sanity check: zero roll and pitch with $90^\circ$ yaw gives
$\boldsymbol{R}_z(90^\circ)$, the planar case again.
:::

:::warning Gimbal lock
At $\beta = \pm\pi/2$ the cosine vanishes and both pairs used to recover roll and yaw
become zero. For $\beta = \pi/2$

$$\boldsymbol{R}_{RPY} = \begin{bmatrix} 0 & \sin(\alpha - \gamma) & \cos(\alpha - \gamma) \\ 0 & \cos(\alpha - \gamma) & -\sin(\alpha - \gamma) \\ -1 & 0 & 0 \end{bmatrix} ,$$

so only the difference $\alpha - \gamma$ is observable; at $\beta = -90^\circ$ only the
sum. The object still has a perfectly good orientation. It is the chosen coordinates that
become ambiguous, and near these configurations small changes in the matrix produce large
changes in the recovered angles.
:::

:::pitfall A parameterization singularity is not a robot singularity
At the singular Euler or RPY configurations the rotation matrix stays valid; only the
uniqueness of the angle description fails. That says nothing, by itself, about whether a
particular mechanism can move.
:::

### Axis and angle

**Euler's rotation theorem:** any proper three-dimensional rotation is a single angle
$\vartheta$ about a single unit axis $\boldsymbol{u}$, with
$\boldsymbol{u}^\top\boldsymbol{u} = 1$. Four numbers, one constraint, three degrees of
freedom. (The notes use $\boldsymbol{u}$ so that $\boldsymbol{k}$ keeps meaning the global
$z$ unit vector.)

A vector along the axis is unchanged; a perpendicular vector turns through $\vartheta$ in
the plane normal to the axis. Any $\boldsymbol{v}$ splits into
$\boldsymbol{v}_\parallel = \boldsymbol{u}(\boldsymbol{u}^\top\boldsymbol{v})$ and
$\boldsymbol{v}_\perp = \boldsymbol{v} - \boldsymbol{v}_\parallel$.

**Recovering the axis.** The axis is the direction the rotation leaves alone:

$$\boldsymbol{R}\boldsymbol{u} = \boldsymbol{u} \qquad \Longleftrightarrow \qquad (\boldsymbol{R} - \boldsymbol{I})\boldsymbol{u} = \boldsymbol{0}, \quad \boldsymbol{u}^\top\boldsymbol{u} = 1 .$$

Solve the homogeneous system, then normalise. $\boldsymbol{u}$ and $-\boldsymbol{u}$ are the
same line; reversing the axis reverses the sign of the angle.

**Recovering the angle.**

:::theorem Angle from the trace
$$\vartheta = \arccos\!\left(\frac{\operatorname{tr}(\boldsymbol{R}) - 1}{2}\right) = \arccos\!\left(\frac{n_x + s_y + a_z - 1}{2}\right), \qquad 0 \le \vartheta \le \pi$$
:::

:::proof
Pick a unit $\boldsymbol{b}_1 \perp \boldsymbol{u}$ and set
$\boldsymbol{b}_2 = \boldsymbol{u} \times \boldsymbol{b}_1$. Then
$\boldsymbol{B} = [\boldsymbol{b}_1\ \boldsymbol{b}_2\ \boldsymbol{u}]$ is a right-handed
orthonormal frame with $\boldsymbol{B}^\top\boldsymbol{B} = \boldsymbol{I}$. In that frame
the rotation axis is the third coordinate direction, so the rotation is an ordinary planar
rotation of the first two:

$$\boldsymbol{B}^\top\boldsymbol{R}\boldsymbol{B} = \begin{bmatrix} \cos\vartheta & -\sin\vartheta & 0 \\ \sin\vartheta & \cos\vartheta & 0 \\ 0 & 0 & 1 \end{bmatrix} .$$

Its trace is $1 + 2\cos\vartheta$. The trace does not change under a change of frame,
because $\operatorname{tr}(\boldsymbol{A}\boldsymbol{C}) = \operatorname{tr}(\boldsymbol{C}\boldsymbol{A})$:
$\operatorname{tr}(\boldsymbol{B}^\top\boldsymbol{R}\boldsymbol{B}) = \operatorname{tr}(\boldsymbol{R}\boldsymbol{B}\boldsymbol{B}^\top) = \operatorname{tr}(\boldsymbol{R})$.
:::

For $0 < \vartheta < \pi$ choose the direction of $\boldsymbol{u}$ so that the positive
right-hand turn agrees with $\boldsymbol{R}$, that is
$\boldsymbol{b}_2^\top\boldsymbol{R}\boldsymbol{b}_1 = \sin\vartheta > 0$; if it comes out
negative, flip $\boldsymbol{u}$. At $\vartheta = 0$ every axis describes the identity, and
at $\vartheta = \pi$ both axis directions describe the same half-turn. Numerically, clip the
argument of $\arccos$ to $[-1, 1]$ against round-off.

:::example Axis and angle of a quarter-turn about global $z$ (example 9)
For $\boldsymbol{R} = \boldsymbol{R}_z(90^\circ)$ the system
$(\boldsymbol{R} - \boldsymbol{I})\boldsymbol{u} = \boldsymbol{0}$ reads
$-u_x - u_y = 0$ and $u_x - u_y = 0$. Adding gives $u_y = 0$, then $u_x = 0$, so
$u_z = \pm 1$. The matrix sends $\boldsymbol{i}$ to $\boldsymbol{j}$, a positive right-hand
quarter-turn about $\boldsymbol{k}$, so $\boldsymbol{u} = \boldsymbol{k}$. The trace is $1$,
hence $\vartheta = \arccos(0) = 90^\circ$.
:::

:::note The approach axis is not the rotation axis
The columns of $\boldsymbol{R}$ are where the frame's axes *end up*:
$\boldsymbol{a} = \boldsymbol{R}\boldsymbol{k}$. The rotation axis is what *does not
move*: $\boldsymbol{R}\boldsymbol{u} = \boldsymbol{u}$. They coincide only when the
initial third direction $\boldsymbol{k}$ is aligned with $\boldsymbol{u}$.
:::

## What an exam wants

:::paper Check that a matrix is a rotation matrix
Two checks, both written out: (1) the columns are unit length and mutually perpendicular,
equivalently $\boldsymbol{R}^\top\boldsymbol{R} = \boldsymbol{I}$; (2)
$\det(\boldsymbol{R}) = +1$, equivalently
$\boldsymbol{n} \times \boldsymbol{s} = \boldsymbol{a}$. State the conclusion:
"$\boldsymbol{R} \in SO(3)$".
:::

:::paper Left or right?
Name the axis of the added rotation before multiplying. "The second rotation is about the
**current** $x$ axis, so its matrix is written in local coordinates and multiplies on the
**right**." Or: "… about the **fixed** $x$ axis, so it multiplies on the **left**." Then
read the answer off the columns: the third column is the approach direction.
:::

:::paper Recover angles from a matrix
State the convention and the range first (ZYZ with $0 \le \theta \le \pi$, or fixed-axis
XYZ with $-\pi/2 \le \beta \le \pi/2$). Write which entries are used, apply
$\operatorname{atan2}$ with $y$ first, and check by substituting back. If
$\sin\theta = 0$ or $\cos\beta = 0$, say that the configuration is singular and that only
a sum or a difference of two angles is determined.
:::

## Where next

- Drill: [](deck:rigid-body-motions).
- Compute: [](problems:rigid-body-practice), the seven numerical problems that close the
  lecture, with solutions.
- The matrices to know cold: the rotation section of [the formula sheet](formulas).
