# NLP 5-2 — Recurrent Neural Networks (RNN, LSTM, GRU)

Source: `course/slides/5-2_RNN.pdf` (16 slides, Satida Sookpong, course 1323326 NLP). Equations read from slide images (slides 4, 6, 10, 13); Thai wording from the PDF text layer (some tone marks are missing there, so I paraphrase in English and quote Thai only where I checked the image). Figures are textbook-style (Jurafsky & Martin, "Speech and Language Processing", ch. 13 and 8; equation numbers 13.x are theirs).
Legend: **[slide N]** = PDF page · **[general]** = general knowledge or my inference · **[computed]** = my own calculation.

**Project relevance: HIGH (conceptual).** RNN is the stepping stone to seq2seq, attention and the Transformer (the project's comparison baseline); the recurrence equations and the vanishing-gradient argument are what the report should be able to explain. Notes: [6-1 encoder-decoder and attention](6-1-encoder-decoder-attention.md), [7-1 Transformer](7-1-transformer.md), [5-1 n-gram LMs](5-1-language-models-ngrams.md).

---

## 1. Why move beyond feed-forward networks? [slide 2]

- Feed-forward network (quoted definition on the slide): a multilayer network whose units are connected with **no cycles**; outputs go to the next higher layer, nothing is passed back.
- Limitations: **fixed-window** approaches (n-gram, basic dense models) only see a set number of prior tokens; they cannot capture long-range dependencies or handle variable-length sequences gracefully.
- **Sequential concept:** an RNN processes data step by step ($t-1, t, t+1$), carrying an internal **hidden state** forward. The hidden state is a memory buffer summarizing everything seen so far.

## 2. RNN topologies [slide 3]

| Topology | Description | Slide example |
|---|---|---|
| Many-to-many (aligned) | one output per input step | token classification, POS tagging |
| Many-to-one | whole sequence collapses to one label | sentiment analysis |
| One-to-many | one input unfolds into a generated sequence | image captioning |
| Many-to-many encoder-decoder | separate input and output sequences | machine translation, **summarization** |
| Text generation model | predicts the next token autoregressively, feeding each output back as the next input | language model |

## 3. The simple RNN (Elman network) [slide 4]

$$\mathbf h_t = g(\mathbf U\mathbf h_{t-1}+\mathbf W\mathbf x_t)\qquad(13.1)$$
$$\mathbf y_t = f(\mathbf V\mathbf h_t)\qquad(13.2)$$
$$\mathbf y_t=\operatorname{softmax}(\mathbf V\mathbf h_t)\qquad(13.3)$$

| Symbol | Meaning on the slide |
|---|---|
| $\mathbf x_t$ | input vector at time $t$ (embedding of the $t$-th word) |
| $\mathbf h_t$ | hidden state, the "memory" summarizing everything so far |
| $\mathbf W$ | weights from the input ($\mathbf U$: recurrent weights, back from the previous hidden state; $\mathbf V$: weights to the output) |
| $g$ | non-linear function, e.g. tanh or ReLU |

- Eq. 13.3 is the softmax case (classification / language model); $f$ in 13.2 is a generic output function the slide does not define.
- **Weight sharing is the key idea:** one set $\mathbf U,\mathbf W,\mathbf V$ is used at every position; the number of parameters does **not** depend on sentence length; any input length is accepted (unlike a feed-forward LM); $\mathbf h_{t-1}$ is a compact summary of all context since the start of the sentence.
- Shapes [general]: $\mathbf x_t\in\mathbb R^{d_x}$, $\mathbf h_t\in\mathbb R^{d_h}$, $\mathbf W\in\mathbb R^{d_h\times d_x}$, $\mathbf U\in\mathbb R^{d_h\times d_h}$, $\mathbf V\in\mathbb R^{|V|\times d_h}$ for a language model; $\mathbf h_0$ is usually the zero vector (figure 13.4 shows $h_0$ as the initial state). The slide's equations have no bias terms. Beware: other textbooks name the matrices differently ($W_{hh}$, $W_{xh}$ ...); on these slides $\mathbf U$ is recurrent and $\mathbf W$ is input.

## 4. Unrolling in time [slide 5]

- Draw the RNN along the time axis (figure 13.4): $h_0$, then $x_1\to h_1\to y_1$, $x_2\to h_2\to y_2$, $x_3\to h_3\to y_3$, with $\mathbf U$ between consecutive $h$'s, $\mathbf W$ from $x$ to $h$, $\mathbf V$ from $h$ to $y$.
- The boxes are **the same cell drawn repeatedly**, not different layers; $\mathbf W,\mathbf U,\mathbf V$ are shared by all.
- The last hidden state is influenced by all earlier words through the chain $h_1\to h_2\to h_3\to\dots$; the slide calls this both the strength of the design and the root of the vanishing-gradient problem. (The slide text says $h_1\dots h_4$ but the figure has three steps; cosmetic mismatch.)

## 5. RNN as a language model [slide 6]

Figure 13.6: input words *So long and thanks for* are embedded ($e$), pass through the RNN ($h$), $\mathbf V\mathbf h$ goes through **softmax over the vocabulary** ($\hat y$), and the targets are the next words *long and thanks for all*. Loss at each step is $-\log\hat y_{\text{next word}}$; the training loss is the average

$$L=\frac1T\sum_{t=1}^{T}L_{CE}(t),\qquad L_{CE}(t)=-\log \hat y_t[w_{t+1}]$$

**Training = self-supervision** [slide 6]
- No human labels: raw text is both input and answer; the answer is the input shifted by one position.
- **Teacher forcing:** always feed the *correct* word as $x_{t+1}$, not the word the model predicted itself.
- One training run gives both a language model and a representation usable downstream.

**How it differs from n-grams** [slide 6]
- Context is not cut off at $N-1$ words: $\mathbf h_t$ summarizes every word since the start of the sentence.
- No smoothing needed, because softmax is always $>0$: every vocabulary word has some probability even if never seen in that context.
- [general] Caveats: words outside the vocabulary (OOV) still need `<UNK>` or subwords; teacher forcing creates a train/test mismatch (at generation time the model sees its own, possibly wrong, words). Perplexity (NLP 5-1) equals $\exp$ of the average cross-entropy $L$.

## 6. Training: BPTT [slide 7]

- **Backpropagation Through Time:** unroll the RNN into a deep network with $T$ layers, then run ordinary backpropagation (see [ML 05](../ML/05-neural-networks.md)). Because weights are reused, the gradient of $\mathbf W,\mathbf U,\mathbf V$ is the **sum over all time steps**. All $h_t$ must be stored, so memory grows with $T$.
- **Truncated BPTT** (practical fix): backpropagate only $k$ steps (often $k=20$-35) instead of to the start of the sequence. Saves memory and time and helps with exploding gradients. Drawback: cannot learn relations longer than $k$.
- Warning box (paraphrased): the $\Pi$ term (a running product) is the heart of the matter; the larger $t-k$, the more factors are multiplied; if each factor is $<1$ the gradient shrinks to zero (vanishing), if each is $>1$ it blows up (exploding). **The formula with $\Pi$ is not shown on the slide** (it is referred to but missing). Standard form [general], with $a_j=\mathbf U\mathbf h_{j-1}+\mathbf W\mathbf x_j$:

$$\frac{\partial \mathbf h_t}{\partial \mathbf h_k}=\prod_{j=k+1}^{t}\frac{\partial \mathbf h_j}{\partial \mathbf h_{j-1}}=\prod_{j=k+1}^{t}\operatorname{diag}\big(g'(a_j)\big)\,\mathbf U$$

  and $\lVert\partial\mathbf h_t/\partial\mathbf h_k\rVert\le(\gamma\lVert\mathbf U\rVert)^{t-k}$ with $\gamma=\max|g'|$ ($\le1$ for tanh). A factor below 1 gives vanishing, a large factor allows explosion.

## 7. Vanishing gradient [slide 8]

- When the gradient travels back many time steps it is multiplied by the same factor again and again.
- Consequences: the model learns only **short-range** relations (about 5-10 words); it is not that there is "no gradient", but far-range gradient is drowned by near-range gradient. Symptoms: loss decreases slowly, the model forgets the beginning of the sentence.
- Thai example needing long context: "นักเรียน ที่ ได้ รับ ทุน จาก มหาวิทยาลัย เมื่อ ปี ที่ แล้ว กำลัง จะ ___" ("the student who received a scholarship from the university last year is about to ___"). The missing word is "สำเร็จการศึกษา" (graduate) and depends on "นักเรียน" far away. A simple RNN often fails because the gradient from the blank back to "นักเรียน" is tiny. This is the **direct motivation for LSTM and GRU**.
- Distance check [computed]: the slide says 11 words apart. Counting the tokens as written there are 12 words between "นักเรียน" and the blank (the blank is 13 positions after it). Off by one or two (it depends on counting/segmentation); it does not affect the argument.

## 8. Exploding gradient and gradient clipping [slide 9]

- Symptoms: loss jumps to NaN or Inf during training; weights change enormously in one update and the model breaks; easier to detect than vanishing (visible in the loss immediately).
- Cause: the factor ($\lambda$ of $\mathbf U$) is greater than 1. Slide example: $\lambda=1.5,\ k=20$ gives a multiplier of **3,325**. [computed: $1.5^{20}=3325.26$, correct]
- **Norm-based gradient clipping:**

$$\text{if }\lVert\mathbf g\rVert>\text{threshold}:\quad \mathbf g\leftarrow\mathbf g\cdot\frac{\text{threshold}}{\lVert\mathbf g\rVert}$$

  It keeps the **direction** of the gradient and changes only its length. Example [computed]: $\mathbf g=(30,40)$, $\lVert\mathbf g\rVert=50$, threshold 5 gives $(3,4)$, norm 5.
- Slide's summary: exploding gradient is fixed by clipping (easy); vanishing gradient is **not** fixed by clipping and needs a different architecture, LSTM or GRU.
- [general] Here $\lambda$ presumably means the dominant eigenvalue (more exactly, the singular values together with $g'$) of $\mathbf U$.

## 9. LSTM [slides 10-12]

Idea [slide 11]: add a "highway" for information. The context-management problem is split into two sub-problems (slide quote from J&M): (1) **remove** information no longer needed from the context, (2) **add** information likely to be needed for later decisions. The cell state $\mathbf c_t$ is updated by **addition**, not by repeated matrix multiplication, so the gradient does not shrink; gates control what to forget, keep and release; $\mathbf h_t$ is still the output passed to the next layer.

Equations [slide 10, figure 13.13: inputs $x_t$, $h_{t-1}$, $c_{t-1}$; outputs $h_t$, $c_t$]:

| Gate | Equations | Role |
|---|---|---|
| Forget | $\mathbf f_t=\sigma(\mathbf U_f\mathbf h_{t-1}+\mathbf W_f\mathbf x_t)$ (13.20), $\mathbf k_t=\mathbf c_{t-1}\odot\mathbf f_t$ (13.21) | mask: which part of old context to keep |
| Candidate | $\mathbf g_t=\tanh(\mathbf U_g\mathbf h_{t-1}+\mathbf W_g\mathbf x_t)$ (13.22) | the actual information extracted from $h_{t-1},x_t$ |
| Add (input) | $\mathbf i_t=\sigma(\mathbf U_i\mathbf h_{t-1}+\mathbf W_i\mathbf x_t)$ (13.23), $\mathbf j_t=\mathbf g_t\odot\mathbf i_t$ (13.24) | mask: which part of the new information to accept |
| New context | $\mathbf c_t=\mathbf j_t+\mathbf k_t$ (13.25) | add the two |
| Output | $\mathbf o_t=\sigma(\mathbf U_o\mathbf h_{t-1}+\mathbf W_o\mathbf x_t)$ (13.26), $\mathbf h_t=\mathbf o_t\odot\tanh(\mathbf c_t)$ (13.27) | mask: which part of $c_t$ to reveal as $h_t$ |

$\odot$ = element-wise product. Compact form: $\mathbf c_t=\mathbf f_t\odot\mathbf c_{t-1}+\mathbf i_t\odot\mathbf g_t$.

**Gate behaviour and examples** [slide 12]
- Forget gate $f_t$: $f=0$ forget everything, $f=1$ remember all. Example: at "แต่" ("but") or a new sentence the model may learn a low $f$ to drop the old context.
- Input gate $i_t$: $i=0$ accept nothing, $i=1$ accept fully. Example: a key word such as the proper name "เชียงใหม่" (Chiang Mai) should get a high $i$ so it is stored.
- Output gate $o_t$: $o=0$ release nothing, $o=1$ release fully. Example: information kept in $c_t$ but not needed yet, e.g. the gender of the subject needed only at the end of the sentence.
- All three gates use $\sigma$ (values 0-1, so they act like valves); $g_t$ uses tanh (values -1 to 1, the "substance" of the information).

[general] Why this helps: along the cell path $\partial\mathbf c_t/\partial\mathbf c_{t-1}\approx\operatorname{diag}(\mathbf f_t)$ (ignoring indirect paths through $\mathbf h_{t-1}$), so if $f$ stays near 1 the gradient is preserved instead of repeatedly multiplied by $\mathbf U$. Constant-$f$ illustration [computed]: over 100 steps $0.99^{100}=0.366$ but $0.9^{100}=2.7\times10^{-5}$. The slide equations carry no bias terms (real implementations do).

## 10. GRU [slides 13-14]

Equations on slide 13 (figure 8.16; the source link is a GeeksforGeeks page):

$$h'_t=\tanh\big(W_h\cdot[\,r_t\cdot h_{t-1},\,x_t\,]+b_h\big)\qquad h_t=(1-z_t)\cdot h_{t-1}+z_t\cdot h'_t$$

- **Reset gate** $r_t$: how much of the old memory is used when building the new candidate $h'$.
- **Update gate** ($z$ and $1-z$): how much to update the memory (mix of $h$ and $h'$).
- $h_t$ is both the memory and the output (no separate $c_t$).
- **25% fewer parameters than LSTM** [slides 13, 14]. [computed] consistent: GRU has 3 weight blocks ($r, z, h'$), LSTM has 4 ($f, i, g, o$), so GRU is 75% of LSTM. Example $d_x=d_h=256$, no biases: simple RNN $\mathbf U,\mathbf W$ = 131,072 parameters; GRU 393,216; LSTM 524,288.
- Not on the slide [general]: $z_t=\sigma(W_z[h_{t-1},x_t]+b_z)$ and $r_t=\sigma(W_r[h_{t-1},x_t]+b_r)$; the "$\cdot$" between $r_t$ and $h_{t-1}$ is an element-wise product.
- Numeric illustration of the update [computed]: $z=0.25$, $h_{t-1}=-0.4$, $h'=0.8$ gives $h_t=0.75(-0.4)+0.25(0.8)=-0.1$.

**Difference from LSTM** [slide 14, figure GRU vs LSTM]

| | GRU | LSTM |
|---|---|---|
| Gates | 2 (reset, update $z$ and $1-z$) | 3 (forget, input, output) |
| Cell state | none; $h_t$ is memory and output | separate $c_t$ |
| Character | simpler, faster | more complex |

GRU merges the forget and input gates into one update gate. **Which to use** [slide 14]: comparative studies find LSTM and GRU very close on most tasks, no clear winner; start with GRU when data is small or speed matters; choose LSTM for very long sequences with enough data.

## 11. Bidirectional and stacked RNNs [slide 15]

| | Bidirectional RNN (BiRNN) | Stacked / deep RNN |
|---|---|---|
| Idea | two separate RNNs, forward and backward; outputs at each time step are concatenated (figure 13.11) | output $h_t$ of a lower layer is the input of the layer above (figure 13.10) |
| Effect | each position sees left and right context | lower layers capture surface patterns, upper layers abstract meaning |
| Typical size | BiLSTM, usually 2 layers | 2-4 layers; deeper is usually not worth it and hard to train |

- BiLSTM was the "gold standard" of NLP in 2015-2018; a 2-layer BiLSTM was the default for NER, POS and chunking. **Thai: BiLSTM-CRF still works well for word segmentation and NER.**
- Limits: needs the whole sentence, so unusable for real-time streaming.
- Cautions: a BiRNN sees the future, so it **must not be used as an autoregressive language model** (it would cheat); bidirectional **doubles** the parameters; deeper networks should add residual connections and layer normalization.

## 12. Case study: Google NMT (2016) and uses [slide 16]

- **GNMT architecture:** encoder = 8-layer LSTM (bottom layer bidirectional, the rest unidirectional); decoder = 8-layer LSTM with **attention** to the encoder outputs; residual connections between layers; rare words handled with wordpiece (subword); training and inference parallelized on TPU.
- **Why it mattered:** replaced phrase-based statistical MT used for over a decade; reported significant error reduction in many language pairs; proved neural seq2seq works at production scale; one of the last very large RNN systems before the Transformer (2017) replaced them. Reference: Wu et al. (2016), arXiv:1609.08144.

| Task | Role of the RNN | Thai example (slide) |
|---|---|---|
| Speech recognition | sound sequence → character sequence | automatic Thai transcription in call centres |
| Translation | encoder-decoder + attention | Thai-English, Thai-Lao/Khmer |
| Summarization | generate short text from a long article | automatic Thai news headline summaries |
| Next-word prediction | keyboard language model | Thai keyboard that guesses the next word |

## 13. Formula cheat sheet

| Model | State update |
|---|---|
| Simple RNN | $\mathbf h_t=g(\mathbf U\mathbf h_{t-1}+\mathbf W\mathbf x_t)$, $\mathbf y_t=\operatorname{softmax}(\mathbf V\mathbf h_t)$ |
| LSTM | $\mathbf c_t=\mathbf f_t\odot\mathbf c_{t-1}+\mathbf i_t\odot\mathbf g_t$, $\mathbf h_t=\mathbf o_t\odot\tanh(\mathbf c_t)$ |
| GRU | $h_t=(1-z_t)h_{t-1}+z_t h'_t$ |
| Clipping | $\mathbf g\leftarrow\mathbf g\cdot\text{threshold}/\lVert\mathbf g\rVert$ if $\lVert\mathbf g\rVert>$ threshold |

Gradient factor $\lambda^k$ over $k$ steps [computed, my illustration; the slide gives only $1.5^{20}$]:

| $\lambda$ | $k=10$ | $k=20$ |
|---|---|---|
| 0.5 | $9.8\times10^{-4}$ | $9.5\times10^{-7}$ |
| 0.9 | 0.349 | 0.122 |
| 1.1 | 2.59 | 6.73 |
| 1.5 | 57.7 | 3325 |

Toy forward pass (my own made-up numbers, not on the slides) [computed]: $d_x=d_h=2$, 3-word vocabulary (ฉัน, กิน, ข้าว), embeddings ฉัน=(1,0), กิน=(0,1) as in NLP 5-1; $\mathbf W=\begin{pmatrix}0.5&-0.3\\0.2&0.4\end{pmatrix}$, $\mathbf U=\begin{pmatrix}0.1&0.2\\-0.1&0.3\end{pmatrix}$, $\mathbf h_0=\mathbf 0$, $g=\tanh$.
- Step 1 (ฉัน): $\mathbf U\mathbf h_0+\mathbf W\mathbf x_1=(0.5,\,0.2)$, so $\mathbf h_1=(0.4621,\,0.1974)$.
- Step 2 (กิน): $\mathbf U\mathbf h_1=(0.0857,\,0.0130)$, $\mathbf W\mathbf x_2=(-0.3,\,0.4)$, sum $=(-0.2143,\,0.4130)$, so $\mathbf h_2=(-0.2111,\,0.3910)$.
- $\mathbf h_2$ now depends on both words; the same $\mathbf U,\mathbf W$ were used at both steps (weight sharing).

## 14. Project relevance and practical notes

- **Stepping stone to the baseline:** simple RNN → gated cells (fixes vanishing gradient) → encoder-decoder (slides 3, 16) → attention (GNMT, slide 16) → Transformer, which replaced RNNs (slide 16). Details in [6-1](6-1-encoder-decoder-attention.md) and [7-1](7-1-transformer.md). [general] The fixed-size final hidden state of an encoder is a bottleneck, which is what attention addresses.
- **Summarization framing:** slide 16 lists summarization as an RNN encoder-decoder task. The project's own Stage 2 is extractive (TF-IDF + cosine) and needs no RNN; the seq2seq/Transformer is only the comparison baseline.
- **Stage 0 (word segmentation):** slide 15 says BiLSTM-CRF is effective for Thai segmentation; this is a neural alternative to the dictionary/statistical methods in [2-1](2-1-word-segmentation-pos-sequence-labeling.md). [general] Not planned for the project.
- **Stage 1 (classification):** a many-to-one BiLSTM over words is possible, but with small data the planned Naive Bayes / SVM / kNN are simpler and easier to explain. [general]
- **Little data:** slide 14 advises starting with GRU when data is small or speed matters.
- **If an RNN/seq2seq is trained:** use gradient clipping (slide 9); truncated BPTT with $k\approx$ 20-35 (slide 7) only when sequences are long; use the **decoder unidirectionally** (slide 15: no BiRNN for autoregressive generation), the encoder may be bidirectional (as in GNMT). [general] Weather reports are short, so long-range dependency is a smaller issue than copying numbers, place names and units correctly.
- **Language-model link (NLP 5-1):** the RNN LM replaces counting with a learned function, needs no smoothing and has unbounded context, but is slower than table-lookup n-grams. [general]
- Embeddings feeding $\mathbf x_t$ come from [4-1](4-1-word-embeddings.md).
