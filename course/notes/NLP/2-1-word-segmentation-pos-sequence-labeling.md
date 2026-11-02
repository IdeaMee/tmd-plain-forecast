# NLP 2-1 — Word Segmentation, POS Tagging and Sequence Labeling

Source: `course/slides/2-1_Word_Segmentation_POS_Tagging_Sequence_Labeling.pdf` (39 slides, Satida Sookpong). Thai words from the PDF text layer; formulas, tables and figures read from slide images (slides 4-11, 13-18, 20-32, 34-39 viewed; slide 2 is the agenda; slides 1, 3, 12, 19, 33 are title/section dividers). Every numeric example below was recomputed in Python. Several slide values are inconsistent; they are flagged with **CHECK**.
Legend: **[slide N]** = PDF page · **[general]** = general knowledge or my inference · **[computed]** = my own calculation.

**Project relevance: HIGH for Part 1 (Stage 0 segmentation), LOW-MEDIUM for Parts 2-3.** Part 1 explains how PyThaiNLP-style segmenters work and where they fail. POS tagging and NER are not in the planned pipeline but could add features (place names, nouns) later. [general]

---

## 1. Word segmentation [slides 4-5]

English uses spaces as word boundaries (`"I go to school"`). Thai, Chinese and Japanese are written without spaces (`"ฉันไปโรงเรียน"`), so boundaries must be inferred. Three difficulties [slide 4]:
1. **No delimiter** between words.
2. **Ambiguity:** the same character string can be cut several ways with completely different meanings, e.g. "ตากลม".
3. **No fixed definition of "word"** (the slide card has only this heading, no body text).

Approaches [slide 5]:

| Approach | Idea |
|---|---|
| Dictionary-based matching | match longest (or shortest) known words against a lexicon, e.g. maximum matching |
| Rule-based heuristics | hand-written linguistic rules resolve ambiguous boundaries |
| Statistical / ML-based | character-level classifiers or sequence models predict boundaries: HMM, CRF, deep learning (LSTM/Transformer) |

## 2. Maximum matching (FMM / BMM) [slides 6-7]

**Forward Maximum Matching (FMM):** start at the leftmost position, try to match the **longest** string against the dictionary; if no match, shorten by one character at a time; cut the first match, move on. **BMM** is the same idea scanning from the right. Greedy, no training.

Slide example [slide 6]: dictionary {นัก, นักเรียน, เรียน, ไป, โรง, โรงเรียน, ...}, sentence "นักเรียนไปโรงเรียน" (18 characters, no spaces):
1. try "นักเรียนไป" ✗ → ... → "นักเรียน" ✓ → cut นักเรียน
2. try "ไปโรงเรี" ✗ → ... → "ไป" ✓ → cut ไป
3. try "โรงเรียน" ✓ → cut โรงเรียน
Result: **นักเรียน | ไป | โรงเรียน**. [computed] A Python FMM and BMM both give this result.
**CHECK:** the lengths printed in parentheses on the slide (8, 4, 4, 1, 4) do not match the string lengths: "นักเรียนไป" has 10 code points (8 if combining vowel marks are not counted), "นักเรียน" 8 (6), "ไปโรงเรี" 8 (7), "ไป" 2, "โรงเรียน" 8 (7). The slide's 8 fits only the no-combining-marks count and the other four fit neither. The total "18 characters" is right [computed]. Ignore the parenthesized numbers.

Ambiguity example "ตากลม" [slide 7]: ตา+กลม = "round eyes" vs ตาก+ลม = "to air out (in the wind)". With a dictionary containing all four words:

| | FMM (left to right) | BMM (right to left) |
|---|---|---|
| Steps | i=0: "ตากลม"(5) ✗, "ตากล"(4) ✗, "ตาก"(3) ✓ cut; i=3: "ลม"(2) ✓ cut | j=5: "ตากลม"(5) ✗, "ากลม"(4) ✗, "กลม"(3) ✓ cut; j=2: "ตา"(2) ✓ cut |
| Result | **ตาก \| ลม** | **ตา \| กลม** |

The two directions disagree, and neither can decide which meaning is right: maximum matching only follows string length, not meaning or frequency. [slide 11: fast and needs no training, but resolves ambiguity poorly and depends on the dictionary]. [computed] Exactly two dictionary segmentations of "ตากลม" exist here, so this is a real tie.

## 3. Statistical segmentation [slides 8-10]

Idea [slide 8]: instead of the greedy "longest word", pick the **sequence of words with the highest probability**, using unigram (or bigram) frequencies from a large corpus. This is the same idea as the N-gram language model of the previous week (see [5-1](5-1-language-models-ngrams.md)).

Unigram formula [slide 8]:

$$\hat W=\arg\max_{W\in\text{Seg}(S)}\ \prod_i P(w_i),\qquad P(w)=\frac{\text{count}(w)}{N}$$

- [general] notation of this note (not on the slide; $P(w)=\text{count}(w)/N$ is shown on slide 10): $S$ = the unsegmented string, $\text{Seg}(S)$ = all possible segmentations into words, $w_i$ = the $i$-th word of segmentation $W$, $N$ = total word count of the corpus.
- Bigram version [general]: replace $P(w_i)$ by $P(w_i\mid w_{i-1})$.

**Probability review ("Prob 101")** [slide 9] (six formulas used by this chapter):

| Name | Formula |
|---|---|
| Classical probability | $P(E)=N(E)/N(S)$ (outcomes where $E$ occurs / all outcomes in the sample space) |
| Conditional probability | $P(A\mid B)=\dfrac{P(A\cap B)}{P(B)}$ |
| Chain rule | $P(A_1,\dots,A_n)=P(A_1)P(A_2\mid A_1)P(A_3\mid A_1,A_2)\cdots$ |
| Independence | $P(A\cap B)=P(A)P(B)$ if $A,B$ independent |
| Bayes' theorem | $P(A\mid B)=\dfrac{P(B\mid A)P(A)}{P(B)}$ |
| Total probability | $P(A)=\sum_i P(A\mid B_i)P(B_i)$ |

**Worked example** [slide 10]: toy corpus counts: ตา 500, กลม 80, ตาก 60, ลม 200; "total number of words" $=500+80+60+200=840$.

| Word | ตา | กลม | ตาก | ลม |
|---|---|---|---|---|
| count | 500 | 80 | 60 | 200 |
| $P(w)=\text{count}/840$ | 0.595 | 0.095 | 0.071 | 0.238 |

- $P(\text{ตา+กลม})=0.595\times0.095=0.0567$
- $P(\text{ตาก+ลม})=0.071\times0.238=0.0170$
- $0.0567>0.0170$ → choose **ตา + กลม** (the BMM answer).

[computed] Verified: exact values are 500/840 = 0.5952, 80/840 = 0.0952, 60/840 = 0.0714, 200/840 = 0.2381; products 0.05669 and 0.01701, ratio 3.33 (= 500·80 / (60·200), independent of the denominator). The slide's products 0.0567 and 0.0170 are computed from the unrounded probabilities; multiplying the printed 3-decimal values gives 0.0565 and 0.0169 (tiny difference, same decision). In log space: ln(0.05669) = -2.870 vs ln(0.01701) = -4.074.

Notes [general]: (a) here both candidates have two words, so the "840" total does not affect the comparison (using N = 10,000 gives 4.0e-4 vs 1.2e-4, same ratio); the "840" is only the sum of the four toy counts, not a real corpus size. (b) When candidates have different numbers of words, the unigram product favours fewer words, since every extra factor is below 1. (c) Real systems use log-probabilities and dynamic programming over the word lattice instead of enumerating all segmentations; the slide only states "all possible segmentations".

**Recap table of Thai segmentation methods** [slide 11]:

| Method | Main idea | Limitation / strength |
|---|---|---|
| Maximum matching (forward/backward) | greedy longest match against a dictionary | fast, no training; poor at ambiguity, depends on the dictionary |
| Statistical segmentation | choose the segmentation with highest (n-gram) probability | resolves ambiguity better; needs a reliable statistics corpus |
| HMM / CRF (sequential statistics) | treat segmentation as sequence labeling | more accurate; needs labeled training data |
| Deep learning (BiLSTM / Transformer) | learn word features directly from lots of data (slide examples: deepcut, PyThaiNLP) | most accurate today; needs a lot of data/resources |

Segmentation as sequence labeling [slide 35]: input $x_i$ = a **character**, label $y_i$ = word boundary tag (B/I): B begins a word, I continues it. [general] Example: "ตากลม" cut as ตา|กลม is B I B I I.

## 4. POS tagging [slides 13-18]

**POS tagging** = assign a part of speech (noun, verb, adjective, ...) to every word of a sentence [slide 13]. Unlike segmentation, which finds the words, tagging says what **function** each word has. It is a base for parsing, NER, information extraction and machine translation. The same word can have several tags depending on context.

Example [slide 13]: `Janet/NNP will/MD back/VB the/DT bill/NN` (name, modal/auxiliary, verb, determiner, noun). Why hard: "back" can be VB (support), NN (the back), JJ (rear) or RB; only context tells which.

**Tagsets** [slides 14-15]:
- The slide-15 table shows 8 universal-style tags: NOUN (algorithm, cat, mango), VERB (draw, provide, go), ADJ (red, young, awesome), ADV (very, slowly, yesterday), PROPN (Regina, IBM, Colorado), DET (a, an, the, this), ADP (in, on, by, under), PRON (she, who, I). The slide titles it "standard tagset" and does not name it in the table, but the box below says PTB is finer than "UD" (Universal Dependencies), which implies this table is UD. [general] UD has 17 tags in total.
- **Penn Treebank** (PTB): about 45 tags, finer than UD (the slide says so); slide 14 is the full table (Fig. 3.3, includes punctuation tags). Tags used in the slides: NNP proper noun, NN noun (singular/mass), MD modal, VB verb base form, DT determiner, JJ adjective, RB adverb.
- **Thai: ORCHID** (NECTEC), about 47 tags, e.g. NCMN = common noun, VACT = active verb [slide 15].

**Three approaches** [slide 16]:

| Approach | Idea |
|---|---|
| Rule-based | dictionary + hand-written grammar rules to remove ambiguity |
| Stochastic / statistical | frequencies/probabilities from a labeled corpus; pick the most probable tag (e.g. HMM) |
| Hybrid (TBL / Brill tagger) | stochastic initial guess, then corrected by rules |

General pipeline [slide 16]: segmented tokens → look up all possible tags of each word in a dictionary → use rules or a statistical model to choose the best tag in context → tag sequence.

**Rule-based** [slide 17]: (1) dictionary lookup gives all possible tags; (2) hand-written rules using neighbouring words disambiguate. Example "a book": a → DET (clear); book → NOUN or VERB? Rule: if the previous word is DET, the next must be NOUN → book = NOUN. Extra knowledge: word-form rules (-ed → past tense, -ing → continuing verb, -ly → adverb), capitalization → proper noun. Pros: explainable, accurate when rules cover the case. Cons: writing rules is laborious, hard to scale.

**Stochastic** [slide 18]: uses frequency of tags and tag sequences from a tagged corpus. Two levels: (a) **most-frequent-tag baseline** (unigram): give each word its most frequent tag, ignoring context; (b) **HMM**: choose the tag sequence for the whole sentence jointly. Pros: learns automatically, no hand-written rules. Cons: needs a large tagged corpus.

## 5. Hidden Markov Model (HMM) [slides 20-23]

Markov chain [slide 20, figure from SLP3 Fig. 17.8]: states with transition probabilities; a start distribution $\pi$ is required (the caption's example: $\pi=[0.1,0.7,0.2]$ for the HOT/COLD/WARM weather chain means probability 0.7 of starting in COLD).

HMM components [slide 21]:

| Symbol | Meaning |
|---|---|
| $Q$ | set of $N$ states = all POS tags |
| $A$ | transition probability matrix, $P(\text{tag}_i\mid\text{tag}_{i-1})$ = probability of moving from tag $i-1$ to tag $i$ (in the Viterbi formula of slide 25 the entry is written $a_{ij}$ = from state $q_i$ to $q_j$) |
| $B$ | observation likelihoods $P(\text{word}_i\mid\text{tag}_i)$ (emission) |
| $\pi$ | initial distribution, $\pi_i$ = probability that the first tag is $i$ |
| $O=o_1\dots o_T$ | the observation sequence (here the words), each drawn from vocabulary $V$ |

Observation = the word sequence; **hidden state = the POS tag** [slide 22].

Two assumptions [slide 21]:
- Markov: $P(q_i\mid q_1,\dots,q_{i-1})=P(q_i\mid q_{i-1})$ (17.6)
- Output independence: $P(o_i\mid q_1\dots q_T,o_1\dots o_T)=P(o_i\mid q_i)$ (17.7)

**Tagging as decoding** [slide 23]: find the most probable tag sequence given the words:

$$\hat t_{1:n}=\arg\max_{t_1\dots t_n}P(t_1\dots t_n\mid w_1\dots w_n)=\arg\max P(w_1\dots w_n\mid t_1\dots t_n)\,P(t_1\dots t_n)\approx\arg\max\prod_{i=1}^{n}\underbrace{P(w_i\mid t_i)}_{\text{emission}}\ \underbrace{P(t_i\mid t_{i-1})}_{\text{transition}}\quad(17.17)$$

Steps: (1) the goal; (2) Bayes' rule, dropping $P(w)$ because it is constant; (3) output independence: $P(w\mid t)\approx\prod P(w_i\mid t_i)$; (4) Markov: $P(t)\approx\prod P(t_i\mid t_{i-1})$.

## 6. Viterbi decoding [slides 24-29]

**Idea** [slide 25]: dynamic programming over a lattice/trellis. Cell $v_t(j)$ = probability of the best path that ends in tag $j$ at position $t$; keep a **backpointer** in every cell, then backtrace from the best final cell.

$$v_t(j)=\max_{i=1}^{N}\ v_{t-1}(i)\,a_{ij}\,b_j(o_t)\quad(17.19),\qquad v_1(j)=\pi_j\,b_j(o_1)$$

- $v_{t-1}(i)$ = previous Viterbi path probability (previous step, tag $i$); $a_{ij}$ = transition probability from state $q_i$ to $q_j$; $b_j(o_t)$ = observation likelihood of the word $o_t$ given tag $j$.
- (17.18) defines $v_t(j)=\max_{q_1\dots q_{t-1}}P(q_1\dots q_{t-1},o_1\dots o_t,q_t=j\mid\lambda)$, with $\lambda$ the HMM.
- Algorithm: (1) initialise column 1 with $\pi_j b_j(o_1)$ (this initialisation is stated on slide 27, not slide 25); (2) for each next word and each tag $j$, take the best previous tag $i$, store the value and the backpointer; (3) pick the best cell of the last column; (4) follow backpointers back to column 1.
- **CHECK (notation):** slide 25 describes the lattice as "N rows (tags) × T columns (words)", but slide 29 uses N = sentence length and T = number of tags. This note follows slide 29 for complexity.

**Tables** ("Janet will back the bill", WSJ, SLP3 Figs. 17.12-17.13) [slides 24, 26]. Slide 24 shows rounded and partial tables; slide 26 has the full ones. Transition $P(t_i\mid t_{i-1})$, row = previous tag:

| prev \ next | NNP | MD | VB | JJ | NN | RB | DT |
|---|---|---|---|---|---|---|---|
| `<s>` | .2767 | .0006 | .0031 | .0453 | .0449 | .0510 | .2026 |
| NNP | .3777 | .0110 | .0009 | .0084 | .0584 | .0090 | .0025 |
| MD | .0008 | .0002 | .7968 | .0005 | .0008 | .1698 | .0041 |
| VB | .0322 | .0005 | .0050 | .0837 | .0615 | .0514 | .2231 |
| JJ | .0366 | .0004 | .0001 | .0733 | .4509 | .0036 | .0036 |
| NN | .0096 | .0176 | .0014 | .0086 | .1216 | .0177 | .0068 |
| RB | .0068 | .0102 | .1011 | .1012 | .0120 | .0728 | .0479 |
| DT | .1147 | .0021 | .0002 | .2157 | .4744 | .0102 | .0017 |

Observation $P(\text{word}\mid\text{tag})$ (all other entries 0):

| tag | Janet | will | back | the | bill |
|---|---|---|---|---|---|
| NNP | .000032 | 0 | 0 | .000048 | 0 |
| MD | 0 | .308431 | 0 | 0 | 0 |
| VB | 0 | .000028 | .000672 | 0 | .000028 |
| JJ | 0 | 0 | .000340 | 0 | 0 |
| NN | 0 | .000200 | .000223 | 0 | .002337 |
| RB | 0 | 0 | .010446 | 0 | 0 |
| DT | 0 | 0 | 0 | .506099 | 0 |

(Slide 24's version rounds the transition values and omits the JJ, NN, RB and DT rows of the transition table and the JJ and RB rows of the observation table.) Note "Janet" occurs only as NNP.

**Worked example** [slides 27-28], values re-run in Python with the full tables [computed]:

Column 1 ("Janet"): $v_1(\text{NNP})=\pi(\text{NNP})\,b(\text{Janet}\mid\text{NNP})=0.2767\times0.000032=8.854\times10^{-6}$; every other tag is 0 because $b(\text{Janet}\mid\text{tag})=0$.
**CHECK:** slide 27 prints "0.28 × 0.000032 = 8.854e-6". 0.28 is the rounded display of 0.2767 (slide 24); 0.28×0.000032 would be 8.96e-6. The value 8.854e-6 is right.

Column 2 ("will"), all from $v_1(\text{NNP})$:

| Tag $j$ | $v_1\times a(\text{NNP},j)$ | $\times\,b_j(\text{will})$ | $v_2(j)$ | backpointer |
|---|---|---|---|---|
| MD | 8.854e-6 × 0.0110 = 9.74e-8 | × 0.308431 | **3.004e-8** | NNP |
| VB | 8.854e-6 × 0.0009 = 7.97e-9 | × 0.000028 | 2.231e-13 | NNP |
| NN | 8.854e-6 × 0.0584 = 5.17e-7 | × 0.000200 | 1.034e-10 | NNP |
| NNP, JJ, RB, DT | | × 0 | 0 | |

Max is MD → "will" is a modal. **CHECK:** the slide writes the NN transition as ".058 = 5.14e-7"; with the printed .058 the product would be 1.028e-10, while the slide's 1.034e-10 uses the exact 0.0584. Rounding in display only.

Columns 3-5 (my full recomputation; the slide shows only the final best row):

| Column | all non-zero cells (value, best previous tag) |
|---|---|
| 3 "back" | VB 1.609e-11 (MD), RB 5.328e-11 (MD), JJ 5.107e-15 (MD), NN 5.359e-15 (MD) |
| 4 "the" | DT 1.816e-12 (VB), NNP 2.486e-17 (VB) |
| 5 "bill" | NN 2.014e-15 (DT), VB 1.017e-20 (DT) |

(computed with unrounded intermediates; reusing the rounded values shifts the last digit) e.g. $v_3(\text{VB})=3.004\text{e-}8\times0.7968\times0.000672=1.609\text{e-}11$; $v_4(\text{DT})=1.609\text{e-}11\times0.2231\times0.506099=1.816\text{e-}12$; $v_5(\text{NN})=1.816\text{e-}12\times0.4744\times0.002337=2.014\text{e-}15$.

Slide summary row [slide 28]: best tag NNP, MD, VB, DT, NN with $v$ = 8.854e-6, 3.004e-8, 1.609e-11, 1.816e-12, 2.014e-15; backpointers (start), NNP, MD, VB, DT. All match my recomputation.
**CHECK:** the slide calls these "the maximum v of each column", but in column 3 the largest cell is **RB = 5.328e-11**, not VB 1.609e-11. The slide row actually lists the cells on the final path. This is fine for Viterbi because the answer comes from backtracing from the last column: the RB route loses at "the" (5.328e-11 × 0.0479 × 0.506099 = 1.29e-12 < 1.816e-12 via VB, because P(DT∣VB) = 0.2231 is much larger than P(DT∣RB) = 0.0479).

**Backtrace** [slide 28]: bill → NN (best), back to DT, VB, MD, NNP: **Janet/NNP → will/MD → back/VB → the/DT → bill/NN** (probability 2.014e-15; matches).

**Complexity** [slide 29] (N = sentence length, T = number of tags): brute force $O(T^N)$ tag sequences; Viterbi fills an $N\times T$ table, each cell compares $T$ previous tags: $O(N\,T^2)$. For N=5, T=7: $7^5=16{,}807$ vs $5\times7^2=245$, about **68.6×** faster [computed: 16807/245 = 68.6, correct]. The gap grows exponentially with sentence length.

## 7. Conditional Random Fields (CRF) [slides 30-31]

Why CRF when HMM exists [slide 30]: HMM is **generative** (models $P(W\mid T)P(T)$, then uses Bayes to get $P(T\mid W)$); it sees one word at a time (cannot use features such as look → looking) and looks only at the previous word (the slide's wording; [general] in an HMM this is the previous tag), so it cannot capture other relationships. CRF is **discriminative**: models $P(T\mid W)$ directly, so it accepts arbitrary features. The slide's version is a **linear-chain CRF**: a log-linear model like logistic regression, extended to whole sequences.

$$\hat Y=\arg\max_{Y\in\mathcal Y}P(Y\mid X)\ (17.22),\qquad p(Y\mid X)=\frac{1}{Z(X)}\exp\Big(\sum_{k=1}^{K}w_kF_k(X,Y)\Big)\ (17.24),\qquad Z(X)=\sum_{Y'\in\mathcal Y}\exp\Big(\sum_{k=1}^{K}w_kF_k(X,Y')\Big)\ (17.25)$$

- $w_k$ = weight of feature $k$; $Z(X)$ = normalization term (the slide labels it "Z(W)" in the legend); $F_k(X,Y)$ = global feature function. [general] $F_k(X,Y)=\sum_i f_k(y_{i-1},y_i,X,i)$, the sum of local features over positions (not written on the slide).

**Feature functions** [slide 31]: $f_k$ at position $i$ may depend on $(y_{i-1},y_i,X,i)$. For "Janet/NNP will/MD back/VB the/DT bill/NN" with $x_i=$ "back", three active (=1) features: f3743: $y_i$=VB and $x_i$="back"; f156: $y_i$=VB and $y_{i-1}$=MD; f99732: $y_i$=VB and $x_{i-1}$="will" and $x_{i+2}$="bill".
Features that help with **unknown words**: word shape (lowercase → x, uppercase → X, digit → d; "I.M.F." → X.X.X., "DC10-30" → XXdd-dd [computed: correct]); prefix/suffix features of length up to 2-3 characters (e.g. "-ing", "-ly", "un-"). The slide states CRF is much more accurate than HMM in practice because it combines such features systematically.

**Comparison** [slide 32]:

| Approach | Model type | Strengths | Limits |
|---|---|---|---|
| Rule-based (+ Brill TBL) | knowledge-based / hybrid | explainable, little data needed | laborious to write, hard to scale |
| HMM | generative (models $P(W,T)$) | learns from data, fast decoding with Viterbi | hard to add special features, strict independence assumptions |
| CRF | discriminative (models $P(T\mid W)$ directly) | free features, more accurate than HMM | slower to train, needs enough labeled data |

## 8. Sequence labeling [slides 34-35]

Definition [slide 35]: assign a label $y_i$ to **every** input $x_i$ of $X=x_1\dots x_n$; the output $Y=y_1\dots y_n$ always has the same length as the input. Labels depend on neighbouring tokens as well as the token itself [slide 34]. Tools: HMM, CRF, or neural sequence models (RNN/Transformer).

| Task | $x_i$ | $y_i$ |
|---|---|---|
| POS tagging | word | POS tag (NNP, VB, ...) |
| NER | word | entity type (B-PER, O, ...) |
| Word segmentation | character | word boundary (B/I) |
| Chunking / shallow parsing | word | phrase part (NP, VP, ...) |

## 9. Named entity recognition (NER) [slides 34, 36-39]

**NER** = find and classify **spans** of text that refer to proper names [slide 36]. It also has a segmentation problem, because an entity can be several words. Uses: question answering, sentiment analysis, information extraction, linking to a knowledge base (Wikipedia/Knowledge Graph).

| Type | Meaning | Examples (slide) |
|---|---|---|
| PER | person | สมชาย, Marie Curie |
| ORG | organization/company | Google, จุฬาลงกรณ์มหาวิทยาลัย |
| LOC | geographic place | ภูเขา, แม่น้ำ, Sunshine Canyon |
| GPE | country/state/city | กรุงเทพ, Palo Alto |

**Type ambiguity** [slide 36]: "Washington" may be PER (George Washington), ORG (a sports team) or LOC/GPE (the city); context decides.

**Tagging schemes** [slide 37]: B = beginning of an entity, I = inside, O = outside, E = end, S = single-token entity. The slide states #tags $=2n+1$ for $n$ entity types, listed under the tag legend without naming a scheme; [general] this is the BIO count (n × {B,I} + O). [general] IO has $n+1$ tags, BIOES has $4n+1$.

Slide example "Jane Villanueva of United Airlines Holding discussed the Chicago route":

| Word | IO | BIO | BIOES |
|---|---|---|---|
| Jane | I-PER | B-PER | B-PER |
| Villanueva | I-PER | I-PER | E-PER |
| of | O | O | O |
| United | I-ORG | B-ORG | B-ORG |
| Airlines | I-ORG | I-ORG | I-ORG |
| Holding | I-ORG | I-ORG | E-ORG |
| discussed, the | O | O | O |
| Chicago | I-LOC | B-LOC | S-LOC |
| route | O | O | O |

The other example [slide 34]: John/B-PER lives/O in/O New/B-LOC York/I-LOC.

**Thai BIO example** [slide 38]: segment words first (Thai has no spaces), then tag. Tokens and tags: นาย/O, สมชาย/B-PER, เรียน/O, ที่/O, ซอฟแวร์/B-ORG, ปาร์ค/I-ORG, ใน/O, กรุงเทพ/B-LOC. "นาย" (title) is not part of the proper name, so it is tagged O.
**CHECK (slide 38 is inconsistent):** (1) the stated sentence is "นายสมชายทำงานที่บริษัทกูเกิลในกรุงเทพ" (Mr. Somchai works at Google in Bangkok), but the tokens shown are "นาย สมชาย เรียน ที่ ซอฟแวร์ ปาร์ค ใน กรุงเทพ" ("studies at Software Park in Bangkok"); the tokens are not the segmentation of the stated sentence. (2) The explanation text says "ปาร์ค → B-ORG (end of the organization name)" but the tag chip says I-ORG; I-ORG is correct for BIO. (3) "ซอฟแวร์" is non-standard spelling of "ซอฟต์แวร์". Treat the token row as the intended example.

## 10. NER evaluation [slide 39]

Entity level (an entity counts only if the whole span and type are right) [general detail; slide says only "at the entity level"]:

$$P=\frac{TP}{TP+FP},\qquad R=\frac{TP}{TP+FN},\qquad F_1=\frac{2PR}{P+R}\ (4.42)$$

- $P$: of all entities the system predicted, the fraction that is correct; $R$: of all true entities, the fraction found; $F_1$ = harmonic mean of $P$ and $R$.
- Slide figure 4.7 is the confusion matrix (system positive/negative vs gold positive/negative) with precision = tp/(tp+fp), recall = tp/(tp+fn), accuracy = (tp+tn)/(tp+fp+tn+fn).
- [computed, made-up numbers] If the gold has 3 entities and the system outputs 4, of which 2 match exactly: P = 2/4 = 0.5, R = 2/3 = 0.667, F1 = 2·2/(4+3) = 0.571 (since $F_1=2TP/(2TP+FP+FN)$).

## 11. Project relevance and practical notes

- **Stage 0 (HIGH):** every later stage (Naive Bayes counts, TF-IDF) depends on the word boundaries. The slides' ranking (maximum matching < statistical < HMM/CRF < deep learning, slide 11) explains why PyThaiNLP offers several engines. [general] The default `newmm` engine is dictionary-based maximal matching, so it inherits the dictionary-coverage weakness of section 2; ML engines such as `deepcut` need extra dependencies.
- [general] Weather reports contain place names, technical terms and numbers that a generic dictionary may cut wrongly. The usual fix is a custom dictionary of province/region names and weather terms (PyThaiNLP accepts one). Inspect segmentation on a sample of reports, as in the "ตากลม" ambiguity: if two engines (or FMM vs BMM) disagree on a sentence, check that sentence by hand.
- [general] Word segmentation = per-character B/I labeling (slide 35), the same framework as NER and POS; this is how CRF/neural segmenters work.
- [general] NER could extract LOC/GPE entities (provinces, seas) and dates from TMD text as extra features for Stage-1 classification or as slots for the Stage-2 templates; this needs a Thai NER model, which is outside the planned scope.
- The P/R/F1 formulas here are the same as the classifier metrics in Stage 1 (ML evaluation notes).
- The statistical segmenter is the unigram case of the n-gram model in [5-1](5-1-language-models-ngrams.md); the segmentation notes in [1-2](1-2-tokenization.md) cover dictionary-based tokenization in PyThaiNLP.
- Exam reminders: FMM/BMM steps, the argmax of the product of word probabilities (recompute ตา+กลม vs ตาก+ลม), HMM = $Q,A,B,\pi$ + two assumptions, the Viterbi recurrence, backtrace, $O(NT^2)$ vs $O(T^N)$, HMM vs CRF (generative vs discriminative), BIO tagging, and P/R/F1.
