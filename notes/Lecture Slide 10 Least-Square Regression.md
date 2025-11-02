---
created_at: 2025-11-02T17:37:35.525219
file_id: 653bb8be-e635-43ee-badf-b8bfa6f2fe8e
original_filename: Lecture Slide 10 Least-Square Regression.pdf
note_style: descriptive
llm_provider: gemini
llm_model: gemini-2.5-flash
tokens_used: 13481
total_chunks: 2
synthesis_method: direct
---

## Least-Squares Regressions: A Comprehensive Guide to Modeling Data Trends

Least-Squares Regression is a fundamental statistical method used to find the "best fit" curve or line that represents the underlying trend within a set of data points, especially when that data contains inherent error or variability. This detailed note will cover the foundational statistical concepts necessary for understanding regression, delve into the principles of linear and polynomial least-squares regression, and explain why the least-squares criterion is the preferred method for fitting models to data.

### I. Fundamental Statistical Concepts

Before exploring least-squares regression, it's crucial to understand how data is described and summarized.

#### 1. Arithmetic Mean ($\bar{y}$)

The **arithmetic mean**, commonly known as the "average," is a measure of the central tendency of a dataset. It provides a single value that represents the typical magnitude of the data points. To calculate the mean, all individual data points in a sample are summed, and this sum is then divided by the total number of data points.

**Formula:**
For a sample of $n$ data points, $y_1, y_2, ..., y_n$, the mean ($\bar{y}$) is:
$\bar{y} = \frac{\sum_{i=1}^{n} y_i}{n}$
Here, $\sum_{i=1}^{n} y_i$ signifies the summation of all $y$ values from the first ($y_1$) to the last ($y_n$) data point.

#### 2. Measures of Spread

While the mean indicates the center of the data, measures of spread quantify how much the data points vary or are dispersed around that center.

*   **Range:**
    The range is the simplest measure of spread, calculated as the difference between the highest and lowest values in a dataset. For example, if data points are 3, 5, 8, 10, 12, the range is $12 - 3 = 9$.

*   **Standard Deviation ($s_y$)**
    The **standard deviation** is the most common and significant measure of spread for a sample. It quantifies, on average, how far each data point deviates from the mean of the dataset. A small standard deviation suggests data points are tightly clustered around the mean, while a large standard deviation indicates a wider spread of data.

    Conceptually, its calculation involves:
    1.  Finding the difference between each data point ($y_i$) and the mean ($\bar{y}$).
    2.  Squaring these differences to ensure all contributions are positive and to penalize larger deviations more heavily.
    3.  Summing these squared differences to get the "total sum of the squares of the residuals between the data points and the mean," denoted as $S_t$.
    4.  Dividing $S_t$ by $n-1$ (for a sample, which provides a more accurate estimate of the population standard deviation).
    5.  Taking the square root of the result to return the measure to the original units of the data.

    **Formulas:**
    $s_y = \sqrt{\frac{S_t}{n - 1}}$
    Where $S_t = \sum_{i=1}^{n} (y_i - \bar{y})^2$

*   **Variance:**
    The **variance** is simply the square of the standard deviation ($s_y^2$). It provides another way to quantify data spread. If the standard deviation is known, squaring it yields the variance; conversely, taking the square root of the variance gives the standard deviation. There exists a more convenient computational formula for variance that does not require prior calculation of the mean, yielding the same result.

*   **Coefficient of Variation (c.v.)**
    The **coefficient of variation** is a valuable statistic for comparing the relative variability or spread of different datasets, particularly when their means differ significantly. It expresses the standard deviation as a percentage of the mean, providing a standardized measure of dispersion.

    **Formula:**
    $c.v. = \frac{s_y}{\bar{y}} \times 100\%$
    For instance, a standard deviation of 10 for data with a mean of 100 (c.v. = 10%) indicates the same relative variability as a standard deviation of 1 for data with a mean of 10 (c.v. = 10%).

### II. Linear Least-Squares Regression: Fitting a Straight Line to Data

When data points exhibit a general linear trend but also contain scatter or error, linear least-squares regression is a powerful technique to determine the "best" straight line that represents this trend.

#### 1. The Goal: Approximating a Trend

The challenge in analyzing real-world data is that points rarely align perfectly on a straight line due to measurement noise or inherent variability. The objective of regression is to find an approximating function (e.g., a straight line) that captures the overall shape or general trend of the data, rather than attempting to connect every single point. While a line can be visually drawn through plotted data, this is subjective. Least-squares regression offers a mathematical, objective method to derive a line that minimizes the discrepancy between the data points and the fitted line.

#### 2. The Linear Model

Linear least-squares regression is typically applied to a set of paired observations: $(x_1, y_1), (x_2, y_2), ..., (x_n, y_n)$. The mathematical expression for a straight line modeling this relationship is:

$y = a_0 + a_1x + e$

Where:
*   **$y$**: The **dependent variable**, which is the value we aim to predict or explain.
*   **$x$**: The **independent variable**, used to make the prediction.
*   **$a_0$**: The **y-intercept**, representing the value of $y$ when $x$ is 0. It is the point where the line crosses the y-axis.
*   **$a_1$**: The **slope**, indicating how much $y$ changes for every one-unit change in $x$. It defines the steepness and direction of the line.
*   **$e$**: The **error** or **residual**, which is the difference between the actual observed $y$ value and the $y$ value predicted by our straight-line model for a given $x$. It accounts for the fact that the line will not perfectly fit every data point.

The residual ($e$) can be explicitly defined as:
$e = y - (a_0 + a_1x)$
A positive residual means the actual data point lies above the fitted line, while a negative residual indicates it lies below the line.

### III. Criteria for a "Best" Fit: Why Least-Squares is Preferred

To identify the "best" line, a criterion is needed to evaluate how well a line fits the data. Various criteria exist, each with distinct advantages and disadvantages.

#### 1. Minimizing the Sum of Residual Errors (Problematic)

An intuitive, but flawed, approach is to minimize the sum of all individual errors ($e$):
$\text{Minimize } \sum_{i=1}^{n} e_i$
This method is problematic because positive errors (for points above the line) and negative errors (for points below the line) can cancel each other out. Consequently, many different lines could result in a sum of zero, making it impossible to uniquely determine the "best" line. For example, a line passing through the exact midpoint of two points might have a zero sum of errors, even if it's a poor fit for other data.

#### 2. Minimizing the Sum of Absolute Residual Errors (Better, but not ideal)

To address the cancellation issue, one could minimize the sum of the *absolute values* of the residuals:
$\text{Minimize } \sum_{i=1}^{n} |e_i|$
This approach prevents positive and negative errors from canceling, ensuring that larger deviations contribute more to the sum. While an improvement over simply summing errors, it is generally less mathematically tractable than the least-squares method for deriving analytical solutions for the coefficients.

#### 3. Minimax Criterion (Sensitive to Outliers)

The **minimax principle** aims to choose the line that minimizes the *maximum* distance any single data point falls from the line. The goal is to make the largest individual error as small as possible.
$\text{Minimize } \max(|e_i|)$
However, this strategy is generally *ill-suited* for standard regression analysis because it gives **undue influence to an outlier**. An outlier is a data point significantly distant from the general trend. If such a point exists, the minimax criterion will heavily adjust the entire line to minimize the error for that single outlier, potentially distorting the fit for the majority of the more representative data points. While not ideal for regression, the minimax principle can be useful in other contexts, such as fitting a simple function to approximate a more complicated one, where minimizing the worst-case error is paramount.

#### 4. The Least-Squares Criterion (The Preferred Method)

The **least-squares principle** is the most widely used and effective strategy for finding the "best" fit line or curve. It overcomes the shortcomings of other methods by minimizing the sum of the *squares* of the residuals:
$\text{Minimize } S_r = \sum_{i=1}^{n} e_i^2 = \sum_{i=1}^{n} (y_i - (a_0 + a_1x_i))^2$
This means the method seeks the line (defined by its slope $a_1$ and intercept $a_0$) that makes the sum of all squared differences between the actual $y$ values and the predicted $y$ values as small as possible.

**Advantages of Least-Squares:**
1.  **Eliminates Cancellation:** Squaring the errors ensures that all errors contribute positively to the sum, preventing positive and negative residuals from canceling each other out.
2.  **Penalizes Large Errors More:** Squaring errors gives disproportionately greater weight to larger errors. For example, a residual of 2 contributes $2^2 = 4$ to the sum, whereas a residual of 4 contributes $4^2 = 16$. This characteristic means the method actively works to reduce larger deviations.
3.  **Unique Solution:** For any given set of data, the least-squares criterion yields a *unique* straight line (or curve) that is considered the "best" fit. This objectivity is a significant advantage over subjective methods like visual inspection.
4.  **Mathematical Tractability:** The mathematical properties of squared errors make it straightforward to derive analytical solutions for the coefficients (slope and intercept) of the best-fit line or curve using calculus.

### IV. Least-Squares Fit of a Straight Line: Derivation and Example

To find the values of $a_0$ and $a_1$ that minimize the sum of the squares of the residuals ($S_r$), we employ calculus. We take the partial derivative of $S_r$ with respect to each unknown coefficient ($a_0$ and $a_1$) and set these derivatives equal to zero. This standard optimization technique identifies the minimum point of the function.

The sum of the squares of the residuals for a straight line is:
$S_r = \sum_{i=1}^{n} (y_i - (a_0 + a_1x_i))^2$

1.  **Differentiate $S_r$ with respect to $a_0$ and set to zero:**
    $\frac{\partial S_r}{\partial a_0} = -2 \sum (y_i - a_0 - a_1x_i) = 0$
    Dividing by -2 and rearranging terms:
    $\sum y_i - \sum a_0 - \sum a_1x_i = 0$
    Since $a_0$ is a constant, $\sum a_0 = n a_0$. Similarly, $a_1$ is a constant and can be factored out of its summation.
    $\sum y_i - n a_0 - a_1 \sum x_i = 0$
    Rearranging into the standard form for a system of equations:
    $n a_0 + (\sum x_i) a_1 = \sum y_i$  **(Equation 1)**

2.  **Differentiate $S_r$ with respect to $a_1$ and set to zero:**
    $\frac{\partial S_r}{\partial a_1} = -2 \sum x_i (y_i - a_0 - a_1x_i) = 0$
    Dividing by -2 and rearranging:
    $\sum x_i y_i - \sum a_0 x_i - \sum a_1 x_i^2 = 0$
    $\sum x_i y_i - a_0 \sum x_i - a_1 \sum x_i^2 = 0$
    Rearranging:
    $(\sum x_i) a_0 + (\sum x_i^2) a_1 = \sum x_i y_i$  **(Equation 2)**

#### The Normal Equations for a Straight Line

Equations 1 and 2 form a system of two simultaneous linear equations with two unknowns ($a_0$ and $a_1$). These are known as the **normal equations**:

1.  $n a_0 + (\sum x_i) a_1 = \sum y_i$
2.  $(\sum x_i) a_0 + (\sum x_i^2) a_1 = \sum x_i y_i$

Solving these equations simultaneously yields the following formulas for $a_1$ and $a_0$:

$a_1 = \frac{n \sum x_i y_i - \sum x_i \sum y_i}{n \sum x_i^2 - (\sum x_i)^2}$

$a_0 = \bar{y} - a_1 \bar{x}$

Where $\bar{y} = \frac{\sum y_i}{n}$ (the mean of the $y$ values) and $\bar{x} = \frac{\sum x_i}{n}$ (the mean of the $x$ values).

#### Example of Least-Squares Fitting for a Straight Line

Let's apply these formulas to fit a straight line to a hypothetical dataset.
Assume the following pre-calculated sums from a given data table:
*   $n = 8$ (number of data points)
*   $\sum x_i = 360$
*   $\sum y_i = 5135$
*   $\sum x_i^2 = 20400$
*   $\sum x_i y_i = 312850$

Now, substitute these values into the formulas for $a_1$ and $a_0$:

**Calculate $a_1$:**
$a_1 = \frac{8(312,850) - 360(5,135)}{8(20,400) - (360)^2}$
$a_1 = \frac{2,502,800 - 1,848,600}{163,200 - 129,600}$
$a_1 = \frac{654,200}{33,600}$
$a_1 \approx 19.47024$

**Calculate $a_0$:**
First, calculate the means:
$\bar{x} = \frac{360}{8} = 45$
$\bar{y} = \frac{5135}{8} = 641.875$

Now, use the formula for $a_0$:
$a_0 = \bar{y} - a_1 \bar{x}$
$a_0 = 641.875 - 19.47024(45)$
$a_0 = 641.875 - 876.1608$
$a_0 \approx -234.2857$

Thus, the least-squares best-fit straight line for this data is:
$y = -234.2857 + 19.47024x$

### V. Polynomial Regression: Fitting Curves to Data

When data does not follow a straight-line pattern but instead exhibits a curve (e.g., parabolic, exponential-like), fitting a straight line would poorly represent the underlying relationship. **Polynomial regression** extends the least-squares principle to fit curves to data using higher-order polynomials, providing a more flexible way to model such trends.

#### Least-Squares Fit of a Curve (e.g., Quadratic)

The least-squares procedure can be readily extended to fit data to a higher-order polynomial. For instance, consider fitting a **second-order polynomial** (a quadratic equation):

$y = a_0 + a_1x + a_2x^2 + e$

Here, $a_2$ is an additional coefficient that determines the curvature of the fitted line. The sum of the squares of the residuals for this quadratic equation is:

$S_r = \sum_{i=1}^{n} (y_i - (a_0 + a_1x_i + a_2x_i^2))^2$

#### Determining the Coefficients ($a_0$, $a_1$, and $a_2$)

Similar to the straight-line case, we take the partial derivative of $S_r$ with respect to each unknown coefficient ($a_0$, $a_1$, and $a_2$) and set them equal to zero to find the values that minimize $S_r$.

1.  **Differentiate $S_r$ with respect to $a_0$ and set to zero:**
    $\frac{\partial S_r}{\partial a_0} = -2 \sum (y_i - a_0 - a_1x_i - a_2x_i^2) = 0$
    Rearranging terms:
    $\sum y_i - n a_0 - a_1 \sum x_i - a_2 \sum x_i^2 = 0$

2.  **Differentiate $S_r$ with respect to $a_1$ and set to zero:**
    $\frac{\partial S_r}{\partial a_1} = -2 \sum x_i (y_i - a_0 - a_1x_i - a_2x_i^2) = 0$
    Rearranging terms:
    $\sum x_i y_i - a_0 \sum x_i - a_1 \sum x_i^2 - a_2 \sum x_i^3 = 0$

3.  **Differentiate $S_r$ with respect to $a_2$ and set to zero:**
    $\frac{\partial S_r}{\partial a_2} = -2 \sum x_i^2 (y_i - a_0 - a_1x_i - a_2x_i^2) = 0$
    Rearranging terms:
    $\sum x_i^2 y_i - a_0 \sum x_i^2 - a_1 \sum x_i^3 - a_2 \sum x_i^4 = 0$

#### The Normal Equations for a Quadratic Fit

These three equations form a system of three simultaneous linear equations with three unknowns ($a_0$, $a_1$, and $a_2$). These are the normal equations for a quadratic fit:

1.  $n a_0 + (\sum x_i) a_1 + (\sum x_i^2) a_2 = \sum y_i$
2.  $(\sum x_i) a_0 + (\sum x_i^2) a_1 + (\sum x_i^3) a_2 = \sum x_i y_i$
3.  $(\sum x_i^2) a_0 + (\sum x_i^3) a_1 + (\sum x_i^4) a_2 = \sum x_i^2 y_i$

Solving this system of equations will yield the unique values for $a_0$, $a_1$, and $a_2$ that define the best-fit quadratic curve.

#### Example of Least-Squares Curve Fitting (Quadratic)

Let's fit a quadratic curve to a hypothetical dataset.
Assume the following pre-calculated sums from a given data table:
*   $n = 6$
*   $\sum x_i = 15$
*   $\sum y_i = 152.6$
*   $\sum x_i^2 = 55$
*   $\sum x_i^3 = 225$
*   $\sum x_i^4 = 979$
*   $\sum x_i y_i = 585.6$
*   $\sum x_i^2 y_i = 2488.8$

Substitute these sums into the normal equations:

1.  $6a_0 + 15a_1 + 55a_2 = 152.6$
2.  $15a_0 + 55a_1 + 225a_2 = 585.6$
3.  $55a_0 + 225a_1 + 979a_2 = 2488.8$

Solving this system of three simultaneous linear equations (e.g., using Gaussian elimination, matrix inversion, or numerical solvers), we find the coefficients:

$a_0 \approx 2.4786$
$a_1 \approx 2.3593$
$a_2 \approx 1.8607$

Therefore, the least-squares quadratic equation for this data is:
$y = 2.4786 + 2.3593x + 1.8607x^2$

### VI. General Linear Least Squares

The principles of least-squares fitting for straight lines and polynomial curves can be generalized to fit any model that is linear in its parameters (coefficients). A **general linear least squares** model describes a dependent variable as a linear combination of parameters and independent variables, where the independent variables themselves can be transformed (e.g., $x^2$, $x^3$, $\log(x)$, $\sin(x)$, $e^x$).

For example, a model such as $y = a_0 + a_1 \cos(x) + a_2 e^x$ is considered a linear model in terms of its coefficients ($a_0, a_1, a_2$), even though it involves non-linear functions of $x$. The same fundamental approach of minimizing the sum of squared residuals by taking partial derivatives with respect to each coefficient and solving the resulting system of normal equations applies. This broader framework allows for fitting a wide variety of complex relationships to data.