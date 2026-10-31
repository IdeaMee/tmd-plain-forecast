# ML 02 — Concept Learning

Source: `course/slides/02 Concept Learning.pptx` (33 slides, lecturer Parinya Sanguansat). All 33 slides were read as images; hypotheses and traces were checked by exhaustive enumeration in Python.
Legend: **[slide N]** = taken from the slide · **[computed]** = my own calculation of an example the slide leaves open · **[general]** = general knowledge or my inference, not on the slides.

**Project relevance: LOW (background).** Gives the vocabulary (hypothesis space, consistent hypothesis, version space, inductive bias) behind the Stage-1 classifiers, but Find-S / Candidate Elimination need noise-free data and are not planned for the project.

---

## 1. Key ideas

- **Concept learning** = infer the general definition of a concept from examples labelled as members / non-members. The concept is usually a **boolean-valued function**, e.g. the category "car" or "bird". [slide 2]
- It can be viewed as **searching a hypothesis space**. [slide 2]
- Formally: infer a boolean-valued function from training pairs $\langle x,f(x)\rangle$; **binary problem only, supervised**; goal = a good approximation to the unknown $f$. [slide 3]

## 2. The EnjoySport task [slides 4-6]

Concept: days on which friend Aldo enjoys his favourite water sports. Task: predict EnjoySport for an arbitrary day from the other attributes.

| | Sky | Temp | Humid | Wind | Water | Forecast | EnjoySport |
|---|---|---|---|---|---|---|---|
| x1 | Sunny | Warm | Normal | Strong | Warm | Same | Yes |
| x2 | Sunny | Warm | High | Strong | Warm | Same | Yes |
| x3 | Rainy | Cold | High | Strong | Warm | Change | No |
| x4 | Sunny | Warm | High | Strong | Cool | Change | Yes |

(One row = one **instance**; the first six columns are the **attributes**.)

**Hypothesis representation** [slide 5]: a hypothesis $h$ is a **conjunction of constraints** on the attributes, one constraint per attribute:
- a specific value, e.g. `Water=Warm`
- `?` = don't care (any value)
- `Ø` = no value allowed (null hypothesis)

Example: `<Sunny, ?, ?, Strong, ?, Same>` = "Sky is Sunny AND Wind is Strong AND Forecast is Same".

**Prototypical learning task** [slide 6]
- Given: instance space $X$ (days described by the 6 attributes); target function $c: X\to\{0,1\}$ (EnjoySport); hypothesis space $H$ (conjunctions of literals); training examples $D=\{\langle x_1,c(x_1)\rangle,\dots,\langle x_n,c(x_n)\rangle\}$.
- Determine: $h\in H$ such that $h(x)=c(x)$ for all $x\in D$.

**Inductive learning hypothesis** [slide 7]: any hypothesis that approximates the target function well over the training examples will also approximate it well over unobserved examples. Learning = find the hypothesis that best fits the training data.

## 3. Counting instances, concepts and hypotheses [slide 8]

Attribute domains on the slide: Sky ∈ {Sunny, Cloudy, Rainy}; AirTemp ∈ {Warm, Cold}; Humidity ∈ {Normal, High}; Wind ∈ {Strong, Weak}; Water ∈ {Warm, Cold}; Forecast ∈ {Same, Change}.

| Quantity | Formula (slide) | Value |
|---|---|---|
| Distinct instances $\lvert X\rvert$ | $3\cdot2\cdot2\cdot2\cdot2\cdot2$ | 96 |
| Distinct concepts (all subsets of $X$) | $2^{96}$ | $\approx 7.9\times10^{28}$ [computed] |
| Syntactically distinct hypotheses (values plus `?` and `Ø`) | $5\cdot4\cdot4\cdot4\cdot4\cdot4$ | 5120 |
| Semantically distinct hypotheses | $1+4\cdot3\cdot3\cdot3\cdot3\cdot3$ | 973 |

Why 973: any hypothesis containing at least one `Ø` classifies every instance as negative, so all of them collapse into **one** semantic hypothesis (the "1"); otherwise each attribute is a value or `?` (Sky 3+1 = 4 choices, the other five 2+1 = 3 choices). [slide 8 + my reading]

The conjunctive $H$ can express only 973 of the $2^{96}$ possible concepts, which is why it is "biased" (section 9).

## 4. General-to-specific ordering [slides 9-10]

Example: $h_1=\langle Sunny,?,?,Strong,?,?\rangle$, $h_2=\langle Sunny,?,?,?,?,?\rangle$. $h_2$ imposes fewer constraints, so it classifies more instances as positive: **$h_2$ is more general**.

**Definition** [slide 9]: for boolean-valued $h_j,h_k$ over $X$,

$$h_j\ \ge\ h_k\iff \forall x\in X:\ \big[h_k(x)=1\ \rightarrow\ h_j(x)=1\big]$$

"$h_j$ is more general than or equal to $h_k$". The relation $\ge$ is a **partial order** on $H$ (some pairs are incomparable) and is used by many concept-learning methods.

**Figure, slide 10.** Left: instances in $X$ with the sets covered by $h_1,h_2,h_3$. Right: the hypotheses arranged from **specific (top) to general (bottom)** with $h_2\ge h_1$ and $h_2\ge h_3$.
- $x_1=\langle Sunny,Warm,High,Strong,Cool,Same\rangle$, $x_2=\langle Sunny,Warm,High,Light,Warm,Same\rangle$; $h_1=\langle Sunny,?,?,Strong,?,?\rangle$, $h_2=\langle Sunny,?,?,?,?,?\rangle$, $h_3=\langle Sunny,?,?,?,Warm,?\rangle$.
- [computed] $x_1$ is covered by $h_1,h_2$ (not $h_3$, Water=Cool); $x_2$ is covered by $h_2,h_3$ (not $h_1$, Wind=Light). $h_1$ and $h_3$ are **incomparable**. With the 96-instance space: $h_1$ covers 16 instances, $h_3$ 16, $h_2$ 32.

## 5. Find-S [slides 11-14]

Idea: start from the **most specific** hypothesis and generalize it only when it fails to cover a **positive** example. [slide 11]

1. Initialize $h$ to the most specific hypothesis in $H$ (all `Ø`).
2. For each **positive** training instance $x$:
   - for each attribute constraint $a_i$ in $h$: if $x$ satisfies it, do nothing; else replace $a_i$ by the next more general constraint that $x$ satisfies (`Ø` → the value → `?`).
3. Output $h$.

**Trace on EnjoySport** [slide 12; re-checked by code]

| Step | Example | Hypothesis after |
|---|---|---|
| $h_0$ | | `<Ø,Ø,Ø,Ø,Ø,Ø>` |
| $x_1$ + | Sunny,Warm,Normal,Strong,Warm,Same | $h_1$ = `<Sunny,Warm,Normal,Strong,Warm,Same>` |
| $x_2$ + | Sunny,Warm,High,Strong,Warm,Same | $h_2$ = `<Sunny,Warm,?,Strong,Warm,Same>` (Humidity Normal≠High → `?`) |
| $x_3$ − | Rainy,Cold,High,Strong,Warm,Change | **ignored** (negative): $h_3=h_2$ |
| $x_4$ + | Sunny,Warm,High,Strong,Cool,Change | $h_4$ = `<Sunny,Warm,?,Strong,?,?>` (Water, Forecast → `?`) |

**Properties** [slide 13]: $H$ = conjunctions of attributes; Find-S outputs the **most specific** hypothesis in $H$ consistent with the positive examples; the output is also consistent with the negatives **provided the target concept is in $H$**.

**Complaints** [slide 14] (the slide gives a short answer to each):
- Cannot tell whether it has converged to the target concept, i.e. whether it found the *only* consistent hypothesis. (More examples → better approximation.)
- Cannot detect inconsistent training data because it ignores negatives. (Prefer to detect and tolerate errors or noise.)
- Why the most specific rather than the most general or another one? ("More specific is less likely to be a coincidence.")
- What if there are several maximally specific hypotheses? ("All are equally likely.")

## 6. Version spaces [slides 15-20]

**Consistency** [slide 15]: $h$ is consistent with a set of training examples $D$ of target concept $c$ iff $h(x)=c(x)$ for every $\langle x,c(x)\rangle\in D$:

$$\text{Consistent}(h,D):=\forall\langle x,c(x)\rangle\in D:\ h(x)=c(x)$$

**Version space** $VS_{H,D}$ = the subset of $H$ consistent with all training examples:

$$VS_{H,D}=\{\,h\in H\mid \text{Consistent}(h,D)\,\}$$

Figure [slide 16]: a lattice from "too specific" (top) to "too general" (bottom); the version space is the band in between.

**List-Then-Eliminate** [slide 17]
1. VersionSpace ← list containing every hypothesis in $H$.
2. For each training example $\langle x,c(x)\rangle$, remove every $h$ with $h(x)\ne c(x)$.
3. Output the remaining list.
(Needs to enumerate all of $H$ — impractical for large $H$. [general])

**Representing the version space** [slide 19]
- General boundary $G$ = set of **maximally general** members of $VS$; specific boundary $S$ = set of **maximally specific** members.
- Every member lies between the boundaries:

$$VS_{H,D}=\{\,h\in H\mid(\exists s\in S)(\exists g\in G)\ (g\ge h\ge s)\,\}$$

**Example version space** [slide 18] (training data $x_1..x_4$ above). The six hypotheses (checked by enumeration over all 973: exactly 6 are consistent) [computed]:

```
S :  <Sunny,Warm,?,Strong,?,?>
     <Sunny,?,?,Strong,?,?>   <Sunny,Warm,?,?,?,?>   <?,Warm,?,Strong,?,?>
G :  <Sunny,?,?,?,?,?>        <?,Warm,?,?,?,?>
```

**Boundaries figure** [slide 20]: nested regions over + and − examples and unlabelled points; asks "Consistent(h,D)? Consistent(s',D)? Consistent(g',D)?" — no answers on the slide. Reading the picture [general]: the middle region $h$ holds the + examples and no −, so consistent; the outer region $g'$ also contains the − examples, so inconsistent (too general); the inner region $s'$ holds the + examples (the right-most + sits on its edge, so the picture is ambiguous).

## 7. Candidate Elimination [slides 21-27]

Maintain both boundaries: $G\leftarrow$ maximally general hypotheses in $H$; $S\leftarrow$ maximally specific hypotheses in $H$. For each training example $d=\langle x,c(x)\rangle$ modify $G,S$ to be consistent with $d$. [slide 21]

**If $d$ is positive** [slide 22]
1. Remove from $G$ any hypothesis inconsistent with $d$.
2. For each $s\in S$ not consistent with $d$: remove $s$; add all **minimal generalizations** $h$ of $s$ such that $h$ is consistent with $d$ **and some member of $G$ is more general than $h$**.
3. Remove from $S$ any hypothesis more general than another hypothesis in $S$.

**If $d$ is negative** [slide 22]
1. Remove from $S$ any hypothesis inconsistent with $d$.
2. For each $g\in G$ not consistent with $d$: remove $g$; add all **minimal specializations** $h$ of $g$ such that $h$ is consistent with $d$ **and some member of $S$ is more specific than $h$**.
3. Remove from $G$ any hypothesis less general than another hypothesis in $G$.

**Trace** [slides 23-27; verified by re-running the algorithm]

| Step | Example | $S_n$ | $G_n$ |
|---|---|---|---|
| 0 | — | `<Ø,Ø,Ø,Ø,Ø,Ø>` | `<?,?,?,?,?,?>` |
| 1 | $x_1$ + | `<Sunny,Warm,Normal,Strong,Warm,Same>` | $G_0$ |
| 2 | $x_2$ + | `<Sunny,Warm,?,Strong,Warm,Same>` | $G_1=G_0$ |
| 3 | $x_3$ − | $S_3=S_2$ | `<Sunny,?,?,?,?,?>`, `<?,Warm,?,?,?,?>`, `<?,?,?,?,?,Same>` |
| 4 | $x_4$ + | `<Sunny,Warm,?,Strong,?,?>` | `<Sunny,?,?,?,?,?>`, `<?,Warm,?,?,?,?>` |

Why step 3 gives exactly those three [computed]: specialize `<?,?,?,?,?,?>` against $x_3=\langle Rainy,Cold,High,Strong,Warm,Change\rangle$ by fixing one attribute to a value different from $x_3$'s. Candidates: Sky∈{Sunny,Cloudy}, Temp=Warm, Humidity=Normal, Wind=Weak, Water=Cool, Forecast=Same. Keep only those more general than $S_2$ (which has Sky=Sunny, Temp=Warm, Humidity=`?`, Wind=Strong, Water=Warm, Forecast=Same): Sky=Sunny, Temp=Warm, Forecast=Same survive; Cloudy, Normal, Weak, Cool are discarded.
Step 4 [computed]: $x_4$ has Forecast=Change, so `<?,?,?,?,?,Same>` is removed from $G$; $S_3$ is generalized on Water (Warm vs Cool) and Forecast (Same vs Change) to `?`. Note $S_4$ equals the Find-S result $h_4$.

## 8. Remarks and classifying new data [slides 28-29]

- **Converges to the target concept** when the training examples have no errors **and** the target concept is in $H$. [slide 28]
- **Converges to an empty version space** when the training data are inconsistent, or the target cannot be described by the hypothesis representation. [slide 28]
- Open questions posed: what should the next training example be? how to classify new instances? [slide 28]

**Classifying unobserved instances with the version space** [slide 29]

| Instance | Slide result | Meaning |
|---|---|---|
| $x_5=\langle Sunny,Warm,Normal,Strong,Cool,Change\rangle$ | 6/0 → + | all 6 VS members say positive |
| $x_6=\langle Rainy,Cold,Normal,Light,Warm,Same\rangle$ | 0/6 → − | all say negative |
| $x_7=\langle Sunny,Warm,Normal,Light,Warm,Same\rangle$ | 3/3 → ? | split vote, undecided |
| $x_8=\langle Sunny,Cold,Normal,Strong,Warm,Same\rangle$ | 2/4 → ? (−) | majority negative |

The slide does not define "a/b"; I read it as (hypotheses voting positive)/(voting negative) among the 6 members. [computed] Re-checking all four by enumeration reproduces exactly 6/0, 0/6, 3/3, 2/4. Shortcut [general]: if $S$ (the most specific) covers $x$ then every member does; if no member of $G$ covers $x$ then none does; otherwise the vote is split.

## 9. Inductive bias [slides 30-33]

**Biased hypothesis space** [slide 30]: conjunctive $H$ cannot express the disjunction $(Sky=Sunny)\lor(Sky=Cloudy)$.
- $x_1=\langle Sunny,Warm,Normal,Strong,Cool,Change\rangle$ +  → $S_1=\{\langle Sunny,Warm,Normal,Strong,Cool,Change\rangle\}$
- $x_2=\langle Cloudy,Warm,Normal,Strong,Cool,Change\rangle$ +  → $S_2=\{\langle ?,Warm,Normal,Strong,Cool,Change\rangle\}$
- $x_3=\langle Rainy,Warm,Normal,Strong,Cool,Change\rangle$ −  → $S_3=\{\}$ (empty): $S_2$ now covers the negative $x_3$. The slide sentence is cut off ("contradicts the already overly …"). [computed] $G$ also becomes empty, so the version space is empty.

**Unbiased learner** [slides 31-32]
- Idea: let $H$ express every teachable concept = the **power set** $\mathcal P(X)$. $\lvert X\rvert=96$, $\lvert\mathcal P(X)\rvert=2^{96}$ ("$\sim10^{28}$" on the slide; exactly $7.9\times10^{28}$ [computed]). $H$ = disjunctions, conjunctions, negations, e.g. $\langle Sunny,Warm,Normal,?,?,?\rangle\lor\langle?,?,?,?,?,Change\rangle$. $H$ surely contains the target; the conjunctive space represents only 973 concepts.
- Example: positives $x_1,x_2,x_3$ and negatives $x_4,x_5$ give $S=\{(x_1\lor x_2\lor x_3)\}$ and $G=\{\lnot(x_4\lor x_5)\}$ (here $x_i$ = those training instances).
- Consequence: only the training examples themselves get classified; to learn the concept you would have to show **every** instance of $X$. Each unobserved instance is classified positive by **exactly half** of the hypotheses in $VS$ and negative by the other half.
- [computed] With 5 labelled instances, $VS$ has $2^{96-5}=2^{91}\approx2.5\times10^{27}$ members (every labelling of the other 91 instances), which is why the vote is always 50/50.

**Three learners with different biases** [slide 33]

| Learner | Inductive bias |
|---|---|
| Rote learner (store examples; classify only if it matches a stored example) | none |
| Version space + Candidate Elimination | the hypothesis space contains the target concept |
| Find-S | the hypothesis space contains the target concept **and** all instances are negative unless the opposite is entailed by its other knowledge |

Take-away [general]: without some bias a learner cannot generalize beyond its training data.

## 10. Slide inconsistencies noticed [computed]

- **Attribute values:** slide 8 lists Water ∈ {Warm, Cold} and Wind ∈ {Strong, Weak}, but the examples use Water = **Cool** (slides 4, 12, 18, 23-30) and Wind = **Light** (slides 10, 29). Counts are unaffected (still 2 values each); my enumeration used Water ∈ {Warm, Cool}, Wind ∈ {Strong, Light}.
- **Slide 18** prints the bottom box as `{<Sunny,?,?,?,?,?>, <?,Warm,?,?,?>, }` (malformed). The correct $G$ is the two hypotheses shown in section 6 (agrees with slides 27, 29 and my enumeration).
- **Slide 8, "Only or more Ø → negative"** is a garbled phrase; read as "one or more Ø ⇒ always negative".

## 11. Project relevance and practical notes

- **Vocabulary only.** Stage 1 (important vs technical sentence) is a binary concept-learning problem, but Find-S / Candidate Elimination assume noise-free labels and an exactly representable conjunctive concept. Human-labelled Thai sentences will violate both, so the version space would collapse to empty (slide 28). [general]
- **Inductive bias:** every classifier in the project has one — Naive Bayes assumes conditional independence of words ([08](08-bayesian-learning.md)); kNN assumes nearby points share labels ([04](04-knn.md)); SVM prefers a large-margin linear separator ([09](09-svm.md)). Useful when explaining why results differ. [general]
- **Hypothesis space / consistent hypothesis** are the terms used in the learning-theory parts of the other lectures (e.g. brute-force MAP learning over $H$ in [08](08-bayesian-learning.md)). [general]
- Find-S is a quick sanity check for rule-style features (e.g. which attribute values all positive sentences share), but it would be a poor final classifier here. [general]
