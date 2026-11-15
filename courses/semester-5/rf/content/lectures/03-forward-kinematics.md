---
title: 'Forward kinematics: homogeneous transformations and Denavit-Hartenberg'
number: 3
topics: [transformations, kinematics]
summary: How one 4×4 matrix combines orientation and position, how such matrices compose and invert, the difference between converting coordinates and commanding a motion, and the standard Denavit-Hartenberg convention that turns a robot drawing into a table of four parameters per link and a chain of matrices giving the tool pose.
takeaways:
  - 'A homogeneous transformation $\boldsymbol{T}^0_1 = \begin{bmatrix} \boldsymbol{R}^0_1 & \boldsymbol{d}^0 \\ \boldsymbol{0}^\top & 1 \end{bmatrix}$ maps $[\boldsymbol{p}^1; 1]$ to $[\boldsymbol{p}^0; 1]$. A point gets a final coordinate 1, a free vector 0, so directions ignore the translation.'
  - 'Chains multiply: $\boldsymbol{T}^0_2 = \boldsymbol{T}^0_1\boldsymbol{T}^1_2$, so $\boldsymbol{d}^0_2 = \boldsymbol{d}^0_1 + \boldsymbol{R}^0_1\boldsymbol{d}^1_2$. Translations in different frames cannot simply be added.'
  - 'The inverse is $\begin{bmatrix} \boldsymbol{R}^\top & -\boldsymbol{R}^\top\boldsymbol{d} \\ \boldsymbol{0}^\top & 1 \end{bmatrix}$, not the transpose of the whole matrix.'
  - 'A motion in the current frame multiplies on the right, $\boldsymbol{T}\boldsymbol{U}$; in the fixed frame on the left, $\boldsymbol{U}\boldsymbol{T}$. A rotation axis needs a direction and a location.'
  - 'Standard DH: the axis of joint $i$ is $z_{i-1}$, $x_i$ lies along the common normal of $z_{i-1}$ and $z_i$, and $\boldsymbol{A}_i = \boldsymbol{T}_z(\theta_i)\boldsymbol{T}_{trans}(0,0,d_i)\boldsymbol{T}_{trans}(\ell_i,0,0)\boldsymbol{T}_x(\alpha_i)$. A revolute joint varies $\theta_i$, a prismatic one $d_i$.'
  - 'Forward kinematics is the product $\boldsymbol{T}^0_n(\boldsymbol{q}) = \boldsymbol{A}_1(q_1)\cdots\boldsymbol{A}_n(q_n)$, with base calibration on the left and tool offset on the right.'
sources:
  - lectures/Lecture 3.pdf
---

## Where this fits

[Lecture 2](lecture:02-rigid-body-motions) described points and orientations and how
rotations compose. This lecture adds the origin displacement into one matrix, then uses a
chain of such matrices to model a robot. The motivating picture (p. 2): a camera sees a cup
in its own frame, the controller works in the base frame, and the gripper's pose depends on
the joint values. Homogeneous transformations solve the first problem, a chain of
joint-dependent transformations the second. References: Spong (chapters 2 and 3),
Siciliano et al. (sections 2.7 and 2.8), Niku (chapter 2).

**Notation.** As in lecture 2: global axes $x, y, z$ with unit vectors
$\boldsymbol{i}, \boldsymbol{j}, \boldsymbol{k}$; a local frame $\{i\}$ with axes
$x_i, y_i, z_i$; the gripper's $\boldsymbol{n}, \boldsymbol{s}, \boldsymbol{a}$ (normal,
sliding, approach). A superscript names the frame the components are expressed in.
$\boldsymbol{T}^0_1$ describes frame $\{1\}$ relative to $\{0\}$ and converts coordinates
from $\{1\}$ into $\{0\}$. Before every calculation, ask: **which frame, which units?**

## Homogeneous transformations

### Combining orientation and position

A point $P$ on a body with local frame $\{1\}$ (origin displaced by $\boldsymbol{d}^0$,
axes $\boldsymbol{R}^0_1$):

$$\boldsymbol{p}^0 = \boldsymbol{R}^0_1\boldsymbol{p}^1 + \boldsymbol{d}^0 . \qquad (1.1)$$

This describes the **same physical point** in two coordinate systems; it does not move
anything. It is affine, not linear: a $3 \times 3$ matrix maps zero to zero, so it cannot
represent a translation.

### Homogeneous coordinates

Append a 1 to each point, $\tilde{\boldsymbol{p}} = [\boldsymbol{p}; 1]$, and define

$$\boldsymbol{T}^0_1 = \begin{bmatrix} \boldsymbol{R}^0_1 & \boldsymbol{d}^0 \\ \boldsymbol{0}^\top & 1 \end{bmatrix} = \begin{bmatrix} n_x & s_x & a_x & d_x \\ n_y & s_y & a_y & d_y \\ n_z & s_z & a_z & d_z \\ 0 & 0 & 0 & 1 \end{bmatrix}, \qquad \boldsymbol{T}^0_1\tilde{\boldsymbol{p}}^1 = \tilde{\boldsymbol{p}}^0 .$$

The upper-left block is the orientation, the last column the position of the local origin,
and the last row keeps the final coordinate 1. The extra coordinate is an algebraic device,
not a fourth spatial dimension.

**A free vector** (a direction such as the approach axis) gets a final **0**:
$\boldsymbol{T}[\boldsymbol{v}^1; 0] = [\boldsymbol{R}\boldsymbol{v}^1; 0]$. The translation
is multiplied by zero. A point such as the TCP takes 1, a direction takes 0.

These matrices form the special Euclidean group
$SE(3) = \{ [\boldsymbol{R}\ \boldsymbol{d};\ \boldsymbol{0}^\top\ 1] : \boldsymbol{R} \in SO(3),\ \boldsymbol{d} \in \mathbb{R}^3 \}$:
rigid placements with three translational and three rotational degrees of freedom. Two
points moved by the same transformation keep their distance, as a rigid body requires.

### Elementary transformations

A pure translation has $\boldsymbol{R} = \boldsymbol{I}$; a pure rotation about an axis
through the origin has $\boldsymbol{d} = \boldsymbol{0}$:

$$\boldsymbol{T}_{trans}(d_x, d_y, d_z) = \begin{bmatrix} \boldsymbol{I} & \boldsymbol{d} \\ \boldsymbol{0}^\top & 1 \end{bmatrix}, \qquad \boldsymbol{T}_z(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta & 0 & 0 \\ \sin\theta & \cos\theta & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix},$$

and $\boldsymbol{T}_x(\theta)$, $\boldsymbol{T}_y(\theta)$ embed $\boldsymbol{R}_x$ and
$\boldsymbol{R}_y$ the same way.

### Composition

With $\boldsymbol{p}^1 = \boldsymbol{R}^1_2\boldsymbol{p}^2 + \boldsymbol{d}^1_2$ and
$\boldsymbol{p}^0 = \boldsymbol{R}^0_1\boldsymbol{p}^1 + \boldsymbol{d}^0_1$, substitution
gives

$$\boldsymbol{R}^0_2 = \boldsymbol{R}^0_1\boldsymbol{R}^1_2, \qquad \boldsymbol{d}^0_2 = \boldsymbol{d}^0_1 + \boldsymbol{R}^0_1\boldsymbol{d}^1_2, \qquad \boldsymbol{T}^0_2 = \boldsymbol{T}^0_1\boldsymbol{T}^1_2 .$$

$\boldsymbol{d}^i_j$ is the displacement from $O_i$ to $O_j$ expressed in frame $\{i\}$. The
second translation must be **rotated into the first frame before adding**; block
multiplication does it automatically. The rightmost factor acts first on a point.

:::example A workpiece seen by a camera (Example 1)
The camera frame $\{1\}$ has $\boldsymbol{R}^0_1 = \boldsymbol{R}_z(90^\circ)$ and origin
$(0.40, 0.20, 0.10)$ m in the base frame. It measures a workpiece frame $\{2\}$ with
$\boldsymbol{R}^1_2 = \boldsymbol{R}_z(-90^\circ)$ and origin $(0.10, 0.20, 0)$ m in camera
coordinates. Then $\boldsymbol{R}^0_2 = \boldsymbol{I}$ and

$$\boldsymbol{d}^0_2 = \begin{bmatrix} 0.40 \\ 0.20 \\ 0.10 \end{bmatrix} + \begin{bmatrix} 0 & -1 & 0 \\ 1 & 0 & 0 \\ 0 & 0 & 1 \end{bmatrix}\begin{bmatrix} 0.10 \\ 0.20 \\ 0 \end{bmatrix} = \begin{bmatrix} 0.20 \\ 0.30 \\ 0.10 \end{bmatrix} \text{ m}.$$

Adding the two columns directly would give $(0.50, 0.40, 0.10)$, which is wrong: they are
in different frames.
:::

### The inverse

Undo the translation, then the rotation:
$\boldsymbol{p}^1 = (\boldsymbol{R}^0_1)^\top(\boldsymbol{p}^0 - \boldsymbol{d}^0)$, so

$$\boldsymbol{T}^{-1} = \begin{bmatrix} \boldsymbol{R}^\top & -\boldsymbol{R}^\top\boldsymbol{d} \\ \boldsymbol{0}^\top & 1 \end{bmatrix}, \qquad \boldsymbol{T}^1_0 = (\boldsymbol{T}^0_1)^{-1}.$$

The inverse translation is the way back to the original origin, **expressed in the new
frame**: it needs both the minus sign and the rotation. A $4 \times 4$ rigid transformation
is not an orthogonal matrix, so its inverse is not its transpose; only the rotation block
inverts by transposing.

:::example A point and its inverse (Example 2)
Frame $\{1\}$: $\boldsymbol{R}_z(90^\circ)$, origin $(0.40, 0.20, 0.10)$ m. A point with
local coordinates $(0.10, 0.05, 0.20)$ m: rotating gives $(-0.05, 0.10, 0.20)$, adding the
origin gives $\boldsymbol{p}^0 = (0.35, 0.30, 0.30)$ m. The inverse has
$-\boldsymbol{R}^\top\boldsymbol{d} = (-0.20, 0.40, -0.10)$ m:

$$\boldsymbol{T}^1_0 = \begin{bmatrix} 0 & 1 & 0 & -0.20 \\ -1 & 0 & 0 & 0.40 \\ 0 & 0 & 1 & -0.10 \\ 0 & 0 & 0 & 1 \end{bmatrix},$$

and $\boldsymbol{T}^1_0\tilde{\boldsymbol{p}}^0$ returns $(0.10, 0.05, 0.20)$.
:::

### Checks before using a transformation

- $\boldsymbol{T}^0_1$ maps **local to global**; its translation is in frame $\{0\}$ and its
  columns are local axes in frame $\{0\}$. All lengths in one unit.
- Rotation block: perpendicular unit columns, determinant $+1$. Last row $(0, 0, 0, 1)$.
- Three quick tests: the local origin maps to the translation column; a local unit
  direction (as a free vector) maps to the matching rotation column; forward then inverse
  returns the starting point.

### Completing a partially specified frame

Example 3 (adapted from Niku's Example 2.4) gives a frame matrix with the translation
$(5, 3, 2)$ and only some orientation entries, including $n_y = c = \frac{\sqrt2}{2}$,
$s_x = 0$ and $a_z = 0$. Unit length and pairwise perpendicularity give six equations;
with the branch $s_y = 0$, $s_z = 1$, $a_y = -c$ they leave $n_x = a_x = \pm c$:

$$\boldsymbol{T}_1 = \begin{bmatrix} c & 0 & c & 5 \\ c & 0 & -c & 3 \\ 0 & 1 & 0 & 2 \\ 0 & 0 & 0 & 1 \end{bmatrix}, \qquad \boldsymbol{T}_2 = \begin{bmatrix} -c & 0 & -c & 5 \\ c & 0 & -c & 3 \\ 0 & 1 & 0 & 2 \\ 0 & 0 & 0 & 1 \end{bmatrix}.$$

Both have orthonormal columns, but only $\boldsymbol{T}_1$ satisfies
$\boldsymbol{n} \times \boldsymbol{s} = \boldsymbol{a}$; $\boldsymbol{T}_2$ is left-handed,
determinant $-1$, not a rotation. Other valid completions exist (for example
$\boldsymbol{n} = (-c, c, 0)$ with $\boldsymbol{a} = (c, c, 0)$).

:::pitfall Orthogonal is not enough
Check unit length and perpendicularity, **then handedness**. A matrix with orthonormal
columns and determinant $-1$ is a reflection, not a rigid rotation. And state which branch
you chose: the given entries may not determine a unique frame.
:::

### Converting coordinates against commanding a motion

Now the matrix moves the body. With current pose $\boldsymbol{T}$ and a commanded transform
$\boldsymbol{U}$:

$$\boldsymbol{T}_{new} = \boldsymbol{T}\,\boldsymbol{U}_{local} \ \text{(current frame)}, \qquad \boldsymbol{T}_{new} = \boldsymbol{U}_{global}\,\boldsymbol{T} \ \text{(fixed frame)}.$$

- **Translation along local axes** by $\boldsymbol{b}$: $\boldsymbol{d}_{new} = \boldsymbol{d} + \boldsymbol{R}\boldsymbol{b}$.
  Moving the tool $h$ along its approach axis gives $\boldsymbol{d} + h\boldsymbol{a}$, which
  is why the third column is so useful for insertion.
- **Translation along global axes** by $\boldsymbol{b}^0$: $\boldsymbol{d}_{new} = \boldsymbol{d} + \boldsymbol{b}^0$.
- **Rotation $\boldsymbol{Q}$ in the current frame** about the local origin: orientation
  $\boldsymbol{R}\boldsymbol{Q}$, origin unchanged.
- **Rotation premultiplied in the fixed frame**: orientation $\boldsymbol{Q}\boldsymbol{R}$
  **and** origin $\boldsymbol{Q}\boldsymbol{d}$: the whole pose swings about the world
  origin.
- **Rotation about an axis through a point $\boldsymbol{c}^0$**:
  $\boldsymbol{p}' = \boldsymbol{Q}\boldsymbol{p} + (\boldsymbol{I} - \boldsymbol{Q})\boldsymbol{c}^0$, i.e.
  $$\boldsymbol{U}_c = \begin{bmatrix} \boldsymbol{Q} & (\boldsymbol{I} - \boldsymbol{Q})\boldsymbol{c}^0 \\ \boldsymbol{0}^\top & 1 \end{bmatrix}.$$

:::example The same command in two frames (Example 4)
From the pose of Example 2: $0.10$ m along the local first axis (which points along global
$y$) gives origin $(0.40, 0.30, 0.10)$; $0.10$ m along global $x$ gives $(0.50, 0.20, 0.10)$.
A $90^\circ$ rotation about global $z$ through the world origin gives orientation
$\boldsymbol{R}_z(180^\circ)$ and origin $(-0.20, 0.40, 0.10)$; the same rotation about a
vertical axis through the tool origin gives $\boldsymbol{R}_z(180^\circ)$ with the origin
staying at $(0.40, 0.20, 0.10)$. **An axis needs both a direction and a location.**
:::

## The Denavit-Hartenberg convention

### From a frame chain to a robot

A serial manipulator with $n$ joints has configuration
$\boldsymbol{q} = [q_1\ \cdots\ q_n]^\top$: an angle for a revolute joint, a displacement for
a prismatic one. **Forward kinematics** computes the tool pose from known joint values.
Attach frame $\{i\}$ to link $i$ and let $\boldsymbol{A}_i = \boldsymbol{T}^{i-1}_i$:

$$\boldsymbol{T}^0_n(\boldsymbol{q}) = \boldsymbol{A}_1(q_1)\boldsymbol{A}_2(q_2)\cdots\boldsymbol{A}_n(q_n).$$

The question is how to place the frames so every $\boldsymbol{A}_i$ is built the same way.
The lecture uses the **standard (classical) DH convention** of Spong and Niku.

### Assigning the frames

- **Joint axes.** Put $z_{i-1}$ along the axis of joint $i$ (rotation axis or sliding
  direction). Frame $\{i-1\}$ carries the axis of joint $i$: **the axis of joint 2 is
  $z_1$**. Positive joint motion agrees with the positive axis.
- **First axes.** $x_i$ lies along a **common normal** of the lines $z_{i-1}$ and $z_i$ (a
  line perpendicular to both and meeting both). $O_i$ is where it meets $z_i$.
- **Second axes.** $\boldsymbol{y}_i = \boldsymbol{z}_i \times \boldsymbol{x}_i$: not a free
  choice.
- **Base and end.** $z_0$ along joint 1 (in the examples the global frame is the DH base).
  For $n$ joints the joint axes are $z_0, \dots, z_{n-1}$; $z_n$ belongs to the chosen final
  frame and adds no joint. A separate fixed transform connects the last DH frame to the
  actual TCP.

### The four parameters

Let $C_i$ be where the $x_i$ common normal meets $z_{i-1}$. Going from $O_{i-1}$ to $O_i$
along $z_{i-1}$ to $C_i$ and then along $x_i$ gives:

| Parameter | Name | Definition |
|---|---|---|
| $\theta_i$ | Joint angle | Angle from $x_{i-1}$ to $x_i$, about positive $z_{i-1}$ |
| $d_i$ | Joint offset | Signed distance from $O_{i-1}$ to $C_i$, along $z_{i-1}$ |
| $\ell_i$ | Link length | Signed distance from $C_i$ to $O_i$, along $x_i$ |
| $\alpha_i$ | Link twist | Angle from $z_{i-1}$ to $z_i$, about positive $x_i$ |

The link length is usually written $a_i$; the notes write $\ell_i$ so it is not confused
with the approach direction $\boldsymbol{a}$. It is the distance between axis lines, not
necessarily the visible length of a bent link.

:::note Why four parameters for six degrees of freedom
DH does not describe arbitrary frame pairs. It restricts the assignment: $x_i$ must meet
$z_{i-1}$ and be perpendicular to it, $\boldsymbol{x}_i \cdot \boldsymbol{z}_{i-1} = 0$, so
$\overrightarrow{O_{i-1}O_i} = d_i\boldsymbol{z}_{i-1} + \ell_i\boldsymbol{x}_i$. The
reduction comes from the frame geometry, not from removing the robot's freedom.
:::

### Special geometries

| Neighbouring axes | Choice |
|---|---|
| Skew | Unique shortest segment: it fixes $x_i$ and $O_i$ |
| Parallel and distinct | Infinitely many normals; often take the one through $O_{i-1}$, making $d_i = 0$. Twist $0$ if the positive directions agree, $\pi$ if opposite |
| Intersecting | $O_i$ at the intersection, $\ell_i = 0$, $x_i \parallel \boldsymbol{z}_{i-1} \times \boldsymbol{z}_i$ (or its negative) |
| Coincident | $\ell_i = 0$; any convenient origin on the axis and any $x_i$ perpendicular to it |

**Procedure.** (1) Draw the robot in a reference configuration and identify every joint
axis. (2) Assign $z_{i-1}$ to joint $i$ with its direction. (3) Choose the common normals
$x_i$ and origins $O_i$. (4) Complete with $\boldsymbol{y}_i = \boldsymbol{z}_i \times \boldsymbol{x}_i$.
(5) Read the four signed parameters and mark which one each joint variable changes. A DH
table without its drawing is hard to interpret: several valid assignments describe the
same robot.

### The standard DH matrix

Rotate about $z_{i-1}$ by $\theta_i$, slide along it by $d_i$, slide along the new $x$ by
$\ell_i$, rotate about it by $\alpha_i$. Each step uses the current frame, so the factors
are postmultiplied:

$$\boldsymbol{A}_i = \boldsymbol{T}_z(\theta_i)\,\boldsymbol{T}_{trans}(0,0,d_i)\,\boldsymbol{T}_{trans}(\ell_i,0,0)\,\boldsymbol{T}_x(\alpha_i) = \begin{bmatrix} c_{\theta_i} & -s_{\theta_i}c_{\alpha_i} & s_{\theta_i}s_{\alpha_i} & \ell_i c_{\theta_i} \\ s_{\theta_i} & c_{\theta_i}c_{\alpha_i} & -c_{\theta_i}s_{\alpha_i} & \ell_i s_{\theta_i} \\ 0 & s_{\alpha_i} & c_{\alpha_i} & d_i \\ 0 & 0 & 0 & 1 \end{bmatrix}.$$

The first two factors commute (same axis), and so do the last two. The translation column
is $d_i$ along $z_{i-1}$ plus $\ell_i$ along the rotated first axis; the zero in the first
column's third entry is the perpendicularity of $x_i$ to $z_{i-1}$.

:::warning Standard, not modified, DH
The convention called **modified DH** places frames differently and multiplies in another
order; its rows cannot be put into this matrix. Write "standard DH" on every table. (URDF,
the robot description format of ROS, and the product-of-exponentials formulation of Lynch
and Park are alternatives that do not need DH frames.)
:::

**Joint variables.** Revolute: $\theta_i = q_i + \theta_{i,0}$ with $d_i, \ell_i, \alpha_i$
fixed. Prismatic: $d_i = q_i + d_{i,0}$ with $\theta_i, \ell_i, \alpha_i$ fixed. Each
$\boldsymbol{A}_i$ depends on one variable. If an encoder counts the other way, the sign
must enter the model.

:::example A link with a twist (Example 5)
$\theta_i = 90^\circ$, $d_i = 0.20$ m, $\ell_i = 0.30$ m, $\alpha_i = 90^\circ$:

$$\boldsymbol{A}_i = \begin{bmatrix} 0 & 0 & 1 & 0 \\ 1 & 0 & 0 & 0.30 \\ 0 & 1 & 0 & 0.20 \\ 0 & 0 & 0 & 1 \end{bmatrix}.$$

The new first, second and third directions point along the previous second, third and first.
The point $(0.10, 0.05, 0.02)$ in frame $\{i\}$ is $(0.02, 0.40, 0.25)$ m in frame
$\{i-1\}$.
:::

### The actual tool, and checks

The last DH origin is not necessarily the TCP. With a fixed tool frame $\{E\}$ and a world
frame $\{G\}$ that differs from the DH base:

$$\boldsymbol{T}^G_E(\boldsymbol{q}) = \boldsymbol{T}^G_0\,\boldsymbol{A}_1(q_1)\cdots\boldsymbol{A}_n(q_n)\,\boldsymbol{T}^n_E, \qquad \boldsymbol{p}^0_{TCP} = \boldsymbol{d}^0_n + \boldsymbol{R}^0_n\boldsymbol{r}^n_E .$$

Base calibration on the left, tool calibration on the right, by the frame indices.

**Checking a model.** Drawing first: $z_{i-1}$ describes joint $i$, $x_i$ meets $z_{i-1}$ at
a right angle, every frame right-handed. Then each $\boldsymbol{A}_i$: last row, rotation
block, image of the local origin. Then a configuration with obvious geometry (all angles
zero). A matrix can pass the orthogonality check and still describe the wrong robot.

## Examples of forward kinematics

### The planar 2R arm (Example 6)

Link lengths $l_1, l_2$, angles $q_1$ (from global $x$) and $q_2$ (relative to link 1). All
$z$ axes point out of the plane, $x_1$ and $x_2$ along the links, so both twists and both
offsets are zero:

| Link | Joint | $\theta_i$ | $d_i$ | $\ell_i$ | $\alpha_i$ |
|---|---|---|---|---|---|
| 1 | Revolute | $q_1$ | 0 | $l_1$ | 0 |
| 2 | Revolute | $q_2$ | 0 | $l_2$ | 0 |

Each link is $\boldsymbol{A}(q, l) = \boldsymbol{T}_z(q)\boldsymbol{T}_{trans}(l, 0, 0)$, and
$\boldsymbol{T}^0_2 = \boldsymbol{A}(q_1, l_1)\boldsymbol{A}(q_2, l_2)$ gives

$$x = l_1\cos q_1 + l_2\cos(q_1 + q_2), \qquad y = l_1\sin q_1 + l_2\sin(q_1 + q_2), \qquad \phi = q_1 + q_2 .$$

Two joints determine three related quantities $(x, y, \phi)$, which cannot be prescribed
independently. For $l_1 = l_2 = 1$ m, $q_1 = 0$, $q_2 = 90^\circ$: TCP at $(1, 1, 0)$ m. This is
lecture 1's planar arm, now derived from a DH table, and the same rule extends to spatial
chains.

### A fixed tool offset (Example 7)

A tool reaching $b$ further along $x_2$: $\boldsymbol{T}^2_E = \boldsymbol{T}_{trans}(b, 0, 0)$.
With $l_1 = 0.40$, $l_2 = 0.30$, $b = 0.10$ m, $q_1 = 30^\circ$, $q_2 = -30^\circ$, the last
frame is aligned with the base, $\boldsymbol{d}^0_2 = (0.6464, 0.2000, 0)$ m and the TCP is at
$(0.7464, 0.2000, 0)$ m. In general the offset must be rotated into the base frame first.

### A revolute-prismatic arm (Example 8)

A horizontal arm of length $L$ at height $h$ rotating about global $z$ by $q_1$, with a
vertical prismatic joint $q_2$ at its end:

| Link | Joint | $\theta_i$ | $d_i$ | $\ell_i$ | $\alpha_i$ |
|---|---|---|---|---|---|
| 1 | Revolute | $q_1$ | $h$ | $L$ | 0 |
| 2 | Prismatic | 0 | $q_2$ | 0 | 0 |

$$\boldsymbol{T}^0_2 = \begin{bmatrix} \cos q_1 & -\sin q_1 & 0 & L\cos q_1 \\ \sin q_1 & \cos q_1 & 0 & L\sin q_1 \\ 0 & 0 & 1 & h + q_2 \\ 0 & 0 & 0 & 1 \end{bmatrix}.$$

For $L = 0.40$, $h = 0.10$, $q_1 = 45^\circ$, $q_2 = 0.20$ m: TCP at $(0.283, 0.283, 0.300)$ m. The
angle sits in the $\theta$ column, the length in the $d$ column: that is the difference
between a revolute and a prismatic joint in a DH table.

## What an exam wants

:::paper Build a forward-kinematics model
1. Draw the robot; mark every joint axis $z_{i-1}$ with its positive direction.
2. Choose $x_i$ along the common normals and $O_i$ where they meet $z_i$; complete with
   $\boldsymbol{y}_i = \boldsymbol{z}_i \times \boldsymbol{x}_i$.
3. Write the standard DH table and say which parameter each joint variable changes.
4. Substitute each row into the standard $\boldsymbol{A}_i$, multiply in order, add fixed
   base or tool transforms.
5. Check with a configuration whose geometry you can see.
:::

:::paper Convert or move with a homogeneous matrix
State the source and destination frames. Points get a final 1, directions a final 0. For a
commanded motion, say whether it is in the current frame (multiply on the right) or the
fixed frame (on the left), and for a rotation where its axis passes.
:::

## Where next

- Drill: [](deck:forward-kinematics).
- The lecture's 12 numerical exercises, solved: [](problems:forward-kinematics-practice).
- The formulas: [the sheet](formulas). The rotation background: [](lecture:02-rigid-body-motions).
