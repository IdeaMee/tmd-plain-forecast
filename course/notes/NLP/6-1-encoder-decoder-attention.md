# NLP 6-1 — Encoder-Decoder (seq2seq), Evaluation Metrics and Attention

Source: `course/slides/6-1_Encoder_Decoder_Seq2Seq_and_Attention_model.pdf` (24 slides, Satida Sookpong; parts "6-1" slides 2-17 and "6-2" slides 18-24). All pages were read from the text layer and rendered images; formulas read from images; every worked number below was recomputed in Python (see section 8).
Legend: **[slide N]** = PDF page · **[general]** = general knowledge or my inference (NOT said by the lecturer) · **[computed]** = my own calculation.

**Project relevance: HIGH for evaluation (slides 12-15), MEDIUM for seq2seq/attention** (the fine-tuned Transformer/seq2seq is only the comparison baseline). **Coverage warning:** the deck covers **BLEU** (slides 12-13) and **chrF** (slide 14) in detail; **ROUGE is not covered at all**, and **BERTScore appears only as one row of a comparison table** (slide 15, plus a one-line mention as an MBR similarity measure on slide 11) with no formula and no worked example. Section 3.5 adds ROUGE/BERTScore definitions, clearly tagged [general]. The slide examples are Thai→English machine translation, not summarization.

---

## 1. Encoder-decoder (seq2seq) [slides 3-6]

**Why not sequence labeling** [slide 3]: in translation the input and output lengths differ and words do not pair one-to-one, so one-label-per-token tagging (NLP 2-1) cannot be used.

| Part | Role [slide 3-4] |
|---|---|
| Encoder | turns the input sequence $x_1\dots x_n$ into hidden states $h_1\dots h_n$ |
| Context vector $c$ | summary of the whole input, handed to the decoder |
| Decoder | generates an output sequence of **any length** |

Main equations [slide 3] (SLP3 eq. 12.8-12.9):

$$h=\text{encoder}(x_1\dots x_n),\qquad y_{t+1}=\text{decoder}(h,\,y_1\dots y_t),\qquad P(y\mid x)=\prod_t P(y_t\mid y_{<t},x)$$

Note from the slide: **everything about the source sentence must pass through the "context"**.

**Encoder (deep LSTM)** [slide 4, SLP3 eq. 13.29-13.33]:

$$h_t=g(h_{t-1},x_t)\ \text{(encoder)};\quad c=h^e_n;\quad h^d_0=c;\quad h^d_t=g(\hat y_{t-1},h^d_{t-1},c)\ \text{(decoder)};\quad \hat y_t=\text{softmax}(h^d_t)$$

- $g$ = activation/recurrent function (the slide says "like tanh, ReLU"; in practice an LSTM cell) [slide 4]; $h^e_n$ = final encoder state; $\hat y_t$ = predicted distribution over the target vocabulary.
- The encoder reads word by word, updating the hidden state until the end; **no output during encoding**, only the final state matters [slide 4].
- Sutskever et al. (2014) setup [slide 4]: 4-layer LSTM, 1,000 units per layer, 1,000-dim embeddings; source vocabulary 160,000 words, target 80,000, all others replaced by `<UNK>`.

**Decoder = a conditional language model** [slide 5]: RNN LM $P(y_t\mid y_1\dots y_{t-1})$ vs decoder $P(y_t\mid y_1\dots y_{t-1},x)$ (the only addition is conditioning on the source sentence). Two ways to feed $c$ into the decoder [slide 5]:
1. $c$ as the initial hidden state, $s_0=c$ (Sutskever et al. 2014).
2. Concatenate $c$ to the input at every step, $s_t=g(y_{t-1},s_{t-1},c)$ (Cho et al. 2014); the slide says this keeps the model from "forgetting" the source when producing late words.

**Inference trace** [slide 5], translating to "I like black cats"; each step predicts $\arg\max\ \text{softmax}(V\cdot s_t)$:

| Step | Input $y_{t-1}$ | State update | Prediction |
|---|---|---|---|
| 1 | `<s>` | $s_1=g(\texttt{<s>},c)$ | I |
| 2 | I | $s_2=g(\text{I},s_1)$ | like |
| 3 | like | $s_3=g(\text{like},s_2)$ | black |
| 4 | black | $s_4=g(\text{black},s_3)$ | cats |
| 5 | cats | $s_5=g(\text{cats},s_4)$ | `</s>` → stop |

The decoder stops when it generates `</s>` itself, so output length need not equal input length and need not be fixed in advance [slide 5].

**Thai-English example** [slide 6]: ฉัน ชอบ แมว ดำ → I like black cats. The links ฉัน–I and ชอบ–like are straight; "แมว ดำ" must become "black cats" (crossing alignment, order swapped). Thai-specific challenges listed: modifiers follow the noun (แมว ดำ vs black cats); no plural/tense inflection ("แมว" may be cat or cats, inferred from context); no spaces between words, so segment first or use subword (BPE/SentencePiece); polite particles ครับ/ค่ะ have no English counterpart (a 1-to-0 alignment). Why seq2seq: it learns the reordering from data instead of hand-written rules; a **shared subword vocabulary** for both languages suits languages without spaces such as Thai and Chinese.

---

## 2. Decoding: greedy, beam search, length normalization [slides 7-11]

**Greedy** [slide 7]: $\hat y_t=\arg\max_{w\in V}P(w\mid y_{<t},x)$. Fastest and least memory (one softmax per step) but no backtracking → **error accumulation**: one wrong word puts all later steps in a wrong context, worse for long sentences.

**Beam search** [slide 8]: keep the best $k$ hypotheses at once ($k$ = beam width).
1. Expand every hypothesis with every word in $V$ → $k\times|V|$ candidates.
2. Keep the best $k$ by total log-probability.
3. When a hypothesis generates `</s>`, move it to the finished pool and **decrease the beam width by 1**.

Score (SLP3 eq. 12.15): $\text{score}(y)=\log P(y\mid x)=\sum_{i=1}^{t}\log P(y_i\mid y_1\dots y_{i-1},x)$.

Notes from the slide: MT typically uses $k=5$ to $10$ (SLP3); cost grows $k$-fold in both time and memory; too large a $k$ can hurt (prefers short, repetitive outputs: the "beam search curse"); compute in **log space** to avoid underflow; log-probabilities are always negative, so "larger" means closer to 0. $k=1$ is exactly greedy; $k=|V|^T$ is exhaustive search (infeasible); beam search is the middle road.

**Worked example, Thai, k = 2** [slides 7, 9-10] (probabilities given on the slide):
- $P(w\mid\texttt{<s>})$: เขา 0.50, ผม 0.40, ฉัน 0.10
- $P(w\mid\text{เขา})$: ไป 0.30, มา 0.40, กิน 0.30
- $P(w\mid\text{ผม})$: ไป 0.70, มา 0.20, กิน 0.10

Step 1 keeps เขา ($\ln 0.50=-0.6931$) and ผม ($\ln 0.40=-0.9163$); ฉัน ($\ln 0.10=-2.3026$) is pruned. Step 2 expands 2 × 3 = 6 paths, keeps 2:

| Hypothesis | prev logP | + log P(new) | total logP | total P | kept |
|---|---|---|---|---|---|
| ผม ไป | −0.9163 | ln 0.70 = −0.3567 | −1.2730 | 0.280 | yes |
| เขา มา | −0.6931 | ln 0.40 = −0.9163 | −1.6094 | 0.200 | yes |
| เขา ไป | −0.6931 | ln 0.30 = −1.2040 | −1.8971 | 0.150 | |
| เขา กิน | −0.6931 | ln 0.30 = −1.2040 | −1.8971 | 0.150 | |
| ผม มา | −0.9163 | ln 0.20 = −1.6094 | −2.5257 | 0.080 | |
| ผม กิน | −0.9163 | ln 0.10 = −2.3026 | −3.2189 | 0.040 | |

**Greedy gets "เขา มา" (P = 0.200); beam k = 2 gets "ผม ไป" (P = 0.280).** Greedy missed it because เขา (0.50) beats ผม (0.40) at step 1, without knowing ผม is followed by ไป with 0.70. [computed, all values verified.] Caveat [computed]: the slide never expands ฉัน, but any continuation has $P\le0.10<0.28$, so ผม ไป really is the best 2-word sequence.

**Length normalization** [slide 11]: every added word adds a negative log-prob, so longer hypotheses automatically score lower; this matters when comparing *finished* hypotheses (during search all paths have equal length). Fix: divide by length (SLP3 eq. 12.16):

$$\text{score}(y)=\frac1t\log P(y\mid x)=\frac1t\sum_{i=1}^t\log P(y_i\mid y_1\dots y_{i-1},x)$$

GNMT uses the general length penalty $lp(Y)=\left(\frac{5+|Y|}{6}\right)^{\alpha}$ [slide 11]. [general: the GNMT score is $\log P(Y\mid X)/lp(Y)$; the slide shows only $lp$.]

| Finished hypothesis | T (words) | total logP | logP / T |
|---|---|---|---|
| ผม ไป | 2 | −1.2730 | −0.6365 |
| ผม ไป ตลาด ตอน เช้า | 5 | −3.9120 | −0.7824 |

The short sentence wins both ways, but the gap shrinks from 2.639 to 0.146 (about 18×). With a longer sentence, normalization can flip the result [slide 11]. [computed: 2.639/0.1459 = 18.1, OK.] The 5-word hypothesis and its logP −3.9120 (P ≈ 0.0200 [computed]) are hypothetical: they cannot be derived from the 2-step tree above.

**Minimum Bayes Risk (MBR) decoding** [slide 11]: instead of the "most probable" translation choose the one with the least expected error, i.e. the candidate most similar to all the other candidates under chrF or BERTScore.

---

## 3. Evaluation metrics [slides 12-15] — most project-relevant

### 3.1 BLEU (Bilingual Evaluation Understudy) [slide 12]
Metric mainly for machine translation; based on **modified n-gram precision combined with a brevity penalty**.

$$P_n=\frac{\sum_{n\text{-gram}}\min\big(\text{Count}_{cand},\ \text{Count}_{ref}\big)}{\sum_{n\text{-gram}}\text{Count}_{cand}}$$

$$BP=\begin{cases}1 & c>r\\ e^{(1-r/c)} & c\le r\end{cases}\qquad BLEU=BP\cdot\exp\Big(\sum_{n=1}^{N}w_n\log P_n\Big)$$

- $c$ = total length of the candidate translation; $r$ = closest reference length; $P_n$ = modified (clipped) precision at order $n$; $w_n$ = weights (the slide examples use uniform $w_n=1/N$, i.e. a geometric mean) [slide 12-13].
- Geometric mean → one bad order is punished hard; if any $P_n=0$ then BLEU = 0 immediately (the "hard zero" problem) [slide 13].
- Uses **precision** because a sentence can be translated correctly in many ways; measuring recall against a single reference is unfair [slide 12].
- References cited on the slide: Papineni et al. 2002; Jurafsky & Martin (2026) §12.6.2; Post (2018) SacreBLEU.

Rough quality scale [slide 12]: BLEU < 10 almost unusable · 10-20 gist can be caught · 20-30 understandable but needs editing · 30-40 good, usable · > 40 very good.

### 3.2 BLEU worked example (Thai tokens) [slide 13]
Reference (r = 8 tokens): `แมว สี ดำ กำลัง นอน อยู่ บน โซฟา` (the slide shows the sentence word-segmented with spaces).

| | Candidate A: `แมว สี ดำ นอน อยู่ บน โซฟา` (c = 7) | Candidate C, same words scrambled: `โซฟา บน นอน อยู่ แมว สี ดำ กำลัง` (c = 8) |
|---|---|---|
| $p_1$ | 7/7 = 1.0000 | 8/8 = 1.0000 |
| $p_2$ | 5/6 = 0.8333 | 4/7 = 0.5714 |
| $p_3$ | 3/5 = 0.6000 | 2/6 = 0.3333 |
| $p_4$ | 1/4 = 0.2500 | 1/5 = 0.2000 |
| GM | $(1\times0.8333\times0.6\times0.25)^{1/4}=0.5946$ | 0.4418 |
| BP | $e^{1-8/7}=0.8669$ | 1.0000 (c = r) |
| **BLEU** | $0.8669\times0.5946=\mathbf{0.5154}$ → **51.54** | **44.18** |

[computed: every cell above verified, including the n-gram match counts.] Slide's lessons: $p_n$ falls as $n$ grows (4-gram matches are much harder, the main drag on the score); the geometric mean gives a hard zero; candidate C, an unreadable word salad, still scores 44 because $p_1=1.0$, so **BLEU captures word order more weakly than one might think**.

### 3.3 chrF (character F-score) [slide 14]

$$chrF\beta=(1+\beta^2)\,\frac{chrP\cdot chrR}{\beta^2\cdot chrP+chrR}\qquad(12.20)$$

- chrP = **average precision** of character 1-grams … k-grams; chrR = **average recall** of character 1-grams … k-grams; common weight $\beta=2$ ("chrF2"), i.e. recall counts twice as much, so incomplete output is punished.
- Why better than BLEU [slide 14]: counts character n-grams (not words); no dependence on word segmentation, so it is comparable across systems with different tokenizers; includes both precision and recall, so no brevity penalty needed; tolerant of misspellings and inflection; correlates well with human judgement in many languages. For Thai (no spaces) the slide calls chrF the clearly safer choice, with no need to agree on a tokenizer first.

Worked example, reference `แมวสีดำนอนอยู่บนโซฟา` (20 characters) [slide 14]; the slide does not state k, but **k = 2 reproduces every value** [computed]:

| Candidate | chrP | chrR | chrF2 |
|---|---|---|---|
| `แมวสีดำนอนบนโซฟา` (missing อยู่) | .967 | .768 | .801 |
| `แมวสีดำ` (too short) | 1.000 | .333 | .384 |
| `…บนโซฟ` (last character dropped) | 1.000 | .949 | .959 |

(The third row is the full sentence minus the final "า"; I inferred this and it reproduces the numbers.) The short candidate has perfect precision but low recall; with $\beta=2$ it is punished (.384).
Method detail for reproducing [computed]: remove whitespace, count Unicode code points (a Thai vowel/tone mark counts as its own character), average P and R over n = 1..k, then combine once with the F formula.

### 3.4 BLEU vs chrF vs BERTScore [slide 15]
Controlled experiment: candidate A vs the same reference as slide 13 (r = 8 words), then A with one character dropped ("โซฟ" instead of "โซฟา"):

| Candidate | BLEU-4 | BLEU-2 | chrF2 (k = 2) |
|---|---|---|---|
| A: แมว สี ดำ นอน อยู่ บน โซฟา | 51.54 | 79.13 | 80.80 |
| A + one character dropped (…โซฟ) | 0.00 | 65.53 | 77.20 |
| change | −51.54 (−100%) | −13.60 (−17%) | −3.60 (−4.5%) |

[computed: all six values and the changes verified.] One typo wipes out BLEU-4 (the only matching 4-gram "นอน อยู่ บน โซฟา" breaks → $p_4=0$ → hard zero), while chrF barely moves. Note the chrF2 values here use the slide-13 reference (with "กำลัง"), whereas the slide-14 table uses a reference without it.

| Metric | Basis | Strengths | Weaknesses |
|---|---|---|---|
| BLEU | word n-gram (precision) | widely used, comparable to older work | very sensitive to tokenizer, hard zero, ignores meaning |
| chrF | character n-gram (F-score) | tokenizer-independent; good for morphologically rich languages and Thai | surface only; cannot judge large phrase movement |
| BERTScore | embedding similarity | accepts synonyms and paraphrase | needs a model, slower, depends on embedding quality for that language |
| COMET / BLEURT | trained on human scores | highest correlation with humans today | needs human-scored data, black box |

Lecturer's recommendation for Thai-English [slide 15]: report **chrF2 as the main metric + BLEU (via SacreBLEU) for comparison with older work + COMET if resources allow**, and always test significance with a **paired bootstrap test**.

### 3.5 ROUGE and BERTScore — NOT on the slides [general]
Added because the project's evaluation plan uses them; nothing in this subsection comes from the lecturer.
- **ROUGE-N** (Lin 2004, designed for summarization): n-gram overlap with the reference summary. Recall $=\dfrac{\sum_{\text{ref }n\text{-grams}}\text{Count}_{match}}{\sum\text{Count}_{ref}}$, precision uses the candidate count in the denominator, F1 is their harmonic mean. Original ROUGE is recall-oriented (opposite emphasis to BLEU).
- **ROUGE-L**: longest common subsequence (LCS) between candidate and reference; $R_{lcs}=\text{LCS}/|ref|$, $P_{lcs}=\text{LCS}/|cand|$, then F. Rewards in-order matches without requiring adjacency.
- **BERTScore** (Zhang et al. 2020): contextual token embeddings from a BERT-like model; greedy match of each token to its most similar token by cosine: $R=\frac1{|x|}\sum_{x_i\in x}\max_{\hat x_j}x_i^\top\hat x_j$, $P=\frac1{|\hat x|}\sum_{\hat x_j}\max_{x_i}x_i^\top\hat x_j$, $F_1=\frac{2PR}{P+R}$ ($x$ = reference tokens, $\hat x$ = candidate tokens). Optional idf weighting and baseline rescaling. A Thai-capable or multilingual encoder is required.
- [computed, my own application of the standard definitions to the slide-13 sentences, not on any slide]:

| Candidate vs reference | ROUGE-1 P / R / F1 | ROUGE-2 P / R / F1 | ROUGE-L P / R / F1 |
|---|---|---|---|
| A (c = 7) | 1.000 / 0.875 / 0.933 | 0.833 / 0.714 / 0.769 | 1.000 / 0.875 / 0.933 (LCS = 7) |
| C, scrambled (c = 8) | 1.000 / 1.000 / 1.000 | 0.571 / 0.571 / 0.571 | 0.500 / 0.500 / 0.500 (LCS = 4) |

Same lesson as BLEU: ROUGE-1 gives the scrambled sentence a perfect score; ROUGE-2 and ROUGE-L expose the order problem.

---

## 4. The bottleneck problem and why attention [slides 16-17]

- The whole source sentence is squeezed into **one fixed-size vector** $c$ (1000 dims in the slide). Early words are the most likely to be overwritten, and the decoder has no access to $h_1\dots h_{n-1}$, only what is in $c$ [slide 16].
- Information budget per word with $d=1000$ [slide 16]: 5 words → 200.0 dims/word; 20 → 50.0; 50 → 20.0; 80 → 12.5. [computed: $1000/n$, OK.]
- Problems of plain seq2seq [slide 17]: fixed-vector bottleneck (5 and 50 words use the same space); no explicit word alignment (cannot tell which source word produced which target word, so errors are hard to debug); quality drops on long sentences (slide quotes BLEU falling from about 27 to about 12 beyond 50 words, Bahdanau et al. 2015; I did not verify this against the paper); the same $c$ is used at every step although each word should look at a different source part.
- **Attention idea** [slide 17]: "if the problem is squeezing everything into one vector, don't squeeze". Old: $c=h_n$ (fixed). New: $c_i=\sum_j a_{ij}h_j$, recomputed at **every** decoder step $i$, where $a_{ij}$ = weight that step $i$ gives to source word $j$. The decoder can see all of $h_1\dots h_n$; $a_{ij}$ can also be read as a soft word alignment (interpretable).

---

## 5. Attention model [slides 19-21]

Intuition [slide 19]: human reading uses a small sharp focus (fovea) and sweeps the eyes; a translator looks back at the source word currently being translated. Decoder update with attention (SLP3 eq. 13.34): $h^d_i=g(\hat y_{i-1},h^d_{i-1},c_i)$, where the context $c_i$ is now a function of all encoder states.

**Three steps (the slide: "memorize just this")** [slide 20], SLP3 eq. 13.35-13.37:

$$\text{1. Score:}\quad \text{score}(h^d_{i-1},h^e_j)=h^d_{i-1}\cdot h^e_j\qquad\text{(how relevant is source word } j \text{ to what is about to be produced)}$$

$$\text{2. Normalize:}\quad \alpha_{ij}=\text{softmax}\big(\text{score}(h^d_{i-1},h^e_j)\big)=\frac{\exp(\text{score}(h^d_{i-1},h^e_j))}{\sum_k\exp(\text{score}(h^d_{i-1},h^e_k))}\qquad\text{(weights sum to 1)}$$

$$\text{3. Combine:}\quad c_i=\sum_j\alpha_{ij}\,h^e_j\qquad\text{(weighted sum of encoder states = context for this step)}$$

All attention variants differ **only in step 1**; steps 2 and 3 are identical [slide 20].

| | Plain seq2seq | Seq2seq + attention [slide 20] |
|---|---|---|
| Context used by decoder | $c=h_n$ (one vector, fixed at every step) | $c_i=\sum_j a_{ij}h_j$ (recomputed every step) |
| Access to encoder | final state only | all states $h_1\dots h_n$ |

**Variants — two questions** [slide 21]: ① how to score $\text{score}(s,h)$; ② how many positions to look at. ($d=512$ in the parameter column.)

| Form | score(s, h) | Extra parameters | weight on "ดำ" (illustrative) |
|---|---|---|---|
| additive, Bahdanau 2015 | $v^\top\tanh(W_1s+W_2h)$ | ≈ 524,800 | 0.58 |
| dot, Luong 2015 | $s^\top h$ | 0 | 0.36 |
| general, Luong 2015 | $s^\top Wh$ | 262,144 | 0.38 |
| scaled dot, Transformer 2017 | $s^\top h/\sqrt d$ | 0 | → next slide |

[computed: additive $=2\times512^2+512=524{,}800$; general $=512^2=262{,}144$; both assume square 512×512 matrices, OK.] The "weight on ดำ" column is the slide's illustration for the decoder producing "black": all three point at "ดำ", differing only in sharpness; the underlying scores are not given, so these cannot be recomputed. **dot** requires both sides to have the same dimension; additive and general do not [slide 21].
- **Global** attention looks at all words ($T_x\times T_y$ scores); **local** attention looks at a window around position $p_t$: local-m sets $p_t=t$ (assumes monotone alignment), local-p lets the model predict $p_t$ with a Gaussian weighting, $\sigma=D/2$. For Thai-English with reordering, **global is safer** [slide 21].
- Luong: dot works well with global, general with local; WMT'14 En→De: global 18.1 → local-p 19.0 BLEU [slide 21]. (Slide 21's footnote says it is used in place of pages 22-26 of the 6-1 deck.)
- [computed, toy numbers of mine, not from any slide] Scores (2.0, 1.0, 0.1) → softmax weights (0.659, 0.242, 0.099), sum 1; $c_i$ is then 0.659 $h_1$ + 0.242 $h_2$ + 0.099 $h_3$.

---

## 6. Preview of Q/K/V, Transformer, applications [slides 22-24]

- **Assignment** [slide 22]: read and summarize the paper *Attention Is All You Need* (arxiv.org/pdf/1706.03762) in a PDF of at most 1 page.
- **Soft lookup view** [slide 23]: Query = decoder $s_{t-1}$ ("what am I looking for now"), Key = encoder $h_j$ ("what I am information about"), Value = encoder $h_j$ ("the actual information to be pulled"). This week (cross-attention): Q from the decoder, K/V from the encoder. Transformer (self-attention): Q, K, V from the **same** sequence:

$$\text{Attention}(Q,K,V)=\text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

- Motivation [slide 23]: RNNs build $h_j$ sequentially (cannot be parallelized, a speed bottleneck); if every position can attend to every other in the same sequence, you get the same context without walking, with full parallelism, but **positional encoding** must be added because pure attention does not know word order. [general: the $\sqrt{d_k}$ scaling stops large dot products from saturating the softmax.]
- **Applications** [slide 24]: summarization (long article → short headline; attention selects important sentences; coverage matters because repetition is obvious; Thai news auto-headlines), speech recognition (audio frames → characters; Listen-Attend-Spell), image captioning (Show-Attend-Tell), parsing (seq2seq produces the tree as a linearized bracket string), QA/chatbots (AliMe, Xiao Ice).
- **Modern NMT (2026)** [slide 24]: all production systems use a Transformer encoder-decoder; multi-head attention (e.g. 8 heads, each capturing a different relation); three attentions per model: encoder self-attention, decoder masked self-attention, cross-attention. Unchanged since this lecture: score → softmax → weighted sum; the Transformer's cross-attention is Bahdanau attention in parallel form; beam search, length normalization and BLEU/chrF are used exactly as before.

---

## 7. Quick reference

| Term | One-line meaning |
|---|---|
| seq2seq | encoder reads input into $c$; decoder generates output of any length until `</s>` |
| Greedy / beam | best word each step / keep $k$ best hypotheses (k = 1 is greedy) |
| Length normalization | divide log-prob by length so short outputs do not win automatically |
| BLEU | $BP\cdot\exp(\sum w_n\log P_n)$, word n-gram precision, hard zero if any $P_n=0$ |
| chrF$\beta$ | character n-gram F-score, recall counts $\beta$ times as much as precision; $\beta=2$ usual (slide: "twice") |
| BERTScore | embedding-similarity metric (slide: table row on 15, MBR mention on 11) |
| Attention | $c_i=\sum_j\alpha_{ij}h_j$, $\alpha=\text{softmax}(\text{score})$ |

## 8. Verification log (all numbers recomputed in Python)

- Beam-search table (slide 10), greedy 0.200 vs beam 0.280, ln values: **all correct**.
- Length normalization (slide 11): −0.6365, −0.7824, gap 2.639 → 0.1459 ("0.146", ≈ 18×): **correct**; the 5-word logP is hypothetical.
- BLEU examples A and C (slide 13), BLEU-2/BLEU-4 of A and of A with a dropped character (slide 15, 79.13, 65.53, 0.00, 51.54): **all correct**.
- chrF (slide 14) all nine values and (slide 15) 80.80 / 77.20 / −3.60 (−4.5%): **correct with k = 2**; k is not printed on slide 14 and the two slides use different references (inferred, not an error).
- Bottleneck table (slide 16) and parameter counts (slide 21): **correct**. Slide 21 attention-weight column (0.58/0.36/0.38) and the "BLEU 27 → 12", "18.1 → 19.0" claims: taken as stated, not verifiable here.
- No slide values found to be wrong. Not legible/not covered: none of the 24 pages was unreadable; the deck simply contains no ROUGE and no BERTScore formula.

## 9. Project relevance and practical notes

- **Metrics for the evaluation plan.** The deck gives the exact BLEU and chrF definitions plus a controlled-experiment mindset: a metric must be checked against small perturbations (typo, word order, truncation). ROUGE/BERTScore definitions are in 3.5 [general], not from this lecture.
- **Tokenization controls word-level scores** (BLEU/ROUGE-1/2 on Thai): [general] segment reference and candidate with the **same** PyThaiNLP engine (e.g. `newmm`) and report it, or add a character-level metric (chrF-style) as the slide recommends for unspaced Thai.
- **Hard zero / short outputs.** [general] Sentence-level BLEU-4 is often 0 for short summaries; prefer ROUGE-1/2/L and BERTScore for summaries, as the project plan does, and use chrF as a tokenizer-free check. ROUGE-1 alone cannot detect scrambled order (3.5).
- **Surface metrics vs paraphrase** [slide 15 + general]: the extractive method copies source sentences, while a generated baseline paraphrases; BERTScore tolerates synonyms but needs a Thai-capable embedding model and is slower.
- **Significance.** The lecturer says to run a paired bootstrap test [slide 15]; with a small test set of weather reports this matters.
- **Seq2seq baseline.** [general] Use beam search (the slide: k = 5-10 typical in MT) with length normalization or a minimum length so outputs are not too short; long multi-sentence bulletins stress input-length limits, which is why the plain RNN encoder-decoder (bottleneck, slides 16-17) is a weak baseline and a pretrained Transformer encoder-decoder is the realistic one [slide 24: production NMT is all Transformer]. Subword tokenization with a shared vocabulary suits Thai [slide 6].
- [general] Generated summaries can hallucinate numbers (temperatures, rainfall, province names); no overlap metric will catch this, so spot-check facts manually.
- Course assignment [slide 22]: one-page summary of *Attention Is All You Need* (course task, not a project deliverable).
- Related: tokenization in [1-2](1-2-tokenization.md); language models and perplexity in [5-1](5-1-language-models-ngrams.md).
