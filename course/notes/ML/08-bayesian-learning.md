# ML 08 — Bayesian Learning

Source: `course/slides/08 Bayesian Learning.pptx` (37 slides, lecturer Parinya Sanguansat). Formulas read from slide images.
Legend: **[slide N]** = taken from the slide · **[computed]** = my own calculation of an example the slide leaves open · **[general]** = general knowledge, not on the slides.

**Project relevance: HIGH.** Naive Bayes text categorization (slides 27-29) is the planned Stage-1 classifier (public-relevant vs. technical sentence, as in PLAN.md).

---

## 1. Key ideas

- Bayesian learning = probabilistic inference: quantities of interest follow probability distributions; best decisions come from reasoning with those probabilities plus observed data. [slide 2]
- Learning = choosing the most probable hypothesis `h` given data `D`.
- **Naive Bayes** makes this practical when there are many attributes, by assuming attributes are conditionally independent given the class. Works "surprisingly well even if the assumption is violated". [slide 23]
- Bayesian Belief Networks relax the naive assumption (only some variables dependent). [slide 30]

## 2. Probability basics [slides 3-5]

| Rule | Formula |
|---|---|
| Range | $0 \le P(A) \le 1$; $P(\text{true})=1$, $P(\text{false})=0$ |
| Union (disjunction) | $P(A \lor B) = P(A) + P(B) - P(A \land B)$ |
| Conditional | $P(A\mid B) = \dfrac{P(A \land B)}{P(B)}$ (B is "all and only information known") |
| Independence | $A,B$ independent iff $P(A\mid B)=P(A)$ and $P(B\mid A)=P(B)$; then $P(A \land B)=P(A)P(B)$ |

Terms: $P(A\land B)$ = joint (conjunction); $P(A)$, $P(B)$ = marginal.

### Practice problems on slides 7-8 (answers [computed])
- Two cards without replacement, both aces: $\frac{4}{52}\cdot\frac{3}{51}=\frac{1}{221}\approx 0.0045$.
- Three cards **with** replacement, all aces: $(\frac{1}{13})^3=\frac{1}{2197}$.
- Second card ace given first is a king: $\frac{4}{51}$ (a king removed, 51 cards left, 4 aces).
- Design survey (slide 8): the two tables (like / dislike) together sum to 1.00 (like 0.25, dislike 0.75), so entries are joint probabilities over (colour, shape, opinion).
  - $P(\text{red}\land\text{circle}) = 0.20+0.05 = 0.25$
  - $P(\text{red}) = 0.20+0.02+0.05+0.30 = 0.57$
  - $P(\text{like}\mid\text{red}\land\text{circle}) = 0.20/0.25 = 0.80$

## 3. Bayes theorem [slide 9]

$$P(h\mid D)=\frac{P(D\mid h)\,P(h)}{P(D)}$$

| Name | Symbol | Meaning |
|---|---|---|
| Evidence | $P(D)$ | prior probability of the training data |
| Prior | $P(h)$ | prior probability of hypothesis $h$ |
| Posterior | $P(h\mid D)$ | probability of $h$ after seeing $D$ |
| Likelihood | $P(D\mid h)$ | probability of the data given $h$ |

## 4. Choosing a hypothesis [slide 10]

**MAP** (maximum a posteriori) — $P(D)$ is constant in $h$, so drop it:

$$h_{MAP}=\arg\max_{h\in H}P(h\mid D)=\arg\max_{h\in H}P(D\mid h)P(h)$$

**ML** (maximum likelihood) — if all priors are equal, $P(h_i)=P(h_j)$:

$$h_{ML}=\arg\max_{h\in H}P(D\mid h)$$

**Brute-force MAP learning** [slide 13]: for every $h\in H$ compute $P(h\mid D)=\frac{P(D\mid h)P(h)}{P(D)}$, output the $h$ with the highest posterior. Posterior mass concentrates on fewer hypotheses as more data arrives [slide 14].

### Worked example: medical diagnosis [slide 12; answer computed]
Given: $P(\text{cancer})=0.008$; test correct-positive 98% so $P(+\mid\text{cancer})=0.98$; correct-negative 97% so $P(+\mid\lnot\text{cancer})=0.03$. Patient tests positive.

- $P(+\mid c)P(c)=0.98\times0.008=0.00784$
- $P(+\mid\lnot c)P(\lnot c)=0.03\times0.992=0.02976$
- $P(c\mid +)=\dfrac{0.00784}{0.00784+0.02976}\approx 0.2085$ (about 21%, despite an accurate test, because the prior is tiny)

## 5. Learning a real-valued function (least squares = ML) [slides 15-16]

Noisy examples $\langle x_i,d_i\rangle$ with $d_i=f(x_i)+e_i$, $e_i\sim$ Gaussian with zero mean. Probabilities cannot be estimated by counting for real values.

$$h_{ML}=\arg\max_h\prod_i\frac{1}{\sqrt{2\pi\sigma^2}}e^{-\frac{(d_i-h(x_i))^2}{2\sigma^2}}
=\arg\min_h\sum_i\,(d_i-h(x_i))^2$$

Take $\ln$, drop constants, flip max to min: **maximum likelihood under Gaussian noise = minimize sum of squared errors.**

## 6. Most probable classification vs. MAP [slides 17-19]

$h_{MAP}$ is not necessarily the most probable *classification*. Example: $P(h_1\mid D)=0.4,\ P(h_2\mid D)=0.3,\ P(h_3\mid D)=0.3$; $h_1(x)=+$, $h_2(x)=-$, $h_3(x)=-$.
- $h_{MAP}(x)=+$ but $P(+)=0.4$, $P(-)=0.3+0.3=0.6$, so the most probable class is $-$.

**Bayes optimal classifier** — combine all hypotheses weighted by posterior:

$$v_{max}=\arg\max_{v_j\in V}\sum_{h_i\in H}P(v_j\mid h_i)\,P(h_i\mid D)$$

Slide 18 applies it to the example above (with $P(+\mid h_1)=1$, $P(-\mid h_2)=P(-\mid h_3)=1$, others 0): $\sum P(+\mid h_i)P(h_i\mid D)=0.4$ and $\sum P(-\mid h_i)P(h_i\mid D)=0.6$, so the Bayes optimal classifier outputs $-$.

| Method | Estimates | Note |
|---|---|---|
| MAP / ML | one hypothesis in $H$ | cheaper [general] |
| Bayes optimal | the full distribution $P(h\mid D)$ | can predict with a hypothesis not in $H$ |

## 7. Practical Bayesian learning → Naive Bayes [slides 20-24]

Setting: only training data and targets (no hypotheses), small training set, more than one attribute. Goal: assign the most probable target value to a new instance $\langle a_1,\dots,a_n\rangle$.

$$v_{MAP}=\arg\max_{v_j\in V}P(a_1,\dots,a_n\mid v_j)\,P(v_j)$$

**The problem** [slide 21]: the joint $P(a_1,\dots,a_n\mid v_j)$ needs $m^n\cdot t$ probabilities ($n$ attributes, $m$ values each, $t$ targets). Example $n=4,\ m=100,\ t=10$: about 1,000,000,000 probabilities and at least 100,000,000 training samples.

**Naive Bayes assumption** [slide 22] — attributes are conditionally independent given the target:

$$P(a_1,\dots,a_n\mid v_j)=\prod_i P(a_i\mid v_j)\qquad
v_{NB}=\arg\max_{v_j\in V}P(v_j)\prod_i P(a_i\mid v_j)$$

Now only about 4,000 probabilities for the same example. Typical uses: diagnosis, text classification. Needs a moderate or large training set. [slide 23]

### Naive Bayes learning algorithm [slide 24]
1. **Learn:** for each target value $v_j$ estimate $P(v_j)$; for each attribute value $a_i$ estimate $P(a_i\mid v_j)$. Discrete: count examples. Continuous: use a pdf (e.g. Gaussian [general]).
2. **Classify:** $v_{NB}=\arg\max_{v_j}P(v_j)\prod_iP(a_i\mid v_j)$.

### Worked example: PlayTennis [slides 11, 25; numbers computed]
Query: ⟨Outlook=Sunny, Temp=Cool, Humidity=High, Wind=Strong⟩, 14 training days (9 Yes, 5 No).

| | $P(v)$ | Sunny | Cool | High | Strong | Score = product |
|---|---|---|---|---|---|---|
| Yes | 9/14 | 2/9 | 3/9 | 3/9 | 3/9 | 1/189 ≈ 0.00529 |
| No | 5/14 | 3/5 | 1/5 | 4/5 | 3/5 | 18/875 ≈ 0.02057 |

Result: **No** (normalized: $P(\text{No})\approx0.795$, $P(\text{Yes})\approx0.205$).
Side question on slide 11 ("chance to play tennis on a sunny day?"): $P(\text{Yes}\mid\text{Sunny})=2/5$ by counting the 5 sunny days (2 Yes). [computed]

### m-estimate of probability [slide 26]
Problem: if $n_c=0$ then $P(a_i\mid v_j)=\frac{n_c}{n}=0$ and the whole product becomes 0. Fix:

$$P(a_i\mid v_j)=\frac{n_c+mp}{n+m}$$

- $n$: training examples with $v=v_j$; $n_c$: those that also have $a=a_i$
- $p$: prior estimate of $P(a_i\mid v_j)$; $m$: weight of the prior (number of "virtual" examples)

### Naive Bayes for text categorization [slides 27-29]
- Instance = a document · Attribute = (index of) each word and its frequency · Target = topic, e.g. {Sport, Politic, Entertainment, …}

**Learn_naive_Bayes_text(Examples, V)**
1. Vocabulary ← all distinct words in Examples
2. For each target $v_j\in V$:
   - $P(v_j)\leftarrow |docs_j|/|Examples|$
   - $text_j\leftarrow$ concatenation of all docs of class $v_j$; $n\leftarrow$ total number of words in $text_j$
   - for each word $w_k$ in Vocabulary: $n_k\leftarrow$ count of $w_k$ in $text_j$, and

$$P(w_k\mid v_j)\leftarrow\frac{n_k+1}{n+|Vocabulary|}$$

**Classify_naive_Bayes_text(Doc)**: Positions ← word positions in Doc whose tokens are in Vocabulary;

$$v_{NB}=\arg\max_{v_j\in V}P(v_j)\prod_{k\in positions}P(w_k\mid v_j)$$

Note: the "+1 / +|Vocabulary|" form is the m-estimate with $p=1/|Vocabulary|$ and $m=|Vocabulary|$ (add-one / Laplace smoothing). [general observation]

## 8. Bayesian belief networks (BBN) [slides 30-37]

- Naive Bayes: all variables conditionally independent. BBN: only some are → less restrictive, still tractable, can combine causal prior knowledge with data.
- **Conditional independence:** $X$ is cond. independent of $Y$ given $Z$ iff $P(X\mid Y,Z)=P(X\mid Z)$. Naive Bayes relies on it: $P(X,Y\mid Z)=P(X\mid Z)P(Y\mid Z)$ [slide 31].
- Network = DAG; each node is cond. independent of its non-descendants given its parents. Joint distribution:

$$P(y_1,\dots,y_n)=\prod_{i=1}^{n}P\big(y_i\mid Parents(Y_i)\big)$$

  Slide 32 example (Storm, BusTourGroup, Lightning, Campfire, Thunder, ForestFire): $P(S,B,L,C,T,F)=P(S)P(B)P(L\mid S)P(C\mid S,B)P(T\mid L)P(F\mid L,S,C)$. Campfire CPT: $P(C\mid S,B),\,P(C\mid S,\lnot B),\,P(C\mid\lnot S,B),\,P(C\mid\lnot S,\lnot B)=0.4,\,0.1,\,0.8,\,0.2$.
- **Inference:** easy if all needed variables are observed; general case is NP-hard; exact methods work for some structures; Monte Carlo simulation gives approximate answers [slide 33].
- **Learning** (known structure, partly observable variables): learn CPTs by **gradient ascent** to (locally) maximize $P(D\mid h)$, similar to training a neural net with hidden units [slides 34-37]. With $w_{ijk}=P_h(y_{ij}\mid u_{ik})$:

$$w_{ijk}\leftarrow w_{ijk}+\eta\sum_{d\in D}\frac{P_h(y_{ij},u_{ik}\mid d)}{w_{ijk}}\quad\text{then renormalize so }\sum_j w_{ijk}=1$$

(Slide 36 shows the long derivation of $\partial\ln P(D\mid h)/\partial w_{ijk}$; not reproduced here.)

## 9. Project relevance and practical notes

- **Stage-1 classifier:** sentence = "document", classes = {public-relevant, technical}; use Section 7 text algorithm with Thai-segmented tokens (NLP 1-2, 2-1).
- Always use the smoothed estimate (m-estimate / add-one); otherwise unseen words zero out the product.
- [general, not on slides] Multiplying many small probabilities underflows; compute with sums of logs: $\log P(v_j)+\sum_k\log P(w_k\mid v_j)$. Same $\arg\max$.
- Compare with SVM ([09](09-svm.md)) and kNN ([04](04-knn.md)) as alternative classifiers.
