# NLP notes — index

Course: Natural Language Processing (lecturer Satida Sookpong). Slides: `../../slides/*.pdf`. Overall index: [../README.md](../README.md). Legend of provenance tags is in the README.

| # | File | What it covers | Project relevance |
|---|---|---|---|
| 0 | [00-course-info.md](00-course-info.md) | outline, CLOs, weekly timetable, grading, groups (rubric is in PLAN.md) | rules and dates |
| 1-1 | [1-1-intro-to-nlp.md](1-1-intro-to-nlp.md) | what NLP is, history, levels of language, upstream vs. downstream tasks, NLU/NLG, challenges (Thai examples), tools | framing |
| 1-2 | [1-2-tokenization.md](1-2-tokenization.md) | text as data, normalization, regex, word/char/subword tokenization, BPE vs. WordPiece vs. Unigram, Thai tokenization | **high (Stage 0)** |
| 2-1 | [2-1-word-segmentation-pos-sequence-labeling.md](2-1-word-segmentation-pos-sequence-labeling.md) | FMM/BMM, statistical segmentation, POS tagging, HMM, Viterbi, CRF, NER/sequence labeling | **high (Stage 0)** |
| 3-1 | [3-1-syntax-parsing.md](3-1-syntax-parsing.md) | CFG, PCFG, CYK, dependency parsing, parser evaluation | low |
| 4-1 | [4-1-word-embeddings.md](4-1-word-embeddings.md) | co-occurrence vectors, cosine similarity, TF-IDF, PMI/PPMI, word2vec, GloVe, fastText, contextual embeddings | **high (Stage 2: TF-IDF + cosine)** |
| 5-1 | [5-1-language-models-ngrams.md](5-1-language-models-ngrams.md) | n-gram LM, MLE, perplexity, add-1/add-k, backoff, interpolation, Kneser-Ney | medium |
| 5-2 | [5-2-rnn.md](5-2-rnn.md) | RNN, vanishing gradient, LSTM/GRU | background |
| 6-1 | [6-1-encoder-decoder-attention.md](6-1-encoder-decoder-attention.md) | seq2seq, beam search, BLEU/chrF (and [general] ROUGE/BERTScore), attention | **high (metrics)** |
| 7-1 | [7-1-transformer.md](7-1-transformer.md) | self-attention, Q/K/V, multi-head, positional encoding, model families (encoder/decoder), efficiency | medium (baseline) |

Not in the folder: 6-2 (attention as a separate deck, if any), 8-1 LLMs, 9-1 Advanced application, 10-1 Multimodal LLMs.

## Mapping to the project pipeline

| Stage | Tools | Notes to read |
|---|---|---|
| 0. Prepare Thai text | segmentation (newmm / dictionary / statistical), normalization, stop words | 1-2, 2-1 |
| 1. Classify sentences (ML course) | features: bag of words / TF-IDF | 4-1, then ML 08/09/04 |
| 2. Summarize | TF-IDF weights, cosine similarity, templates (NLG) | 4-1, 1-1 |
| Baselines and metrics | n-gram/Lead-3, Transformer baseline; BLEU/chrF, ROUGE/BERTScore | 6-1, 7-1, 5-1 |

## Reading order

1-2 → 2-1 → 4-1 → 6-1 (metrics section) → 7-1; read 5-1 for smoothing ideas (same trick as Naive Bayes in ML 08), and 5-2 before 6-1/7-1 if the attention material is unclear.
