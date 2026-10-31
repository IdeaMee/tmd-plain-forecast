# ML 05 — Artificial Neural Networks (ANN)

Source: `course/slides/05 Artificial Neural Networks.pptx` (56 slides, lecturer Parinya Sanguansat). Formulas, diagrams and tables read from slide images.
Legend: **[slide N]** = taken from the slide · **[computed]** = my own calculation of an example the slide leaves open · **[general]** = general knowledge or my inference, not said on the slides.

**Project relevance: MEDIUM (indirect, but foundational).** An MLP is an optional extra Stage-1 classifier next to Naive Bayes / SVM / kNN; more importantly this chapter (weighted sums, sigmoid, gradient descent, backpropagation, epochs, overfitting) is the base for the NLP half (RNN, seq2seq, Transformer). See section 10.

---

## 1. Key ideas

- ANN = network of simple units loosely inspired by the brain; learns real-valued, discrete-valued or vector-valued functions; works well on noisy, complex sensor data (cameras, microphones). Uses: visual scene interpretation, speech recognition, robot control. [slide 2]
- **Perceptron** = one threshold unit (linear classifier, hyperplane); **linear unit** = no threshold, trained by gradient descent; **sigmoid unit** = smooth differentiable threshold; **multilayer network + backpropagation** = gradient descent on the whole network. [slides 9, 29, 38, 40]
- Progression the deck follows (summary slide 56): Perceptron -> Gradient descent -> Multi-layer networks -> Backpropagation.

## 2. Biology, neuron model, history [slides 3-8]

- Real neuron parts: cell body, dendrites, axon, synaptic terminals. A spike (action potential) starts in the cell body, travels down the axon, and makes terminals release neurotransmitters, which cross the synapse to other neurons' dendrites. Neurotransmitters are excitatory or inhibitory; if the net input is excitatory and exceeds a threshold, the neuron fires. [slides 3-4]
- **Hebbian learning:** when two connected neurons fire at the same time, the synapse between them gets stronger ("neurons that fire together, wire together"); synapses change size/strength with experience. [slide 5]
- **Artificial neuron model** [slide 6]: network = graph, cells = nodes, synapses = weighted edges $w_{ji}$ from node $i$ to node $j$.

$$net_j=\sum_i w_{ji}\,o_i\qquad o_j=\begin{cases}0 & net_j<T_j\\ 1 & net_j\ge T_j\end{cases}$$

  $T_j$ = threshold of unit $j$; $o_i$ = output of the units feeding $j$. (Slide prints "$net_i$" in the second case; read it as $net_j$.) Threshold form (0/1 output) differs from the perceptron on slide 9 (+1/-1 output, threshold folded into bias $w_0=-T$ [general]).
- **History** [slide 7]: McCulloch & Pitts (1943) = first neural network (threshold + many simple units combined); 1950s-60s perceptron research; Minsky & Papert showed perceptrons were limited, research died down for ~15 years (slide says 1967; the book *Perceptrons* is usually dated 1969 [general]); mid-1980s revival with backpropagation (Rumelhart, Hinton, Williams); 1987 IEEE International Conference on Neural Networks.
- **Applications** [slide 8]: classification, clustering, recognition, prediction, adaptive filtering, function approximation.

## 3. Perceptron [slides 9-19]

### 3.1 Model [slide 9]
Inputs $x_1..x_n$, weights $w_1..w_n$, **bias** weight $w_0$ on a constant input 1, symmetric hard-limit (signum-like) transfer function:

$$o(x_1,\dots,x_n)=\begin{cases}1 & w_0+\sum_{i=1}^n w_i x_i>0\\-1 & \text{otherwise}\end{cases}\qquad
\text{hardlims}(x)=\begin{cases}1 & x>0\\-1&\text{otherwise}\end{cases}$$

Note the strict $>0$: net input exactly 0 gives $-1$ (matters in the XOR/AND tables below).

### 3.2 Geometry: hyperplane [slide 10]
- 2-D: a line, $y=mx+c$ or $ax+by+c=0$. n-D: a hyperplane.

$$w_1x_1+\dots+w_nx_n+b=0\iff\mathbf w^{T}\mathbf x+b=0$$

- $\mathbf w$ is normal to the hyperplane; sign of $\mathbf w^T\mathbf x+b$ gives the class. ($b$ here = $w_0$.) [general]

### 3.3 Perceptron learning rule [slide 11]
1. Initialise $w_i$ to small values or zero.
2. Until the termination condition is met: for each training example $\langle(x_1,\dots,x_n),t\rangle$ (target $t\in\{+1,-1\}$):
   - if $t\,\langle\mathbf w,\mathbf x\rangle\le 0$ (misclassified or on the boundary), then $\mathbf w\leftarrow\mathbf w+\eta\,t\,\mathbf x$.
3. Return $\mathbf w$.

- $\eta$ = learning rate. Update only on mistakes; the update adds $\eta\,t\,\mathbf x$ so the sample's score $t\langle\mathbf w,\mathbf x\rangle$ increases by $\eta\|\mathbf x\|^2$. [general]
- The slide indexes sloppily ("$t_i\langle w_i,x_i\rangle$"); standard reading is $\mathbf w$ = whole weight vector, $\mathbf x_i$ = i-th sample. The bias is handled by $x_0=1$ (slide 9 draws it; slide 11 does not mention it). [general]

### 3.4 Geometric walk-through [slides 12-16] (pictures only, no numbers)
Green points = class +1, red = class -1, drawn as vectors from the origin. My reading of the figures [general inference]:
- Step 0 -> 1: red points are multiplied by $t=-1$ (reflected through the origin), so every sample becomes $t\mathbf x$ and the goal is "find $\mathbf w$ with positive inner product with all $t\mathbf x$".
- Step 2: yellow arrows = current $\mathbf w$ and the circled, misclassified sample $t\mathbf x$ (negative inner product with $\mathbf w$).
- Step 3: blue arrow = vector sum $\mathbf w+\eta t\mathbf x$ (dashed parallelogram) = new weight vector.
- Step 4: final blue $\mathbf w$ and the decision line perpendicular to it; all points on the correct side.

### 3.5 AND, OR, XOR with a perceptron [slides 17-19]
Inputs coded $\pm1$; output +1 = green, -1 = red. Verified by recomputation [computed].

| Problem | $w_0$ (bias) | $w_1,w_2$ | Boundary | Rows $(x_1,x_2)$: net -> out |
|---|---|---|---|---|
| AND [17] | -0.5 | 0.5, 0.5 | $x_2=-x_1+1$ | (1,1): 0.5 -> 1; (1,-1): -0.5 -> -1; (-1,1): -0.5 -> -1; (-1,-1): -1.5 -> -1 |
| OR [18] | 0.5 | 0.5, 0.5 | $x_2=-x_1-1$ | (1,1): 1.5 -> 1; (1,-1): 0.5 -> 1; (-1,1): 0.5 -> 1; (-1,-1): -0.5 -> -1 |
| XOR [19] | ? | ?, ? | none | **A single perceptron cannot solve XOR** (slide's own caption) |

Why XOR fails: positives $(1,-1),(-1,1)$ and negatives $(1,1),(-1,-1)$ cannot be separated by one line (not linearly separable). [general explanation; slide 19 only shows the picture and the caption]

### 3.6 Worked trace: perceptron rule learns AND [computed; the slides show no trace]
Setup: $\pm1$ coding, $\eta=1$, $\mathbf w=(w_0,w_1,w_2)=(0,0,0)$, sample $\mathbf x=(1,x_1,x_2)$, order (1,1),(1,-1),(-1,1),(-1,-1), targets +1,-1,-1,-1.

| Epoch | Sample | $\langle\mathbf w,\mathbf x\rangle$ | Action | New $\mathbf w$ |
|---|---|---|---|---|
| 1 | (1,1), t=+1 | 0 | $\le0$ -> update | (1, 1, 1) |
| 1 | (1,-1), t=-1 | 1 | $t\cdot1\le0$ -> update | (0, 0, 2) |
| 1 | (-1,1), t=-1 | 2 | update | (-1, 1, 1) |
| 1 | (-1,-1), t=-1 | -3 | $t\cdot(-3)=3>0$ ok | (-1, 1, 1) |
| 2 | all four | 1, -1, -1, -3 | all correct | (-1, 1, 1) |

Result $(-1,1,1)$ = 2x the slide-17 weights $(-0.5,0.5,0.5)$: same boundary $x_2=-x_1+1$. Converged after epoch 2.

## 4. Multi-layer networks [slides 20-28]

- Add a **hidden layer** between input and output layers. Layers read as: input = features, hidden = "feature of feature", output = estimated target. [slides 20, 23]
- **Hidden unit representations** [slide 21]: trained hidden units can be seen as newly constructed features that make the target concept **linearly separable in the transformed space**. In real domains they can be meaningful (vowel detectors, edge detectors), but a hidden layer can also become a **distributed representation** where no single unit is easily interpretable.
- **8-input / 3-hidden / 8-output example** [slides 22, 24]: each of the 8 one-hot inputs (10000000, 01000000, ...) must be reproduced at the output. The 3 hidden units must squeeze the 8 patterns through a 3-unit bottleneck, so they learn a compact code [general interpretation]. Slide 22 shows trained hidden values, e.g. input 10000000 -> (.89, .04, .08), 01000000 -> (.01, .11, .88), 00010000 -> (.99, .97, .71), 00001000 -> (.03, .05, .02); rounded they give 8 distinct 3-bit codes (100, 001, 010, 111, 000, 011, 101, 110). Slide 24 shows a second table of rounded hidden codes (011, 001, 101, 000, 110, 111, 010, 100) and outputs ~1.00 on the diagonal (one entry 0.99); since the codes differ from slide 22, it is presumably another training run [general inference]. The task name "8-3-8 encoder" is [general]. The garbled numbers in the PDF text layer of slide 24 are not real content; I used the image.

### 4.1 XOR solved with two layers [slides 25-27]
Network (read from slide 25 image): hidden unit $H_1$: weights $x_1\to H_1=+1$, $x_2\to H_1=-1$; hidden unit $H_2$: $x_1\to H_2=-1$, $x_2\to H_2=+1$; both hidden biases 0 (none drawn); output unit: weights 1 and 1, bias 0.5; all units hardlims.

$$v_1=\text{hardlims}(x_1-x_2),\quad v_2=\text{hardlims}(-x_1+x_2),\quad o=\text{hardlims}(0.5+v_1+v_2)$$

| $(x_1,x_2)$ | hidden net | $(v_1,v_2)$ | output net | out |
|---|---|---|---|---|
| (1,1) | (0, 0) | (-1,-1) | -1.5 | -1 |
| (1,-1) | (2,-2) | (1,-1) | 0.5 | +1 |
| (-1,1) | (-2,2) | (-1,1) | 0.5 | +1 |
| (-1,-1) | (0, 0) | (-1,-1) | -1.5 | -1 |

[computed] Matches slides 26-27: in the $(v_1,v_2)$ plane the two red points collapse onto $(-1,-1)$ and the green points are $(-1,1)$ and $(1,-1)$, so one line separates them; layer 2 then reduces it to a 1-D separation (red at -1, green at +1). The table relies on hardlims(0) = -1.

### 4.2 Exercise 1 [slide 28] (answers [computed]; slide gives none)
Network read from the image: $H_1$: bias 0.2, weights $x_1$: +1, $x_2$: -1. $H_2$: bias 0.3, $x_1$: -1, $x_2$: +1. Output: bias 0.5, weights $H_1$: -1, $H_2$: +1. The slide shows step icons; I assume hardlims (+1/-1) as on slides 25-27.

$$h_1=\text{hardlims}(0.2+x_1-x_2),\ h_2=\text{hardlims}(0.3-x_1+x_2),\ o=\text{hardlims}(0.5-h_1+h_2)$$

| Point | $(x_1,x_2)$ | $net_{h1}$ | $net_{h2}$ | $(h_1,h_2)$ | $net_o$ | Output |
|---|---|---|---|---|---|---|
| A | (0.1, 1) | -0.7 | 1.2 | (-1, 1) | 2.5 | **+1** |
| B | (-0.5, 0.3) | -0.6 | 1.1 | (-1, 1) | 2.5 | **+1** |
| C | (0.4, -1) | 1.6 | -1.1 | (1, -1) | -1.5 | **-1** |
| D | (0.25, 0.25) | 0.2 | 0.3 | (1, 1) | 0.5 | **+1** |

Observation [computed]: output is -1 only when $h_1=+1,h_2=-1$, i.e. $x_1-x_2\ge0.3$; so this particular net behaves like one linear threshold. With 0/1 step units the outputs are 1,1,0,1 (same pattern).

## 5. Linear unit and gradient descent [slides 29-37]

### 5.1 Linear unit [slide 29]
Linear transfer function $lin(x)=ax+b$, output $o(x_1..x_n)=w_0+\sum_{i=1}^n w_i x_i=\mathbf w\cdot\mathbf x$ (with $x_0=1$). Unlike the perceptron it outputs a real number, and it is differentiable.

### 5.2 Gradient descent [slide 30]
- To find a **local minimum**, take steps proportional to the **negative** of the gradient at the current point: $\mathbf w\leftarrow\mathbf w-\eta\nabla e$.
- Other names: steepest descent; hill climbing on continuous space. **LMS** (Least Mean Square) = used when the gradient vector cannot be computed exactly (it is estimated with the MSE); also called **delta rule / Adaline rule / Widrow-Hoff rule**.

### 5.3 Error [slide 31]
Error = actual - estimated = target - output ($t_d-o_d$). Slide poses "Error of ???" and answers with:

$$e(\mathbf w)=\frac1N\sum_{d=1}^N(t_d-o_d)^2\ \approx\ \frac12\sum_{d\in D}(t_d-o_d)^2$$

The slide writes "$\approx$": the two forms differ only by a constant factor ($1/N$ vs $1/2$), which just rescales the gradient (absorbed into $\eta$). The deck uses $\frac12\sum$ from here on; the $\frac12$ cancels the 2 from differentiating the square. [general explanation]

### 5.4 Gradient of the error [slide 32]

$$\nabla e(\mathbf w)=\Big[\tfrac{\partial e}{\partial w_1},\dots,\tfrac{\partial e}{\partial w_n}\Big]$$

$$\frac{\partial e}{\partial w_i}=\frac{\partial}{\partial w_i}\frac12\sum_{d\in D}(t_d-o_d)^2
=\sum_{d\in D}(t_d-o_d)\frac{\partial(t_d-\mathbf x_d\cdot\mathbf w)}{\partial w_i}
=\sum_{d\in D}(t_d-o_d)(-x_{di})$$

Hence the **delta rule** (batch):

$$\Delta w_i=-\eta\frac{\partial e}{\partial w_i}=\eta\sum_{d\in D}(t_d-o_d)\,x_{di}\qquad w_i\leftarrow w_i+\Delta w_i$$

($t_d$ target, $o_d$ output, $x_{di}$ = i-th input of example $d$, $\eta$ learning rate.) The "$\eta(t-o)x_i$ ???" on slide 33 is the open question that this derivation answers; slide 33 boxes $\partial e/\partial w_i=\sum_d(t_d-o_d)(-x_{di})$ as the link.

### 5.5 Batch algorithm [slide 33] — Gradient-Descent(training_examples, $\eta$)
Each example is $\langle(x_1..x_n),t\rangle$; $\eta$ e.g. 0.1.
1. Initialise each $w_i$ to a small random value.
2. Until termination: set each $\Delta w_i=0$; for each example: feed $\mathbf x$ to the linear unit, compute $o$; for each weight $\Delta w_i\leftarrow\Delta w_i+\eta(t-o)x_i$.
3. After the pass over all examples: $w_i\leftarrow w_i+\Delta w_i$. Return the weights.

### 5.6 Batch vs incremental (stochastic) [slides 34-35]

| | Batch | Incremental / stochastic |
|---|---|---|
| Update | $\mathbf w\leftarrow\mathbf w-\eta\nabla e_D(\mathbf w)$ over entire $D$ | $\mathbf w\leftarrow\mathbf w-\eta\nabla e_d(\mathbf w)$ per example $d$ |
| Error | $e_D=\frac12\sum_d(t_d-o_d)^2$ | $e_d=\frac12(t_d-o_d)^2$ |
| Weight rule | $\Delta w_i$ accumulated, applied once per pass | $w_i\leftarrow w_i+\eta(t-o)x_i$ after each example |

- Incremental GD can approximate batch GD arbitrarily closely if $\eta$ is small enough. [slide 34]
- Slide 35 note: updating per sample "frequently update -> avoid local trap". [slide 35] (Slide 35's pseudo-code still lists "initialize each $\Delta w_i$ to zero", which the incremental version never uses — leftover from slide 33. [general observation])
- [general] For a single linear unit the squared-error surface is a convex bowl (one global minimum); local minima become a real issue only in multilayer nets (section 8).

### 5.7 Perceptron rule vs gradient descent rule [slide 36]
- Perceptron rule: guaranteed to succeed if the training examples are **linearly separable** and $\eta$ is sufficiently small. (For the classic perceptron with zero initial weights, convergence holds for any $\eta>0$ since $\eta$ only rescales $\mathbf w$ [general].)
- Linear unit with gradient descent: guaranteed to converge to the hypothesis with **minimum squared error**, given sufficiently small $\eta$, **even if the data are noisy or not separable** by the hypothesis space.

### 5.8 Epochs and presentation order [slide 37]
- One **epoch** = presenting all training examples once. Order in incremental SGD: fixed (1,2,...,M); random permutation (5,2,7,...,3); completely random with repeats (4,1,7,1,5,4,...).
- Slide also states "1 epoch of Perceptron = 1 training sample; 1 epoch of Gradient descent = all training samples". **This conflicts with the epoch definition one bullet above** (an epoch is a full pass). Probable meaning: the perceptron changes weights after each sample, batch GD changes weights once per full pass [general inference].

### 5.9 Worked delta-rule example [computed; not on slides]
Linear unit, $\mathbf w=(w_0,w_1,w_2)=(0.1,0.2,-0.1)$, $\eta=0.1$, examples $\mathbf x=(1,1,2),t=1$ and $\mathbf x=(1,2,0),t=0$.
- Batch: $o_1=0.1$, $o_2=0.5$ with the same $\mathbf w$; $\Delta\mathbf w=0.1[(0.9)(1,1,2)+(-0.5)(1,2,0)]=(0.04,-0.01,0.18)$ -> $\mathbf w=(0.14,0.19,0.08)$.
- Incremental: ex.1: $o=0.1$ -> $\mathbf w=(0.19,0.29,0.08)$; ex.2 uses the new $\mathbf w$: $o=0.77$ -> $\mathbf w=(0.113,0.136,0.08)$. Different from batch because the second error is computed after the first update.

## 6. Sigmoid unit [slides 38-39]

$$\sigma(x)=\frac1{1+e^{-x}},\qquad y(x_1..x_n)=\frac1{1+e^{-w_0-\sum_{i=1}^n w_ix_i}},\qquad \frac{\partial\sigma(x)}{\partial x}=\sigma(x)\big(1-\sigma(x)\big)$$

- **Why** [slide 39]: the signum function is discontinuous at zero (not differentiable); we need a nonlinear **differentiable** function similar to signum; and the derivative is easy to compute. Slide 38 plots a smooth S-curve through 0 on the $net_j$ axis; its output range is (0,1). [general]
- Derivative check [general]: $\sigma'(x)=\dfrac{e^{-x}}{(1+e^{-x})^2}=\sigma(x)\cdot\dfrac{e^{-x}}{1+e^{-x}}=\sigma(x)(1-\sigma(x))$; maximum $0.25$ at $x=0$ [computed, numerically checked].

## 7. Backpropagation [slides 40-46]

### 7.1 Setup and notation [slides 40-41]
Learn weights of a multilayer network by gradient descent on the error between output and target. With multiple output units the error becomes

$$e(\mathbf w)=\frac12\sum_{d\in D}\ \sum_{k\in outputs}(t_{kd}-o_{kd})^2$$

| Symbol | Meaning [slide 41] |
|---|---|
| $x_{ji}$ | i-th input to unit $j$ |
| $w_{ji}$ | weight of the i-th input to unit $j$ |
| $net_j=\sum_i w_{ji}x_{ji}$ | weighted sum of inputs of unit $j$ |
| $o_j$, $t_j$ | output computed by / target for unit $j$ |
| $\sigma$ | sigmoid |
| $outputs$ | set of units in the final layer |
| $Downstream(j)$ | units whose immediate inputs include the output of $j$ |
| $\delta_j=-\dfrac{\partial e_d}{\partial net_j}$ | **error term** of unit $j$ |

(The input $x_{ji}$ of unit $j$ coming from unit $i$ equals $o_i$.) [general]

### 7.2 Derivation [slide 42] — error on one example $e_d(\mathbf w)=\frac12\sum_{k\in outputs}(t_k-o_k)^2$
**Chain rule** (weight $w_{ji}$ affects the error only through $net_j$):

$$\frac{\partial e_d}{\partial w_{ji}}=\frac{\partial e_d}{\partial net_j}\frac{\partial net_j}{\partial w_{ji}}=\frac{\partial e_d}{\partial net_j}\,x_{ji}$$

**Case 1: $j$ is an output unit.** $\dfrac{\partial e_d}{\partial net_j}=\dfrac{\partial e_d}{\partial o_j}\dfrac{\partial o_j}{\partial net_j}$.
- Only the $k=j$ term depends on $o_j$: $\dfrac{\partial e_d}{\partial o_j}=-(t_j-o_j)$.
- Sigmoid: $\dfrac{\partial o_j}{\partial net_j}=o_j(1-o_j)$.
- So $\dfrac{\partial e_d}{\partial net_j}=-(t_j-o_j)\,o_j(1-o_j)$, i.e. $\delta_j=o_j(1-o_j)(t_j-o_j)$ and

$$\Delta w_{ji}=-\eta\frac{\partial e_d}{\partial w_{ji}}=\eta\,(t_j-o_j)\,o_j(1-o_j)\,x_{ji}=\eta\,\delta_j\,x_{ji}$$

**Case 2: $j$ is a hidden unit.** $net_j$ influences the error only through the units it feeds:

$$\frac{\partial e_d}{\partial net_j}=\sum_{k\in Downstream(j)}\frac{\partial e_d}{\partial net_k}\frac{\partial net_k}{\partial net_j}
=\sum_{k\in Downstream(j)}-\delta_k\,\frac{\partial net_k}{\partial o_j}\frac{\partial o_j}{\partial net_j}
=\sum_{k\in Downstream(j)}-\delta_k\,w_{kj}\,o_j(1-o_j)=-\delta_j$$

so $\delta_j=o_j(1-o_j)\sum_{k\in Downstream(j)}\delta_k w_{kj}$ and again $\Delta w_{ji}=\eta\,\delta_j\,x_{ji}$.
(Uses $\partial net_k/\partial o_j=w_{kj}$ and the sigmoid derivative. Slide 42's last steps are consistent with this.)

### 7.3 Algorithm [slide 43] — Backpropagation(training_example, $\eta$, $n_{in}$, $n_{out}$, $n_{hidden}$)
1. Create a feed-forward network with $n_{in}$ inputs, $n_{hidden}$ hidden units, $n_{out}$ outputs.
2. Initialise all weights to small random numbers, e.g. in $[-0.5,0.5]$.
3. Until the termination condition is met, for each $\langle(x_1..x_n),t\rangle$:
   - **Forward:** feed the instance in and compute the output $o_u$ of every unit.
   - **Backward:** for each output unit $k$: $\delta_k=o_k(1-o_k)(t_k-o_k)$; for each hidden unit $h$: $\delta_h=o_h(1-o_h)\sum_{k\in outputs}w_{kh}\delta_k$.
   - **Update every weight:** $w_{ji}\leftarrow w_{ji}+\eta\,\delta_j\,x_{ji}$.
4. Return the weights.

Notes: (a) the hidden formula on slides 43-46 sums over $k\in outputs$, which is correct for one hidden layer; for deeper nets use $Downstream(h)$ as derived on slide 42. [general] (b) The algorithm updates after every example (stochastic/incremental mode). (c) Bias weights are not mentioned on slides 40-46; treat them as weights on a constant input 1. [general]

### 7.4 Step-by-step pictures [slides 44-46]
1. Compute output-unit errors $\delta_k$, update the top-layer weights: $w_{kh}\leftarrow w_{kh}+\eta\delta_kx_{kh}$.
2. Compute hidden errors from the output errors they feed into: $\delta_h=o_h(1-o_h)\sum_k\delta_kw_{kh}$.
3. Update the bottom-layer weights: $w_{hi}\leftarrow w_{hi}+\eta\delta_hx_{hi}$.

**Slide 44 number:** $o_k=0.2,\ t_k=1.0$: $\delta_k=0.2(1-0.2)(1-0.2)=0.128$. [computed check: 0.2 x 0.8 x 0.8 = 0.128, correct]

### 7.5 Full worked example [computed; slides give only the 0.128 step]
Net 2-2-1, all sigmoid, biases as weights on constant input 1, $\eta=0.5$, input $\mathbf x=(1,0)$, target $t=1$.
Weights as $[\text{bias},x_1,x_2]$: $H_1=[0.1,0.4,-0.3]$, $H_2=[-0.2,0.2,0.5]$; output $=[0.3,\,0.6\ (\text{from }H_1),\,-0.4\ (\text{from }H_2)]$.

| Step | Calculation | Value |
|---|---|---|
| Forward $H_1$ | $net=0.1+0.4\cdot1$ ; $\sigma(0.5)$ | $o_{h1}=0.6225$ |
| Forward $H_2$ | $net=-0.2+0.2\cdot1=0$ ; $\sigma(0)$ | $o_{h2}=0.5$ |
| Forward out | $net=0.3+0.6(0.6225)-0.4(0.5)=0.4735$ ; $\sigma$ | $o=0.6162$ |
| Error | $\frac12(1-0.6162)^2$ | $e=0.0736$ |
| $\delta_k$ | $0.6162(1-0.6162)(1-0.6162)$ | $0.09077$ |
| $\delta_{h1}$ | $0.6225(0.3775)(0.6\cdot0.09077)$ | $0.01280$ |
| $\delta_{h2}$ | $0.5(0.5)(-0.4\cdot0.09077)$ | $-0.00908$ |
| Output weights | $+\eta\delta_k\cdot(1,\,0.6225,\,0.5)$ | $(0.3454,\ 0.6282,\ -0.3773)$ |
| $H_1$ weights | $+\eta\delta_{h1}\cdot(1,1,0)$ | $(0.1064,\ 0.4064,\ -0.3)$ |
| $H_2$ weights | $+\eta\delta_{h2}\cdot(1,1,0)$ | $(-0.2045,\ 0.1955,\ 0.5)$ |
| After update | forward again | $o=0.6343$, $e=0.0669$ (error decreased) |

$x_2$-weights do not change because $x_2=0$ (update is proportional to $x_{ji}$). I checked every gradient $-\partial e/\partial w=\delta\,x$ against finite differences (max error ~1e-11).

## 8. Practical issues [slides 47-52]

- **Convergence** [slide 47]: not guaranteed to reach zero training error; may reach a local optimum or oscillate indefinitely. Remedies: **random restarts** (several trials with different random weights; keep the trial with lowest training error; or build a **committee** of the trials, possibly weighting votes by training accuracy). In practice it does reach low error on many large real-data networks. Many epochs (thousands) may be needed; hours or days for large networks.
- **Local optima** [slide 48]: gradient descent can be trapped in a local minimum instead of the global one; plot with a global and a local minimum.
- **Momentum** [slide 49]: add a fraction of the previous update to escape local optima:

$$w_{ji}(n+1)=w_{ji}(n)+\Delta w_{ji}(n),\qquad \Delta w_{ji}(n)=\eta\,\delta_j\,x_{ji}+\alpha\,\Delta w_{ji}(n-1)$$

  Slide ranges: $\eta\in[0,\infty)$, momentum constant $\alpha\in[0,1]$. (Without momentum, slide 48: $\Delta w_{ji}(n)=\eta\delta_jx_{ji}$.)
- **Representational power** [slide 50]: any Boolean function by a two-layer network with enough hidden units; any bounded continuous function approximated to arbitrary error by a two-layer network (sigmoids act as basis functions, like sine waves in Fourier analysis); any function approximated to arbitrary accuracy by a network with two hidden layers. "Two-layer" presumably means one hidden layer plus the output layer [general].
- **Overfitting** [slide 51]: too many epochs overfit (training error keeps falling, test error turns upward). Keep a hold-out validation set, check it every epoch, stop when more epochs increase validation error (**early stopping**). To avoid giving up training data: internal 10-fold CV on the training set to find the average best number of epochs, then train the final net on the full training set for that many epochs.
- **Number of hidden units** [slide 52]: too few -> cannot fit the data; too many -> overfit; choose by internal cross-validation.

## 9. Application slides [slides 53-56]

- **XOR by feed-forward backpropagation** [slide 53]: a 3-D surface plot of the trained network output over $(x_1,x_2)\in[0,1]^2$ (no formulas/numbers on the slide; individual values not legible).
- **ALVINN** [slide 54]: steers a vehicle on a highway at 90 mile/hour. Figure labels: 30x32 sensor input retina -> 4 hidden units -> 30 output units (sharp left ... straight ahead ... sharp right); the grey-dot images on the right look like learned weights (not explained on the slide).
- **Face pose recognition** [slide 55]: learns the pose of a human face, 90% accuracy. Figure: 30x32 inputs, outputs left / straight / right / up, learned-weight images, typical input images.
- **Summary** [slide 56]: Perceptron; Gradient descent; Multi-layer networks; Backpropagation.

## 10. Slide inconsistencies / ambiguities (so nothing is silently "fixed")

| Slide | Issue | How I handled it |
|---|---|---|
| 6 vs 9 | Threshold unit outputs 0/1 with $net\ge T$; perceptron outputs +/-1 with $>0$. Slide 6 prints $net_i$ for $net_j$. | Kept both forms, noted $w_0=-T$ [general]. |
| 7 | "Rumehart" typo; 1967 for Minsky & Papert (usually 1969). | Reported as written, flagged. |
| 11 | Indexing $t_i\langle w_i,x_i\rangle$ sloppy; bias not mentioned. | Standard reading, flagged. |
| 24 | Hidden codes differ from slide 22; PDF text layer garbled. | Used image; likely a different run [general]. |
| 28 | Exercise has no answers; activation icon not labelled. | Assumed hardlims; gave 0/1 variant. |
| 31 | "$\frac1N\sum\approx\frac12\sum$" | Explained as constant factor. |
| 33 | "$\Delta w_i=\Delta w_i+\eta(t-o)x_i$ ???" | Derived on slide 32; sign: $-\eta\,\partial e/\partial w_i$. |
| 35 | $\Delta w_i$ initialisation unused in incremental version. | Flagged. |
| 37 | "1 epoch of Perceptron = 1 training sample" contradicts the epoch definition. | Probable meaning given; flagged. |
| 43, 45, 46 | Hidden $\delta_h$ sums over $k\in outputs$ (one hidden layer only). | General form via $Downstream$ (slide 42). |

## 11. Project relevance and practical notes

- **Stage 1 (sentence classification):** a small MLP on bag-of-words / TF-IDF sentence vectors is a possible extra classifier beside Naive Bayes ([08](08-bayesian-learning.md)), SVM ([09](09-svm.md)) and kNN ([04](04-knn.md)). [general] A perceptron is a *linear* classifier (hyperplane, section 3.2), conceptually close to a linear SVM; XOR-type interactions between words need hidden units. [general]
- **Small data warning:** with a small labelled Thai-weather set an MLP overfits easily. Use a validation set with early stopping, few hidden units, random restarts (slides 47, 51, 52); compare against Naive Bayes as the cheap baseline. [general advice built on those slides]
- **Binary output:** one sigmoid output, class = (output > 0.5). [general] The slides only use squared error with sigmoid outputs; modern practice usually pairs sigmoid/softmax with cross-entropy, not covered here. [general]
- **Link to the NLP half (RNN, seq2seq, Transformer)** [general, not on slides]:
  - Each layer = weighted sum + nonlinearity; training = gradient descent with the chain rule (backprop). RNNs apply the same chain rule through time steps.
  - $\sigma'(x)\le0.25$ [computed], so $\delta_h$ gets multiplied by factors $\le0.25$ per sigmoid layer: gradients shrink in deep or long-unrolled nets (vanishing gradient), the motivation for LSTM/ReLU later.
  - Hidden layer = learned features ("feature of feature", slide 21); this is the idea behind learned word embeddings.
  - Learning rate, epochs, SGD, momentum (slide 49) carry over to modern optimisers; epoch/validation/early stopping logic is identical.
- **Calculation patterns on these slides** (for checking by hand): perceptron update $\mathbf w+\eta t\mathbf x$ (3.3, 3.6); AND/OR/XOR unit tables (3.5, 4.1); Exercise 1 (4.2); delta rule (5.4, 5.9); $\delta_k$ and $\delta_h$ (7.3-7.5).
