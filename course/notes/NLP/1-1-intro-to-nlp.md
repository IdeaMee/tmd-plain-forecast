# NLP 1-1 — Introduction to NLP

Source: `course/slides/1-1_Intro_to_NLP.pdf` (33 slides, Satida Sookpong). Text from the PDF text layer; the history timeline, levels-of-language diagram, pipeline figure and the Thai example slides were checked against slide images (diagram and meme crops re-checked at 2.5x zoom). The text layer drops some Thai tone marks, so Thai words below are taken from the images and the English is my own translation.
Legend: **[slide N]** = PDF page · **[general]** = general knowledge or my inference · **[computed]** = my own calculation.

**Project relevance: MEDIUM (concepts and vocabulary).** This is an overview chapter with no formulas. It gives the vocabulary used everywhere else (upstream/downstream, NLU/NLG, levels of language) and the list of Thai-specific difficulties (segmentation) that motivate Stage 0. Slides 3, 5, 15, 19, 21, 29, 32 are section dividers with no content (What / History / NLP task / Main component / Challenge / Application / Tools); slide 2 is the outline.

---

## 1. What is NLP [slide 4]

> "NLP is the science that integrates linguistics, computer science, and artificial intelligence to enable computers to **understand, interpret, and generate** human language." (slide cites "Huaping")

- Built from 3 fields: **Linguistics + Computer Science + Artificial Intelligence**.
- Core problem on the slide: **human language (meaning) <-> computer language**, i.e. translate between meaning that people express and data a computer can process (the slide's meme: "alphabets, sentences, words, information everywhere").
- The definition has three verbs, which map onto the three components in section 5: understand (NLU), interpret/reason (KAI), generate (NLG).

## 2. History [slides 6-12]

Roadmap line (slide 6): **philosophy -> rules -> statistics -> learned representations -> massively pretrained transformers.**

| # | Period | Theme | Items on the slide |
|---|---|---|---|
| 1 [7] | Before 1960s | Machine translation (rule-based); "philosophical roots" = relation between words and languages | 1950 Alan Turing, "Computing Machinery and Intelligence", proposes the **Turing Test**. 1952 international conferences on MT use rule-based and stochastic techniques. 1957 Noam Chomsky, universal grammar / **Chomsky Hierarchy**. Slide note: "Human define knowledge" |
| 2 [8] | 1960s-70s | Early AI on NLP | 1961 **BASEBALL** (Green et al.): Q&A domain-expert system, input limited to one domain in key-value form, e.g. {Month: July, Place: Boston, Team: Red Sox, Score: 5}. 1968 **Minsky's inference engine**: AI-based question answering with knowledge-based interpretation of questions and answers. 1970 **Augmented Transition Networks** (William A. Woods): represent natural-language input and encode real-world knowledge in machine-understandable form |
| 3 [9] | 1970s-80s | "Grammatical logic": knowledge, logic and reasoning | Powerful sentence processing, early Q&A chatbots, SRI's **Core Language Engine (CLE)**. Pipeline: text (message) -> morphology (word structure) -> syntax -> semantics -> logical form -> context -> meaning. **Discourse Representation Theory (DRT)**: interpret meaning **across sentences** |
| 4 [10] | 1980s-2000s | AI and machine learning; corpus linguistics | Hopfield network (John Hopfield; slide wording: machine learning vs complex rule-based and stochastic methods, "hand crafted feature"). Corpus linguistics and lexicalization: more computing power and memory, corpus-based machine learning, lexicalized grammar. 2006 **IBM DeepQA** (David Ferrucci): question-answering system, "large algorithm, learn from data" |
| 5 [11] | 2010s-2017 | Cloud, mobile, big data, deep networks | RNNs with **LSTM** become the workhorse for sequence modeling. Google, Amazon, Facebook invest in agents and deep nets: 2013 **Word2Vec** (word as a vector, Google); 2014 **Seq2Seq, Attention**; 2016 **Google NMT** (Google Translate) |
| 6 [12] | 2017-2026 (slide label: "Stage 6, added") | Transformers and LLMs | 2017 **Transformer**, "Attention is all you need" (Vaswani et al., Google), self-attention. 2018-2020 pretrained giants **BERT, GPT-2, GPT-3**: pretrain one giant model, then adapt it. Nov 2022 **ChatGPT**: OpenAI chat interface reaches 1 million users in five days. 2023-2026 frontier race (GPT-4/5, Claude, Gemini, LLaMA, DeepSeek): multimodal, reasoning, coding, agentic ability |

Slides 13-14 ("NLP today"): slide 13 is a figure of a timeline of representative LLMs 2019-2026 from a Springer survey of large language models (Zhao et al.); slide 14 is a screenshot of an LLM leaderboard (llm-stats.com) with columns rank, model, reasoning, coding, agent, context, speed, price. Slide gives no commentary; I do not copy the model names.

Caveats [general]:
- Hopfield networks (1982) are neural-network memory models, not an NLP-specific method; the slide's wording for stage 4 is loose. Treat "1980s-2000s" as the shift from hand-written rules to **statistical / corpus-based learning**, which is the point the slide makes.
- IBM DeepQA (built from 2006) is the system behind IBM Watson, which won the quiz show Jeopardy! in 2011.
- The arXiv links on slide 12 are 1706.03762 (the Transformer paper) and 2005.14165 (the GPT-3 paper).
- Course-relevant takeaway: stage 1-3 = knowledge written by humans (rules/logic); stage 4 = statistics learned from corpora (Naive Bayes, n-grams belong here); stage 5-6 = learned representations (embeddings, then pretrained transformers).

## 3. Levels of language [slides 16-17]

**Slide 16** is a concentric-ring diagram (Wikimedia "Major levels of linguistic structure"). From the center outward:

| Level | What it studies (label in the ring) | Order |
|---|---|---|
| Phonetics | speech sounds | innermost |
| Phonology | phonemes (sound categories) | |
| Morphology | words (structure of words) | |
| Syntax | phrases and sentences (grammar) | |
| Semantics | literal meaning of phrases and sentences | |
| Pragmatics | meaning in context of discourse | outermost |

**Slide 17** gives the "5 steps in NLP" (Twilio graphic) with the lecturer's one-line gloss:

| Step | Name | Lecturer's gloss |
|---|---|---|
| 1 | Lexical analysis | Text -> paragraph, sentence, word (split the text into units) |
| 2 | Syntactic analysis | Grammar + relationships between words |
| 3 | Semantic analysis | Exact meaning (of one sentence) |
| 4 | Discourse integration | Meaning of the sentence based on the previous sentence (e.g. a pronoun) |
| 5 | Pragmatic analysis | Actual meaning based on context and real-world knowledge |

- [general] The 5 NLP steps are the text-processing version of the 6 linguistic levels: phonetics and phonology only matter for speech, so a text pipeline starts at the lexical/morphological level; "discourse integration" is a step the ring diagram folds into semantics/pragmatics.
- Direction: each level builds on the one before (words -> grammar -> sentence meaning -> cross-sentence meaning -> real-world meaning). Errors at a lower level (for example wrong word segmentation) propagate upward. [general]

## 4. Upstream and downstream tasks [slide 18]

| | Upstream tasks | Downstream tasks |
|---|---|---|
| Slide wording | Linguistic preprocessing; pre-training model | Applied tasks built on the upstream output; specific application; fine-tuning |
| Examples | tokenization, tagging, parsing | classification, translation, Q&A |

Pipeline figure on the slide: **Text -> Tokenize + Normalize -> POS Tagger -> Syntactic Parsing -> NER (Named-Entity Recognition) -> Application**. The first four boxes after "Text" are upstream (they prepare linguistic structure); the final "Application" is the downstream task that uses it.

- The slide groups **pre-training** with upstream and **fine-tuning** with downstream, so it uses the words in two senses at once: (a) preprocessing vs application in a classic pipeline, (b) pretraining vs adaptation of a large model. [general] Both senses share the idea "general-purpose first, task-specific afterwards".
- Definitions to remember: **NER** = identify people, places, dates, etc. (slide 30 wording). The slides do not define the other two, so [general]: **POS tagging** = label each word with its part of speech; **syntactic parsing** = recover the grammatical structure of the sentence.

## 5. Main components of NLP: NLU, KAI, NLG [slide 20]

Drawn as three boxes in sequence **NLU -> KAI -> NLG**:

| Component | Full name | Role (slide wording) |
|---|---|---|
| NLU | Natural Language Understanding | Interprets meaning, intent, and structure from human input |
| KAI | Knowledge Acquisition and Inferencing | Applies knowledge representation and inference (reasoning) to process the intent |
| NLG | Natural Language Generation | Produces fluent, human-readable text or speech as output |

[general] Not every application uses all three: spam filtering is NLU only; machine translation and chatbots use NLU and NLG; question answering over a knowledge base also uses KAI.

## 6. Why NLP is hard [slides 22-28]

Five core challenges (slide 22), each with a Thai heading and example. Thai glosses below are my translations; the slides give only the examples, and the "why it matters" readings are my inference unless the slide states them.

| Challenge | Slide definition | Thai heading |
|---|---|---|
| **Abstractness** | Meaning is rarely literal; words encode concepts beyond their surface form | ความเป็นนามธรรม |
| **Combinability** | Words combine in near-infinite ways, producing new, unseen meanings | ผสมกันได้ ("can be mixed") |
| **Evolutiveness** | Language constantly evolves with new slang, terms and usage | มีวิวัฒนาการ ("evolving") |
| **Nonstandardness** | Typos, dialects and informal grammar deviate from clean rules | ไม่มีหลักการที่แน่นอน ("no fixed rules") |
| **Subjectivity** | Tone, sentiment and intent vary by speaker, context and culture | ขึ้นกับแต่ละบุคคล/บริบท ("depends on person/context") |

Slide 22 closes with a joke line: "ภาษาไทยง่ายเพราะเราเป็นคนไทย" = "Thai is easy because we are Thai" (my reading [general]: native speakers do not notice how hard it is).

**Thai examples used by the lecturer:**

- **Abstractness [slide 23].** The slide shows "ไปให้แม่แกทำ" (literally "go have your mother do it"; no gloss on the slide, I read it as a sarcastic brush-off [general]) and two flips where the literal word and the intended meaning are opposite:
  - สวย ("beautiful") -> สวยกี่โมง ("beautiful at what time?") = **not beautiful**
  - ได้ ("can / OK") -> ได้อยู่ = **cannot** (the slide's equation)
  - So the surface form is positive but the meaning is negative; a bag-of-words model sees only "สวย" or "ได้".
- **Combinability [slide 24].**
  - แม่ ("mother") -> แม่น้ำ ("river", lit. mother of water) -> แม่ยก (a female fan/supporter) -> แม่ไม้มวยไทย (the fundamental techniques of Muay Thai): one word, many compounds with unrelated meanings (compound glosses [general]).
  - กับ = "with", ข้าว = "rice", กับข้าว = **"no rice"** (slide's own gloss: the compound does not mean rice; [general] it means side dishes eaten with rice).
  - Meme on the slide: ไป (bpai) = "to go", สบาย (sà-baai) = "comfortable", **ไปสบาย = "passed away"**. Two common words combine into a meaning you cannot get by adding them.
- **Evolutiveness [slide 25].** Slang drift: ใช่ไหม ("right?") -> ใช่ปะ -> ช้ะ (increasingly reduced, informal forms; [general] reading); เลิศ ("excellent") -> เริด (slang variant); "จะรั่ว" (current slang, literally "going to leak"; slide gives no gloss). A dictionary built from older text will not contain these.
- **Nonstandardness [slide 26].** The sentence "กำลัง จะ ไป กินข้าว อยู่ แล้ว" stacks several tense/aspect markers (กำลัง, จะ, อยู่, แล้ว); the slide then shows shorter variants with different meanings: กำลังจะไปกินข้าว ("about to go eat"), กินข้าวอยู่ ("is eating"), กินข้าวแล้ว ("has eaten"). Particles are optional and can be combined or dropped freely, and the spaces differ between the full and shortened writings, so there is no fixed rule to code.
- **Subjectivity [slide 27].**
  - แกงส้ม - แกงเหลือง ("sour curry" vs "yellow curry"): the slide gives no gloss; [general] reading: what a dish is called, or which dish a name refers to, depends on region and speaker.
  - "ไปส่ง" กินข้าวหน่อย: quoted phrase "ไปส่ง" (go drop off / see off) inside a sentence about eating; the slide does not explain the intended reading.
  - Two memes: a Spider-Man pointing meme labelled with seven Thai words that all sound like "khao" and differ by tone/vowel: คาว (fishy), เข้า (enter), เข่า (knee), เขา (he/she), ข่าว (news), ขาว (white), ข้าว (rice); and a screenshot from a 2012 Thai TV drama (แรงเงา) with the caption "นกอยู่ข้างพี่ตานะคะ" (no gloss). The slides do not say what these are meant to show; the first is clearly about near-identical-sounding words.

**Thai-specific challenge [slide 28]:** **Segmentation (การตัดคำภาษาไทย)**, split into **word segmentation** and **sentence segmentation**. The slide shows two social-media "can you read this?" images of long unspaced Thai text (one begins "ใครเก่งภาษาไทยมาลองอ่านกันดูซิ" = "whoever is good at Thai, try reading this"; the other is lines of strings like หมา / หู / หมี / เห็น / หัน that can be cut in several ways). Point: with no spaces, a reader (and a program) has to decide the word boundaries, and several segmentations can be valid. Details of the algorithms are in [1-2 tokenization](1-2-tokenization.md) and [2-1](2-1-word-segmentation-pos-sequence-labeling.md).

## 7. Applications [slides 30-31]

Slide 30 (tasks):

| Task | Slide description |
|---|---|
| Text classification | Assigning labels like spam or topic categories |
| Sentiment analysis | Detecting positive, negative or neutral emotion |
| Machine translation | Converting text from one language to another |
| Named entity recognition | Identifying people, places, dates, etc. |
| **Text summarization** | Shortening text while keeping key meaning |
| Question answering | Reading text to return exact answers |

Slide 31 (real-world products): voice assistants (Alexa, Google Assistant, Siri); customer chatbots (automated support); spam filtering (email classification and security); predictive typing (auto-correct and suggestions); translation tools (cross-language communication); sentiment tracking (social media monitoring); document search (search and recommendation systems).

## 8. Tools [slide 33]

| Library | Slide description |
|---|---|
| **NLTK** | Natural Language Toolkit: the classic Python library for teaching and research; rich in classic algorithms and corpora |
| **spaCy** | Industrial-strength NLP: fast, production-ready pipelines for tokenization, tagging, parsing and NER |
| **PyThaiNLP** | Thai Natural Language Processing: open-source toolkit purpose-built for Thai tasks |

## 9. Project relevance and practical notes

- The mini project is a **text summarization / NLG application** [slide 30 task: summarization]. Where each part sits in the chapter's taxonomy [general]:

| Project stage | NLP task | Upstream or downstream | Level of language |
|---|---|---|---|
| Stage 0: Thai word segmentation, normalization | tokenization (maybe POS) | **upstream** | lexical / morphology |
| Stage 1: classify sentences (Naive Bayes / SVM / kNN) | text classification | **downstream** | semantics (what the sentence is about) |
| Stage 2: TF-IDF + cosine to pick sentences | extractive summarization | downstream | cross-sentence importance (discourse level, loosely) |
| Stage 2: fill templates | NLG (template-based) | downstream | produces text for the reader |

- NLU / KAI / NLG for the project [general]: **NLU** = read the weather report and label its sentences; **KAI** = little or none (at most simple rules such as which label triggers which template slot); **NLG** = template-filled output sentences. Extractive selection copies sentences, so only the template step generates new text.
- The five challenges mostly hit this project lightly because TMD (Thai Meteorological Department) reports are formal, standardized text [general]: abstractness, evolutiveness and subjectivity (slang, sarcasm) are rare. The two that do matter are **segmentation** (the chapter's Thai challenge) and **combinability** (compound terms and place names that a dictionary may split wrongly or fail to know).
- [general] Sentence segmentation is a real Stage 1/2 issue: Thai has no full stop, and a space often separates clauses or sentences in reports, so sentence boundaries must be decided by rules (spaces, line breaks, keywords) before sentence classification and summarization.
- [general] Tool choice: use **PyThaiNLP** for Thai (`word_tokenize`, sentence tokenization, POS tagging). NLTK is useful for teaching-style classic algorithms; spaCy's Thai support is, from memory, only a tokenizer that relies on PyThaiNLP, so verify before depending on it.
- For exam purposes, be ready to: define NLP and its 3 source fields; list the 6 levels of language in order (phonetics, phonology, morphology, syntax, semantics, pragmatics) and the 5 NLP steps; contrast upstream and downstream with examples; expand NLU, KAI, NLG; name the 5 challenges with a Thai example each; name the three libraries.
