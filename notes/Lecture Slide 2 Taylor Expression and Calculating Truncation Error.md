---
created_at: 2025-11-02T17:31:23.895376
file_id: e30e0a00-e6ae-4423-87f9-99f401e087d2
original_filename: Lecture Slide 2 Taylor Expression and Calculating Truncation Error.pdf
note_style: descriptive
llm_provider: gemini
llm_model: gemini-2.5-flash
tokens_used: 25344
total_chunks: 4
synthesis_method: direct
---

This comprehensive note combines the academic content from all provided sections, offering a detailed explanation of Taylor Series, Truncation Error, and their applications in numerical approximation and differentiation.

---

## Taylor Series, Numerical Approximation, and Error Analysis

Numerical methods are indispensable tools in science and engineering, allowing us to approximate complex mathematical functions and operations using simpler, computable steps. At the heart of many of these methods lies the **Taylor Series**, a powerful concept for representing functions and analyzing the errors inherent in their approximations.

### 1. Introduction to Taylor Series

The **Taylor Theorem** is a fundamental principle stating that any sufficiently "smooth" function (one that has derivatives of all orders) can be approximated as a polynomial. This is incredibly valuable because polynomials are much easier to manipulate and compute than many complex functions.

The **Taylor Series** is the mathematical expression of this theorem, representing a function as an infinite sum of terms. Each term is derived from the function's derivatives evaluated at a single point, known as the expansion point.

#### 1.1 General Form of the Taylor Series

For a function $f(x)$ expanded around a point $x_0$, the general form of its Taylor series is:

$f(x) = f(x_0) + f'(x_0)(x - x_0) + \frac{f''(x_0)}{2!}(x - x_0)^2 + \frac{f'''(x_0)}{3!}(x - x_0)^3 + \dots + \frac{f^{(n)}(x_0)}{n!}(x - x_0)^n + R_n$

Where:
*   $f(x_0)$ is the function's value at the expansion point $x_0$.
*   $f'(x_0)$, $f''(x_0)$, $f'''(x_0)$, etc., are the first, second, third, and higher-order derivatives of the function, all evaluated at $x_0$.
*   $n!$ denotes the factorial of $n$ (e.g., $3! = 3 \times 2 \times 1 = 6$).
*   $(x - x_0)$ represents the distance from the expansion point $x_0$ to the point $x$ where the function is being approximated.
*   $R_n$ is the **remainder term**, which quantifies the error introduced when the infinite series is truncated after the $n$-th term.

#### 1.2 Simplified Notation for Practical Applications

In numerical methods, it's common to use a simplified notation. Let:
*   $x_{i+1}$ be the point where we want to approximate the function's value.
*   $x_i$ be the point from which we are expanding the series (the expansion point).
*   $h = (x_{i+1} - x_i)$ be the step size, representing the distance between the two points.

Using this notation, the Taylor series can be written as:

$f(x_{i+1}) = f(x_i) + f'(x_i)h + \frac{f''(x_i)}{2!}h^2 + \frac{f'''(x_i)}{3!}h^3 + \dots + \frac{f^{(n)}(x_i)}{n!}h^n + R_n$

### 2. Understanding Truncation Error

When we use a Taylor series to approximate a function, we typically cannot sum an infinite number of terms. Instead, we "truncate" the series after a finite number of terms. The error introduced by this truncation is called **truncation error**.

#### 2.1 Characteristics of Truncation Error

*   **Exact for Polynomials:** If the original function $f(x)$ is itself an $n$-th order polynomial, then its $n$-th order Taylor series expansion will be exact, meaning the remainder term $R_n$ will be zero. This is because all derivatives beyond the $n$-th order for an $n$-th degree polynomial are zero.
*   **Remainder Term ($R_n$):** For functions that are not $n$-th order polynomials, $R_n$ is non-zero and represents the truncation error. The remainder term is often expressed using **Big O notation**:
    $R_n = O(h^{n+1})$
    This notation "$O(h^{n+1})$" signifies that the truncation error is proportional to $h$ raised to the power of $(n+1)$. It indicates the *order* of the error, meaning how quickly the error decreases as the step size $h$ gets smaller. For instance, an error of $O(h^2)$ implies that if the step size $h$ is halved, the error will be reduced by a factor of $2^2 = 4$.
*   **Impact of Terms and Spacing:**
    *   **More terms used:** Including more terms in the Taylor series approximation (i.e., increasing $n$) generally leads to a smaller truncation error. This is because more information about the function's behavior (through higher-order derivatives) is incorporated.
    *   **Smaller spacing ($h$):** A smaller step size $h$ (meaning $x_{i+1}$ is closer to $x_i$) results in a smaller truncation error for a given number of terms. The Taylor series is most accurate in the immediate vicinity of the expansion point $x_i$.

#### 2.2 Relationship between Order of Error and Step Size Reduction

A critical insight into truncation error is how it scales with the step size $h$. If an approximation method has a truncation error of $O(h^n)$, then halving the step size $h$ will reduce the error by a factor of approximately $2^n$. This is a fundamental concept for understanding the efficiency and accuracy of numerical methods. Higher-order methods (larger $n$) are much more sensitive to changes in $h$, meaning a small reduction in $h$ can lead to a dramatic increase in accuracy.

#### 2.3 Visualizing Truncation Error

Graphs illustrating "Truncation error vs. Number of Terms (N)" or "Percent Error vs. Number of Terms (N)" typically show a sharp decrease in error as N increases. Furthermore, curves for smaller step sizes ($h$) consistently demonstrate lower truncation errors for any given number of terms, emphasizing the importance of both factors in achieving accuracy.

### 3. Total Numerical Error

In numerical computations, the **total numerical error** is the sum of two primary types of errors:

1.  **Truncation Error:** As discussed, this error arises from approximating an infinite mathematical process (like a Taylor series) with a finite number of steps or terms.
2.  **Roundoff Error:** This error originates from the finite precision of computer arithmetic. Computers store numbers with a limited number of digits, leading to small inaccuracies when numbers are represented or calculations are performed.

#### 3.1 Relationship between Errors and Step Size ($h$)

These two error types exhibit opposing behaviors with respect to the step size $h$:

*   **Truncation Error vs. Step Size:** Truncation error generally *increases* as the step size $h$ increases. This is because the Taylor series approximation becomes less accurate further away from the expansion point.
*   **Roundoff Error vs. Step Size:** Roundoff error generally *decreases* as the step size $h$ increases. A larger step size often means fewer computational steps are required to cover a given range, thus accumulating less roundoff error. Conversely, a very small step size necessitates many more calculations, each contributing its tiny roundoff error, which can accumulate to a significant total roundoff error.

This opposing behavior leads to a "point of diminishing returns" for the step size. There exists an **optimal step size** where the total numerical error is minimized. If $h$ is too large, truncation error dominates; if $h$ is too small, roundoff error dominates.

### 4. Applications of Taylor Series for Function Approximation

The Taylor series is widely used to approximate function values. Let's explore several examples.

#### 4.1 Example 1: Approximating a General Function $f(x)$

Consider approximating a function $f(x)$ from $x_i = 0$ to $x_{i+1} = 1$ with a step size $h = 1$. We are given $f(0) = 1.2$ and that the function curves downward to $f(1) = 0.2$ (the true value). We aim to predict $f(1)$ using different orders of Taylor series expansions.

**a) Zero-Order Taylor Series Expansion:**
This uses only the first term, assuming the function is constant over the interval.
Formula: $f(x_{i+1}) \approx f(x_i)$
Approximation for $f(1)$: $f(1) \approx f(0) = 1.2$
Truncation Error: $0.2 - 1.2 = -1.0$. This is a large error, as it doesn't account for any change.

**b) First-Order Taylor Series Expansion:**
Includes the first derivative term, accounting for the slope.
Formula: $f(x_{i+1}) \approx f(x_i) + f'(x_i)h$
Given $f(0) = 1.2$, $h = 1$, and $f'(0) = -0.25$:
Approximation for $f(1)$: $f(1) \approx 1.2 + (-0.25)(1) = 0.95$
Truncation Error: $0.2 - 0.95 = -0.75$. The error is reduced.

**c) Second-Order Taylor Series Expansion:**
Includes the second derivative term, accounting for curvature.
Formula: $f(x_{i+1}) \approx f(x_i) + f'(x_i)h + \frac{f''(x_i)}{2!}h^2$
Given $f(0) = 1.2$, $f'(0) = -0.25$, $h = 1$. To match the provided result of $0.45$, we infer $f''(0) = -1.0$:
Approximation for $f(1)$: $f(1) \approx 1.2 + (-0.25)(1) + \frac{(-1.0)}{2!}(1)^2 = 1.2 - 0.25 - 0.5 = 0.45$
Truncation Error: $0.2 - 0.45 = -0.25$. The error is further reduced, demonstrating improved accuracy with more terms.

#### 4.2 Example 2: Taylor Expansion of $e^x$ about $x_0 = 0$ (Maclaurin Series)

Let's approximate $e^{0.5}$ by expanding $f(x) = e^x$ around $x_0 = 0$. Here, $h = x - x_0 = 0.5 - 0 = 0.5$.
All derivatives of $e^x$ are $e^x$, so $f^{(n)}(0) = e^0 = 1$ for all $n$.

The Taylor series for $e^x$ about $x_0=0$ is:
$e^x = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \frac{x^4}{4!} + \frac{x^5}{5!} + \dots$
The true value of $e^{0.5}$ is approximately $1.648721$.

| Order of Approx. (n) | Terms Used | Approximation for $e^{0.5}$ | Truncation Error ($\mathcal{O}(x^{n+1})$) | Actual Error |
| :------------------- | :--------- | :-------------------------- | :---------------------------------------- | :----------- |
| 0                    | $1$        | $1 + 0.5 = 1.5$             | $\mathcal{O}(x^2)$                        | $0.148721$   |
| 1                    | $1+x$      | $1.5 + \frac{(0.5)^2}{2} = 1.625$ | $\mathcal{O}(x^3)$                        | $0.023721$   |
| 2                    | $1+x+\frac{x^2}{2!}$ | $1.625 + \frac{(0.5)^3}{6} \approx 1.645833$ | $\mathcal{O}(x^4)$                        | $0.002888$   |
| 3                    | $1+x+\frac{x^2}{2!}+\frac{x^3}{3!}$ | $1.645833 + \frac{(0.5)^4}{24} \approx 1.648437$ | $\mathcal{O}(x^5)$                        | $0.000284$   |
| 4                    | $1+x+\dots+\frac{x^4}{4!}$ | $1.648437 + \frac{(0.5)^5}{120} \approx 1.648697$ | $\mathcal{O}(x^6)$                        | $0.000024$   |

#### 4.3 Example 3: Taylor Expansion of $e^x$ about $x_0 = 0.25$

Now, let's approximate $e^{0.5}$ by expanding $f(x) = e^x$ around $x_0 = 0.25$. Here, $h = x - x_0 = 0.5 - 0.25 = 0.25$.
All derivatives of $e^x$ are $e^x$, so $f^{(n)}(0.25) = e^{0.25} \approx 1.284025$ for all $n$.

The Taylor series for $e^x$ about $x_0=0.25$ is:
$e^x = e^{0.25} \left( 1 + h + \frac{h^2}{2!} + \frac{h^3}{3!} + \frac{h^4}{4!} + \dots \right)$
The true value of $e^{0.5}$ is approximately $1.648721$.

| Order of Approx. (n) | Terms Used | Approximation for $e^{0.5}$ | Truncation Error ($\mathcal{O}(h^{n+1})$) | Actual Error |
| :------------------- | :--------- | :-------------------------- | :---------------------------------------- | :----------- |
| 0                    | $e^{0.25}$ | $e^{0.25}(1+h) \approx 1.605031$ | $\mathcal{O}(h^2)$                        | $0.04369$    |
| 1                    | $e^{0.25}(1+h)$ | $e^{0.25}(1+h+\frac{h^2}{2!}) \approx 1.64515$ | $\mathcal{O}(h^3)$                        | $0.003571$   |
| 2                    | $e^{0.25}(1+h+\frac{h^2}{2!})$ | $e^{0.25}(1+h+\frac{h^2}{2!}+\frac{h^3}{3!}) \approx 1.648494$ | $\mathcal{O}(h^4)$                        | $0.000227$   |
| 3                    | $e^{0.25}(\dots+\frac{h^3}{3!})$ | $e^{0.25}(\dots+\frac{h^4}{4!}) \approx 1.648703$ | $\mathcal{O}(h^5)$                        | $0.000018$   |

**Key Takeaways from $e^x$ Examples:**
*   **Accuracy Improves with More Terms:** In both examples, including more terms in the Taylor series approximation consistently leads to a more accurate result and a smaller truncation error.
*   **Closer Expansion Point, Better Accuracy:** Comparing Example 2 ($x_0=0$, $h=0.5$) and Example 3 ($x_0=0.25$, $h=0.25$), for the same number of terms, the approximation in Example 3 (expanded around a point closer to $x=0.5$) yields a significantly smaller truncation error. This highlights that choosing an expansion point closer to the desired evaluation point can greatly improve the accuracy of the approximation for a given number of terms.

#### 4.4 Comparative Analysis of Truncation Error for $e^x$

The following table explicitly compares the actual truncation errors from the two $e^x$ examples, demonstrating the impact of both the order of approximation and the step size.

| Order of Trunc. Er. | Error (x₀=0, h=0.5) | Error (x₀=0.25, h=0.25) | Ratio (Error_h=0.5 / Error_h=0.25) | Expected Ratio ($2^n$) |
| :------------------ | :-------------------- | :------------------------ | :---------------------------------- | :--------------------- |
| $\mathcal{O}(h^2)$  | $0.14872$             | $0.04369$                 | $3.40$                              | $2^2 = 4$              |
| $\mathcal{O}(h^3)$  | $0.023721$            | $0.003571$                | $6.64$                              | $2^3 = 8$              |
| $\mathcal{O}(h^4)$  | $0.002888$            | $0.000227$                | $12.72$                             | $2^4 = 16$             |
| $\mathcal{O}(h^5)$  | $0.000284$            | $0.000018$                | $15.78$                             | $2^5 = 32$             |

This table clearly illustrates that when the step size $h$ is halved (from $0.5$ to $0.25$), the error is reduced by a factor that is approximately $2^n$, where $n$ is the exponent in the Big O notation for the truncation error. This confirms the theoretical scaling of truncation error with step size.

#### 4.5 Example 4: Taylor Expansion of $\cos(x)$ about $x_0 = \pi/4$

Let's approximate $f(x) = \cos(x)$ at $x_{i+1} = \pi/3$ based on the value and derivatives at $x_i = \pi/4$.
*   True value: $\cos(\pi/3) = 0.5$.
*   Step size: $h = x_{i+1} - x_i = \pi/3 - \pi/4 = \pi/12 \approx 0.261799$.

Derivatives of $f(x) = \cos(x)$ evaluated at $x_i = \pi/4$:
*   $f(\pi/4) = \cos(\pi/4) = \sqrt{2}/2 \approx 0.707106781$
*   $f'(\pi/4) = -\sin(\pi/4) = -\sqrt{2}/2 \approx -0.707106781$
*   $f''(\pi/4) = -\cos(\pi/4) = -\sqrt{2}/2 \approx -0.707106781$
*   $f'''(\pi/4) = \sin(\pi/4) = \sqrt{2}/2 \approx 0.707106781$
*   The pattern of derivatives repeats every four terms.

Using the Taylor series formula $f(x_{i+1}) = f(x_i) + f'(x_i)h + \frac{f''(x_i)}{2!}h^2 + \dots$:

| n (Order of Approx.) | Approximated Value $f(\pi/3)$ | Percent Relative Error ($\epsilon_t$) |
| :------------------- | :------------------------------ | :------------------------------------ |
| 0                    | $0.707106781$                   | $41.4213562\%$                        |
| 1                    | $0.521986659$                   | $4.397331725\%$                       |
| 2                    | $0.497754491$                   | $0.4491017457\%$                      |
| 3                    | $0.499869147$                   | $0.0262\%$                            |
| 4                    | $0.500007551$                   | $0.00151\%$                           |
| 5                    | $0.500000304$                   | $0.0000608\%$                         |
| 6                    | $0.499999988$                   | $0.000000244\%$                       |

This example vividly demonstrates how the percent relative error decreases rapidly with each additional term, leading to highly accurate approximations.

### 5. Numerical Differentiation

The Taylor series is also fundamental to **numerical differentiation**, which involves approximating the derivative of a function using its values at discrete points.

Consider the Taylor series expansion of $f(x+h)$ around $x$:
$f(x+h) = f(x) + f'(x)h + \frac{f''(x)}{2!}h^2 + \frac{f'''(x)}{3!}h^3 + \dots$

#### 5.1 Forward Difference Approximation

Rearranging the first two terms of the Taylor series to solve for $f'(x)$:
$f'(x)h = f(x+h) - f(x) - \frac{f''(x)}{2!}h^2 - \frac{f'''(x)}{3!}h^3 - \dots$
$f'(x) = \frac{f(x+h) - f(x)}{h} - \frac{f''(x)}{2!}h - \frac{f'''(x)}{3!}h^2 - \dots$

If we approximate $f'(x)$ by just the first term, we get the **forward difference approximation**:
$f'(x) \approx \frac{f(x+h) - f(x)}{h}$
The terms we neglected, $-\frac{f''(x)}{2!}h - \frac{f'''(x)}{3!}h^2 - \dots$, represent the truncation error. The dominant term is proportional to $h$, so this approximation has a truncation error of **$O(h)$**. This means halving $h$ approximately halves the error.

#### 5.2 Backward Difference Approximation

Similarly, using $f(x-h) = f(x) - f'(x)h + \frac{f''(x)}{2!}h^2 - \dots$, we can derive the **backward difference approximation**:
$f'(x) \approx \frac{f(x) - f(x-h)}{h}$
This also has a truncation error of **$O(h)$**.

#### 5.3 Centered Difference Approximation

The **centered difference approximation** is derived by subtracting the Taylor series for $f(x-h)$ from the series for $f(x+h)$:
$f(x+h) = f(x) + f'(x)h + \frac{f''(x)}{2!}h^2 + \frac{f'''(x)}{3!}h^3 + \frac{f^{(4)}(x)}{4!}h^4 + \dots$
$f(x-h) = f(x) - f'(x)h + \frac{f''(x)}{2!}h^2 - \frac{f'''(x)}{3!}h^3 + \frac{f^{(4)}(x)}{4!}h^4 - \dots$

Subtracting the second from the first:
$f(x+h) - f(x-h) = 2f'(x)h + 2\frac{f'''(x)}{3!}h^3 + \dots$
Solving for $f'(x)$:
$f'(x) = \frac{f(x+h) - f(x-h)}{2h} - \frac{f'''(x)}{3!}h^2 - \dots$

The **centered difference approximation** is:
$f'(x) \approx \frac{f(x+h) - f(x-h)}{2h}$
The dominant neglected term is proportional to $h^2$, giving this approximation a truncation error of **$O(h^2)$**.

#### 5.4 Comparison of Numerical Differentiation Methods

The **centered difference approximation is generally more accurate** than forward or backward differences. This is because its truncation error is $O(h^2)$, while forward and backward differences are $O(h)$. As discussed, an $O(h^2)$ method means the error decreases much faster (quadratically) as $h$ is reduced, compared to an $O(h)$ method where the error decreases linearly with $h$. For example, halving $h$ reduces the error by a factor of 4 for centered difference, but only by a factor of 2 for forward/backward differences.

**Conceptual Example: Estimating a First Derivative at $x=0.5$**

To estimate the first derivative of a function $f(x)$ at $x=0.5$ using different step sizes:

*   **Using $h = 0.5$:**
    *   Forward: $f'(0.5) \approx (f(1.0) - f(0.5)) / 0.5$
    *   Backward: $f'(0.5) \approx (f(0.5) - f(0.0)) / 0.5$
    *   Centered: $f'(0.5) \approx (f(1.0) - f(0.0)) / 1.0$

*   **Using $h = 0.25$:**
    *   Forward: $f'(0.5) \approx (f(0.75) - f(0.5)) / 0.25$
    *   Backward: $f'(0.5) \approx (f(0.5) - f(0.25)) / 0.25$
    *   Centered: $f'(0.5) \approx (f(0.75) - f(0.25)) / 0.5$

Comparing the results, especially for the centered difference, would show a significant increase in accuracy with the smaller step size, consistent with the $O(h^2)$ error behavior.

### 6. Conclusion

The Taylor series is a cornerstone of numerical analysis, providing the theoretical foundation for approximating functions and their derivatives. Understanding **truncation error**, its dependence on the **number of terms** and **step size ($h$)**, and its relationship with **roundoff error** is crucial for developing and applying effective numerical methods. By carefully selecting the order of approximation and the step size, engineers and scientists can achieve desired levels of accuracy in their computations, making complex problems tractable.