# Course notes index (ML + NLP)

Study notes written from the lecture slides in `../slides/`, in English, so an assistant (or a teammate) can read markdown instead of PDF/PPTX. Project plan: [../../PLAN.md](../../PLAN.md).

## How to use

1. Find the chapter below (or use the "Where is X?" table).
2. Open only that file; each is self-contained: key ideas, definitions, LaTeX formulas, algorithms, worked examples, and a final **Project relevance** section.
3. Trust the provenance tags: **[slide N]** = taken from the slide/page; **[general]** = general knowledge or my inference, *not* taught by the lecturer; **[computed]** = my own recomputation of a slide example. **CHECK** marks a place where the slide's own number or label is inconsistent.

How the notes were made: text layer for words, slide images for formulas/figures/tables, every numeric example recomputed in Python. The NLP chapters 2-1, 4-1, 6-1, 7-1 (and, in the second batch, ML 02/03/05/06/07 and NLP 1-1/3-1/5-2) were drafted by helper agents with the same method.

**Audit status (2026-11-14):** the main chapters ML 08, 09, 04 and NLP 1-2, 2-1, 4-1, 6-1 were each re-audited by an independent reviewer against all slide images (formulas, citations, numbers, provenance tags); the audits found no wrong formulas or numbers, only tag/attribution/wording fixes, already applied. The other chapters (ML 01, 02, 03, 05, 06, 07 and NLP 1-1, 3-1, 5-1, 5-2, 7-1) were only spot-checked, not re-audited. If a number matters (exam, report), verify against the slide.

## Machine Learning ([ML/00-index.md](ML/00-index.md))

| # | Chapter | Project relevance |
|---|---|---|
| 01 | [Introduction to ML](ML/01-intro-to-ml.md) | low: T/P/E framing, LMS, grading |
| 02 | [Concept learning](ML/02-concept-learning.md) | low |
| 03 | [Decision tree](ML/03-decision-tree.md) | medium: alternative Stage-1 classifier |
| 04 | [k-NN](ML/04-knn.md) | medium-low: Stage-1 comparison |
| 05 | [Neural networks](ML/05-neural-networks.md) | background for RNN/Transformer |
| 06 | [Clustering](ML/06-clustering.md) | low-medium: grouping sentences/reports |
| 07 | [Genetic algorithms](ML/07-genetic-algorithms.md) | low |
| 08 | [Bayesian learning / Naive Bayes](ML/08-bayesian-learning.md) | **high: Stage-1 classifier** |
| 09 | [SVM](ML/09-svm.md) | medium: Stage-1 comparison |

## NLP ([NLP/00-index.md](NLP/00-index.md))

| # | Chapter | Project relevance |
|---|---|---|
| 0 | [Course info and grading](NLP/00-course-info.md) | rules, dates |
| 1-1 | [Intro to NLP](NLP/1-1-intro-to-nlp.md) | framing (NLU/NLG, tasks) |
| 1-2 | [Tokenization](NLP/1-2-tokenization.md) | **high: Stage 0** |
| 2-1 | [Word segmentation, POS, sequence labeling](NLP/2-1-word-segmentation-pos-sequence-labeling.md) | **high: Stage 0 (Thai segmentation)** |
| 3-1 | [Syntax and parsing](NLP/3-1-syntax-parsing.md) | low |
| 4-1 | [Word embeddings, TF-IDF, cosine](NLP/4-1-word-embeddings.md) | **high: Stage 2 (TF-IDF + cosine)** |
| 5-1 | [Language models, n-grams](NLP/5-1-language-models-ngrams.md) | medium: smoothing, perplexity |
| 5-2 | [RNN](NLP/5-2-rnn.md) | background |
| 6-1 | [Encoder-decoder, attention, evaluation](NLP/6-1-encoder-decoder-attention.md) | **high: metrics (BLEU/chrF; ROUGE/BERTScore are [general])** |
| 7-1 | [Transformer](NLP/7-1-transformer.md) | medium: baseline model |

Not in the folder: NLP 6-2 (a separate attention slide set, if it exists), 8-1 LLMs, 9-1 Advanced application, 10-1 Multimodal LLMs.

## Where is X?

| Need | File and section |
|---|---|
| Naive Bayes classifier, text-categorization algorithm, m-estimate | [ML 08](ML/08-bayesian-learning.md) sections 7 |
| Linear/kernel SVM, soft margin, C | [ML 09](ML/09-svm.md) |
| k-NN, distance norms | [ML 04](ML/04-knn.md) |
| Thai word segmentation (FMM/BMM, statistical, newmm), HMM/Viterbi | [NLP 2-1](NLP/2-1-word-segmentation-pos-sequence-labeling.md), [NLP 1-2](NLP/1-2-tokenization.md) |
| Cosine similarity, TF-IDF formulas (and the slide's tf inconsistency) | [NLP 4-1](NLP/4-1-word-embeddings.md) sections 4-6 |
| Add-one / add-k smoothing, perplexity | [NLP 5-1](NLP/5-1-language-models-ngrams.md) |
| BLEU, chrF, beam search, attention basics | [NLP 6-1](NLP/6-1-encoder-decoder-attention.md) |
| Self-attention, Q/K/V, positional encoding, model families | [NLP 7-1](NLP/7-1-transformer.md) |
| Grading, dates, mini-project rubric | [NLP 0](NLP/00-course-info.md), [ML 01](ML/01-intro-to-ml.md), [PLAN.md](../../PLAN.md) |

## Slide inconsistencies worth remembering

- **TF-IDF (NLP 4-1):** formula tf = 1 + log10(count) but the worked example uses log10(count + 1); the slide's printed results follow the latter. Library defaults (scikit-learn) differ again.
- **Checkers value signs (ML 01):** the slide gives the blue player V = −100 for a win, the reverse of the usual textbook convention; its example follows the slide.
- **Evaluation metrics (NLP 6-1):** the lecture has no ROUGE; the note's ROUGE/BERTScore text is general knowledge, not lecturer content.
- **Viterbi/HMM and segmentation examples (NLP 2-1):** several printed parenthesized lengths and rounded intermediate values do not match; all flagged **CHECK** in that note.
- Course code appears as 1323326 and 1323404 in different NLP slides.
