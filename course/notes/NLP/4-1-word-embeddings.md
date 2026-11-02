# NLP 4-1 — Word Embeddings and Vector Representations

Source: `course/slides/4-1_Word_Embeddings.pdf` (38 slides, Satida Sookpong; title slide shows course code 1323326 NLP). Text from the PDF text layer (Thai tone marks partly missing there, so Thai wording is paraphrased in English); formulas, matrices and tables were read from slide images, and every numeric example was re-computed in Python.
Legend: **[slide N]** = PDF page · **[general]** = general knowledge or my inference (NOT said by the lecturer) · **[computed]** = my own calculation.

**Project relevance: HIGH for two parts.** Cosine similarity (section 4) and TF-IDF (section 6) are exactly the Stage 2 tools (TF-IDF + cosine extractive summary). The rest (PMI, word2vec, fastText, contextual embeddings, drift) is background, an optional "dense vector" upgrade, or exam material. [general]

**Slide-vs-slide discrepancies to know about (details in the sections):**
1. TF-IDF: formula (11.4) says $\text{tf}=1+\log_{10}\text{count}$, but the worked example actually uses $\text{tf}=\log_{10}(\text{count}+1)$ (section 6).
2. Weighted-PMI slide: (แมว, กิน) is printed as 0.244; the exact value is 0.243 (section 5).

---

## 1. From one-hot to dense vectors [slide 3]

Slide 2 is only an intro minigame ("Contexto", Thai version; the slide says to search "contexto ภาษาไทย"). [general] It is a word-guessing game that ranks guesses by embedding similarity.

| | One-hot (sparse) | Dense embedding |
|---|---|---|
| Size | $\lvert V\rvert$ dimensions, may reach 50,000 | $d$ = 50-1000 (100-300 typical) |
| Example | แมว = [1,0,0,0,...,0], หมา = [0,1,0,0,...,0] | แมว = [0.21,-0.44,0.67,...], หมา = [0.19,-0.41,0.71,...], คน = [-0.55,0.32,-0.12,...] |
| Values | 0/1 | real, positive and negative |
| Similarity | every pair orthogonal: แมว·หมา = 0 = แมว·คอมพิวเตอร์, so **no notion of semantic similarity**; all words equally far apart | words with close meaning get close vectors (แมว·หมา high, แมว·คอมพิวเตอร์ low) |
| Unseen word (OOV) | cannot be represented | still a problem for plain word vectors (see fastText, section 9) [general] |
| Parameters | huge | far fewer, so downstream models learn better and overfit less; handles synonyms (car / automobile are near) |

## 2. Distributional hypothesis, contexts, collocations [slides 4-6]

- **Firth (1957):** "You shall know a word by the company it keeps." Words that occur in similar contexts tend to have similar meaning. [slide 4]
- Slide 4 demo: three Thai sentences containing the unknown word "ตงฉ่าย"; from context alone you guess it is a salty food. This is the same principle a computer uses.
- Two kinds of similarity between words [slide 4]:
  - **paradigmatic** (substitutable): appear in similar positions, e.g. ไทย ↔ ญี่ปุ่น.
  - **syntagmatic** (co-occurring): appear together in a sentence, e.g. ไทย ↔ กรุงเทพ.
- **Collocation** [slide 5]: a pair that appears together more often than chance would give. Slide examples: "น้ำ+ตก", "ตั้ง+ใจ", "ทำ+งาน", "ข้าว+ผัด". Raw frequency cannot show which pairs are interesting, because words like "ที่" and "และ" co-occur with everything. We need a measure that **subtracts chance**: PMI (section 5).
- Three ways to define "context" [slide 6]:

| Context | Meaning | Effect |
|---|---|---|
| Document | whole document/article is one context | topical relations (e.g. "หมอ" with "โรงพยาบาล") |
| Window ±k words | k words around the target | small k (±2) gives syntax-like similarity |
| Syntactic | dependency relations from a parse | most precise, but needs a parser first and is costly |

## 3. Co-occurrence matrices [slides 7-8]

1. **Term-document matrix** [slide 7]: rows = words, columns = documents, cell = how many times the word occurs in the document. Two documents are similar if their **column vectors** are similar (used in information retrieval). Weight with **TF-IDF** instead of raw counts.
2. **Term-term (word-context) matrix** [slide 8]: rows = target words, columns = context words, cell = number of co-occurrences within the window. Size $\lvert V\rvert\times\lvert V\rvert$, extremely sparse (mostly zeros). Weight with **PPMI** instead of raw counts ("we will use this one").

Slide figures (from the Jurafsky and Martin textbook): word-count vectors over context words (e.g. digital and information vs. computer, data, pie, sugar) and a 2-D plot of "digital" = [1683, 1670] and "information" = [3982, 3325] on the axes data and computer. [slide 7-8; figure values confirmed at 2x zoom]

Rule of thumb on the slides: **TF-IDF goes with term-document, PPMI with term-term.** [slide 13]

## 4. Cosine similarity [slide 9]

$$\cos(\mathbf v,\mathbf w)=\frac{\mathbf v\cdot\mathbf w}{\lVert\mathbf v\rVert\,\lVert\mathbf w\rVert}=\frac{\sum_{i=1}^{N}v_iw_i}{\sqrt{\sum_{i=1}^{N}v_i^2}\;\sqrt{\sum_{i=1}^{N}w_i^2}}\qquad(5.10)$$

Derived from the dot product $\mathbf a\cdot\mathbf b=\lVert\mathbf a\rVert\lVert\mathbf b\rVert\cos\theta$. Meaning of symbols [general]: $\mathbf v,\mathbf w$ = the two vectors, $N$ = number of dimensions, $\lVert\cdot\rVert$ = Euclidean (L2) length.

- For **non-negative** vectors (the slide says frequency counts) the value lies in **[0, 1]**: 1 = same direction, 0 = orthogonal. [slide 9] The same holds for PPMI and TF-IDF vectors, and "orthogonal" here means no shared non-zero dimension. [general]
- Dividing by the lengths removes the effect of vector length (e.g. frequent words have big raw dot products). [general]
- For dense embeddings with negative entries the range is [-1, 1]. [general]

**Worked example** (term-term counts, "hypothetical numbers for teaching") [slide 9]:

| | กิน | อาหาร | อ่าน | หนังสือ | row total |
|---|---|---|---|---|---|
| แมว | 50 | 30 | 1 | 0 | 81 |
| หมา | 45 | 35 | 0 | 1 | 81 |
| คน | 40 | 25 | 35 | 50 | 150 |

Step by step, $\mathbf{แมว}=[50,30,1,0]$, $\mathbf{หมา}=[45,35,0,1]$:
- dot = 50(45) + 30(35) + 1(0) + 0(1) = 2250 + 1050 = 3300
- $\lVert$แมว$\rVert=\sqrt{2500+900+1+0}=58.318$, $\lVert$หมา$\rVert=\sqrt{2025+1225+0+1}=57.018$
- cos = 3300 / (58.318 × 57.018) = **0.9924** (very similar)

All pairs on the slide: cos(แมว,หมา) = 0.9924, cos(แมว,คน) = 0.6191, cos(หมา,คน) = 0.6196. Interpretation on the slide: cat and dog (animals that eat) are more similar to each other than either is to คน, learned from raw numbers only.

[computed] All three values and the intermediate numbers re-checked: dot(แมว,หมา) = 3300, norms 58.318 / 57.018 / 77.136 (คน), cosines 0.99244 / 0.61910 / 0.61958. **All match the slide.**

## 5. PMI and PPMI [slides 10-12]

**Problem with raw counts** [slide 10]: very frequent words ("ที่", "และ", "เป็น") co-occur with everything, so high counts say nothing about meaning. We want to ask "do they co-occur **more often than expected**?"

$$\text{PMI}(w,c)=\log_2\frac{P(w,c)}{P(w)\,P(c)}\qquad(6.14)$$

$$\text{PPMI}(w,c)=\max\!\Big(\log_2\frac{P(w,c)}{P(w)\,P(c)},\,0\Big)\qquad(6.15)$$

- $P(w,c)=f(w,c)/N$ = observed joint probability, $N$ = sum of the whole matrix; $P(w)$ = row total / $N$, $P(c)$ = column total / $N$ (as used in the slide-11 example). $P(w)P(c)$ = value expected if independent. **Log base 2** on these slides.
- PMI > 0: co-occur **more** than expected (really associated). PMI = 0: exactly as expected (independent). PMI < 0: **less** than expected, but such estimates are **unreliable** (needs a huge corpus to confirm). [slide 10]
- **PPMI** = clip negatives to 0 because they are unreliable. The PPMI row is used as the word's vector. [slide 10-11]

**Worked example** (same matrix as section 4 with the extra column total) [slide 11]:
- Totals: row 81, 81, 150; columns กิน 135, อาหาร 90, อ่าน 36, หนังสือ 51; **N = 312**.
- Cell (แมว, กิน): P(แมว,กิน) = 50/312 = 0.1603; P(แมว) = 81/312 = 0.2596; P(กิน) = 135/312 = 0.4327; PMI = log₂(0.1603 / (0.2596 × 0.4327)) = log₂(1.4266) = **0.513**.
- Repeat for every cell, then clip negatives:

| PMI | กิน | อาหาร | อ่าน | หนังสือ |
|---|---|---|---|---|
| แมว | 0.513 | 0.361 | -3.224 | -∞ |
| หมา | 0.361 | 0.583 | -∞ | -3.727 |
| คน | -0.698 | -0.791 | 1.016 | 1.028 |

PPMI = same table with every negative or -∞ entry replaced by 0 (so แมว = [0.513, 0.361, 0, 0], หมา = [0.361, 0.583, 0, 0], คน = [0, 0, 1.016, 1.028]). Slide conclusion: with PPMI, cos(แมว,หมา) = 0.92 but cos(แมว,คน) = 0.00, so PPMI separates semantic groups much better than raw counts.

[computed] All 12 PMI cells match the slide (zero counts give -∞). cos_PPMI(แมว,หมา) = 0.9196 (slide: 0.92 OK), cos_PPMI(แมว,คน) = 0.0000 OK, cos_PPMI(หมา,คน) = 0.0000 (not shown on slide). Compare raw counts: cos(แมว,คน) was 0.619, so PPMI moves it to 0 because the only positive cells of คน are อ่าน and หนังสือ, while its (negative) กิน/อาหาร cells are clipped.

**PMI is biased toward rare events** [slide 12], with a second matrix (columns กิน, อาหาร, อ่าน, เหมียว; N = 262; rows แมว 82, หมา 80, คน 100; column totals 135, 90, 36, 1):

| Pair | Slide calculation | Slide result | [computed] exact |
|---|---|---|---|
| แมว-กิน | log₂[(262×50)/(82×135)] = log₂(13100/11070) = log₂(1.1834) | ≈ 0.244 | **0.2429** (slide rounds wrongly; should read ≈ 0.243) |
| แมว-อาหาร | log₂(7860/7380) = log₂(1.0650) | ≈ 0.091 | 0.0909 OK |
| แมว-อ่าน | log₂(262/2952) = log₂(0.0888) | ≈ -3.494 | -3.4941 OK |
| แมว-เหมียว | log₂(262/82) = log₂(3.1951) | ≈ 1.676 | 1.6759 OK |

Point of the example: (แมว, เหมียว) occurs only once yet gets the **highest** PMI (1.676) because the context word เหมียว is itself extremely rare (column total 1).

Two fixes listed on the slide [slide 12]:
1. **K-smoothing:** add 2 (k = 2) to every cell.
2. **Context distribution smoothing:** give rare context words a higher probability:

$$P_\alpha(c)=\frac{\text{count}(c)^{\alpha}}{\sum_{c'}\text{count}(c')^{\alpha}}$$

The slide does not state $\alpha$ and does not compute any smoothed PMI. [general] A common choice is $\alpha=0.75$, and PMI then uses $P_\alpha(c)$ in place of $P(c)$ in the denominator.
[computed] Illustration on the slide-12 matrix: with add-2 smoothing (N becomes 286) PMI(แมว,เหมียว) drops from 1.676 to 0.446 and PMI(แมว,อ่าน) rises from -3.494 to -2.139; with $\alpha=0.75$, $P_\alpha(\text{เหมียว})$ = 0.0118 instead of 0.0038 and PMI(แมว,เหมียว) drops to 0.044. (Both confirm the intended effect: the rare-pair bonus shrinks.)

## 6. TF-IDF [slide 13]

Purpose: weight words in a **term-document matrix**: high score for a word that is **frequent in this document but rare in other documents**; low score for words found everywhere (e.g. "ที่", "และ", "การ"). The slide also notes that two common term-weighting schemes are tf-idf and its variant **BM25** (no BM25 formula is given).

**Formulas exactly as printed on the slide:**

$$\text{tf}_{t,d}=\begin{cases}1+\log_{10}\text{count}(t,d)&\text{if }\text{count}(t,d)>0\\ 0&\text{otherwise}\end{cases}\qquad(11.4)$$

$$\text{idf}_t=\log_{10}\frac{N}{\text{df}_t}\qquad(11.5)$$

$$\text{tf-idf}(t,d)=\text{tf}_{t,d}\cdot\text{idf}_t\qquad(11.6)$$

- $\text{count}(t,d)$ = number of times term $t$ occurs in document $d$ ("tf: how often t occurs in d").
- $N$ = total number of documents; $\text{df}_t$ = number of documents that contain $t$ at least once.
- **Log base 10** for both tf and idf. **No smoothing** (no +1 in idf's numerator or denominator) and **no normalization step** (no L2-normalization of document vectors) appears on the slide. A term that occurs in all documents gets idf = log₁₀(N/N) = 0, so its tf-idf is 0 (the "ที่" case).

**Worked example from the slide** (N = 3 documents):

| word | d1 | d2 | d3 | df | idf = log₁₀(3/df) |
|---|---|---|---|---|---|
| เป็ด | 3 | 2 | 0 | 2 | 0.176 |
| ที่ | 10 | 8 | 9 | 3 | 0 |
| รถ | 0 | 0 | 5 | 1 | 0.477 |

| Cell | tf as shown on slide | × idf | TF-IDF on slide |
|---|---|---|---|
| (เป็ด, d1) | log₁₀ 4 = 0.602 | × 0.176 | 0.106 |
| (ที่, d1) | log₁₀ 11 = 1.041 | × 0 | 0 |
| (รถ, d3) | log₁₀ 6 = 0.778 | × 0.477 | 0.371 |

**Discrepancy found [computed]:** the tf column uses $\log_{10}(\text{count}+1)$ (counts 3, 10, 5 become log₁₀ 4, log₁₀ 11, log₁₀ 6), **not** formula (11.4) $1+\log_{10}\text{count}$. The slide's final numbers (0.106, 0, 0.371) are arithmetically correct for the log₁₀(count+1) version. Using the printed formula (11.4) instead gives:

| Cell | count | tf by (11.4) | idf | tf-idf by (11.4) | slide (log10(count+1)) |
|---|---|---|---|---|---|
| (เป็ด, d1) | 3 | 1 + log₁₀ 3 = 1.477 | 0.1761 | **0.260** | 0.106 |
| (ที่, d1) | 10 | 1 + log₁₀ 10 = 2.000 | 0 | 0 | 0 |
| (รถ, d3) | 5 | 1 + log₁₀ 5 = 1.699 | 0.4771 | **0.811** | 0.371 |

So "tf = log₁₀(1+count)" is what the lecturer **calculates**, "tf = 1 + log₁₀(count)" is what the lecturer **writes** as the definition (the equation number 11.4 suggests a Jurafsky and Martin textbook form, but the slide does not name its source [general]). Whichever the project uses, state it explicitly. Both agree that count = 0 gives tf = 0, and both give identical document-vector directions in this toy case.

[computed] Document vectors over (เป็ด, ที่, รถ) using the slide's tf variant: d1 = (0.106, 0, 0), d2 = (0.084, 0, 0), d3 = (0, 0, 0.371). Cosine similarity of **raw counts** d1=[3,10,0], d2=[2,8,0], d3=[0,9,5]: cos(d1,d2) = 0.999, cos(d1,d3) = 0.837, cos(d2,d3) = 0.848 (dominated by the stop-word-like "ที่"). With TF-IDF (either tf variant): cos(d1,d2) = 1.0, cos(d1,d3) = 0, cos(d2,d3) = 0. This shows idf removing the common word's influence (in this toy only one informative dimension survives per document).

[general] Other common variants, **not on the slides**: scikit-learn's `TfidfVectorizer` default is tf = raw count, idf = ln((1+N)/(1+df)) + 1 (natural log, smoothed, so a word in every document still has idf = 1), followed by L2-normalizing each document vector. For the slide's df values (2, 3, 1 with N = 3) that idf would be 1.288, 1.000, 1.693 ([computed]). Numbers from such a library will therefore not match the slide.

## 7. Explicit vs. implicit representations [slide 14]

| Aspect | Explicit / sparse (count-based) | Implicit / dense (prediction-based) |
|---|---|---|
| Examples | co-occurrence counts, tf-idf, PPMI, LSA | word2vec, GloVe, fastText |
| Dimensions | $\lvert V\rvert$: tens of thousands to hundreds of thousands | $d$ = 50-1000 (100-300 typical) |
| Interpretable dimensions? | yes, each dimension is one context word | no, dimensions have no clear meaning |
| Values | non-negative (frequency or PPMI) | positive and negative |
| How obtained | count directly from the corpus | train a model to predict context |
| Downstream performance | usable but worse | better on almost every NLP task |

## 8. word2vec (skip-gram with negative sampling) [slides 15-19]

**Idea** [slide 16]: instead of counting how often context words appear near a target, train a classifier to predict "will this word appear near the target?", then **keep the learned weights as the embedding** (the predictions themselves are not used).

**Self-supervision** [slide 16]: no human labels needed; plain text is the training data.
- Words that really appear near "แมว" in the text = correct answers (positive examples).
- Random words drawn from the vocabulary = wrong answers (negative examples).
- Train **logistic regression** to separate the two; the weights are the embeddings.

**Architectures** [slide 16]:
- **Skip-gram:** use the center word to predict the surrounding context words. Better for rare words and small corpora.
- **CBOW (Continuous Bag-of-Words):** use the surrounding context to predict the center word. Faster, better for frequent words.

**Skip-gram model** [slide 17]: $w$ = target word, $c$ = context or noise word.

$$P(+\mid w,c)=\sigma(\mathbf c\cdot\mathbf w),\qquad \sigma(x)=\frac{1}{1+e^{-x}}$$

The higher the dot product, the more likely the pair is a real neighbour. Two embedding matrices are learned: the target matrix $\mathbf W$ and the context+noise matrix $\mathbf C$ (parameter $\theta$ = a $2\lvert V\rvert\times d$ matrix, Figure 5.6). [computed] σ(0) = 0.5, σ(2) = 0.881, σ(-2) = 0.119.

Slide example (Figure from the textbook, window $L=\pm2$): "... lemon, a [tablespoon of **apricot** jam, a] pinch ..." gives 4 positive instances (apricot, tablespoon), (apricot, of), (apricot, jam), (apricot, a), each paired with sampled negatives (e.g. apricot with aardvark, my, where, coaxial, seven, forever, dear, if; 2 negatives per positive in that figure).

**Loss for one positive pair and $k$ noise words** [slide 18]: binary classification "real pair (+) or fake pair (-)".

$$L(w,c_{pos},c_{neg_{1..k}})=-\log\Big[P(+\mid w,c_{pos})\prod_{i=1}^{k}P(-\mid w,c_{neg_i})\Big]=-\Big[\log\sigma(c_{pos}\cdot w)+\sum_{i=1}^{k}\log\sigma(-c_{neg_i}\cdot w)\Big]\qquad(5.21)$$

**Gradient-descent updates** ($\eta$ = learning rate, $t$ = step):

$$\mathbf c_{pos}^{t+1}=\mathbf c_{pos}^{t}-\eta\big[\sigma(\mathbf c_{pos}^{t}\cdot\mathbf w^{t})-1\big]\mathbf w^{t}\qquad(5.25)$$

$$\mathbf c_{neg_i}^{t+1}=\mathbf c_{neg_i}^{t}-\eta\big[\sigma(\mathbf c_{neg_i}^{t}\cdot\mathbf w^{t})\big]\mathbf w^{t}\qquad(5.26)$$

$$\mathbf w^{t+1}=\mathbf w^{t}-\eta\Big[\big(\sigma(\mathbf c_{pos}^{t}\cdot\mathbf w^{t})-1\big)\mathbf c_{pos}^{t}+\sum_{i=1}^{k}\sigma(\mathbf c_{neg_i}^{t}\cdot\mathbf w^{t})\,\mathbf c_{neg_i}^{t}\Big]\qquad(5.27)$$

Intuition (Figure 5.7): each step moves the target closer to its true context word (apricot and jam) and pushes it away from noise words (apricot vs. matrix, Tolstoy).

**Algorithm in steps** [slides 16-18; items marked [general] are not on the slides]:
1. Slide a window over the segmented corpus; each (target, neighbour) is a positive pair.
2. For each positive pair, sample $k$ noise words as negative pairs. [general: noise words are usually drawn from a smoothed unigram distribution]
3. Score pairs with $\sigma(c\cdot w)$ and compute loss (5.21).
4. Update $\mathbf w$, $\mathbf c_{pos}$, $\mathbf c_{neg_i}$ with (5.25)-(5.27). [general: vectors start random]
5. Repeat over the corpus for several epochs; keep the learned vectors as embeddings. [general: usually $\mathbf W$, sometimes $\mathbf W+\mathbf C$]

The slide also writes the famous analogy as an annotation: $v(\text{king})-v(\text{man})+v(\text{woman})\approx v(\text{queen})$ (see section 11).

**Hyperparameters** [slide 19]:

| Parameter | Typical value | Effect |
|---|---|---|
| dimension $d$ | 100-300 | larger captures finer meaning but needs more data, overfitting risk |
| window size | ±2 to ±10 | small window gives syntactic similarity; large window gives topical similarity |
| negative samples $k$ | 5-20 | small corpus: larger k (15-20); large corpus: k = 2-5 is enough |
| min count | 5 | drop words rarer than this (less noise, smaller model) |
| subsampling $t$ | 1e-3 to 1e-5 | randomly drop very frequent words (e.g. "ที่", "และ") so the model focuses on informative words |
| epochs | 5-15 | more helps small corpora; one pass is often enough for large ones |
| learning rate $\eta$ | 0.025 (decreasing) | too high diverges, too low learns slowly |

**Thai warning on the slide** [slide 19]: always **segment words correctly first** (week 2 topic). If segmentation is wrong, all the embeddings are wrong; this is "where Thai pipelines most often break".

## 9. fastText and GloVe (other static embeddings) [slides 20-21]

**fastText** (Bojanowski et al., 2017) [slide 20]
- Word2vec problems: unseen (OOV) words have no vector; rare words get poor vectors; in languages with heavy inflection every form is a separate word although the root is the same.
- Fix: represent a word as the **sum of the vectors of its character n-grams** (plus the whole word). Same skip-gram architecture, only the word representation changes. An unseen word can still be composed from known pieces.
- Examples with n = 3 (with boundary markers < >): "where" → `<wh, whe, her, ere, re>` + `<where>`; Thai "ความสุข" → `<คว, ควา, วาม, ามส, มสุ, สุข, ุข>` + `<ความสุข>`. The unseen "ความสงบ" still shares `<คว`, `ควา`, `วาม` with seen words.
- Slide claim: well suited to Thai because Thai constantly forms compounds (ความ+สุข, นัก+เรียน, การ+ทำงาน). Site: fasttext.cc.
- [general] [computed] The n-grams are over Unicode code points, so Thai vowel marks split into odd pieces such as `ุข>`; the 7 trigrams listed match what a code-point sliding window gives for `<ความสุข>`.

**GloVe** (Global Vectors for Word Representation) [slide 21]
- Word2vec looks at one window at a time; GloVe uses **global co-occurrence statistics**; a log-bilinear model; uses **ratios** of co-occurrence probabilities rather than the probabilities themselves. (The slide gives no GloVe loss formula.) Site: nlp.stanford.edu/projects/glove.
- Slide table (from the GloVe paper): P(k | ice) vs P(k | steam) for k = solid, gas, water, fashion. Ratios on the slide: 8.9, 8.5×10⁻², 1.36, 0.96. [general] How to read the ratio (from the GloVe paper, not stated on the slide): large ratio = k relates to ice, small = relates to steam, near 1 = unrelated or shared.
- [computed] Dividing the rounded probabilities printed on the slide gives 8.64, 0.0846, 1.364, 0.944, so the printed 8.9 and 0.96 come from unrounded source values (minor, not an error).

## 10. Contextual embeddings [slides 22-26]

- **Problem of static embeddings (polysemy)** [slide 23]: "ขัน" has three meanings: "ไก่ขันตอนตีห้า" = crow (rooster sound), "เรื่องนี้น่าขันจริงๆ" = funny, "ตักน้ำด้วยขันใบเล็ก" = a bowl (vessel). A static model gives one vector E["ขัน"] for all.
- **Type vs. instance** [slide 24]: static embeddings represent the meaning of word **types** (vocabulary entries); contextual embeddings represent the meaning of word **instances**: a particular word type in a particular context.

| | Static (word2vec, GloVe, fastText) | Contextual (ELMo, BERT) |
|---|---|---|
| Vector per | word type: 1 vector per vocabulary word | word instance: 1 vector per word in each sentence |
| Ambiguity | all senses mixed in one vector | separated by context |
| Typical size | 50-300 dims | 768 (BERT-base), 1024 (ELMo, BERT-large) |
| Training goal | predict neighbouring words / factorize co-occurrence | language model: predict next word (ELMo) or masked word (BERT) |
| Usage | feature fed to other models | feature, or fine-tune the whole model |
| Cost | very cheap | must run a deep network every time |

- Timeline [slide 26]: static = word2vec 2013, GloVe 2014, fastText 2017; contextual = ELMo 2018, BERT 2019, RoBERTa 2019. [general] The BERT paper first appeared in 2018 (the 2019 date is the conference publication).
- BERT is only mentioned in these comparisons; there is no architecture detail on the slides.

## 11. Evaluating embeddings, analogy, visualization [slides 27-29]

**Extrinsic** (most important, but expensive): use the embedding in a real task (text classification, NER, translation) and check whether results improve vs. alternatives. **Intrinsic** (fast, direct) [slide 28]: word similarity (compare model cosine with human scores), word analogy ($a:b::a^*:?$ by the parallelogram method), categorization/clustering (do words group into the right categories?).

Intrinsic example [slide 28] (human scores 0-10 vs. model cosine):

| Pair | Human | Rank | Model cosine | Rank |
|---|---|---|---|---|
| แมว-หมา | 9.0 | 1 | 0.92 | 1 |
| กิน-ทาน | 8.5 | 2 | 0.65 | 3 |
| รถ-รถยนต์ | 7.0 | 3 | 0.81 | 2 |
| แมว-หนังสือ | 3.0 | 4 | 0.30 | 4 |
| ปลา-คอมพิวเตอร์ | 1.5 | 5 | 0.12 | 5 |

The slide only shows the ranks; it does not compute a correlation. [general] Standard practice is Spearman rank correlation. [computed] Rank differences (0, 1, 1, 0, 0) give $\rho = 1-\frac{6\cdot 2}{5\cdot 24}=0.90$.

**Word analogy (parallelogram method)** [slide 29]: for $a:b::a^*:b^*$ find

$$\hat b^*=\arg\min_x\ \text{distance}(x,\ b-a+a^*)\qquad(5.28)$$

Examples on the slide: king − man + woman ≈ queen; กรุงเทพ − ไทย + ญี่ปุ่น ≈ โตเกียว. Figure: apple:tree :: grape:vine.

**Visualizing** [slide 29]: embeddings have 100-300 dimensions, reduce to 2-3 to plot. **PCA**: linear, fast, keeps the overall structure, good for main directions. **t-SNE**: non-linear, keeps near neighbours, shows word clusters clearly. **UMAP**: faster than t-SNE and keeps global structure better.

## 12. Bias and applications [slides 30-31]

- **Embedding bias** [slide 30]: Bolukbasi et al. (2016): "computer programmer" − "man" + "woman" gives "homemaker" as nearest word; also the analogy "father : doctor :: mother : nurse". Learned directly from the news text used for training.
  - **Allocational harm:** unfair allocation of resources (jobs, loans), e.g. a CV screener unintentionally lowers scores for documents with female names.
  - **Representational harm:** demeaning or ignoring groups, e.g. names of some ethnic groups have high cosine with negative words (Caliskan et al., 2017).
  - **Bias amplification:** embeddings do not only reflect bias in the data, they can amplify it beyond the real statistics.
  - Debiasing (removing the stereotype direction) reduces but does not eliminate bias; Gonen and Goldberg (2019) show it is only hidden deeper. Open problem.
- **Applications** [slide 31]: semantic search (search "รถ" and find "ยานพาหนะ"), sentiment analysis (embedding features instead of bag-of-words), NER/POS tagging (input layer of sequence labelers, helps unseen words), machine translation (cross-lingual embeddings underlie unsupervised MT), recommendation (item2vec: items bought in the same context are similar), diachronic analysis (second half of the lecture).

## 13. Semantic drift [slides 32-37]

(The "project" mentioned on slides 35-36, with periods 2010 and 2026, appears to be the slides' own diachronic-embedding example (slide wording "โปรเจกต์นี้"), not our weather-summary mini project [general reading].)

- **Definition** [slide 33]: the meaning of a word changes over time while the spelling stays the same, because the contexts people use it in change.
- Types and slide examples [slide 33]: **Broadening** ("เมาส์" mouse animal → also computer device); **Narrowing** (English "meat": any food → animal flesh); **Pejoration** (English "awful": awe-inspiring → very bad); **Amelioration** (Thai "ปัง": loud bang/bread → excellent); **Metaphorical** (Thai "เท": pour water → ditch a date or lover).
- Consequences: models trained on old data misunderstand current language; sentiment systems may misread "ปัง" or "เท"; measuring drift is also a tool for studying society and culture.
- Case study [slide 34], Hamilton et al. (2016): gay (1900 cheerful → 2000 homosexual), broadcast (1900 sowing seeds → 2000 radio/TV), awful (1850 awe-inspiring → 2000 terrible).
- **Method** [slide 35] (5 steps): (1) split the corpus by time period; (2) train word2vec/GloVe separately per period; (3) **align** the vector spaces (separately trained spaces differ by rotation/reflection); (4) measure change = cosine between a word's vectors across periods (lower cosine = more change); (5) qualitative check by looking at nearest neighbours in each period.
- **Statistical laws** [slide 36] (Hamilton, Leskovec and Jurafsky 2016): *Law of Conformity*: rate of change is inversely related to word frequency (frequent words like กิน, ไป, น้ำ change more slowly). *Law of Innovation*: controlling for frequency, polysemous words change faster. Practical warning: rare words show high apparent drift just because their vectors are noisy, so compare only words of similar frequency or use frequency-matched control words.
- **Data** [slide 37]: news corpora (dated, formal, consistent, plentiful; but slang like "ปัง"/"เท" may be rare; check terms of use and copyright); Thai National Corpus (Chulalongkorn, well annotated but limited time span); Wikipedia dumps (dated free snapshots, supplementary); OSCAR / mC4 (large multilingual web text incl. Thai); social media archive (best for slang, mind privacy and terms of use).
- **Library** [slide 38]: Gensim (slide gives a GeeksforGeeks tutorial link). Figure lists Gensim strengths: easy document similarity, efficient memory use, pre-trained embeddings, topic modeling, easy integration.

## 14. Project relevance and practical notes

**Stage 2 (TF-IDF + cosine summary) [general unless a slide is cited]:**
- Treat each **sentence as a "document"**; the term-sentence matrix gives each sentence a sparse TF-IDF vector. Sentence importance can be a sum or mean of its TF-IDF weights; redundancy or similarity to a "centroid" can be measured with cosine (5.10). Decide whether $N$ is the number of sentences in one report or in the whole corpus.
- With the lecturer's idf, $\log_{10}(N/\text{df})$ is **0 for any word in every sentence** and large for words in one sentence. With a small $N$ (a few sentences per report) idf values are coarse and noisy; consider computing idf over the whole report collection.
- **Be explicit about which tf variant you use** (printed formula vs. the slide's worked example; section 6). The expected outputs of the lecturer's example (0.106, 0, 0.371) require tf = log₁₀(count+1).
- Guard against zero vectors: a sentence whose words all have idf = 0 has norm 0, so cosine divides by zero. Add a small epsilon or skip it.
- Cosine on non-negative TF-IDF vectors lies in [0, 1] (slide 9 states this for non-negative frequency vectors). If you use library TF-IDF (e.g. scikit-learn), remember its defaults differ (section 6 [general] note).

**Thai-specific [slide 19 + general]:**
- Word segmentation (PyThaiNLP, Stage 0) must come first; wrong segmentation corrupts counts, TF-IDF and any embedding. Add weather terms (province names, "ร่องมรสุม") to the custom dictionary.
- Remove or down-weight stop words; TF-IDF already does this partly through idf, PPMI through the "expected" term (the slides' "ที่", "และ" examples).

**Optional dense upgrade (not required by the project) [general]:**
- Pretrained Thai embeddings (fastText Thai, thai2fit, see also the embedding-initialization note in [5-1](5-1-language-models-ngrams.md)) can give sentence vectors by averaging word vectors, then cosine similarity as in section 4. Because fastText uses character n-grams (slide 20), unseen weather terms still get vectors.
- Training word2vec from scratch on a small weather corpus is possible but weak; skip-gram with larger $k$ and more epochs is the lecture's advice for small corpora (slides 16, 19).

**Other uses of this chapter [general]:**
- PMI/PPMI can find weather collocations (e.g. "ฝน ตก" or "ร่อง มรสุม") from segmented reports (slide 5 uses "น้ำ+ตก" as a collocation example).
- Evaluation: slide 28's **extrinsic evaluation** logic is what the project does anyway, judging the summarizer by ROUGE/classifier F1 rather than by vector quality.
- Not needed for the pipeline: contextual embeddings (BERT), bias and semantic drift; useful as exam material.

**Quick formula sheet:** cosine (5.10) · PMI (6.14, log₂) · PPMI (6.15) · tf (11.4, log₁₀) · idf (11.5, log₁₀) · tf-idf (11.6) · skip-gram $P(+|w,c)=\sigma(c\cdot w)$ and loss (5.21) · analogy (5.28).
