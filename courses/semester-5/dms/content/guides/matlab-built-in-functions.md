---
title: MATLAB built-in functions
topics: [matlab]
summary: A lookup table of MATLAB built-in functions grouped by subject, from the appendix supplied with the lab material, with notes on which names have since been replaced.
sources:
  - labs/MATLAB Built-in Functions (2).pdf
---

## What this is

The lab material includes a four-page appendix, "Appendix B: MATLAB Built-in Functions"
(pp. 517 to 520 of a textbook), listing functions by subject area. This page reproduces it
as a lookup table for the labs, which use MATLAB and Simulink.

:::warning The list comes from an old MATLAB
Several names in the appendix belong to early MATLAB versions and have since been renamed
or removed. The "Today" column gives the current function where one is known. That column
is **not in the source**; check anything you rely on with `doc name` or `help name` in your
own MATLAB.
:::

## Special matrices

| Function | Builds | Today |
|---|---|---|
| `diag` | Diagonal matrix | |
| `eye` | Identity matrix | |
| `zeros` | Matrix of zeros | |
| `ones` | Matrix of constants (ones) | |
| `rand` | Random elements | |
| `linspace` | Linearly spaced vector | |
| `logspace` | Logarithmically spaced vector | |
| `magic` | Magic square | |
| `meshdom` | Domain for mesh points | `meshgrid` |
| `hadamard`, `hankel`, `hilb`, `invhilb`, `pascal`, `toeplitz`, `vander` | Hadamard, Hankel, Hilbert, inverse Hilbert, Pascal, Toeplitz and Vandermonde matrices | |

## Decompositions and factorisations

| Function | Computes | Today |
|---|---|---|
| `inv` | Inverse | |
| `eig` | Eigenvalues and eigenvectors | |
| `svd` | Singular value decomposition | |
| `lu` | Factors from Gaussian elimination | |
| `qr` | Orthogonal-triangular decomposition | |
| `chol` | Cholesky factorisation | |
| `rref` | Reduced row echelon form | |
| `orth` | Orthogonalisation | |
| `nnls` | Non-negative least squares | `lsqnonneg` |
| `backsub` | Back substitution | Not a current built-in; use the backslash operator |

## Roots, interpolation, integration, differential equations

| Function | Does | Today |
|---|---|---|
| `fzero` | Zero of a function | |
| `roots` | Roots of a polynomial | |
| `spline` | Cubic spline interpolation | |
| `interp1` | One-dimensional interpolation | |
| `table1`, `table2` | One- and two-dimensional table look-up | `interp1`, `interp2` |
| `quad`, `quadl` | Numerical integration of a function | `integral` |
| `ode23` | 2nd and 3rd order Runge-Kutta method | |
| `ode45` | 4th and 5th order Runge-Kutta-Fehlberg method (as the appendix names it) | |
| `ode113`, `ode15s`, `ode23s`, `ode23t` | Further numerical ODE solvers | |

## Plotting

The appendix calls this group "Graph paper".

| Function | Draws | Today |
|---|---|---|
| `plot` | Linear X-Y plot | |
| `loglog` | Log-log X-Y plot | |
| `semilogx`, `semilogy` | Semi-log X-Y plots | |
| `polar` | Polar plot | `polarplot` |
| `mesh` | 3-dimensional mesh surface | |
| `contour` | Contour plot | |
| `bar` | Bar chart | |
| `stairs` | Stair-step graph | |
| `errorbar` | Adds error bars | |

## Elementary maths

| Function | Returns |
|---|---|
| `abs` | Absolute value or complex magnitude |
| `angle` | Phase angle |
| `sqrt` | Square root |
| `real`, `imag`, `conj` | Real part, imaginary part, complex conjugate |
| `round` | Nearest integer |
| `fix` | Rounded toward zero |
| `floor` | Rounded toward $-\infty$ |
| `ceil` | Rounded toward $+\infty$ |
| `sign` | Signum function |
| `rem` | Remainder |
| `exp` | Exponential, base $e$ |
| `log`, `log10` | Natural logarithm, logarithm base 10 |

:::pitfall `fix`, `floor`, `ceil` and `round` differ on negative numbers
For $-2.5$: `fix` gives $-2$ (toward zero), `floor` gives $-3$, `ceil` gives $-2$, and
`round` gives $-3$ (halves round away from zero). The example is not in the source; the
four definitions are.
:::

## Text and strings

| Function | Does | Today |
|---|---|---|
| `num2str`, `int2str` | Convert a number or an integer to a string | |
| `sprintf` | Convert a number to a string under a format | |
| `abs` | Convert a string to ASCII values | `double` |
| `eval` | Evaluate a text macro | |
| `hex2num` | Convert a hex string to a number | |
| `setstr` | Flag a matrix as a string | `char` |
| `isstr` | Detect string variables | `ischar` |
| `strcomp` | Compare string variables | `strcmp` |

## Control flow

| Keyword | Does |
|---|---|
| `if`, `elseif`, `else` | Conditionally execute statements |
| `for` | Repeat statements a number of times |
| `while` | Repeat while a condition holds |
| `switch` | Switch on an expression |
| `break` | Break out of `for` and `while` loops |
| `return` | Return from a function |
| `end` | Terminate `if`, `for`, `while` |
| `pause` | Pause until a key is pressed |

## Programming and M-files

| Function | Does | Today |
|---|---|---|
| `function` | Define a function | |
| `input` | Get numbers from the keyboard | |
| `error` | Display an error message | |
| `global` | Define global variables | |
| `exist` | Check whether variables exist | |
| `eval` | Interpret text held in variables | |
| `feval` | Evaluate a function given by a string | Function handles, `f = @sin` |
| `keyboard` | Hand control to the keyboard as if it were an M-file (for debugging) | |
| `echo` | Enable command echoing | |
| `startup` | Startup M-file | |
| `getenv` | Get an environment string | |
| `menu` | Select an item from a menu | |
| `etime` | Elapsed time | `tic` and `toc` |
| `casesen` | Set case sensitivity | Removed; MATLAB is always case sensitive |

## A first session

:::note Not in the source
The appendix only lists names. This short script uses several of them (`ode45`, `plot`,
`exp`, `abs`, `num2str`) the way a modelling lab would: it simulates the first-order
system $\dot x = -x/\tau$ and compares the numerical solution with the exact one,
$x(t) = e^{-t/\tau}$.
:::

```matlab
tau = 0.5;                            % time constant in seconds
f = @(t, x) -x / tau;                 % right-hand side of dx/dt = -x/tau
[t, x] = ode45(f, [0 3], 1);          % simulate 3 s from x(0) = 1

plot(t, x, t, exp(-t / tau), '--')    % numerical and exact solution on one plot
xlabel('t [s]'), ylabel('x')
legend('ode45', 'exact')

disp(num2str(max(abs(x - exp(-t / tau)))))   % largest difference: small
```

The two curves lie on top of each other and the last line prints a small number, the
error of the solver at its default tolerance. The plot has labelled axes with time on the
horizontal one and both signals on the same axes, which is what the report rules in
[](guide:lab-rules) ask for.

## Not written up

The lab folder also holds the full textbook Siauw and Bayen, *An Introduction to MATLAB
Programming and Numerical Methods for Engineers* (2015, 311 pages in the supplied file).
It is a reference book, not a lab sheet, and has not been turned into notes here. Its
first part teaches programming from the ground up and its second part covers numerical
methods; use it alongside the labs. The session-sized introduction is
[](lab:00-matlab-introduction).
