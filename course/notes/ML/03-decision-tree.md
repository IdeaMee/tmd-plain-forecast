# ML 03 — Decision Trees

Source: `course/slides/03 Decision Tree.pptx` (62 slides, lecturer Parinya Sanguansat). Formulas, tables and trees read from slide images; every number re-computed.
Legend: **[slide N]** = taken from slide N · **[computed]** = my own calculation of an example the slide leaves open (or an exact re-check) · **[general]** = general knowledge or my inference, not on the slides.

**Project relevance: MEDIUM.** Optional extra comparison classifier for Stage 1 (sentence class) next to Naive Bayes, SVM, kNN. Easy to read as IF-THEN rules, but easy to overfit on a small sparse bag-of-words dataset. See Section 16.

---

## 1. Key ideas

- A decision tree is a hierarchical data structure that represents data by **divide and conquer**. Non-parametric method for **classification and regression**. [slide 2]
- Task: given a collection of examples, learn a tree that represents it, then use the tree to classify new examples. [slide 2]
- Evaluating a tree is easy; many trees fit the same data, so **learning a good tree is the challenge**. [slide 8]
- Learning is a **greedy top-down** search; the split attribute is picked by **information gain** (ID3, Quinlan). [slides 16, 25]
- A perfect fit to the training data can hurt on unseen data (**overfitting**) → prune. [slides 41, 47]

## 2. Tree representation [slides 3-6]

- **Nodes** test an attribute; **one branch per attribute value**; **leaves** give the class label. [slide 3]
- **Boolean tree** [slide 4]: can represent any Boolean function; can be rewritten as **DNF** rules (disjunction of conjunctions). Slide example, tree on Color then Shape:
  - $(\text{color}=\text{green})\land(\text{shape}=\text{square})\rightarrow +$
  - $(\text{color}=\text{blue})\land(\text{shape}=\text{circle})\rightarrow +$
  - $(\text{color}=\text{blue})\land(\text{shape}=\text{square})\rightarrow +$
  - Tree in the picture: blue → Shape {triangle −, square +, circle +}; red → +; green → Shape {square +, circle −}. **Note:** the picture has `red → +` but the slide's DNF list omits $(\text{color}=\text{red})\rightarrow +$ (slide inconsistency).
- **Multiclass tree** [slide 5]: leaves can be any of several classes. Example (classes A, B, C drawn as coloured shapes): Color: blue → Shape {triangle B, square A, circle C}; red → B; green → Shape {square B, circle A}.
- **Real-valued attributes** [slide 6]: discretize, or split by **thresholds**. The tree then divides the feature space into **axis-parallel rectangles**, each labelled. Slide figure (2-D, thresholds X=1, X=3, Y=5, Y=7):

| | $X<1$ | $1\le X<3$ | $X\ge 3$ |
|---|---|---|---|
| $Y>7$ | + | + | + |
| $5<Y<7$ | + | + | − |
| $Y<5$ | − | + | − |

  Tree: `X<3?` no → `Y>7?` (no −, yes +); yes → `Y<5?` (no +, yes → `X<1?` giving − / +). Leaf labels of the bottom `X<1` node are cluttered in the picture; read from the grid. [slide 6, reconstructed]

## 3. When to consider decision trees [slides 7-8]

- Instances describable by **attribute-value pairs**: discrete, continuous, missing values, values with costs.
- Target discrete (**classification tree**, binary or multiclass) or continuous (**regression tree**).
- A **disjunctive hypothesis** may be required; training data possibly **noisy**; compactly represents a lot of data.
- Can be shown as **IF-THEN rules** for readability.

## 4. Generic top-down induction [slides 9, 24]

```
DTree(examples, features) returns a tree
  If all examples are in one category -> leaf with that label.
  Else if features is empty           -> leaf with the most common label in examples.
  Else pick a feature F and create node R for it
    For each possible value v_i of F:
      examples_i = examples with F = v_i ; add edge E labelled v_i from R
      If examples_i is empty -> leaf on E with the most common label in examples
      Else attach DTree(examples_i, features - {F}) under E
    Return the subtree rooted at R
```

The generic version does not say *how* to pick F. ID3 (Section 8) fills that in.

### Toy example [slides 10, 13-14; gains computed]
Training set: ⟨big,red,circle⟩ +, ⟨small,red,circle⟩ +, ⟨small,red,square⟩ −, ⟨big,blue,circle⟩ −. Slide 10 asks "which is the first node?"; slide 13 picks **color**; slide 14 finishes: color → red: shape {circle +, square −, triangle +}; blue: −; green: −. The `triangle` and `green` leaves have **no examples**, so they get the most common label (rule in the pseudocode).
- [computed] $\text{Entropy}(S)=1$ (2+, 2−). $\text{Gain}(\text{size})=0$; $\text{Gain}(\text{color})=\text{Gain}(\text{shape})=0.311$ → **tie**; the slide picks color without saying why.
- [computed] Inside the red node (2+, 1−): $\text{Gain}(\text{shape})=0.918$ (both children pure) vs $\text{Gain}(\text{size})=0.252$ → shape, as on the slide.
- [computed] The `green` leaf (parent set 2+, 2−) is a tie; the slide labels it `neg`. The `triangle` leaf = majority of the red node (2+, 1−) = `pos`.

## 5. Choosing a good split [slides 11-16]

- Goal: smallest tree (Occam's razor). Finding a minimal tree (nodes, leaves or depth) is **NP-hard**; top-down divide and conquer is a **greedy search** that does not guarantee the smallest tree. "Greed is good." [slide 11]
- Pick the feature whose subsets are relatively **pure** in one class, so they are closer to leaves. [slides 11, 16]
- Example, 2 Boolean attributes [slide 12]: ⟨A=0,B=0⟩− ×50, ⟨A=0,B=1⟩− ×50, ⟨A=1,B=1⟩+ ×100. Split on **A**: purely labelled nodes (A=1 → +, A=0 → −). Split on **B**: not pure (B=0 → −, B=1 needs another split on A). [computed] $\text{Gain}(A)=1$, $\text{Gain}(B)=1-\tfrac{150}{200}(0.918)=0.311$.
- Harder variant [slide 15]: add ⟨A=1,B=0⟩− ×3. Splitting on B first: B=0 → − (53), B=1 → split A: A=1 → +100, A=0 → −50. Splitting on A first: A=0 → − (100), A=1 → split B: B=1 → +100, B=0 → −3. "Which is better?" is answered by information gain (Section 7).

## 6. Entropy [slides 17-18]

Entropy = disorder / impurity of a set $S$. Binary classification:

$$\text{Entropy}(S)=-p_1\log_2 p_1-p_0\log_2 p_0$$

Multiclass with $c$ categories:

$$\text{Entropy}(S)=\sum_{i=1}^{c}-p_i\log_2 p_i$$

$p_i$ = fraction of examples in $S$ that belong to class $i$.

- All examples in one class → entropy **0**. Equally mixed ($p_1=p_0=0.5$) → entropy **1** (maximum for binary). [slide 17]
- Interpretation: average number of **bits** needed to encode the class of an example in $S$ (shorter codes for likelier cases, e.g. Huffman coding). [slide 17]
- Slide 18 plots binary entropy against the fraction of positives: symmetric arch, 0 at fraction 0 and 1, peak 1 at 0.5.
- [general] Convention $0\log_2 0=0$. Slides 27-31 write "log" without a base; the results match base 2.

Handy values [computed] (entropy of a split $p : 1-p$):

| class mix | 1/2 : 1/2 | 3/4 : 1/4 | 2/3 : 1/3 | 3/5 : 2/5 | 4/7 : 3/7 | 6/7 : 1/7 | 9/14 : 5/14 |
|---|---|---|---|---|---|---|---|
| Entropy | 1 | 0.8113 | 0.9183 | 0.9710 | 0.9852 | 0.5917 | 0.9403 |

## 7. Information gain [slides 19-23]

**Information gain** of feature $F$ = expected reduction in entropy from splitting on $F$:

$$\text{Gain}(S,F)=\text{Entropy}(S)-\sum_{v\in \text{Values}(F)}\frac{\lvert S_v\rvert}{\lvert S\rvert}\,\text{Entropy}(S_v)$$

$S_v$ = subset of $S$ with value $v$ for feature $F$. Each subset's entropy is weighted by its relative size. Partitions that lower entropy ↔ high gain. [slide 19]
Slides 20-21 draw it with sets of + / − symbols: before the split the set is "highly disorganized, high entropy, much information required"; after splitting the subsets are "highly organized, low entropy, little information required". **Gain = information required before the split − information required after the split.**

### "Which one is better?" [slides 22-23; numbers re-computed]
Data: ⟨A=0,B=0⟩− ×50, ⟨A=0,B=1⟩− ×50, ⟨A=1,B=0⟩− ×3, ⟨A=1,B=1⟩+ ×100. Totals: 100+, 103−.

$$\text{Entropy}(S)=-\tfrac{100}{203}\log_2\tfrac{100}{203}-\tfrac{103}{203}\log_2\tfrac{103}{203}\approx 1$$

| Split | Child (+,−) | Entropy | Weight |
|---|---|---|---|
| B=1 | 100+, 50− | 0.918 (slide 0.92) | 150/203 |
| B=0 | 0+, 53− | 0 | 53/203 |
| A=1 | 100+, 3− | 0.190 (slide 0.19) | 103/203 |
| A=0 | 0+, 100− | 0 | 100/203 |

$\text{Gain}(S,B)=1-\tfrac{150}{203}(0.918)\approx 0.32$ and $\text{Gain}(S,A)=1-\tfrac{103}{203}(0.190)\approx 0.90$. [slide 23; exact 0.321 and 0.903, with $\text{Entropy}(S)=0.9998$] → **split on A**. (The slide gives only the two gains; "A is better" is implied.)

## 8. ID3 — Iterative Dichotomiser 3 [slide 25]

Same pseudocode as Section 4 except the choice of F: **pick the feature F that best classifies examples; best = highest information gain.**

Step by step (as demonstrated on slides 27-36):
1. Compute $\text{Entropy}(S)$ of the current example set.
2. For every remaining attribute $F$, compute $\text{Gain}(S,F)$.
3. Choose the attribute with the highest gain; create a node, one branch per value.
4. Send each example down its branch; recurse on every branch with $S_v$ and the remaining attributes.
5. Stop a branch when all examples share one class (leaf), no attributes remain (majority-class leaf), or the subset is empty (majority-class leaf from the parent).

## 9. Worked example: PlayTennis [slides 26-36, 51]

14 days, 9 Yes / 5 No. Attributes: Outlook {Sunny, Overcast, Rain}, Temp {Hot, Mild, Cool}, Humidity {High, Normal}, Wind {Weak, Strong}. [slide 26]

| Day | Outlook | Temp | Humidity | Wind | Play |
|---|---|---|---|---|---|
| 1 | Sunny | Hot | High | Weak | No |
| 2 | Sunny | Hot | High | Strong | No |
| 3 | Overcast | Hot | High | Weak | Yes |
| 4 | Rain | Mild | High | Weak | Yes |
| 5 | Rain | Cool | Normal | Weak | Yes |
| 6 | Rain | Cool | Normal | Strong | No |
| 7 | Overcast | Cool | Normal | Strong | Yes |
| 8 | Sunny | Mild | High | Weak | No |
| 9 | Sunny | Cool | Normal | Weak | Yes |
| 10 | Rain | Mild | Normal | Weak | Yes |
| 11 | Sunny | Mild | Normal | Strong | Yes |
| 12 | Overcast | Mild | High | Strong | Yes |
| 13 | Overcast | Hot | Normal | Weak | Yes |
| 14 | Rain | Mild | High | Strong | No |

**Step 1, root entropy** [slide 27]: $\text{Entropy}(S)=-\tfrac{9}{14}\log_2\tfrac{9}{14}-\tfrac{5}{14}\log_2\tfrac{5}{14}=0.940$ (exact 0.9403).

**Steps 2-5, gain of each attribute** [slides 28-31]. Children shown as (Yes,No) with entropy:

| Attribute | Children | Gain (slide) | Gain (exact) |
|---|---|---|---|
| Outlook | Sunny (2,3) 0.971 · Overcast (4,0) 0 · Rain (3,2) 0.971 | 0.246 | 0.2467 |
| Temp | Hot (2,2) 1 · Mild (4,2) 0.918 · Cool (3,1) 0.811 | 0.029 | 0.0292 |
| Humidity | High (3,4) 0.985 · Normal (6,1) 0.592 | 0.151 | 0.1518 |
| Wind | Weak (6,2) 0.811 · Strong (3,3) 1 | 0.048 | 0.0481 |

Example line (slide 28): $\text{Gain}(S,\text{Outlook})=0.94-\tfrac{5}{14}(0.971)-\tfrac{5}{14}(0.971)=0.246$ (Overcast term is 0). The slide values are truncated, not rounded (0.2467 → 0.246, 0.1518 → 0.151); ranking unchanged.

**Step 6** [slide 32]: Outlook has the highest gain (0.246) → **root = Outlook**.

**Step 7, Sunny branch** [slide 33; days 1,2,8,9,11; 2+,3−; $\text{Entropy}=0.97$]:

| Attribute | Children | Gain (slide) | Exact |
|---|---|---|---|
| Temp | Hot {1,2} (0,2) 0 · Mild {8,11} (1,1) 1 · Cool {9} (1,0) 0 | $0.97-\tfrac{2}{5}\cdot1=0.57$ | 0.571 |
| Humidity | High {1,2,8} (0,3) 0 · Normal {9,11} (2,0) 0 | 0.97 | 0.971 |
| Wind | Weak {1,8,9} (1,2) 0.918 · Strong {2,11} (1,1) 1 | 0.02 | 0.020 |

→ **Humidity** under Sunny (both children pure: High → No, Normal → Yes). [slides 33-35]
**Overcast** (days 3,7,12,13; 4+,0−) is pure → **Yes**. [slide 34]
**Rain branch** (days 4,5,6,10,14; 3+,2−): the slides jump to Wind [slide 36]. [computed] $\text{Gain}(\text{Wind})=0.971$ (Weak {4,5,10} all Yes; Strong {6,14} all No), $\text{Gain}(\text{Temp})=\text{Gain}(\text{Humidity})=0.020$ → Wind.

**Final tree** [slide 36]:

```
Outlook
├─ Sunny    → Humidity ── High → No      Normal → Yes
├─ Overcast → Yes
└─ Rain     → Wind ────── Strong → No    Weak   → Yes
```

As IF-THEN rules [slide 51] (one rule per branch):
- R1: Outlook=Sunny ∧ Humidity=High → PlayTennis=No
- R2: Outlook=Sunny ∧ Humidity=Normal → Yes
- R3: Outlook=Overcast → Yes
- R4: Outlook=Rain ∧ Wind=Strong → No
- R5: Outlook=Rain ∧ Wind=Weak → Yes

[computed] All leaves are pure, so the tree classifies all 14 training days correctly. Temp is never used.

## 10. ID3 properties and history [slides 37-39]

**Hypothesis space / bias of ID3** [slide 37]:
- Hypothesis space is **complete** (the target function is surely in there).
- Outputs a **single hypothesis**.
- **No backtracking** on selected attributes (greedy) → can land in local minima (suboptimal splits).
- **Statistically-based** search choices → robust to noisy data.
- **Inductive (search) bias:** prefer shorter trees; place high-gain attributes close to the root.

**History** [slides 38-39]:
- Hunt and colleagues (psychology) used full-search decision trees to model human concept learning in the 1960s.
- Quinlan: **ID3** with the information-gain heuristic, late 1970s. ID3 follows Occam's razor (smallest tree possible).
- Breiman, Friedman et al. (statistics): **CART** (classification and regression trees), developed simultaneously.
- 1980s improvements: noise, continuous attributes, missing data, non-axis-parallel splits.
- **C4.5** (Quinlan, 1993), commonly used: handles discrete and continuous attributes, missing values, attributes with differing costs, and **pruning** (replace irrelevant branches by leaves).
- **C5.0** (commercial): much faster, more memory-efficient, smaller trees, boosting, attribute weighting, winnowing (reduces noise).

## 11. Generalization and overfitting [slides 40-46]

- We want accuracy on **future** examples; computations from the training set are only estimates; the tree is built by a sequence of decisions that are **local, dependent, approximate**; the algorithm gives **no guarantee** on how good the tree is. [slide 40]
- Perfect training accuracy may not generalize: the tree may fit **noise**, and splits near the leaves rest on very little data and may not reflect reliable trends. [slide 41]
- **Definition:** hypothesis $h$ **overfits** the training data if some other hypothesis $h'$ has greater error than $h$ on the training data but smaller error on independent test data. Figure: accuracy vs hypothesis complexity; training accuracy rises and plateaus, test accuracy peaks then declines. [slide 41]
- **Example 1, noisy sample** [slides 42-43]: take the PlayTennis tree and add ⟨Sunny, Hot, Normal, Strong⟩ labelled **No** (the picture shows an arrow from YES to NO; the clean tree says Yes for Sunny+Normal). The Sunny/Normal leaf is crossed out and the tree grows: Sunny → Humidity → Normal → **Wind** {Strong No, Weak Yes} (slide asks "Correct tree?").
  - [computed] The slide's grown tree is a simplification: under Sunny/Normal the Strong branch would hold day 11 (Yes) and the noisy example (No), still impure, so a real learner would need yet another split (e.g. Temp). Either way, one wrong label makes the tree bigger.
- **Example 2, Ohm's law** [slides 44-45]: 10 measured (voltage, current) points; a 9th-degree polynomial fits them perfectly (n points can be fitted exactly by degree n−1) but wiggles; a linear fit that matches the training data less well **generalizes better**. Slide's irony: "Ohm was wrong, we have found a more accurate function!"
- **When overfitting happens** [slide 46]: in both classification and regression; with **noisy data** (incorrect data make the tree grow deeper); with **too few training examples** (some attributes partition the examples well by chance despite being unrelated to the target). A correct, complete training set would avoid it. The slide ends with "Is it possible?" (rhetorical).

## 12. Avoiding overfitting [slides 47-51]

Two approaches [slide 47]:
- **Pre-pruning:** stop growing when there is not enough data to make reliable choices.
- **Post-pruning:** grow the full tree, then remove nodes that lack sufficient evidence.

Methods to evaluate which subtrees to prune [slide 47]: **cross-validation** (hold-out set), **statistical testing** (is the regularity likely due to chance?), **Minimum Description Length** (is the added complexity smaller than remembering the exceptions?).

**k-fold cross-validation** [slide 48]: split data $D$ into $k$ mutually exclusive subsets $D_1,\dots,D_k$; run $k$ evaluations, each trained on $D\setminus D_i$ and tested on $D_i$; **average the $k$ results**.

**Reduced-error pruning** (post-pruning, cross-validation style) [slide 49]:
1. Split training data into a training set and a validation set.
2. Build the complete tree on the training set.
3. Until accuracy on the validation set decreases: for each non-leaf node, **temporarily** replace the subtree below it by a majority-vote leaf and test validation accuracy; **permanently** prune the node giving the greatest increase in validation accuracy.

(The slide's wording is "until accuracy on validation set decreases"; read it as: stop when pruning no longer helps.) Slide 50 opens with "Problem: uses less data to construct the tree"; I read this as the cost of holding out a validation set. [general inference]

**Rule post-pruning** (used in C4.5) [slide 50]:
1. Infer the tree from the training set.
2. Convert the tree to rules, one rule per branch (see R1-R5 in Section 9).
3. Prune each rule by removing preconditions that improve estimated accuracy.
4. Sort pruned rules by estimated accuracy and apply them in that order to unseen instances.
Rules are generalized by erasing a condition; slide has a red "(different ?)" next to it, i.e. the lecturer flags a contrast with tree pruning without explaining it here.

## 13. Extensions [slides 52-61]

### 13.1 Continuous attributes [slides 52-53]
- Discretize in advance (e.g. big / medium / small), **or** use threshold tests $A<T$ vs $A\ge T$. $T$ must lie at a **class boundary** [Fayyad 1991]. Gain of threshold splits is computed in the same way and compared with discrete splits. Open question on slide: "How to split into multiple intervals?"
- Example [slide 53]: sorted Temp (40, 48, 60, 72, 80, 90 °C) with PlayTennis (No, No, Yes, Yes, Yes, No); $S$ = 3+, 3−, $\text{Entropy}(S)=1$. Class changes between 48/60 and 80/90, giving candidate thresholds $(48+60)/2=54$ and $(80+90)/2=85$.

| Test | Yes branch | No branch | Gain |
|---|---|---|---|
| Temp>54 | 3+,1− (E=0.811) | 0+,2− (E=0) | $1-\tfrac{4}{6}(0.811)=0.459$ |
| Temp>85 | 0+,1− (E=0) | 3+,2− (E=0.971) | $1-\tfrac{5}{6}(0.971)=0.191$ |

  Re-computed: 0.4591 and 0.1909. → choose **Temp>54** (circled on slide). The gain formula on the slide says "Temp>84", a typo for 85.
- [general] Candidate thresholds only need checking at midpoints between adjacent sorted values whose class labels differ (this is what the Fayyad boundary rule gives).

### 13.2 Missing values [slides 54-57]
- Values may be missing in training or testing (e.g. blood_test = ? in diagnosis). Training: evaluate $\text{Gain}(S,A)$ when some examples lack $A$. Testing: classify without knowing $A$. [slide 54]
- Options [slide 55]: still sort the example down the tree; if node $n$ tests $A$, assign the **most common value of $A$** among the examples at $n$; or the most common value among examples **with the same target value**; or assign probability $p_i$ to each value $v_i$ and send **fraction $p_i$** of the example down each branch. Classify new examples the same way.
- **Training example** [slide 56]: day 8 has Humidity = ??? (Sunny, Mild, ???, Weak, No). (A) most common Humidity among Sunny days: {High, Normal} (tie). (B) same but only target = No: {High}. [computed] Other Sunny days: High ×2 (days 1,2), Normal ×2 (days 9,11) → tie confirmed; Sunny+No days 1,2 are both High → {High}.
- **Test example** [slide 57]: Outlook = ???, Temp=Hot, Humidity=Normal, Wind=Strong. Following all three Outlook branches: Sunny → Humidity=Normal → Yes; Overcast → Yes; Rain → Wind=Strong → No.
  - (A) equal weights: $\tfrac13\text{Yes}+\tfrac13\text{Yes}+\tfrac13\text{No}$ → **Yes**.
  - (B) weights from counts: $\tfrac28\text{Yes}+\tfrac48\text{Yes}+\tfrac28\text{No}$ → **Yes**. The weights 2, 4, 2 are the counts shown under the leaves reached (Normal 2, Overcast 4, Strong 2). [general] C4.5 usually weights by branch sizes (5/14, 4/14, 5/14 here); same answer (Yes, 9/14).

### 13.3 Attributes with many values → Gain Ratio [slides 58-59]
- **Problem:** maximizing information gain favours attributes with many values; a unique ID like Date splits the data into singleton subsets (perfectly pure) but is useless for prediction. [slide 58]
- Fix: use **GainRatio**.

$$\text{GainRatio}(S,A)=\frac{\text{Gain}(S,A)}{\text{SplitInformation}(S,A)}\qquad
\text{SplitInformation}(S,A)=-\sum_{i=1}^{c}\frac{\lvert S_i\rvert}{\lvert S\rvert}\log_2\frac{\lvert S_i\rvert}{\lvert S\rvert}$$

$S_i$ = subset where $A$ has value $v_i$; $c$ = number of values. SplitInformation is the entropy of the partition sizes themselves (it grows with the number of values).
- Slide 59 example, 14 examples: $A$ = 14 singleton branches → $\text{SplitInfo}(S,A)=14\cdot(-\tfrac1{14}\log_2\tfrac1{14})=\log_2 14=3.81$; $B$ = two branches of 7 → $\text{SplitInfo}(S,B)=2\cdot(-\tfrac12\log_2\tfrac12)=1$. "If A and B produce the same information gain, B will be chosen according to GainRatio." (slide spells it "GainRadio")
- [computed] For PlayTennis (Section 9): SplitInfo / GainRatio = Outlook 1.577 / 0.156, Temp 1.557 / 0.019, Humidity 1.000 / 0.152, Wind 0.985 / 0.049. Outlook still wins. A Date-like attribute would have Gain = 0.940 (all pure) but GainRatio = 0.940/3.807 = 0.247.

### 13.4 Attributes with cost [slide 60]
Examples: blood test costs 1000 SEK; robot measurement takes 23 s. Goal: a consistent tree with low expected cost, by changing the gain so cheap attributes are preferred. Two replacements for Gain:

$$\frac{\text{Gain}^2(S,A)}{\text{Cost}(A)}\ \text{[Tan, Schlimmer 1990]}\qquad
\frac{2^{\text{Gain}(S,A)}-1}{(\text{Cost}(A)+1)^{w}},\ w\in[0,1]\ \text{[Nunez 1988]}$$

The slide text is flat ("Gain2(S,A)/Cost(A)", "2Gain(S,A)-1/(Cost(A)+1)w") with the superscripts lost; I restored the standard forms from the literature. [general] The slide spells the first author "Schimmer".

### 13.5 Other issues [slide 61]
- **Incremental induction:** update an existing tree for new examples (keeping it consistent is the open concern).
- **Trees as features:** with very many features one large tree overfits; instead learn **small, depth-limited trees** (each correct only on a small region of the domain, treated as experts), then learn another function, typically **linear**, over them as features.

## 14. Classwork CW#1 [slide 62]

The slide only shows the data table (no instructions or answer). Presumably "build the tree with ID3". [computed] below:

| A | B | C | D | Target |
|---|---|---|---|---|
| 1 | 2 | 1 | 2 | + |
| 2 | 1 | 1 | 2 | − |
| 1 | 2 | 2 | 2 | + |
| 3 | 2 | 2 | 1 | − |
| 1 | 2 | 4 | 2 | + |
| 3 | 2 | 1 | 2 | − |
| 1 | 2 | 1 | 3 | − |
| 2 | 1 | 1 | 1 | − |

- $S$ = 3+, 5−, $\text{Entropy}(S)=0.954$.
- Gains: **A = 0.549**, B = 0.204, C = 0.253, D = 0.348 → root **A** (A=1: 3+,1−; A=2: 0+,2−; A=3: 0+,2−).
- A=2 → −; A=3 → −. Node A=1 (rows 1,3,5,7): $\text{Entropy}=0.811$; B is constant (gain 0); $\text{Gain}(C)=0.311$; $\text{Gain}(D)=0.811$ (D=2 → +++, D=3 → −) → split on **D**.
- Result: `A: 2→−, 3→−, 1→ D: 2→+, 3→−`; D=1 never occurs under A=1, so by the pseudocode that branch (if drawn) gets the node's majority label +.

## 15. Slide values checked

- All slide arithmetic matches my recomputation (entropies, gains, split information). Slides truncate rather than round (0.246 vs 0.2467, 0.151 vs 0.1518); decisions unaffected.
- Slide 4: tree has `red → +` but DNF list omits it (inconsistency).
- Slide 53: gain label says Temp>84, node says Temp>85 (typo; 0.191 matches 85).
- Slide 23: $\text{Entropy}(S)$ printed as ≈1 (exact 0.9998), gains ≈0.9 / ≈0.32 (exact 0.903 / 0.321). Fine.
- Slide 43: grown tree is a simplification (see Section 11).
- Slide 60: superscripts lost in the export; formulas restored from the literature.
- Slide 62: no task text. Slides 1-62 all read; none illegible. Slides 9 and 24 repeat the DTree pseudocode; 11/16, 12/15/22 and 13/14 repeat the split-feature examples.

## 16. Project relevance and practical notes

- **Stage-1 candidate:** sentence → binary features "word $w$ present?" (Thai-segmented tokens from Stage 0), class = important vs technical. Each node then tests one word, exactly the Boolean-attribute case of slides 4 and 12. [general]
- **Overfitting risk is high:** a small training set with a large sparse vocabulary lets words that happen to separate the examples look useful (slide 46's "too few training data" warning). Use pre-pruning (max depth, minimum examples per leaf), post-pruning, and k-fold cross-validation (slide 48) to choose them. [general; mapped to slides 46-49]
- **Gain ratio / many values:** if features are word counts or ID-like values, raw gain favours many-valued attributes (slide 58); prefer binary presence features or gain ratio. [general]
- **Interpretability:** the tree converts to IF-THEN rules (slide 51), so one can read which words drive the decision. [general application of slide 51]
- **Library note:** scikit-learn's `DecisionTreeClassifier` is CART-style (binary threshold splits; Gini by default, `criterion="entropy"` gives the information-gain criterion of these slides) and uses cost-complexity pruning (`ccp_alpha`), not reduced-error pruning. It is not ID3. [general]
- **Comparison set:** Naive Bayes ([08](08-bayesian-learning.md)), SVM ([09](09-svm.md)), kNN ([04](04-knn.md)); evaluate all with the same cross-validation folds. [general]
- Slide 61's "small trees as features" idea is the seed of tree ensembles (random forest, boosting). [general; ensembles are not on these slides]
