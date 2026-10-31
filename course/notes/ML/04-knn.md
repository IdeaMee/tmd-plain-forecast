# ML 04 — k-Nearest Neighbors (k-NN)

Source: `course/slides/04 k-Nearest Neighbor.pptx` (18 slides, Parinya Sanguansat). Formulas read from slide images.
Legend: **[slide N]** = from the slide · **[general]** = general knowledge or my inference · **[computed]** = my own calculation.

**Project relevance: MEDIUM-LOW.** Simple comparison classifier for Stage 1 (sentence vectors compared by distance); slow at prediction time with many training sentences, but the dataset here is small. The "non-numeric data → numeric (frequency)" idea on slide 7 is exactly how text becomes vectors.

---

## 1. Key idea

Classify a new point by looking at the most similar points already collected. [slides 4-6] No explicit training phase ("no training required", slide 14); calling it a "lazy" learner is the usual term. [general]

**k-NN procedure** [slide 6]:
1. Collect data.
2. Define the similarity measurement.
3. For a new item, compute its similarity to all collected data.
4. Find the most similar item(s).
5. Assign the class of the most similar one (k=1 case on the slide).

$k$ = number of neighbors considered; **if $k=1$ it is called the nearest neighbor** rule. [slide 5]
Slide 5 asks "X belongs to class ?" for $k=1,3,6$ on a 2-D picture with blue (1, 2, 3), green (4, 5, 6), red (7, 8, 9) points. Reading the picture [general]: $k=1$ → red (point 7 is nearest); $k=3$ → the three points inside the middle circle are 7 (red), 4, 6 (green) → green; $k=6$ → the six inside the outer circle are 7, 4, 6, 1, 2, 3 = 1 red, 2 green, 3 blue → blue by majority (points 1-3 sit on the edge of the $k=3$ circle, 8-9 on the edge of the $k=6$ circle). So the answer changes with $k$ (red, green, blue), which is the point of the exercise; the slide itself gives no answers.
For $k>1$ the usual rule is majority vote among the $k$ neighbors (the slide does not spell this out). [general]

## 2. Similarity measurement [slide 7]

$$\text{similarity}\ \propto\ \frac{1}{\text{distance}}$$

- Build a **vector space** from the data. Numeric data: normalized or not. **Non-numeric data: represent by numbers (e.g. frequency).**
- Distance in a vector space is a **norm**.

## 3. Vector length and norms [slides 8-13]

2-D/3-D vector length: $v=\sqrt{x^2+y^2+z^2}$. Properties: $v\ge0$; multiplying by a positive scalar changes length but not direction; **triangle inequality** $|\overrightarrow{AB}|+|\overrightarrow{BC}|\ge|\overrightarrow{AC}|$.
A **norm** $\|\cdot\|$ generalizes length to $\mathbb{R}^n$; a vector space with a norm is a normed vector space.

| Norm | Other names | Formula | Unit-ball shape |
|---|---|---|---|
| $L_1$ | Rectilinear / City block / Manhattan / Taxicab | $\lVert\mathbf{x}\rVert_1=\lvert x_1\rvert+\lvert x_2\rvert+\dots+\lvert x_n\rvert$ | diamond |
| $L_2$ | Euclidean | $\lVert\mathbf{x}\rVert_2=\sqrt{\lvert x_1\rvert^2+\dots+\lvert x_n\rvert^2}$ | circle |
| $L_\infty$ | Uniform / Supremum / Chebyshev / Infinity | $\lVert\mathbf{x}\rVert_\infty=\max\{\lvert x_1\rvert,\dots,\lvert x_n\rvert\}$ | square |
| $L_p$ | p-norm | $\lVert\mathbf{x}\rVert_p=\sqrt[p]{\lvert x_1\rvert^p+\dots+\lvert x_n\rvert^p}$ | slide shows $p=3/2$ (rounded diamond) and $p=2/3$ (star/astroid) |

Distance between $\mathbf{a}$ and $\mathbf{b}$ = norm of the difference $\|\mathbf{a}-\mathbf{b}\|$. [general]

## 4. Pros and cons [slide 14]

- **Pros:** high accuracy, insensitive to outliers, no assumptions about the data, no training required.
- **Cons:** computationally expensive, requires a lot of memory.
- Works with numeric and nominal values.

## 5. Making k-NN cheaper [slides 15-18]

- **Condensed nearest neighbor (CNN)** [slide 15]: build a small *prototype* set $U$ sampled from the training set $X$; almost as accurate as 1-NN. Iterate:
  1. Scan all $x\in X$, looking for an $x$ whose nearest prototype in $U$ has a **different label** than $x$.
  2. Remove $x$ from $X$ and add it to $U$.
  3. Repeat the scan until no more prototypes are added to $U$.
- **Border ratio** [slide 16], used to choose the order of training samples:

$$a(\mathbf{x})=\frac{\lVert\mathbf{x}'-\mathbf{y}\rVert}{\lVert\mathbf{x}-\mathbf{y}\rVert}$$

  The slide gives only the formula and a figure (points $\mathbf{X}$, $\mathbf{X}'$, $\mathbf{Y}$). From the figure [general inference]: $\mathbf{y}$ is the nearest point to $\mathbf{x}$ with a different class, and $\mathbf{x}'$ is the point of $\mathbf{x}$'s own class closest to $\mathbf{y}$; samples close to the class border get larger ratios.
- **K-d tree** [slide 17]: partition the space with axis-aligned splits stored in a binary tree to **reduce the number of comparisons** (slide shows a 2-D partition and its tree).
- **Locality-sensitive hashing (LSH)** [slide 18]: dimension reduction, hash → bits. Slide example: three directions/hyperplanes (arrows 1, 2, 3, each with a perpendicular line); each point gets one bit per hyperplane by which side it falls on: A = 110 → code 6, B = 001 → code 1, C = 011 → code 3 (the table's Code column, the bits read as binary). [general] Nearby points tend to share codes, and the hyperplanes are normally chosen at random.

## 6. Warm-up examples on slides 2-3

- **Look-up table (slide 2):** a table of $n\to\log(n)$ ($1.00\to0.00000000$, $1.01\to0.00432137$, $1.02\to0.00860017$, $1.03\to0.01283722$, $1.04\to0.01703334$). Questions: $\log(1.01)$, $\log(1.03)$, $\log(1.035)$; the third is circled with the label "Interpolation?". The first two can be read straight off the table, the third cannot, and the analogy to k-NN (predict from neighbors) is my reading. [general] [computed] The table values are base-10 logs (checked). Linear interpolation: $\log(1.035)\approx(0.01283722+0.01703334)/2=0.01493528$ (true $\log_{10}1.035\approx0.014940$).
- **Iris (slide 3):** classify flowers as Setosa / Versicolor / Virginica.

## 7. Project relevance and practical notes

- Stage-1 comparison with Naive Bayes ([08](08-bayesian-learning.md)) and SVM ([09](09-svm.md)).
- Represent each sentence as a vector (word counts / TF-IDF, see NLP 4-1) then use $L_2$ distance. [general] For sparse text vectors, cosine similarity is commonly preferred to Euclidean distance; NLP 4-1 covers cosine similarity.
- Choose $k$ on a validation set; with an even $k$ ties are possible. [general]
