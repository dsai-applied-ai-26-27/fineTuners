---
title: MATLAB introduction
number: 0
topics: [matlab]
summary: The introductory MATLAB slides worked through as a session. What MATLAB and Simulink are, variables and operators, MATLAB as a calculator with its try-it exercises, the reference tables, the symbolic toolbox, and the two closing problems with solutions.
takeaways:
  - MATLAB treats every variable as a matrix. A vector is a matrix with one row or one column, a scalar a matrix with one row and one column.
  - '`*`, `/` and `^` are matrix operations. Their dotted forms `.*`, `./` and `.^` work element by element.'
  - '`log` is the natural logarithm, `sin` takes radians and `sind` takes degrees.'
  - A semicolon at the end of a line suppresses the output. Without an assignment the result goes to `ans`.
  - The symbolic toolbox does calculus on expressions with `syms`, `diff`, `int`, `limit`, `subs` and `taylor`.
sources:
  - labs/MATLAB.pdf
---

## What this is

The lab folder has a 23-slide MATLAB introduction with "TRY IT!" exercises and two
problems at the end. This page works through it in order, with every exercise solved.

:::note Where it sits among the lab exercises
The slides do not say which of the ten lab exercises they belong to, so the page is filed
as session 0, before lab exercise 1. Nothing in the slides is marked for hand-in. The
rules that apply to graded exercises are in [](guide:lab-rules).
:::

## MATLAB and Simulink

**MATLAB** is short for **MATrix LABoratory** (slide 2). It was first developed by a
lecturer in the 1970s to help students learn linear algebra, and later marketed and
developed by MathWorks, founded in 1984. It is a software package for analysis and for
solving mathematical and engineering problems, with good programming and graphics
features, and it is also a programming language widely used as a platform for machine
learning tools. **Toolboxes** are collections of functions for one domain: control
systems, signal processing, neural networks, image processing, system identification.

**Simulink** (slide 4) is used to model, analyse and simulate **dynamic systems using
block diagrams**. It is fully integrated with MATLAB, has a block library for linear,
non-linear and discrete systems, and can generate C code from a model for embedded
applications and rapid prototyping of control systems. The slide's examples are small
electrical circuits built from blocks, with current measurements fed to Scopes.

## Variables

- MATLAB treats **all variables as matrices**. A vector has one row *or* one column; a
  scalar has one row *and* one column.
- Variables are **not declared** beforehand. There is no `int a; double b;`.
- Names can have up to **63 characters**, are **case sensitive** (`A` is not `a`), must
  **start with a letter**, and may contain letters, digits and underscores but **no
  spaces**.

## Operators

| Operation | Matrix form | Element-wise form | Example |
|---|---|---|---|
| Assignment | `=` | | `a = b` assigns `b` to `a` |
| Addition | `+` | | `a + b` |
| Subtraction | `-` | | `a - b` |
| Multiplication | `*` | `.*` | `a*b` or `a.*b` |
| Division | `/` | `./` | `a/b` or `a./b` |
| Power | `^` | `.^` | `a^b` or `a.^b` |

:::pitfall Forgetting the dot
For scalars the two forms agree. For vectors and matrices they do not: `a*b` is the matrix
product and needs matching inner dimensions, `a.*b` multiplies matching elements. Squaring
every element of a vector is `v.^2`; `v^2` is an error unless `v` is a square matrix. (The
slide lists both forms; the consequence is spelled out here.)
:::

## Task 1: MATLAB as a calculator

**Compute** $\dfrac{3 \cdot 4}{2^2 + 4/2}$.

:::solution
```matlab
>> (3*4)/(2^2 + 4/2)
ans = 2
```

The brackets matter: the whole denominator has to be grouped. $12 / (4 + 2) = 2$.
:::

**Compute 3 divided by 4, multiply the result by 2, then raise the result to the 3rd
power.**

:::solution
```matlab
>> 3/4
ans = 0.75
>> ans*2
ans = 1.5
>> ans^3
ans = 3.3750
```

A result that is not assigned goes to the variable `ans`, which the next line can use.
:::

**Compute** $e^{\log 10}$ **and** $e^{3/4}$.

:::solution
```matlab
>> exp(log(10))
ans = 10
>> exp(3/4)
ans = 2.1170
```

`log` is the **natural** logarithm, so `exp(log(10))` gives back 10. The base-10 logarithm
is `log10`. There is no constant `e`: write `exp(1)`.
:::

**Compute** $1/0$, $1/\infty$ **and** $\infty \cdot 2$; **then** $\infty/\infty$; **verify
that** `i` **squares to** $-1$; **compute the imaginary sum** $2 + 5i$.

:::solution
```matlab
>> 1/0
ans = Inf
>> 1/Inf
ans = 0
>> Inf*2
ans = Inf
>> Inf/Inf
ans = NaN
>> i^2
ans = -1
>> 2 + 5i
ans = 2.0000 + 5.0000i
```

`NaN`, "not a number", marks an undefined operation such as $\infty/\infty$ or $0/0$.
:::

**Compute the logical expressions for "Is 5 equal to 4?" and "Is 2 smaller than 3?"**

:::solution
```matlab
>> 5 == 4
ans = 0
>> 2 < 3
ans = 1
```

A comparison returns a logical value: `1` for true, `0` for false. Equality is `==`; a
single `=` is assignment.
:::

## Reference tables

### Elementary functions (slide 12)

| Mathematics | MATLAB | Note |
|---|---|---|
| $e^x$ | `exp(x)` | |
| $e^x - 1$ for small $x$ | `expm1(x)` | |
| $\sqrt{x}$ | `sqrt(x)` | `realsqrt(x)` is faster when every element is positive |
| $\ln x$ | `log(x)` | `reallog(x)` is faster when every element is positive |
| $\log_{10} x$ | `log10(x)` | |
| absolute value of $x$ | `abs(x)` | |
| $\operatorname{signum}(x)$ | `sign(x)` | |
| $\ln(1 + x)$ for small $x$ | `log1p(x)` | |
| $n!$ | `factorial(n)` | 15 digits of accuracy for $n \le 21$ |
| all primes $\le n$ | `primes(n)` | |

### Trigonometric and hyperbolic functions (slide 11)

| Function | Radians | Degrees | Inverse | Hyperbolic | Inverse hyperbolic |
|---|---|---|---|---|---|
| sine | `sin(x)` | `sind(x)` | `asin(x)` | `sinh(x)` | `asinh(x)` |
| cosine | `cos(x)` | `cosd(x)` | `acos(x)` | `cosh(x)` | `acosh(x)` |
| tangent | `tan(x)` | `tand(x)` | `atan(x)` | `tanh(x)` | `atanh(x)` |
| secant | `sec(x)` | `secd(x)` | `asec(x)` | `sech(x)` | `asech(x)` |
| cosecant | `csc(x)` | `cscd(x)` | `acsc(x)` | `csch(x)` | `acsch(x)` |
| cotangent | `cot(x)` | `cotd(x)` | `acot(x)` | `coth(x)` | `acoth(x)` |

`atan2(y, x)` is the four-quadrant version of the arctangent and must be used when the
signs of $y$ and $x$ can each be positive or negative.

### Constants and special quantities (slide 14)

| Quantity | MATLAB | Comment |
|---|---|---|
| $\pi$ | `pi` | 3.141592653589793 |
| $\sqrt{-1}$ | `i` or `j` | A complex number is written `a + 1j*b` |
| floating-point relative accuracy | `eps` | Distance from 1.0 to the next larger number, about $2.22 \times 10^{-16}$ |
| $\infty$ | `inf` | |
| $0/0$, $0 \times \infty$, $\infty/\infty$ | `NaN` | An undefined mathematical operation |
| largest floating-point number | `realmax` | about $1.7977 \times 10^{308}$ |
| smallest floating-point number | `realmin` | about $2.2251 \times 10^{-308}$ |

Scientific notation uses the letter `e` between two numbers: `1e6` is $10^6$ and `1e-3` is
$0.001$.

### Relational operators (slide 16)

| Condition | Mathematics | MATLAB |
|---|---|---|
| equal | $=$ | `==` |
| not equal | $\ne$ | `~=` |
| less than | $<$ | `<` |
| greater than | $>$ | `>` |
| less than or equal | $\le$ | `<=` |
| greater than or equal | $\ge$ | `>=` |

### Decimal-to-integer conversion (slide 17)

| Function | Rule | 2.7 | -1.9 | 2.49 - 2.51j |
|---|---|---|---|---|
| `fix(x)` | toward zero | 2 | -1 | 2 - 2i |
| `round(x)` | to the nearest integer | 3 | -2 | 2 - 3i |
| `ceil(x)` | toward infinity | 3 | -1 | 3 - 2i |
| `floor(x)` | toward minus infinity | 2 | -2 | 2 - 3i |

The four differ on negative numbers: `fix(-1.9)` is $-1$ and `floor(-1.9)` is $-2$.

### Complex numbers (slide 18)

| Function | For z = 3 + 4j | Meaning |
|---|---|---|
| `complex(a, b)` | | Forms `a + b*j` from real `a` and `b` |
| `abs(z)` | 5 | Absolute value $\sqrt{a^2 + b^2}$ |
| `conj(z)` | 3 - 4j | Complex conjugate |
| `real(z)` | 3 | Real part |
| `imag(z)` | 4 | Imaginary part |
| `angle(z)` | `atan2(b, a)` | Phase angle in radians, between $-\pi$ and $\pi$ |

### Special characters (slides 19 and 20)

| Character | Use |
|---|---|
| `.` | Decimal point; part of the dot operators, `c = a.*b`; field access in a structure, `name.first` |
| `,` | Separates elements and arguments, `b(2,7)`, `[x, s] = max(a)`; separates several expressions on one line |
| `;` | **Suppresses the display** of a result at the end of an expression; ends a row when a matrix is created, `m = [x y z; a b c]` |
| `:` | Builds a vector, `x = a:b:c`; means "all rows" in `z(:,k)` or "all columns" in `z(k,:)` |
| `( )` | Index of an element, `z(j,k)`; grouping in expressions, `a^(b+c)`; arguments of a function, `sin(x)` |
| `[ ]` | Creates an array: a vector, a matrix or an array of strings |
| `{ }` | Creates a cell array |
| `%` | Starts a comment; everything to its right is ignored, except inside a string |
| `%%` | Delimits a cell, a section of code, in the editor |
| `%{` and `%}` | Enclose a block of comment lines |
| `'` | Delimits a string, `'Expression'`; transposes a vector or matrix (conjugate transpose if complex) |
| `...` | Continues an expression on the next line |
| blank | Depends on context: ignored, or a delimiter as in `c = [a b]` and in `syms a b` |
| `@` | Builds a function handle, `@FunctionName` |
| `\` | A matrix operator; also introduces Greek letters and symbols in plot annotations |

## Task 2: the symbolic toolbox

The functions on slide 21, and what each does:

| Function | Does |
|---|---|
| `syms a b c` | Declares symbolic variables |
| `vpa(f, n)` | Evaluates `f` to `n` significant digits |
| `diff(f, x, n)` | The `n`-th derivative of `f` with respect to `x` |
| `int(f, x, c, d)` | The integral of `f` over `x` from `c` to `d`; indefinite without the limits |
| `limit(f, x, z)` | The limit of `f` as `x` tends to `z` |
| `subs(f, a, b)` | Substitutes `b` for `a` in `f` |
| `taylor(f, x, a, 'Order', n)` | The Taylor expansion of `f` about `x = a` |

The slide's examples, runnable as written:

```matlab
y = vpa('factorial(32)-exp(100)', 50)

syms b t
dt = diff(b*cos(b*t), t, 1)     % derivative with respect to t
db = diff(b*cos(b*t), b, 1)     % derivative with respect to b
it = int(dt, t)                 % integrating dt over t
ib = int(db, b)

syms a b
Lim = limit((2*a + b)/(3*a - 4), a, inf)

syms x tho
Tay = taylor(cos(x), x, tho, 'Order', 4)
```

:::solution What these return
- `dt = -b^2*sin(b*t)` and `db = cos(b*t) - b*t*sin(b*t)`, by the chain and product rules.
- `it` and `ib` both give back `b*cos(b*t)`, the function that was differentiated (up to a
  constant).
- `Lim = 2/3`: for large $a$ the ratio $(2a + b)/(3a - 4)$ tends to $2/3$ whatever $b$ is.
- `Tay` is the expansion of $\cos x$ about the point `tho`, the sum
  $\sum_{k=0}^{n-1} (x - a)^k \dfrac{f^{(k)}(a)}{k!}$ with $a$ = `tho` and $n = 4$.

Worked out here; the slides show only the commands. In recent MATLAB versions `vpa` wants a
symbolic expression instead of a quoted string.
:::

## Task 3: flow rate in an open channel

The flow rate $Q$ in an open channel of circular cross-section is

$$Q = \frac{2^{3/2}\, D_c^{5/2}\, \sqrt{g}\, \big(\theta - 0.5 \sin(2\theta)\big)^{3/2}}{8 \sqrt{\sin\theta}\, (1 - \cos\theta)^{5/2}} ,$$

where $g = 9.8\ \text{m/s}^2$ is the gravitational constant and

$$D_c = \frac{d}{2}(1 - \cos\theta) .$$

Assume $d = 2$ and $\theta = 60^\circ$. Write a MATLAB script.

:::solution
```matlab
g     = 9.8;                 % m/s^2
d     = 2;
theta = 60*pi/180;           % the formula needs theta in radians

Dc = d/2 * (1 - cos(theta));

Q = (2^(3/2) * Dc^(5/2) * sqrt(g) * (theta - 0.5*sin(2*theta))^(3/2)) / ...
    (8 * sqrt(sin(theta)) * (1 - cos(theta))^(5/2))
```

Result: `Dc = 0.5` and `Q = 0.5725`.

**Why radians:** $\theta$ also appears on its own, in $\theta - 0.5\sin(2\theta)$, so it
must be a pure number. Using `sind` and `cosd` with `theta = 60` would get the
trigonometric parts right and that term wrong.

A check by hand: $\cos 60^\circ = 0.5$ gives $D_c = 0.5$, so $D_c^{5/2}$ and
$(1 - \cos\theta)^{5/2}$ are equal and cancel, leaving
$Q = 2^{3/2}\sqrt{g}\,(\theta - 0.5\sin 2\theta)^{3/2} / (8\sqrt{\sin\theta})$ with
$\theta - 0.5\sin 2\theta = 1.0472 - 0.4330 = 0.6142$.
:::

## Task 4: curvature of a deltoid

The curvature $K$ of a plane curve with parametric equations $x = x(t)$, $y = y(t)$ is

$$K = \frac{x' y'' - y' x''}{\left(x'^2 + y'^2\right)^{3/2}} ,$$

where the prime is the derivative with respect to $t$. Determine an expression for the
curvature of a deltoid with

$$x = 2b\cos t + b\cos 2t, \qquad y = 2b\sin t - b\sin 2t .$$

Write a script to obtain the curvature.

:::solution
```matlab
syms t b
x = 2*b*cos(t) + b*cos(2*t);
y = 2*b*sin(t) - b*sin(2*t);

xp  = diff(x, t);      yp  = diff(y, t);        % first derivatives
xpp = diff(x, t, 2);   ypp = diff(y, t, 2);     % second derivatives

K = simplify((xp*ypp - yp*xpp) / (xp^2 + yp^2)^(3/2))
```

By hand, to check what MATLAB prints: the numerator is
$x'y'' - y'x'' = -4b^2(1 - \cos 3t)$ and $x'^2 + y'^2 = 8b^2(1 - \cos 3t)$, so for $b > 0$

$$K = -\frac{1}{4\sqrt2\, b\, \sqrt{1 - \cos 3t}} = -\frac{1}{8b\, \lvert \sin(3t/2) \rvert} .$$

The curvature is negative with this orientation and blows up where $\sin(3t/2) = 0$, the
three cusps of the deltoid. MATLAB may print an equivalent but differently arranged
expression. A numerical spot check: `subs(K, [b t], [1.7 0.9])` evaluates to about
$-0.0754$.

The hand derivation and the spot check are added here; the slide asks only for the script.
:::

## Hand in

Nothing is marked for submission in these slides. For a graded exercise, the checklist is:

- [ ] Lab Preparation taken at the start of the session.
- [ ] Report written in the C3 template, with derivations, the Simulink model and plots
      made in MATLAB.
- [ ] All `.m`, `.mlx` and `.slx` files, running without errors.
- [ ] One zip, named as the policy requires, on C3 within 7 days.

Details: [](guide:lab-rules). Drill the basics: [](deck:matlab-basics).
