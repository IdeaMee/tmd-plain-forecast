# NLP 1-2 — Tokenization

Source: `course/slides/1-2_Tokenization.pdf` (15 slides, Satida Sookpong). Text from the PDF text layer, checked against slide images (Thai text on small renders can be misread; the BPE row of the comparison table was re-checked at high zoom).
Legend: **[slide N]** = PDF page · **[general]** = general knowledge or my inference · **[computed]** = my own calculation.

**Project relevance: HIGH (Stage 0).** Thai reports have no spaces between words, so every later step (Naive Bayes counts, TF-IDF, summarization) depends on this segmentation.

---

## 1. Text as data [slides 2-3]

| Unit | Meaning | Example |
|---|---|---|
| Word | smallest meaningful standalone unit in a sentence | "playing" |
| Morpheme | smallest unit of meaning inside a word (roots, affixes, suffixes) | "play" + "-ing" |
| Unicode | each character mapped to a universal code point, the foundation of digital text | U+0041 = "A" |
| Subword (BPE) | rare words split into frequent pieces learned from a corpus | "un" + "play" + "able" |

Basic vocabulary (slide 3):
- **Corpus:** text collection used to train models (e.g. Brown Corpus, Wall Street Journal).
- **Token:** a piece of text: a word, a symbol, a punctuation mark.
- **Type:** a *distinct* word in the corpus (distinct word types).
- **Word form:** the surface form actually appearing in the corpus (inflected form).
- **Stem / Lemma:** stem = root (the slide's example: *compute* for computers, computation); lemma = dictionary form of an inflected word.

## 2. Normalization [slides 4-5]

Raw text varies: upper/lower case, punctuation, abbreviations, emoji. Text normalization = make it easy to process. Example of a rule-based method: Penn Treebank tokenization.

Normalization pipeline [slide 5]:
1. **Lowercasing**: "Hello" → "hello"
2. **Punctuation removal**: strip or separate punctuation from words
3. **Stop-word removal**: drop common words ("the", "is", "at")
4. **Stemming / lemmatization**: "running" → "run" (reduces inflections)
5. **Unicode normalization**: NFC / NFD, unify accented characters to one form

## 3. Regular expressions [slides 6-7]

Test online at regex101.com.

| Pattern | Matches |
|---|---|
| `\w+` | a word token |
| `\d{4}-\d{2}-\d{2}` | a date YYYY-MM-DD |
| `[A-Z][a-z]+` | a capitalized word (NER hint) |
| `\s+` | split on whitespace |

| Syntax | Name |
|---|---|
| `[ ]` | character class, `[aeiou]` matches any vowel |
| `*  +  ?` | quantifiers, `a+` = one or more "a" |
| `^  $` | anchors, `^Hello` matches start of string |
| `( )` | groups, `(ab)+` repeating group |
| `\|` | alternation, `cat\|dog` |
| `\w  \d  \s` | shorthand classes: word, digit, whitespace |

Project use [general]: regex is handy for pulling dates, province names, and "ฉบับที่ N" bulletin numbers out of TMD text.

## 4. What is tokenization [slide 8]

Tokenization = splitting text into smaller units (tokens): words, symbols, or sub-word units, so a computer can process it further.
- "How long is this text?" depends on how you tokenize: **1 token ≠ 1 word**.
- "don't" = 1 token or 2? (`do` + `n't`) affects downstream models.
- **Fixed tokenization:** most algorithms (e.g. perplexity) need a consistent token split.

## 5. Tokenization techniques [slides 9-11]

| Approach | How | Problem |
|---|---|---|
| Word-based | split on whitespace/punctuation: "I love NLP" → ["I","love","NLP"] | fails on contractions, compounds and **OOV** (out-of-vocabulary) words; "don't" → ["don", "'", "t"]; vocabulary becomes huge |
| Character-based | split into characters: "I love NLP" → ["I"," ","l","o","v","e"," ","N","L","P"] | no OOV, but meaning lost and sequences too long |
| Subword (BPE / WordPiece / Unigram) | split by learned frequent pieces | balances vocabulary size and sequence length; standard for current LLMs |

Evolution (slide 11): word-based → character-based → subword.

## 6. Byte-Pair Encoding (BPE) [slides 12-13]

**BPE training** = repeatedly merge the most frequent adjacent pair of symbols.

Worked example from the slide, corpus **new ×2, renew ×2, set ×1, reset ×1**:
- Step 0: characters only, vocab = {e, n, r, s, t, w}
- Step 1: pair (n, e) occurs 4 times (new×2 + renew×2) → merge to "ne"; vocab += "ne"
- Step 2: pair (ne, w) occurs 4 times → "new"
- Step 3: pair (r, e) occurs 3 times (the slide gives the count; the split renew×2 + reset×1 is [computed]) → "re"; then (re, new) → "renew"
- Step 4: continue with set/reset: (s, e) → "se", then (se, t) → "set"
- Tie note [computed]: at step 1, (e, w) also occurs 4 times; the slide picks (n, e). Ties are broken by some fixed rule (e.g. first seen); the result depends on it.

**BPE encoding** (applying it to new text):
- Split the test sentence into characters first.
- Apply the merge rules learned in training **one by one, in the order they were learned**. Frequencies in the test data do **not** matter; only the order of rules from training.
- Every unseen word can still be represented by known subword sequences.

**In practice:**
- Runs on **UTF-8 bytes (byte-level BPE)** so every language/character is supported, including Thai.
- Typical number of merges: 50,000 / 100,000 / 200,000 tokens (e.g. GPT-4o ≈ 200K).
- No unknown token any more, because there are only 256 base byte values.
- Multilingual systems may have tokens dominated by English, which disadvantages low-resource languages.

## 7. BPE vs. WordPiece vs. Unigram LM [slide 14]

| Method | Rule for choosing what to merge/keep | Used in |
|---|---|---|
| BPE | merge the pair of tokens that appears **most often** | GPT-2 / GPT-4o, RoBERTa |
| WordPiece | merge the pair that increases the training-data likelihood the most | BERT |
| Unigram LM (ULM) | start from a large vocabulary, then prune units that hurt likelihood least | SentencePiece, T5, ALBERT |

All three share the goal: balance vocabulary size against token-sequence length so the model generalizes and stays efficient.

## 8. Thai tokenization [slide 15]

- **Core challenge:** Thai has no spaces between words, e.g. "ฉันรักคุณ" has no visible word boundary; boundaries must be inferred from context and a dictionary.
- **Dictionary-based segmentation:** uses a pre-built lexicon of Thai words and scans the text for valid entries. Fast and interpretable, but limited by vocabulary coverage; OOV words (new names, slang) are the key weakness.
- **Longest matching:** greedy, at each position match the longest dictionary word.
  - Forward maximum matching (FMM): scan left to right.
  - Backward maximum matching (BMM): scan right to left.
  - **Ambiguity problem:** the page text reads "multiple valid segmentations may" and stops there, cut off by the code box (the ending is not recoverable from the PDF). For a worked ambiguity example ("ตากลม") see 2-1. [general]
- PyThaiNLP: `word_tokenize("ฉันรักคุณ", engine="newmm")`.

## 9. Project relevance and practical notes

- Stage 0 of the pipeline: segment TMD sentences with PyThaiNLP (`newmm`), normalize, and remove stop words before counting words for Naive Bayes / TF-IDF.
- [general] Weather text contains place names and technical terms (e.g. province names, "ร่องมรสุม"); the default dictionary may split them wrongly. PyThaiNLP lets you add a custom dictionary; check segmentation on a sample of reports and add missing terms.
- [general] Sentence segmentation for Thai is also non-trivial (no full stops); see NLP 2-1 / 1-1 (Thai challenges: word and sentence segmentation).
- Related: statistical segmentation and the HMM view are in [2-1](2-1-word-segmentation-pos-sequence-labeling.md).
