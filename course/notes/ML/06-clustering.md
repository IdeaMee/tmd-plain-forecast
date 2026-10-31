# ML 06 — Clustering

Source: `course/slides/06 Clustering.pptx` (27 slides, lecturer Parinya Sanguansat). All 27 slides were read as images; the SOM example was fully recomputed in Python. Slide 19 (k-means flowchart) is in Thai; translated here.
Legend: **[slide N]** = taken from the slide · **[computed]** = my own calculation of an example the slide leaves open · **[general]** = general knowledge or my inference, not on the slides.

**Project relevance: MEDIUM-LOW (optional).** Clustering could group similar sentences/reports (e.g. to avoid picking near-duplicate sentences in the Stage-2 extractive summary). The slides cover **SOM, k-means, fuzzy c-means, EM and Gaussian mixture models**; hierarchical clustering is **not** covered.

---

## 1. Key ideas

- Clustering = **unsupervised learning**: there is **no class label information**. [slide 2]
- Figure [slide 2]: points drawn in three visual groups (red, green, blue) plus one black point lying between groups; the slide gives no comment on it.
- Methods on these slides: SOM (neural, slides 3-18), K-means (19), fuzzy c-means (20), EM and GMM (21-27).

## 2. Self-Organizing Map (SOM / Kohonen network) [slides 3-18]

### 2.1 Architecture [slides 3-8]
- SOM = a neural network developed in the 1980s by Teuvo Kohonen (Finland); **unsupervised**. [slide 3]
- An **input layer** ($n$-dimensional) is fully connected to a **Kohonen layer** of nodes arranged as a **1-D line** [slide 4] or a **2-D grid** [slide 5]. Each node holds a weight vector of the same dimension as the input.
- **Winning node = BMU** (best matching unit); the nodes around it form its **neighbourhood**. [slides 3-5]
- **Location vector** [slide 6]: each node on the grid has a position $\mathbf r_i$ (labelled by row,column, e.g. 1,1 … 3,3); $\mathbf r_{BMU}$ is the position of the BMU. (The slide only draws the two vectors; using $\lVert\mathbf r_i-\mathbf r_{BMU}\rVert$ as the lattice distance $d$ of slide 18 is my reading. [general])
- **Shrinking radius** [slides 7-8]: the neighbourhood circle around the BMU gets smaller over time (large circle first, then only the BMU and its direct neighbours).

### 2.2 SOM algorithm [slide 9]
1. **Initialize weights:** randomly set the weights of every node.
2. **Competitive process:** find the winning node.
3. **Cooperative process:** determine the neighbourhood of the winning neuron at this time step.
4. **Weight adjustment:** weights of the winning neuron are "strengthened" and those of neighbouring neurons "suppressed" (slide wording):

$$\mathbf w(t+1)=\mathbf w(t)+\eta\big(\mathbf x-\mathbf w(t)\big)$$

$\mathbf x$ = input vector, $\mathbf w(t)$ = node weight at step $t$, $\eta$ = learning rate. Geometry [slide 10]: $\mathbf x-\mathbf w(t)$ is the vector from $\mathbf w$ to $\mathbf x$; the update moves $\mathbf w$ a fraction $\eta$ of the way towards $\mathbf x$. [general]

"Winner" is the node whose weight vector is closest to $\mathbf x$ (smallest distance). The slide-9 text does not say which distance; the example uses squared Euclidean (below).

### 2.3 Worked example: cluster 4 vectors into 2 clusters [slides 11-17]
Input vectors (columns on slide 11): $x_1=(1,0,0,1)$, $x_2=(0,1,0,1)$, $x_3=(1,0,0,0)$, $x_4=(0,0,1,1)$. Two Kohonen nodes with initial weights
$w_1=(0.9355,\,0.9169,\,0.4103,\,0.8936)$, $w_2=(0.0579,\,0.3529,\,0.8132,\,0.0099)$ [slide 12].

One **epoch** = present $x_1..x_4$ in order, updating the winner each time. The slide states neither $\eta$ nor the distance; I recovered them by recomputation [computed]:
- $d_k=\lVert x-w_k\rVert^2$ = **squared Euclidean** distance (e.g. $d_1(x_1)=1.0245$, whereas plain Euclidean would be 1.0122);
- $\eta=0.6$ in epoch 1, and only the **winner** is updated (neighbourhood radius 0).

| Trace | Input | $d_1$ | $d_2$ | Winner | Updated weight (slide) |
|---|---|---|---|---|---|
| 1 [slide 12] | $x_1$ | 1.0245 | 2.6537 | node 1 | $w_1=(0.9742,\,0.3668,\,0.1641,\,0.9575)$ |
| 2 [slide 13] | $x_2$ | 1.3788 | 2.0637 | node 1 | $w_1=(0.3897,\,0.7467,\,0.0656,\,0.9830)$ |
| 3 [slide 14] | $x_3$ | 1.9006 | 1.6734 | node 2 | $w_2=(0.6232,\,0.1411,\,0.3253,\,0.0039)$ |
| 4 [slide 15] | $x_4$ | 1.5827 | 1.8556 | node 1 | $w_1=(0.1559,\,0.2987,\,0.6263,\,0.9932)$ |

All four distance pairs and winners reproduce exactly. Last-digit differences (0.9575 vs my 0.9574; 0.1411/0.0039 vs my 0.1412/0.0040) come from rounding of the 4-decimal initial weights. Example update [computed]: $w_1\leftarrow w_1+0.6(x_1-w_1)$ gives $0.9355+0.6\cdot0.0645=0.9742$ and $0.9169\cdot0.4=0.3668$.

**Trace of weights** [slide 16] — each row lists $w_1\ |\ w_2$:

| Epoch | $w_1$ | $w_2$ |
|---|---|---|
| Initial | 0.9355, 0.9169, 0.4103, 0.8936 | 0.0579, 0.3529, 0.8132, 0.0099 |
| 1 | 0.1559, 0.2987, 0.6263, 0.9932 | 0.6232, 0.1411, 0.3253, 0.0039 |
| 2 | 0.1083, 0.2612, 0.6359, 0.9995 | 0.8470, 0.0573, 0.1321, 0.0016 |
| 5 | 0.0006, 0.2968, 0.7026, 1.0000 | 0.9992, 0.0003, 0.0007, 0.2954 |
| 20 | 0.0000, 0.3345, 0.6655, 1.0000 | 1.0000, 0.0000, 0.0000, 0.3345 |
| 50 | 0.0000, 0.3868, 0.6132, 1.0000 | 1.0000, 0.0000, 0.0000, 0.3868 |
| 100 | 0.0000, 0.4365, 0.5635, 1.0000 | 1.0000, 0.0000, 0.0000, 0.4365 |
| 1000 | 0.0000, 0.4987, 0.5013, 1.0000 | 1.0000, 0.0000, 0.0000, 0.4987 |

[computed] The whole table is reproduced exactly (to 4 decimals) if $\eta$ **decays by a factor 0.99 per epoch**: $\eta_e=0.6\cdot0.99^{\,e-1}$ for epoch $e$. Other schedules do **not** match: constant $\eta=0.6$ ends at $w_1=(0,0.2857,0.7143,1)$ instead of $(0,0.4987,0.5013,1)$, and halving $\eta$ each epoch freezes the weights near $(0.263,0.324,0.423,0.999)$. The slides never state this schedule; it is my inference.

**Final clusters** [slide 17]: final weights $w_1=(0,\,0.4987,\,0.5013,\,1)$, $w_2=(1,\,0,\,0,\,0.4987)$.

| Input | $d_1$ | $d_2$ | Cluster |
|---|---|---|---|
| 1 = $x_1$ | 1.5000 | 0.2513 | 2 |
| 2 = $x_2$ | 0.5025 | 2.2513 | 1 |
| 3 = $x_3$ | 2.5000 | 0.2487 | 2 |
| 4 = $x_4$ | 0.4975 | 2.2513 | 1 |

Result: cluster 1 = $\{x_2,x_4\}$, cluster 2 = $\{x_1,x_3\}$. [computed] The weights approach the **cluster means**: mean of $x_2,x_4$ = $(0,0.5,0.5,1)$, mean of $x_1,x_3$ = $(1,0,0,0.5)$ (they stop at 0.4987 rather than 0.5 because $\eta$ has decayed). Recomputed $d$ values agree with the slide except $0.5026$ (slide 0.5025) and $0.4974$ (slide 0.4975), a rounding difference.

### 2.4 Decay and neighbourhood functions [slide 18]
To update **not only the BMU**:

$$L(t)=L_0\,e^{-t/\lambda},\qquad \Theta(t)=e^{-\frac{d^2}{2\sigma^2(t)}},\qquad \sigma(t)=\sigma_0\,e^{-t/\lambda},\qquad t=1,2,3,\dots$$

$$\mathbf w(t+1)=\mathbf w(t)+L(t)\,\Theta(t)\,\big(\mathbf x-\mathbf w(t)\big)$$

- $L(t)$ = exponentially decaying learning rate; $\sigma(t)$ = exponentially shrinking neighbourhood width ("shrink the width of the lattice"); $\Theta(t)$ = neighbourhood function. [slide 18]
- Variable meanings below are my reading, not stated on the slide [general]: $d$ = lattice distance between a node and the BMU; $\lambda$ = time constant of the decay; $L_0,\sigma_0$ = initial values (the slide writes them as $L_0(t),\sigma_0(t)$, normally constants).
- [computed] With $\sigma=1$: $\Theta=1$ for the BMU ($d=0$), $e^{-1/2}\approx0.607$ at $d=1$, $e^{-2}\approx0.135$ at $d=2$. So neighbours are pulled **toward** $\mathbf x$ by a smaller amount, not pushed away. This is consistent with this slide's equation, and conflicts with the word "suppressed" on slide 9.

## 3. K-means [slide 19]

The slide shows only a flowchart (Thai labels) and the notes "Clustering the data" and "Need to define the number of groups".

Flowchart steps [slide 19]:
1. Start.
2. Specify the number of groups ($K$).
3. Define the initial centroids.
4. Compute the distance between each data point and each centroid.
5. Assign each point to a group using the **shortest distance**.
6. Compute new centroids from the members of each group.
7. Decision: **did any centroid change?** Yes → go back to step 4; No → end.

Formulas (not on the slide) [general]: assignment $c(x)=\arg\min_k\lVert x-\mu_k\rVert^2$; update $\mu_k=\frac{1}{\lvert C_k\rvert}\sum_{x\in C_k}x$; it decreases $J=\sum_k\sum_{x\in C_k}\lVert x-\mu_k\rVert^2$ at each step, so it converges, but only to a **local** optimum that depends on the initial centroids. Hard assignment; $K$ must be chosen in advance.

**Illustration, not from the slides** [general; numbers computed]: the four vectors of slide 11 with $K=2$ and initial centroids $c_1=x_3=(1,0,0,0)$, $c_2=x_4=(0,0,1,1)$ (squared Euclidean distances).
- Iteration 1: distances to $(c_1,c_2)$: $x_1$ (1,2), $x_2$ (3,2), $x_3$ (0,3), $x_4$ (3,0) → groups $\{x_1,x_3\},\{x_2,x_4\}$. New centroids $c_1=(1,0,0,0.5)$, $c_2=(0,0.5,0.5,1)$.
- Iteration 2: assignments unchanged, centroids unchanged → stop.
- Same partition and the same limits as the SOM of section 2.3. Caution: starting from $c_1=x_1,c_2=x_2$ makes $x_4$ equidistant (2 and 2), so a tie-breaking rule is needed.

## 4. Fuzzy c-means (FCM) [slide 20]

- Similar to K-means but each point has a **membership** in every cluster instead of a hard label. **Membership is the inverse of distance.**
- Slide formula ($i$ = data point, $k$ = cluster, $K$ clusters, $n$ points):

$$\mu_k^{\,i}=\frac{1}{d(x_i,c_k)^{2/(m-1)}},\qquad m>1$$

- Constraint $\sum_{k=1}^{K}\mu_k^{\,i}=1$, so **normalize** by $\sum_{k=1}^{K}\mu_k^{\,i}$. Combining the two statements [computed]:

$$\mu_k^{\,i}=\frac{d(x_i,c_k)^{-2/(m-1)}}{\sum_{j=1}^{K}d(x_i,c_j)^{-2/(m-1)}}$$

- **All data** are used to compute every centre, weighted by membership:

$$c_k=\frac{\sum_{i=1}^{n}(\mu_k^{\,i})^m\,x_i}{\sum_{i=1}^{n}(\mu_k^{\,i})^m}$$

- $m$ is the fuzzifier [general name]: $m\to1$ approaches hard K-means; larger $m$ makes memberships more equal. Loop (not on slide) [general]: initialize centres, compute memberships, recompute centres, repeat until they stop changing. $d=0$ makes the formula undefined, so handle that case separately.
- **Illustration, not from the slides** [computed]: $m=2$, centres $1$ and $5$, point $x=2$: raw $1/1^2=1$ and $1/3^2=1/9$, normalized memberships $0.9$ and $0.1$. One full update with points $\{1,2,4,5\}$, centres $(1.5,4.5)$, $m=2$: memberships to cluster 1 are $0.98,\ 0.9615,\ 0.0385,\ 0.02$, giving new centres $1.4932$ and $4.5068$.

## 5. Expectation-Maximization (EM) [slides 21-22]

**When to use** [slide 21]: data only **partially observable** — unsupervised clustering (the target value is unobservable) or supervised learning with some unobservable instance attributes. **Applications:** training Bayesian belief networks (see [08](08-bayesian-learning.md)), unsupervised clustering, learning hidden Markov models.

**Algorithm** [slide 22]: estimate parameters of the pdf given only the observed data $X$. $h$ = current parameters, $h'$ = revised parameters, $Z$ = unobserved data, $Y$ = complete data.
- **E-step:** estimate the distribution of the hidden variable given the data and current parameters:

$$Q(h'\mid h)\leftarrow E\big[\ln P(Y\mid h')\ \big|\ h,X\big]$$

- **M-step:** maximize it by modifying the parameters:

$$h\leftarrow\arg\max_{h'}Q(h'\mid h)$$

- The slide prints "$Y=X\cap Z$"; the standard definition is $Y=X\cup Z$ (observed plus hidden data). [general]
- EM alternates the two steps until convergence; it finds a local maximum of the likelihood. [general]

## 6. Gaussian Mixture Models (GMM) [slides 23-27]

**When needed** [slide 23]: data are continuous, not all instances can be observed, and the distribution is complex. Model the pdf as a weighted sum of $M$ Gaussians:

$$P(x)=\sum_{i=1}^{M}w_i\,N(x;\mu_i,\sigma_i^2),\qquad\sum_{i=1}^{M}w_i=1$$

(The slide writes $\mu,\sigma^2$ without the subscript $i$.) Figure [slide 23]: a narrow and a wide 1-D Gaussian whose weighted sum is the mixture density.

**Multivariate normal** [slide 24]: for vector data of dimension $d$,

$$N(\mathbf x;\boldsymbol\mu,\Sigma)=\frac{1}{(2\pi)^{d/2}\sqrt{\lvert\Sigma\rvert}}\exp\Big(-\tfrac12(\mathbf x-\boldsymbol\mu)^T\Sigma^{-1}(\mathbf x-\boldsymbol\mu)\Big)$$

$\boldsymbol\mu$ = mean vector, $\Sigma$ = covariance matrix. **A pdf value can exceed 1** (it is a density, not a probability). [computed] e.g. 1-D with $\sigma=0.1$ has peak $1/\sqrt{2\pi\cdot0.01}\approx3.99$.

**Characteristics** [slide 25]
- ANNs are universal approximators of *functions*; GMMs are universal approximators of *densities* (given enough Gaussians). Even **diagonal** GMMs are.
- Full-rank GMMs are hard to handle: the number of parameters grows as the **square** of the number of dimensions (exactly $d(d+1)/2$ per covariance matrix [general]).
- GMMs are trained by maximum likelihood with an efficient algorithm: **EM**.

**Estimating a GMM by EM** [slides 26-27]
- Input: the data and the number of classes (components) $K$. Parameters: means $\mu_j$, covariance matrices $\Sigma_j$, mixture weights $w_j$.
- All means and covariances must be initialized. **EM is an iterative procedure that is very sensitive to initial conditions**; K-means is often used to initialize the means (and "EM can be used for K-means" [slide 26], i.e. K-means is a special case [general]).
- Hidden variable: we cannot observe which distribution generated each instance (slide 26 figure: Old Faithful geyser waiting time vs eruption time with two Gaussian contours).

Initial: $w_j,\mu_j,\Sigma_j$. With $m$ data points $x_i$ and $K$ components [slide 27]:

**E-step** — responsibility of component $j$ for point $i$:

$$E[z_{ij}]=\frac{p(x=x_i\mid\mu=\mu_j,\Sigma=\Sigma_j)}{\sum_{n=1}^{K}p(x=x_i\mid\mu=\mu_n,\Sigma=\Sigma_n)}=\frac{w_j\,e^{-\frac12(x_i-\mu_j)^T\Sigma_j^{-1}(x_i-\mu_j)}}{\sum_{n=1}^{K}w_n\,e^{-\frac12(x_i-\mu_n)^T\Sigma_j^{-1}(x_i-\mu_n)}}$$

**M-step:**

$$w_j\leftarrow\frac1m\sum_{i=1}^{m}E[z_{ij}],\qquad \mu_j\leftarrow\frac{\sum_{i=1}^{m}E[z_{ij}]\,x_i}{\sum_{i=1}^{m}E[z_{ij}]},\qquad \Sigma_j\leftarrow\frac{\sum_{i=1}^{m}E[z_{ij}]\,(x_i-\mu_j)(x_i-\mu_j)^T}{\sum_{i=1}^{m}E[z_{ij}]}$$

Caveats on the slide's E-step [general]: the first expression has no $w_j$; the second drops the normalizing constants $(2\pi)^{d/2}\lvert\Sigma\rvert^{1/2}$ and uses $\Sigma_j^{-1}$ in the $n$-th term (probably a typo for $\Sigma_n^{-1}$). The complete form is

$$E[z_{ij}]=\frac{w_j\,N(x_i;\mu_j,\Sigma_j)}{\sum_{n=1}^{K}w_n\,N(x_i;\mu_n,\Sigma_n)}$$

and the slide's simplification is exact only when all components share the same $\Sigma$. [computed] 1-D check, $w=(0.5,0.5)$, $\mu=(0,4)$, $x=1$: with $\sigma^2=(1,1)$ the responsibilities are $0.982,\ 0.018$ (either form). With $\sigma^2=(1,4)$ the correct values are $0.789,\ 0.211$, while dropping the constants gives $0.651,\ 0.349$.

## 7. Method comparison [general]

| Method | Assignment | Needs $K$ | What it learns | Note |
|---|---|---|---|---|
| SOM | hard (BMU), neighbours move too | map size | weight vectors on a lattice | topology preserving, good for visualization |
| K-means | hard | yes | centroids | local optimum, spherical clusters |
| Fuzzy c-means | soft (membership) | yes | centres + memberships | needs fuzzifier $m>1$ |
| GMM + EM | soft (responsibility) | yes | $w_j,\mu_j,\Sigma_j$ | init-sensitive, many parameters in high dimension |

## 8. Slide issues noticed

- **Slide 22:** "$Y=X\cap Z$" (should be $\cup$). **Slide 27:** E-step formula simplified / likely typo (section 6).
- **SOM example (slides 11-17):** $\eta$, distance measure and decay schedule are not stated; recovered by computation (section 2.3). Last-digit rounding differences are noted above; no substantive error found.
- **Slide 9** says neighbours are "suppressed" while slide 18's equation pulls them toward $\mathbf x$ (section 2.4).
- **Slide 18** shows $L_0(t),\sigma_0(t)$ as functions of $t$; presumably constants.

## 9. Project relevance and practical notes

- **Possible use:** after Stage 1, vectorize each sentence with TF-IDF and run K-means (or GMM after dimensionality reduction) to group similar sentences; pick one representative per cluster to reduce redundancy in the extractive summary, or group daily reports by topic. [general]
- **Distance choice:** plain K-means uses Euclidean distance. For TF-IDF text use L2-normalized vectors, where Euclidean ordering matches cosine similarity (the Stage-2 similarity). Connects to the kNN distance discussion in [04](04-knn.md). [general]
- **GMM on text is a poor fit:** high-dimensional sparse vectors make covariance estimation unstable; slide 25 itself warns that full-rank GMMs have too many parameters. [general]
- **Choosing $K$ and initialization:** all slide methods need $K$ (or map size) up front and depend on initialization (slide 26); try several seeds, inspect clusters by hand since the dataset is small. [general]
- **Not covered by the slides** (do not attribute to the lecturer): hierarchical/agglomerative clustering, DBSCAN, cluster-quality measures (silhouette, elbow). Hierarchical clustering would avoid fixing $K$ in advance. [general]
- Clustering is **unsupervised** (slide 2), so it cannot replace the labelled Stage-1 classifier; it is an optional Stage-2 helper.
