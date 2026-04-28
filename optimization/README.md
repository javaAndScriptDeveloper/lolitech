# Experimental Design & Optimization — Assignments

Three assignments applying statistical experiment design and response surface methods to empirical data.

**Stack:** Python · NumPy · SciPy · `scipy.stats` · `decimal`

---

## Assignment 1 — Full Factorial Design (2³)

Constructs a $2^3$ full factorial experiment with three factors ($x_1, x_2, x_3$), each at a high/low level. Builds the design matrix, runs trials, and fits a first-order regression model:

$$\hat{y} = b_0 + b_1 x_1 + b_2 x_2 + b_3 x_3 + b_{12} x_1 x_2 + \ldots$$

Coefficient significance is evaluated with Student's $t$-test; model adequacy with Fisher's $F$-test.

---

## Assignment 5 — Coded Variables & Bounds

Extends the DOE framework to natural (uncoded) variables with asymmetric bounds:
$x_1 \in [-2, 3]$, $x_2 \in [0, 10]$, $x_3 \in [-4, 8]$.

Introduces coded-to-natural variable transformation, repeated trials for variance estimation, and `decimal.Decimal` arithmetic for numerical stability in hypothesis tests.

---

## Assignment 6 — Cochran's Test & Variance Homogeneity

Focuses on checking homogeneity of variances across experiment runs before pooling results. Implements:

- **Cochran's test** — identifies outlier variance in replicated trials.
- Fisher distribution lookup — critical values for $F$-ratio comparison.
- Random $y$-value generation with configurable noise to simulate realistic experimental scatter.
- Matrix-based regression coefficient estimation.
