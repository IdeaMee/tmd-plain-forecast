# ML 09 — Support Vector Machine (SVM)

Source: `course/slides/09 Support Vector Machine.pptx` (40 slides, Parinya Sanguansat). Formulas read from slide images.
Legend: **[slide N]** = from the slide · **[general]** = general knowledge or my inference, not stated on the slide.

**Project relevance: MEDIUM.** Candidate comparison classifier for Stage 1 (sentence = TF-IDF vector, linear SVM). Also the standard strong baseline for text classification. [general]

---

## 1. Key ideas

- A linear classifier separates classes with a hyperplane. Many hyperplanes separate the data; SVM picks the one with the **maximal margin** (best generalization). [slides 5-8]
- Only a few training points, the **support vectors**, determine the boundary; all others get $\alpha=0$. [slide 18]
- Noisy data: allow errors with **soft margin** (slack $\xi_i$, trade-off $C$). [slides 19-20]
- Non-linear data: map to a higher-dimensional space, or use the **kernel trick** so you never compute the mapping explicitly [general]. [slides 25-34]
- SVM is binary; for $N$ classes use $N$ one-vs-rest SVMs or DAG SVM. [slides 35-38]

## 2. VC dimension [slides 2, 28-29]

- VC dimension of model $f$ = largest $h$ such that some set of $h$ points can be **shattered** by $f$ (every labeling of them is separable). It gives a probabilistic upper bound on test error.
- A straight line in 2-D has VC dimension **3**: 3 non-collinear points can be separated in all $2^3=8$ labelings (slide 28); 4 points cannot (XOR-like layout, slide 2).
- Slide 29 shows 3 collinear points labeled green-red-green (no text on the slide). [general] A line cannot separate this labeling, but the definition only needs *some* set of $h$ points to be shattered.
- Slide questions left open: "VC dimension of a rectangle = ?" and "what has the highest VC dimension?". [general] An axis-aligned rectangle has VC dimension 4; the answer depends on which family of rectangles is meant, so confirm with the lecturer's key if it matters.

## 3. Hyperplane [slides 3-4]

- 1-D: a point; 2-D: a line $y=mx+c$ or $ax+by+c=0$; n-D: a hyperplane

$$w_1x_1+w_2x_2+\dots+w_nx_n+b=0\quad\Longleftrightarrow\quad \mathbf{w}^T\mathbf{x}+b=0$$

- One side: $\mathbf{w}^T\mathbf{x}+b>0$, other side: $<0$.
- The perceptron also finds a separating hyperplane, but the result depends on initialization. [slide 5]

## 4. Margin and the linear SVM

Canonical hyperplanes [slide 8]: $\mathbf{w}^T\mathbf{x}+b=+1$ and $=-1$ pass through the support vectors; the decision boundary is $\mathbf{w}^T\mathbf{x}+b=0$.

**Margin** $\gamma$ = shortest distance between the two outer lines [slide 9]. With $\mathbf{w}^T\mathbf{x}_++b=1$, $\mathbf{w}^T\mathbf{x}_-+b=-1$ we get $\mathbf{w}^T(\mathbf{x}_+-\mathbf{x}_-)=2$, and projecting $\mathbf{x}_+-\mathbf{x}_-$ onto $\mathbf{w}$:

$$\gamma=\frac{2}{\|\mathbf{w}\|}$$

**Binary labels** $y_i\in\{+1,-1\}$ [slide 10]: all points satisfy

$$y_i(\mathbf{w}^T\mathbf{x}_i+b)\ge 1$$

**Linear SVM problem** [slide 11]: maximize the margin, equivalently minimize $\frac12\mathbf{w}^T\mathbf{w}$:

$$\max\ \gamma=\frac{2}{\|\mathbf{w}\|}\ \ \text{s.t. } y_i(\mathbf{w}^T\mathbf{x}_i+b)\ge1\ \forall i
\qquad\Longleftrightarrow\qquad
\min\ \tfrac12\mathbf{w}^T\mathbf{w}\ \ \text{s.t. } y_i(\mathbf{w}^T\mathbf{x}_i+b)\ge1\ \forall i$$

## 5. Quadratic programming (QP) [slides 12-13]

General form: $\min J(\mathbf{x})=\frac12\mathbf{x}^TQ\mathbf{x}+\mathbf{c}^T\mathbf{x}$ s.t. $A\mathbf{x}\le\mathbf{b},\ E\mathbf{x}=\mathbf{d}$. No closed-form solution; solved iteratively (interior-point, active-set, trust-region-reflective). MATLAB: `quadprog`, with $J=\frac12\mathbf{x}^TH\mathbf{x}+\mathbf{f}^T\mathbf{x}$, $A\mathbf{x}\le\mathbf{b}$, $A_{eq}\mathbf{x}=\mathbf{b}_{eq}$, $lb\le\mathbf{x}\le ub$.

Primal SVM mapped to `quadprog` (slide 13): $H=I$, $\mathbf{f}=0$, $A=-D_yX^T$, $\mathbf{b}=-1$ (with $D_y=\mathrm{diag}(y)$ and samples as columns of $X$ [general]). The $A_{eq}$ and $lb\le\mathbf{x}\le ub$ terms are crossed out on slide 13 (the primal does not use them; slide 17 does). The slide circles $+b$ in the constraint but does not show how $b$ is handled, and this mapping covers $\mathbf{w}$ only.

## 6. Dual form (hard margin) [slides 14-17]

Generalized Lagrangian with multipliers $\alpha_i\ge0$ (KKT conditions):

$$L(\mathbf{w},b,\boldsymbol\alpha)=\tfrac12\mathbf{w}^T\mathbf{w}-\sum_i\alpha_i\big[y_i(\mathbf{w}^T\mathbf{x}_i+b)-1\big],\qquad
\alpha_i\big[y_i(\mathbf{w}^T\mathbf{x}_i+b)-1\big]=0,\quad \alpha_i\ge0$$

Set derivatives to zero:

$$\frac{\partial L}{\partial\mathbf{w}}=0\Rightarrow \mathbf{w}=\sum_i y_i\alpha_i\mathbf{x}_i,\qquad
\frac{\partial L}{\partial b}=0\Rightarrow\sum_i y_i\alpha_i=0$$

Substitute back → **dual problem** (a QP in $\boldsymbol\alpha$ only):

$$\max_{\boldsymbol\alpha}\ J(\boldsymbol\alpha)=\sum_i\alpha_i-\tfrac12\sum_{i,j}y_iy_j\alpha_i\alpha_j\,\mathbf{x}_i^T\mathbf{x}_j
\quad\text{s.t. }\sum_i y_i\alpha_i=0,\ \ \alpha_i\ge0$$

Solution:

$$\mathbf{w}^*=\sum_i y_i\alpha_i^*\mathbf{x}_i,\quad \gamma^*=\frac{2}{\|\mathbf{w}^*\|},\quad
b^*=-\frac{\max_{y=-1}(\mathbf{w}^*\!\cdot\mathbf{x}_i)+\min_{y=+1}(\mathbf{w}^*\!\cdot\mathbf{x}_i)}{2},\quad
f(\mathbf{x})=\mathbf{w}^*\!\cdot\mathbf{x}+b^*,\ \ y^*=\begin{cases}+1&f>0\\-1&f<0\end{cases}$$

`quadprog` form (slide 17): minimize $-J(\boldsymbol\alpha)$ with $H=D_yX^TXD_y$, $\mathbf{f}=-\mathbf{1}$, $A_{eq}=\mathbf{y}^T$, $b_{eq}=0$, $lb=0$, $ub=\infty$.

**Only support vectors are kept** [slide 18]: $\alpha_i=0$ for points not on the margin lines, so

$$f(\mathbf{x})=\sum_{i\in SV}y_i\alpha_i^*\,\mathbf{x}_i\cdot\mathbf{x}+b^*$$

## 7. Soft margin [slides 19-24]

Allow slack $\xi_i\ge0$ for noisy points. Primal:

$$\min\ \tfrac12\mathbf{w}^T\mathbf{w}+C\sum_i\xi_i\quad\text{s.t. } y_i(\mathbf{w}^T\mathbf{x}_i+b)\ge1-\xi_i,\ \ \xi_i\ge0\ \ \forall i$$

- $\frac12\mathbf{w}^T\mathbf{w}$ = hard-margin term (large margin); $\sum\xi_i$ = training error. **$C$ is the trade-off parameter**; it can be viewed as a way to control over-fitting. [slide 20]
- Lagrangian adds multipliers $\alpha_i,r_i\ge0$; differentiating gives $\mathbf{w}=\sum y_i\alpha_i\mathbf{x}_i$, $C-\alpha_i-r_i=0$ (so $C=\alpha_i+r_i$), $\sum y_i\alpha_i=0$. [slides 21-22]
- The dual objective comes out the same as the hard-margin one; the only change is the box constraint:

$$\max\ J(\boldsymbol\alpha)=\sum_i\alpha_i-\tfrac12\sum_{i,j}y_iy_j\alpha_i\alpha_j\,\mathbf{x}_i^T\mathbf{x}_j\quad\text{s.t. }\sum y_i\alpha_i=0,\ \ C\ge\alpha_i\ge0$$

  Solution formulas same as Section 6; `quadprog` identical except $ub=C\cdot\mathbf{1}$. [slides 23-24]

## 8. Non-linear SVM and kernels [slides 25-34]

- Data not separable by a line (e.g. XOR layout, slide 25). Two approaches [slide 26]:
  1. **2 steps:** transform to a (usually higher-dimensional) linear space, then run a linear classifier. Example slide 27 (same dimension, #attribute = #feature): $x_1'=x_1^2,\ x_2'=x_2$ turns the curve $x_2=x_1^2$ into the line $x_2'=x_1'$. Slide 30 ("higher dimension transformation") is an animated GIF: the 4 XOR-layout points go from 2-D to 3-D and end up separated by a line (the PDF export shows only the first frame).
  2. **1 step:** kernel machine.
- **Mercer's theorem:** any continuous, symmetric, positive semi-definite kernel function is a dot product in some high-dimensional space. **Kernel trick:** wherever a dot product appears, replace it with the kernel:

$$\langle\mathbf{x}_i,\mathbf{x}_j\rangle\leftarrow K(\mathbf{x}_i,\mathbf{x}_j)=\langle\Phi(\mathbf{x}_i),\Phi(\mathbf{x}_j)\rangle$$

  $\Phi$ maps lower-dimensional non-linear space to higher-dimensional linear space ([general] never computed explicitly).

| Kernel | $K(\mathbf{x}_i,\mathbf{x}_j)$ |
|---|---|
| Linear | $\langle\mathbf{x}_i,\mathbf{x}_j\rangle$ |
| Polynomial | $(\langle\mathbf{x}_i,\mathbf{x}_j\rangle+1)^d$ |
| RBF | $e^{-\gamma\|\mathbf{x}_i-\mathbf{x}_j\|^2},\ \gamma>0$ |
| Gaussian RBF | $e^{-\frac{1}{2\sigma^2}\|\mathbf{x}_i-\mathbf{x}_j\|^2}$ |
| Sigmoid | $\tanh(a\langle\mathbf{x}_i,\mathbf{x}_j\rangle+b)$, slide writes $\exists[a>0\wedge b<0]$ (valid for some such $a,b$) |

- Computing RBF efficiently (slide 33): $\|\mathbf{x}_i-\mathbf{x}_j\|^2=\|\mathbf{x}_i\|^2-2\mathbf{x}_i^T\mathbf{x}_j+\|\mathbf{x}_j\|^2$, a matrix expression (MATLAB code on slide).
- **Non-linear SVM dual** [slide 34]:

$$\max\ J(\boldsymbol\alpha)=\sum_i\alpha_i-\tfrac12\sum_{i,j}y_iy_j\alpha_i\alpha_jK(\mathbf{x}_i,\mathbf{x}_j)\ \ \text{s.t. }\sum y_i\alpha_i=0,\ C\ge\alpha_i\ge0;\qquad
f(\mathbf{x})=\sum_i y_i\alpha_i^*K(\mathbf{x}_i,\mathbf{x})+b^*$$

  with $b^*$ chosen so that $y_if(\mathbf{x}_i)=1$ (slide wording; [general] this holds only for margin support vectors).

## 9. Multiclass SVM [slides 35-38]

- **One-vs-rest:** train $N$ SVMs (SVM-$k$: "Class $k$" vs "not Class $k$"); predict with all and choose the one that puts the input furthest into the positive region. Gives multiple hyperplanes (slide 36).
- **DAG SVM:** a decision DAG of pairwise (one-vs-one) classifiers. For 3 classes: root 1v3 → "Not 3" goes to 1v2, "Not 1" goes to 2v3; leaves are the classes (slide 37; slide 38 generalizes the indexing to more classes). [general] One-vs-one needs $N(N-1)/2$ classifiers.

## 10. SMO (Sequential Minimal Optimization) [slides 39-40]

Only diagrams on the slides (no text). Idea [general, consistent with the plots]: optimize two multipliers $\alpha_1,\alpha_2$ at a time. The constraint $\sum y_i\alpha_i=0$ confines the pair to a line (slope +1 when labels differ, slope −1 when equal, shifted by $k$); the box $0\le\alpha\le C$ clips that line to a segment (slide plots mark $k$ (the $\alpha_2$-intercept) and the lengths $|k|$, $k-C$ where the box cuts the line; slide 39 is the slope +1 case, slide 40 the slope −1 case).

## 11. Project relevance and practical notes

- Stage-1 comparison: linear SVM on TF-IDF vectors of Thai-segmented sentences vs. Naive Bayes ([08](08-bayesian-learning.md)) and kNN ([04](04-knn.md)).
- Tune $C$ (and kernel parameters, if non-linear) on a validation set, not on the test set. [general]
- Multi-class (e.g. several hazard types) needs the one-vs-rest or DAG scheme of Section 9. [general]
