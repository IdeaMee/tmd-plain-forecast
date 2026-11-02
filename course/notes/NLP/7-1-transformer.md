# NLP 7-1 — The Transformer

Source: `course/slides/7-1_Transformer.pdf` (32 slides, Satida Sookpong; course header on slide 1 is NLP 1323326). Thai wording from the PDF text layer (some tone marks are missing there, so I paraphrase in English); formulas, tables and diagrams read from slide images (all 32 pages viewed as contact sheets; slides 3, 5, 11, 12, 24 re-checked at zoom). Slides cite the original paper as "AIAYN" (Vaswani et al. 2017, *Attention Is All You Need*) and the textbook "SLP3" (Jurafsky & Martin, 3rd ed.) with section numbers; equation numbers below are the slides' own.
Legend: **[slide N]** = PDF page · **[general]** = general knowledge or my inference, not said on the slides · **[computed]** = my own calculation (re-run in Python).

**Project relevance: HIGH for the comparison baseline, NONE for Stages 0-2.** The Naive Bayes / SVM / kNN / TF-IDF pipeline does not use a Transformer. The fine-tuned baseline (mT5 or a Thai encoder such as WangchanBERTa) does, and slides 24, 29, 31, 32 say which family fits which job. [general]

---

## 1. From attention to the Transformer [slides 2-6]

| Year | Model | Idea [slide 2] |
|---|---|---|
| 2014 | Sutskever, seq2seq | pure RNN; the whole sentence is squeezed into one vector $c$, a **bottleneck** |
| 2015 | Bahdanau / Luong | RNN + attention; the decoder can look back at every source word, but still steps one word at a time |
| 2017 | Vaswani, Transformer | drop the RNN, keep only attention; all words are computed at the same time |

**Attention recap (week 6)** [slide 3] (full treatment in [6-1](6-1-encoder-decoder-attention.md)), three steps. Notation as drawn: $\mathbf h^d_{i-1}$ = previous decoder state, $\mathbf h^e_j$ = encoder state of source word $j$ (the slide does not spell out the d/e superscripts; reading them as decoder/encoder is my inference [general]).

1. **Score** (how related is source word $j$ to what is about to be generated): $\text{score}(\mathbf h^d_{i-1},\mathbf h^e_j)=\mathbf h^d_{i-1}\cdot\mathbf h^e_j$ (13.35)
2. **Normalize** (scores become weights that sum to 1): $\alpha_{ij}=\text{softmax}\big(\text{score}(\mathbf h^d_{i-1},\mathbf h^e_j)\big)=\dfrac{\exp\big(\text{score}(\mathbf h^d_{i-1},\mathbf h^e_j)\big)}{\sum_k\exp\big(\text{score}(\mathbf h^d_{i-1},\mathbf h^e_k)\big)}$ (13.36)
3. **Combine** (weighted sum of encoder states = context of this step): $\mathbf c_i=\sum_j\alpha_{ij}\,\mathbf h^e_j$ (13.37)

| Issue | Plain seq2seq | Seq2seq + attention [slide 3] |
|---|---|---|
| Context used by decoder | $c=h_n$ (one vector, fixed at every step) | $c_i=\sum_j a_{ij}h_j$ (recomputed every step) |
| Access to encoder | last state only | all states $h_1\dots h_n$ |

**Limits of RNNs, "why drop recurrence"** [slide 5]. RNN: $\mathbf h_t=g(\mathbf U\mathbf h_{t-1}+\mathbf W\mathbf x_t)$ (13.1), $\mathbf y_t=f(\mathbf V\mathbf h_t)$ (13.2).
1. *Sequential computation:* a length-$n$ sequence needs $n$ ordered steps, no parallelism across time; GPUs/TPUs are built for big parallel matrix products, so training time becomes the bottleneck at billions of tokens.
2. *Long-range dependencies:* information from token 1 to token $n$ passes through $n$ steps (path length $O(n)$); gradients get multiplied repeatedly and shrink (week 5). LSTM helps a lot but does not shorten the path, it only keeps the multiplier near 1. Seq2seq attention lets the decoder see all encoder positions, but the encoder itself still runs sequentially.
- Question the slide poses: "if attention already gives direct access to every position, why keep recurrence?" Answer of Vaswani et al. (2017): not needed; attention alone is enough and works better.

**Why self-attention (AIAYN §4, Table 1)** [slide 6]. RNN: info from the first word walks through every word, $n-1$ sequential steps, step $t$ waits for step $t-1$, signal fades. Self-attention: every word sees every word directly in 1 step, all pairs computed together as one matrix product $QK^T$.

| Per layer | Self-attention | RNN |
|---|---|---|
| Computation | $O(n^2\cdot d)$ | $O(n\cdot d^2)$ |
| Sequential operations | $O(1)$ | $O(n)$ |
| Max path length between two words | $O(1)$ | $O(n)$ |

$n$ = sentence length, $d$ = vector dimension. For ordinary sentences $n<d$ (slide: $n\approx30$, $d=512$), so self-attention costs less. [computed] $n^2d=460{,}800$ vs $nd^2=7{,}864{,}320$, about 17x fewer operations. Caveat [general]: this reverses when $n>d$ (very long inputs, see the $N\times N$ table in section 4).

## 2. Contextual meaning [slide 18]

Static embedding (week 4): one word = one vector always. Transformer: the vector of a word changes with its sentence. Attention's job: **pull information from the other words of the sentence and mix it into the current word.**
- SLP3 8.1-8.2: "The chicken didn't cross the road because **it** was too tired" → it = chicken; "...too wide" → it = road.
- Thai version on the slide: "แมว ไม่ กระโดด ข้าม รั้ว เพราะ **มัน** เหนื่อย" → มัน ≈ แมว; "...สูงเกินไป" → มัน ≈ รั้ว; "ทอดมันฝรั่ง" → มัน ≈ พืช. word2vec gives the same vector $v_{\text{มัน}}$ in all three; the Transformer gives three different ones.

## 3. Scaled dot-product attention [slides 8-10]

$$\text{Attention}(Q,K,V)=\text{softmax}\!\left(\frac{QK^{T}}{\sqrt{d_k}}\right)V\qquad(1)$$

| Symbol | Shape | Meaning [slide 8] |
|---|---|---|
| $X$ | $[n\times d]$ | input: $n$ tokens, each an embedding of dimension $d$ (model dimension) |
| $Q=XW^Q$ | $[n\times d_k]$ | queries of every position ($W^Q$ is $[d\times d_k]$) |
| $K=XW^K$ | $[n\times d_k]$ | keys of every position |
| $V=XW^V$ | $[n\times d_v]$ | values of every position |
| $QK^T$ | $[n\times n]$ | score of every (query $i$, key $j$) pair in one matrix product |
| output | $[n\times d_v]$ | contextual representation of every position |

Same $X$ is used for all three ($Q=XW_Q,\ K=XW_K,\ V=XW_V$) [slide 9]; $W_Q,W_K,W_V$ are learned.

**Five steps** [slide 8]: (1) Project $Q,K,V$ · (2) Score $QK^T$ · (3) Scale $/\sqrt{d_k}$ · (4) Normalize softmax (each row sums to 1) · (5) Aggregate $\times V$ (weighted average of values, same idea as $c_i=\sum_j\alpha_{ij}h_j$) [slide 9].

**Why divide by $\sqrt{d_k}$** [slide 9]: the larger $d_k$, the more the dot products swing (variance $=d_k$); softmax then puts nearly all weight on one word and the gradient is almost zero. (The variance claim assumes components of $q,k$ are independent with mean 0 and variance 1, an assumption not stated on the slide [general].) Slide example, $d_k=64$, raw scores 16, 8, 0:

| | scores | softmax |
|---|---|---|
| no scaling | 16, 8, 0 | 1.00, 0.00, 0.00 |
| $\div\sqrt{64}=8$ | 2, 1, 0 | 0.67, 0.24, 0.09 |

[computed] unscaled: 0.99966, 0.00034, 0.0000001; scaled: 0.6652, 0.2447, 0.0900. Matches the slide. The paper uses $d_k=64$ (512 / 8 heads).

**Worked example** (slide 10, $d_k=2$; numbers are given directly, in a real model $q,k,v$ come from $XW_Q,XW_K,XW_V$):

| word | $q$ | $k$ | $v$ |
|---|---|---|---|
| แมว | [1, 0] | [2, 0] | [1, 0] |
| กิน | [1, 1] | [0, 1] | [0, 1] |
| ปลา | [0, 1] | [1, 2] | [1, 1] |

Row of "กิน" ($q=[1,1]$) against the keys of แมว, กิน, ปลา:

| | แมว | กิน | ปลา |
|---|---|---|---|
| $q\cdot k$ | 2 | 1 | 3 |
| $\div\sqrt2$ | 1.41 | 0.71 | 2.12 |
| softmax | 0.28 | 0.14 | 0.58 |

$q_{\text{กิน}}\cdot k_{\text{ปลา}}=1\cdot1+1\cdot2=3$ is the highest, so "กิน" attends most to "ปลา" (its object). Mix the values: $0.28[1,0]+0.14[0,1]+0.58[1,1]=[0.86,\,0.72]$, a new vector for "กิน" with the most information from "ปลา".
All three rows at once $=\text{softmax}(QK^T/\sqrt2)$: แมว → [0.58, 0.14, 0.28] · กิน → [0.28, 0.14, 0.58] · ปลา → [0.14, 0.28, 0.58] (each row sums to 1).

[computed] full check: $QK^T=\begin{bmatrix}2&0&1\\2&1&3\\0&1&2\end{bmatrix}$; unrounded weights: แมว [0.576, 0.140, 0.284], กิน [0.284, 0.140, 0.576], ปลา [0.140, 0.284, 0.576]; output rows [0.860, 0.424], [0.860, 0.716], [0.716, 0.860]. All slide numbers verified. The slide's [0.86, 0.72] uses the rounded weights; unrounded it is [0.860, 0.716], same to 2 decimals.

## 4. Multi-head attention [slides 11, 20]

Each head has its own $W^Q,W^K,W^V$ and "attends differently to context" (slide example: one head pairs subject-verb, another links a pronoun to its referent). Head outputs (each $[1\times d_v]$) are **concatenated** ($[1\times Ad_v]$) and projected by $W^O$ (shape $[Ad_v\times d]$, usually $d_v=d/A$, so $[d\times d]$) back to size $d$, the same size as the input [slide 11, SLP3 Fig 8.6; the figure uses $A$ for the number of heads, the paper and Table 3 use $h$].

Matrix form with a single $X$ (SLP3 §8.3) [slide 20]:
$$Q=XW^Q,\ K=XW^K,\ V=XW^V\quad(8.32)$$
$$\text{head}=\text{softmax}\!\left(\text{mask}\!\left(\frac{QK^T}{\sqrt{d_k}}\right)\right)V\quad(8.33)\qquad A=\text{head}\,W^O\quad(8.34)$$
(8.33) is one head; with several heads the $\text{head}_1\dots\text{head}_A$ are concatenated before $W^O$. The explicit $\text{MultiHead}=\text{Concat}(\text{head}_1,\dots,\text{head}_h)W^O$ is the paper's form, not written out on the slides [general]. Every word gets its result at once in a few matrix products, which suits GPUs.

**Effect of the number of heads** (Table 3 A, base model, BLEU on dev set) [slide 11]:

| heads | $d_k$ | BLEU dev |
|---|---|---|
| 1 | 512 | 24.9 |
| 4 | 128 | 25.5 |
| **8** | **64** | **25.8** |
| 16 | 32 | 25.8 |
| 32 | 16 | 25.4 |

One head is 0.9 BLEU worse; too many heads also hurt. [computed] $25.8-24.9=0.9$; $d_k=512/\text{heads}$ in every row. Note: the text layer scrambles this table; the order above is from the image (8 highlighted). Small figure typo: Head 4 in the slide's figure is labeled $W^{K3}$ (probably should be $W^{K4}$) [general].

**Size of the score table** (per head, per layer, $N\times N$) [slide 20]: $N=512\to262{,}144$ · $8{,}192\to$ 67 million · $131{,}072\to$ 1.7×10^10. [computed] $512^2=262{,}144$; $8192^2=67{,}108{,}864$; $131072^2=17{,}179{,}869{,}184$. Verified. This quadratic growth is the cost side of $O(n^2d)$.

## 5. Three kinds of attention and the causal mask [slide 12]

- **Encoder self-attention:** $Q,K,V$ all come from the source sentence; every word sees every word (replaces the encoder RNN).
- **Masked self-attention in the decoder:** a word sees only earlier words; still a language model predicting the next word (as in week 5).
- **Cross-attention (encoder-decoder):** $Q$ from the decoder, $K,V$ from the encoder = the attention of week 6.

**Causal mask** (figure: tokens `<s>`, I, eat, rice). Rows = query at position $i$ (used to predict word $i+1$), columns = key. Allowed cells are the lower triangle including the diagonal; every cell above the diagonal gets $-\infty$ added **before softmax**, so $e^{-\infty}=0$ gives exactly zero weight and each row still sums to 1. E.g. row `<s>` sees only `<s>`; row "eat" sees `<s>`, I, eat.
- Why the decoder needs it: in training the whole target sentence is fed in at once (parallel); without the mask word $t$ would see word $t+1$ (the answer) and copy it.
- Same figure family appears in SLP3 Fig 8.10 (upper triangle of $QK^T$ set to $-\infty$).

## 6. Positional encoding [slides 13, 21]

Attention itself is order-blind, so a position vector is **added** to each word embedding.

$$PE_{(pos,2i)}=\sin\!\big(pos/10000^{2i/d_{model}}\big),\qquad PE_{(pos,2i+1)}=\cos\!\big(pos/10000^{2i/d_{model}}\big)$$

- $pos$ = position of the token; $i$ = index of the dimension pair; $d_{model}$ = embedding size. Low dimensions rotate fast, high dimensions slowly (heat-map on the slide: $max\_len=64$, $d_{model}=32$).
- Why sin/cos [slide 13]: every position gets a unique pattern; $PE(pos+k)$ is a **linear function** of $PE(pos)$, so relative distance can be learned; a *learned* position table (Table 3 E) reaches 25.7 BLEU, almost the same as 25.8.

Worked example, $d=4$ (slide table). With $d_{model}=4$: $i=0\Rightarrow 10000^{0}=1$ (columns $\sin(pos),\cos(pos)$); $i=1\Rightarrow 10000^{0.5}=100$ (columns $\sin(pos/100),\cos(pos/100)$) [computed derivation, consistent with the slide's column headers].

| pos | sin(pos) | cos(pos) | sin(pos/100) | cos(pos/100) |
|---|---|---|---|---|
| 0 | 0.000 | 1.000 | 0.000 | 1.000 |
| 1 | 0.841 | 0.540 | 0.010 | 1.000 |
| 2 | 0.909 | −0.416 | 0.020 | 1.000 |
| 3 | 0.141 | −0.990 | 0.030 | 1.000 |

[computed] all values reproduced. The last column is just rounding: exact $\cos(pos/100)$ is 1.0000, 0.99995, 0.9998, 0.9996, which all round to 1.000 at 3 decimals (so the column carries almost no position signal at these small $pos$; it only changes slowly).

**Input = token embedding + position** [slide 21]: $x_i=E[\text{id}(w_i)]+P[i]$, each $[1\times d]$; stacking gives $X$ of size $[N\times d]$; $E$ is $[|V|\times d]$, the lookup equals one-hot $\times E$. (The slide indexes positions $P[1],P[2],P[3]$ for ฉัน กิน ข้าว, while the PE table above starts at $pos=0$; just a convention difference.)

| Method | How | Used in [slide 21] |
|---|---|---|
| absolute (learned) | table $P[pos]$ learned like word vectors | BERT 512 · GPT-2 1,024 |
| sinusoidal | sin/cos formula, nothing to learn | Transformer 2017 |
| RoPE | rotate $q,k$ by position in every layer | Llama · Qwen · Gemma |

Learned tables have a ceiling: late positions are trained less and positions beyond the maximum length cannot be used (SLP3 p.188).

## 7. The Transformer block [slides 14, 19]

- **Wrap every sublayer:** $\text{LayerNorm}(x+\text{Sublayer}(x))$ (residual shortcut, then LayerNorm) [slide 14].
- **Position-wise feed-forward network (FFN):** $\max(0,\,xW_1+b_1)W_2+b_2$; dimension $512\to2048\to512$ (expand 4x, squeeze back); the same weights for every position, different weights per layer.
- **Parameters per encoder layer** (without biases and LayerNorm): attention $4\times512^2=1.05$ M; FFN $2\times512\times2048=2.10$ M. The FFN holds about 2/3 of each layer; researchers see it as where the model stores "knowledge". [computed] 1,048,576 and 2,097,152; share $2.097/3.146=2/3$ exactly.

**Post-norm vs pre-norm** [slides 14, 19]:

| | post-norm (paper, 2017) | pre-norm (textbook, 2026) |
|---|---|---|
| Formula | $\text{LN}(x+F(x))$ | $x+F(\text{LN}(x))$ |
| Shortcut | passes through a LayerNorm in every layer | straight from bottom to top (clean residual stream) |
| Deep training | needs a lot of warmup | more stable |
| Used in | original Transformer, BERT | GPT-2 onward, Llama, Qwen |

Pre-norm block (SLP3 8.38-8.39): $\mathbf O=\mathbf X+\text{MultiHeadAttention}(\text{LayerNorm}(\mathbf X))$, $\ \mathbf H=\mathbf O+\text{FFN}(\text{LayerNorm}(\mathbf O))$. Only attention reads information from other words' streams; all other layers work inside a single word.

## 8. Full architecture, training, results [slides 7, 15, 16]

**Encoder x 6:** multi-head self-attention → Add & Norm → feed-forward → Add & Norm. **Decoder x 6:** masked self-attention → Add & Norm → cross-attention (K, V from the encoder) → Add & Norm → feed-forward → Add & Norm; then Linear → softmax → next word. Both stacks start from embedding + positional encoding. Example on the slide: source "ฉัน กิน ข้าว", target shifted right `<s> I eat`. Every sublayer has a residual shortcut then LayerNorm [slide 7].

| Setting (Table 3) | base | big |
|---|---|---|
| N (layers) | 6 | 6 |
| $d_{model}$ | 512 | 1024 |
| $d_{ff}$ | 2048 | 4096 |
| h (heads) | 8 | 16 |
| $d_k=d_v$ | 64 | 64 |
| parameters | 65 M | 213 M |

Layer ablation (dev BLEU): 2 layers 23.7 (down from 25.8), 8 layers 25.5, so 6 is the sweet spot. big keeps $d_k=1024/16=64$ [slide 7]. [computed] $512/8=64$, $1024/16=64$. Parameter sanity check [computed, approximate]: encoder 6x3.15 M = 18.9 M, decoder 6x(2x1.05+2.10) M = 25.2 M, a shared embedding $37{,}000\times512=18.9$ M (the shared-embedding assumption is mine, [general]): total 63.0 M vs the slide's 65 M; for big the same recipe gives 214 M vs 213 M. Close, not exact; the slide's counts are as reported in the paper.

**Training in the paper** [slide 15]: data WMT14 EN-DE 4.5 M pairs, EN-FR 36 M pairs · tokens BPE 37,000 (shared bilingual vocabulary) / word-piece 32,000 · batch about 25,000 source + 25,000 target tokens · Adam $\beta_1=0.9,\ \beta_2=0.98,\ \epsilon=10^{-9}$ with 4,000 warmup steps · dropout 0.1, label smoothing 0.1 · decoding beam 4, length penalty $\alpha=0.6$, max length = input + 50 · average the last 5 checkpoints (base) / 20 (big).

**Results, newstest2014** (Table 2) [slide 16]:

| Model | EN→DE BLEU | EN→FR BLEU | Training cost EN→DE (FLOPs) |
|---|---|---|---|
| GNMT + RL (RNN) | 24.6 | 39.92 | 2.3×10^19 |
| ConvS2S (CNN) | 25.16 | 40.46 | 9.6×10^18 |
| ConvS2S ensemble | 26.36 | 41.29 | 7.7×10^19 |
| Transformer base | 27.3 | 38.1 | 3.3×10^18 |
| Transformer big | 28.4 | 41.8 | 2.3×10^19 |

Slide claims: base uses about 1/7 of GNMT's compute yet scores 2.7 BLEU higher; big beats every ensemble. [computed] $2.3\times10^{19}/3.3\times10^{18}=6.97$; $27.3-24.6=2.7$; big 28.4 > 26.36 and 41.8 > 41.29. Verified. **Ambiguity the slide itself flags:** §6.1 of the paper says EN→FR 41.0 but Table 2 says 41.8. **My observation:** base EN→FR (38.1) is below GNMT (39.92) and ConvS2S (40.46), so "Transformer wins" holds for EN→DE and for big on EN→FR, not for base on EN→FR.
Parsing test (week 3 link): tree turned into a symbol string and a 4-layer Transformer "translates" the sentence into the tree. WSJ only (40k sentences): **91.3 F1** (seq2seq RNN 88.3, best listed 91.7, i.e. slightly above the Transformer); semi-supervised (17 M sentences): **92.7 F1**, above every baseline.
Impact: one architecture that trains fast on GPU and scales → BERT (2018, encoder) and GPT (2018, decoder) each took half of it within a year.

## 9. LM head and sampling [slides 22-23]

Top layer: unembedding $\mathbf u=\mathbf h^L_N E^T$ (8.46), $\mathbf y=\text{softmax}(\mathbf u)$ (8.47); $\mathbf u$ = logits $[1\times|V|]$, $\mathbf y$ = word probabilities over vocabulary $V$ (the unembedding is $E^T$, $[d\times|V|]$).
- The LM head does not choose the word; it only gives probabilities. The choice (greedy, sampling or beam search) is a separate step and can change without retraining.
- Pick by task: near single-answer tasks (translation) use **beam search** (paper: beam 4); free text or chat use **sampling**.

**Top-k sampling:** (1) fix $k$ in advance; (2) model gives $P$ of every word given the context; (3) sort descending, drop everything outside the top $k$; (4) renormalize the remaining $k$ scores to sum to 1; (5) sample one word from the $k$ by the new weights.
**Nucleus / top-p sampling:** top-k's problem is that $k$ is fixed while the distribution shape changes (sometimes the top 10 hold almost all the mass, sometimes the distribution is flat and they hold little). Fix: keep the smallest set $V^{(p)}$ whose total probability is at least $p$:
$$\sum_{w\in V^{(p)}}P(w\mid \mathbf w_{<t})\ \ge\ p\qquad(8.48)$$
Result: the number of kept words adapts to context; the goal is the same as top-k, cut the very-low-probability tail.

## 10. Three model families [slides 24, 31, 32]

All three use the same block; they differ in the **mask**, the **training task** and size [slide 24, 32].

| Family | Attention (mask) | Trained with | Examples | Good for |
|---|---|---|---|---|
| **Decoder-only** | causal, sees only left | predict next word (causal LM) | GPT, Llama, Qwen, Typhoon | text generation, chat, QA |
| **Encoder-only** | no mask, sees both directions | predict masked words (MLM, 15% masked) | BERT, RoBERTa, WangchanBERTa | text classification, NER, search |
| **Encoder-decoder** | encoder: both directions; decoder: causal + cross-attention | convert input → output | T5 / mT5, BART, NLLB, Whisper | translation, summarization, transcription |

References on the slide: decoder-only SLP3 ch. 8 / Lee p.228; encoder-only SLP3 ch. 9 / Lee §8.6 p.192; encoder-decoder SLP3 §12.3 p.267-268.

**Task → family → Thai example** [slide 31]:

| Task | Family | Thai example |
|---|---|---|
| text classification / sentiment | encoder + classification head | WangchanBERTa on wisesight (positive / neutral / negative) |
| word segmentation, POS, NER | encoder + token-labeling head | NER on the LST20 corpus |
| translation | encoder-decoder | Thai → English, measured with chrF |
| summarization | encoder-decoder **or** decoder | Thai news summarization (ThaiSum) |
| chat, QA, RAG | decoder (LLM) | Typhoon / OpenThaiGPT + document retrieval |
| speech, image | encoder-decoder (Whisper), ViT | transcribing Thai and dialect speech |

**Decision rule** [slide 32]:
1. Output is a label or a span from the input, and enough labeled data? → **encoder + fine-tune** (fast, cheap, runs on CPU, stable results, easy to verify).
2. Need to turn one sequence into another tied tightly to the input? → **encoder-decoder** (translation, transcription, summarization).
3. Need free text, or many tasks with one model? → **decoder LLM** (start with a prompt → RAG → LoRA if still not enough).

## 11. Thai models [slide 29]

| Model | Family | Developer · year | Notes on the slide |
|---|---|---|---|
| WangchanBERTa | encoder (RoBERTa) | VISTEC-depa AI Research Institute · 2021 | trained on 78.5 GB of Thai text; used in lab part 4 |
| Typhoon 2 | decoder | SCB 10X · Dec 2024 | built on Llama 3.x / Qwen2.5; 1B-70B; has vision and audio versions |
| OpenThaiGPT 1.5 | decoder | OpenThaiGPT team · 2024 | built on Qwen2.5; 7B / 14B / 72B |
| OpenThai 2.0 * | hybrid Mamba-attention | iApp · 2026 | "per the model card": context 262k, Apache 2.0 (starred on the slide; I could not verify it) |
| Typhoon ASR (Isan) | speech | SCB 10X | dialect speech transcription, week 10 |

Common recipe: take an open multilingual model → continue training on Thai text → extend the Thai vocabulary → instruction-tune. **Why the tokenizer matters for Thai:** a tokenizer learned on English cuts Thai into very small pieces → sentences several times longer → slower and more expensive (lab part 2).

## 12. Transformer 2026, KV cache, interpretation [slides 25, 27, 28]

**2017 → 2026** [slide 27]:

| Part | Paper 2017 | LLMs in 2026 | Reason given |
|---|---|---|---|
| family | encoder-decoder | decoder-only | next-word training on huge text works for every task |
| normalization | post-norm LayerNorm | pre-norm RMSNorm (+ QK-norm) | stable deep training, cheaper |
| position | sinusoidal added at input | RoPE (some layers none = NoPE) | relative distance, can extend context |
| feed-forward | ReLU 512 → 2048 | SwiGLU (gated) | better quality at equal parameters |
| attention | multi-head, 8 heads | GQA or MLA | KV cache several times smaller |
| FFN width | dense, every token uses all | MoE, only some experts active | large capacity, low compute |
| length | single sentence | 128k-1M tokens | sliding window, hybrid |
| size | 65M-213M | about 1B to about 1T | scaling laws |

Unchanged: scaled dot-product attention, residual connections, per-token FFN, next-word prediction with softmax.

**KV cache** [slide 28]: queries from many heads share K, V. MHA = 8 Q : 8 KV; GQA = 8 Q : 2 KV; MQA = 8 Q : 1 KV; MLA (DeepSeek-V3, Kimi K2) compresses K, V into a small latent vector before storing and expands it when used. Why a cache exists (reuse the K, V of earlier tokens while generating) is not explained on the slide [general].
$$\text{cache size}=2\times\text{layers}\times\text{KV heads}\times d_{head}\times N\times\text{bytes}$$
Llama 3 8B example (32 layers, 32 Q heads, 8 KV heads, $d_{head}=128$, fp16 = 2 bytes):

| Length | MHA (32 KV) | GQA (8 KV) |
|---|---|---|
| 1 token | 512 KB | 128 KB |
| 8,192 | 4 GiB | 1 GiB |
| 131,072 | 64 GiB | 16 GiB |

[computed] GQA per token $2\cdot32\cdot8\cdot128\cdot2=131{,}072$ B = 128 KB; MHA with 32 KV heads 524,288 B = 512 KB; x8,192 → 1 and 4 GiB; x131,072 → 16 and 64 GiB. All verified.

**Interpreting the Transformer** (open research, mechanistic interpretability) [slide 25]: *attention weights* (plot each head's matrix $A$; caution: high weight does not always mean it is the "reason" for the answer) · *induction heads* (two-head circuit: sees A again → finds the earlier A → predicts the word after it, B; "A B ... A → B", e.g. "ช้าง ม้า ... ช้าง" → "ม้า"; believed to be one mechanism of in-context learning; SLP3 §8.9.1) · *logit lens* (multiply a middle layer's residual stream by the unembedding to see what each layer "is thinking of answering"; works sometimes, since middle layers were not trained to answer directly; SLP3 §8.9.2). Overview: attention moves information across words, the FFN adds knowledge, the LM head reads out the answer, all through the residual stream.

## 13. Checks and cautions on the slides

- Every worked number re-computed (section 3 attention example, $\sqrt{d_k}$ example, PE table, parameter counts, Table 2 ratios, $N\times N$ sizes, KV cache). No wrong values found; only rounding remarks above (PE cos column, [0.86, 0.72] from rounded weights).
- Slide-flagged ambiguity: EN→FR big 41.0 (text) vs 41.8 (Table 2) [slide 16].
- Not legible / not covered: the slides never write the full multi-head formula with $\text{Concat}$, define the d/e superscripts of slide 3, or explain MLM masking details or what mT5 is. The slide 29 row for OpenThai 2.0 is hedged by the slide itself. Labs (parts 2, 2.4, 4, week 10) are referenced but not in this PDF.
- The text layer scrambles Table 3 A (slide 11), the training table (slide 15) and the architecture figure (slide 7); the values here come from the images.

## 14. Project relevance and practical notes

- **Which baseline fits which stage** [slides 24, 31, 32 + inference]. Stage 1 sentence classification = "label from the input with labeled data" → rule 1: a fine-tuned encoder (WangchanBERTa + classification head) is the natural Transformer comparison against Naive Bayes / SVM / kNN. Summarization is listed for encoder-decoder (or decoder), so **mT5 (encoder-decoder, slide 24) is the matching generative baseline** for the Stage-2 extractive TF-IDF summary. An encoder-only model cannot generate text by itself [general], but it can score or embed sentences for an extractive method.
- [general] Weather reports contain numbers (temperatures, rain percentages, province names); an abstractive model can get them wrong, so a check of generated numbers against the source report is worth adding when comparing to the extractive + template output.
- [general] Sequence limits matter: BERT-style learned positions stop at 512 (slide 21), and a Thai subword tokenizer may produce many tokens per report, so long TMD bulletins may need truncation or sentence-level chunking. Attention cost grows with $n^2$ (slide 20), which is not a problem for short reports.
- [general] Tokenizers differ across models (slide 29 warns an English-trained one fragments Thai); check each model card for its tokenizer and whether the input should be pre-segmented with PyThaiNLP, and compare with the BPE / WordPiece / Unigram table in [1-2](1-2-tokenization.md).
- [general] Link to the pipeline: $QK^T$ is a learned dot-product similarity (the Transformer's version of the TF-IDF + cosine similarity score), and encoder sentence embeddings could replace TF-IDF vectors in Stage 2 as an extra comparison.
- Decoder-only training is exactly the language-model task of [5-1](5-1-language-models-ngrams.md) with a neural model (the slide: "still an LM predicting the next word as in week 5").
- Evaluation: slide 31 names chrF for translation; summarization metrics (ROUGE, BERTScore) and classifier F1 belong to the project plan (check PLAN.md for the exact choice). [general]
- Do not read attention weights as an explanation of the summary (slide 25 caution).
