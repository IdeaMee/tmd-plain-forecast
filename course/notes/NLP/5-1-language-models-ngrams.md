# NLP 5-1 — Language Models and N-grams

Source: `course/slides/5-1_Language_Models_Ngrams.pdf` (13 slides, Satida Sookpong). Formulas read from slide images; Thai wording from the PDF text layer (some tone marks are missing in that layer, so I paraphrase in English).
Legend: **[slide N]** = PDF page · **[general]** = general knowledge or my inference · **[computed]** = my own calculation.

**Project relevance: MEDIUM.** Not part of the main pipeline, but (a) the smoothing ideas (add-one, add-k) are the same trick as the m-estimate in Naive Bayes (ML 08), (b) statistical word segmentation (NLP 2-1) is an n-gram idea, and (c) bigram features can enrich Stage-1 sentence classification. [general]

---

## 1. What is a language model? [slide 2]

A language model (LM) assigns a **probability to a sequence of words**: "how likely is this word sequence in this language?" and "what is the next word likely to be?"

1. $P(W)=P(w_1,w_2,\dots,w_n)$, probability of the whole sequence
2. $P(w_n\mid w_1\dots w_{n-1})$, probability of the next word

**Chain rule** links the two views:

$$P(w_1^n)=P(w_1)\,P(w_2\mid w_1)\,P(w_3\mid w_1w_2)\cdots P(w_n\mid w_1^{n-1})=\prod_{i}P(w_i\mid w_1\dots w_{i-1})$$

Uses: speech recognition ("ฉันกินข้าว" is more probable than "ฉันกินค่าว"), machine translation (choose the most natural translation), autocomplete on a phone keyboard, large language models (ChatGPT/Claude are very large LMs).

## 2. N-gram models [slides 3-4]

**Markov assumption:** the next word depends only on the previous $N-1$ words.

$$P(w_n\mid w_{1:n-1})\approx P(w_n\mid w_{n-N+1:n-1})\qquad(3.8)$$

**Maximum likelihood estimation (MLE)** = "count and normalize"; the values that make the training corpus most probable:

$$P(w_n\mid w_{n-N+1:n-1})=\frac{C(w_{n-N+1:n-1}\,w_n)}{C(w_{n-N+1:n-1})}\qquad(3.12)$$

- bigram: $P(w_n\mid w_{n-1})=\dfrac{C(w_{n-1}w_n)}{C(w_{n-1})}$
- trigram: $P(w_n\mid w_{n-2}w_{n-1})=\dfrac{C(w_{n-2}w_{n-1}w_n)}{C(w_{n-2}w_{n-1})}$

| N | Name | Context used (slide example: predict "กระเพรา" / "ผัด") | Accuracy | Sparsity |
|---|---|---|---|---|
| 1 | Unigram | none, just word frequency, e.g. $P(\text{ผัด})$ | very low | no problem, but model nearly useless |
| 2 | Bigram | previous 1 word, $P(\text{ผัด}\mid\text{ข้าว})$ | fair | some unseen bigrams |
| 3 | Trigram | previous 2 words, $P(\text{ผัด}\mid\text{กิน ข้าว})$ | good | most trigrams have zero count |
| 4+ | 4-gram and up | previous 3+ words | very good if enough data | almost every n-gram is zero, unusable |

**Bias-variance trade-off** [slide 4]: larger $N$ captures more context (low bias) but data gets sparse and estimates are noisy (high variance). In practice trigram to 5-gram is the common balance.

## 3. Evaluating an LM [slides 5-6]

- **Extrinsic evaluation** (best): plug the LM into a real system (speech recognition, MT, chatbot) and measure the system. Expensive and slow (days per experiment).
- **Intrinsic evaluation** (cheaper): measure the model directly with **perplexity**; good for pilot experiments. Caution: lower perplexity does not guarantee a better downstream task.
- **Three data splits:** training set (learn parameters), development set (tune hyperparameters), test set (final measurement). **Never use the test set to build or tune the model**, or perplexity will be misleadingly low. Comparing perplexity between two models is valid only if both use the **same vocabulary**.

**Perplexity** [slide 6]:

$$\text{perplexity}(W)=P(w_1w_2\dots w_N)^{-\frac1N}=\sqrt[N]{\frac{1}{P(w_1w_2\dots w_N)}}\qquad(3.14)$$

With the chain rule applied:

$$\text{perplexity}(W)=\sqrt[N]{\prod_{i=1}^{N}\frac{1}{P(w_i\mid w_1\dots w_{i-1})}}\qquad(3.15)$$

Interpretation:
- It is the **inverse probability** of the test set, normalized per word by taking the $N$-th root. The length normalization is needed because longer text always has smaller probability.
- **Lower perplexity = better model.**
- Another view, **weighted average branching factor**: PP = 100 means the model is as confused as if it had to choose among 100 equally likely words.
- Slide example, Wall Street Journal (train 38M words, test 1.5M words): perplexity Unigram **962**, Bigram **170**, Trigram **109**.

## 4. Zeros and unknown words [slide 7]

**Problem 1, zero counts:** the words exist in the vocabulary but the n-gram never appeared in training. Slide example: "ฉัน" and "ผลไม้" both occur but $C(\text{ฉัน},\text{ผลไม้})=0$, so $P(\text{ผลไม้}\mid\text{ฉัน})=0/3=0$; any sentence containing it gets $P(W)=0$ and **perplexity = ∞** (division by zero).

**Problem 2, unknown words (OOV):** words never seen in training (new slang, proper names, new loanwords). Worse for Thai because wrong word segmentation can create "new words" not in the vocabulary. The model gives them probability zero.

**Open vocabulary with `<UNK>`:**
1. Create a special token `<UNK>` for "unknown word".
2. Fix a vocabulary $L$ of size $V$ (from a dictionary, or words above a frequency threshold in training).
3. When normalizing training data, replace words not in $L$ with `<UNK>` and count it like any word.
4. At test time, an unseen word uses the probability of `<UNK>`.

## 5. Smoothing [slides 8-10]

**Laplace (add-1) smoothing**: add 1 to every count (bigram):

$$P_{Laplace}(w_n\mid w_{n-1})=\frac{C(w_{n-1}w_n)+1}{\sum_w\big(C(w_{n-1}w)+1\big)}=\frac{C(w_{n-1}w_n)+1}{C(w_{n-1})+V}\qquad(2.17)$$

Drawback: moves too much probability mass from seen n-grams to unseen ones, so it can be poor for some tasks.

**Add-k smoothing**: add $0<k<1$ instead of 1:

$$P^*_{Add\text{-}k}(w_n\mid w_{n-1})=\frac{C(w_{n-1}w_n)+k}{C(w_{n-1})+kV}\qquad(2.18)$$

More flexible, but $k$ must be tuned on the development set.

**Backoff:** if $C(\text{trigram})>0$ use the trigram; if 0, back off to the bigram; if still 0, to the unigram. Uses high-order n-grams when data exists. Needs a discount factor so probabilities still sum to 1.

**Interpolation:** always mix all levels (not choose one):

$$\hat P(w_n\mid w_{n-2}w_{n-1})=\lambda_1P(w_n\mid w_{n-2}w_{n-1})+\lambda_2P(w_n\mid w_{n-1})+\lambda_3P(w_n)\qquad(2.19)$$

$\lambda$ weights are learned from held-out data (usually better than backoff); **the $\lambda$'s must sum to 1**.

Slide example, predict the word after "กิน ข้าว", candidate "ผัด", with $\lambda=(0.6,0.3,0.1)$: $P=0.6\times0.00+0.3\times0.20+0.1\times0.01=0+0.060+0.001=0.061$. [arithmetic checked] Even though the trigram probability is zero, the model still gives a non-zero value from lower levels.

**Kneser-Ney** (best of the n-gram family): replace "how common is this word?" by the **continuation probability**, "how many *different* words does it follow?". Words that appear in many new contexts deserve higher probability in unseen contexts.
Slide example (total bigram types in corpus = 500):

| Word $w$ | $C(w)$ | # distinct words preceding it $\lvert\{v:C(v,w)>0\}\rvert$ | $P_{CONT}(w)$ | Meaning |
|---|---|---|---|---|
| ยอร์ก | 60 | 1 | 1/500 = 0.0020 | only follows "นิว" (New York) |
| เมือง | 60 | 45 | 45/500 = 0.0900 | follows many different words |

So $P_{CONT}(w)=\dfrac{\lvert\{v:C(v,w)>0\}\rvert}{\text{number of bigram types}}$ (formula inferred from the table). [general] Full Kneser-Ney also uses absolute discounting, per the summary table.

**Summary table** [slide 11]:

| Method | Idea | Notes |
|---|---|---|
| Laplace (add-1) | add 1 to every count | simplest; shifts too much mass, not used for real LMs |
| Add-k | add small $k$ | more flexible, $k$ must be tuned |
| Backoff | fall back to lower order when count is zero | needs discount so sum = 1 |
| Interpolation | mix all orders with weights $\lambda$ | usually better than backoff |
| Kneser-Ney | absolute discount + continuation probability | best n-gram method, the standard of the 2000s |

**Limits smoothing cannot fix** (the reason to move to neural LMs): sparsity remains (most n-grams still zero); no sharing between similar words (the model does not know "แมว" and "หมา" are similar, so what it learns about P(กิน|แมว) cannot be used for P(กิน|หมา)); context limited to $N-1$ words (misses long-distance dependencies); model size grows exponentially with $N$.

## 6. From n-gram to neural LMs [slides 12-13]

| Aspect | N-gram LM (statistical) | Neural LM |
|---|---|---|
| Learning | count frequencies from corpus | learn parameters with gradient descent |
| Context | fixed window of $N-1$ words | RNN: theoretically unlimited |
| Similar words | no notion of similarity ("แมว" ≠ "หมา") | nearby embeddings share knowledge |
| Unseen data | needs smoothing/backoff | generalizes through the vector space |
| Model size | grows like $O(V^N)$ | grows linearly with $V$ (embedding + weights) |
| Speed | very fast (table lookup) | slower (matrix computation) |

Key idea: instead of **counting**, **learn a function** $f(w_1\dots w_{t-1})\to$ a probability distribution over the next word, representing each word by a dense vector learned jointly with the model.

Embedding setup [slide 13]: toy 2-D embeddings used in the following examples: ฉัน = (1.0, 0.0), กิน = (0.0, 1.0), ข้าว = (0.5, 0.5) (real ones are 100-1024 dims). Initialization options: random and train from scratch; load word2vec/GloVe/fastText and freeze; load and fine-tune (usually best with little data). For Thai use thai2fit or fastText-th trained on Thai Wikipedia. Embedding parameters are often the largest part of a model; OOV is handled by subword/BPE (NLP 1-2); bigger dimension is not always better (risk of overfitting on small corpora).

## 7. Project relevance and practical notes

- Same smoothing idea as Naive Bayes (ML 08): the "+1 / +|Vocabulary|" estimate is Laplace smoothing.
- [general] A bigram language model could be used for a statistical word segmenter (NLP 2-1 compares segmentations by $\prod P(w_i)$, the unigram case).
- Perplexity is the intrinsic metric for LMs; for this project the summary metrics are ROUGE/BERTScore and classifier F1 instead (see PLAN.md).
