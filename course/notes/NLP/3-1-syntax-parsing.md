# NLP 3-1 — Syntax and Parsing

Source: `course/slides/3-1_Syntax_and_Parsing.pdf` (53 slides, Satida Sookpong; course code on slide 1 is 1323326 NLP). Thai wording from the PDF text layer (some tone marks and table column orders are scrambled there, so I paraphrase in English and re-read tables from slide images). Trees, tables, formulas and figures were read from slide images; every numeric example was re-computed in Python.
Legend: **[slide N]** = PDF page · **[general]** = general knowledge or my inference, not said on the slides · **[computed]** = my own calculation.
Slides 2, 8, 12, 15, 29, 33 are section dividers (Syntax Tree / Constituency Trees / Dependency Trees / Algorithm-Constituency / Algorithm-Dependency / Parsing).

**Project relevance: LOW.** The Stage 0-2 pipeline (segmentation, sentence classification, TF-IDF extractive summary + templates) does not need a parser. Useful as background and for exam material; a few ideas transfer (Viterbi-style DP, relative-frequency estimation, precision/recall/F1). See section 14. [general]

---

## 1. Why syntax matters [slides 3-6]

- A **syntax tree (parse tree)** is a tree-shaped picture of a sentence's grammatical structure: it breaks the sentence into words and phrases and maps the hierarchical relations between them according to a set of grammar rules. [slide 3]
- Motivating sentence: "I shot an elephant in my pajamas". [slides 4-5]
  - Slide 4 gives a shallow labelling (B-/I- tags look like IOB chunk tags [general]):

    | Token | I | shot | an | elephant | in | my | pajamas |
    |---|---|---|---|---|---|---|---|
    | Label | B-NP | B-VP | B-NP | I-NP | B-PP | B-NP | I-NP |
    | POS | PRON | VERB | DET | NOUN | ADP | PRON | NOUN |

  - Slide 5 (textbook Fig. 18.9) shows **two parse trees** for it: left tree = the PP "in my pajamas" attaches inside the object NP (the elephant is wearing the pajamas, the "humorous" reading); right tree = the PP attaches to the VP (the shooter was in his pajamas).
- Uses of syntax [slide 6]: **disambiguation** ("I saw the man with the telescope": who holds the telescope?); **question answering** must know which part of the sentence a question asks about; **machine translation** (languages order words differently, so structure must be known); **grammar checkers** such as Grammarly (e.g. subject-verb agreement errors).

## 2. Two kinds of syntax tree [slides 7-14]

| | Constituency tree | Dependency tree |
|---|---|---|
| Idea | nested phrases built from words up to a full sentence | directed word-to-word grammatical relations |
| Structure | nested phrases (NP, VP, ...) | direct word-to-word links |
| Root | sentence S | the main verb |
| Nodes | words + phrase nodes | exactly one node per word |
| Captures | phrase-level grouping (noun phrase, verb phrase) | grammatical function (subject, object, ...) |
| Common tools | Stanford PCFG parser | spaCy, Universal Dependencies |

(Slide 14 table; the text layer shifts the columns, the image shows the row pairing above. The same comparison is repeated in Thai on slide 32, see section 8.)

### 2.1 Constituents [slide 9]
A **constituent** = a group of words that behaves as a single unit. Tests (slide examples in quotes):
- **Substitution:** can be replaced by one word, "เด็กผู้ชายคนนั้น" → "เขา" (that boy → he).
- **Movement:** the whole group can move to another position.
- **Coordination:** can be joined with "and/or" to a group of the same type.
- **Answer:** can stand alone as the answer to a question, "ฉันเห็นใคร" (whom do I see?) → "ช้างใส่ชุดนอน" (an elephant in pajamas).

| Label | Phrase | Slide examples |
|---|---|---|
| NP | noun phrase | แมวดำ, "A cat with long tail" |
| VP | verb phrase | วิ่งเร็ว, "show me the cat" |
| PP | prepositional phrase | ด้วยกล้อง, ที่โรงเรียน |
| ADJP | adjective phrase | สวยมาก |

### 2.2 Syntactic patterns [slide 10]
POS in English follow ordered patterns within sentences and clauses; the rules help language convey coherent meaning. The slide shows a textbook excerpt of **seven common syntactic patterns** (no source line visible on the slide):

| # | Pattern | Example |
|---|---|---|
| 1 | Subject → Verb | The cat meowed. |
| 2 | Subject → Verb → Direct Object | The cat plays the ball. |
| 3 | Subject → Verb → Subject Complement (linking verbs: be, is, like, seem) | The cat is playful. |
| 4 | Subject → Verb → Adverbial Complement | The cat paced slowly. |
| 5 | Subject → Verb → Indirect Object → Direct Object | The cat gave me the ball. (also "The cat gave the ball to me.") |
| 6 | Subject → Verb → Direct Object → Direct Complement (as printed) | The cat made the ball dirty. |
| 7 | Subject → Verb → Direct Object → Adverbial Complement | The cat perked its ears up. |

### 2.3 Constituency tree example [slide 11, textbook Fig. 19.1]
"I prefer the morning flight through Denver." Terminals sit under POS nodes; S is the root; NP is grouped around a noun ("The smart professor"); VP is an action and its object ("taught data science"). Tree as read from the image (bracket form, [general] rendering of the figure):

```
(S (NP (Pro I))
   (VP (Verb prefer)
       (NP (Det the)
           (Nom (Nom (Nom (Noun morning)) (Noun flight))
                (PP (P through) (NP (Pro Denver)))))))
```

### 2.4 Dependency tree example [slides 12-13]
Same sentence. The figure is unlabeled; arcs read from the image: prefer → I, prefer → flight, flight → the, flight → morning, flight → Denver, Denver → through.
- **Root:** usually the main verb. **Edges:** connect a governor ("head") to its dependent, labelled with the relation (e.g. nsubj, dobj).
- Why NLP prefers it (slide): tools like spaCy use dependency trees; computationally efficient and strong on flexible word order.

## 3. Context-free grammar (CFG) [slides 16-19]

A CFG (= phrase-structure grammar) is the standard formalism for constituency; a set of **rewrite rules** saying how a symbol may be replaced. Each rule expands one non-terminal into a sequence of symbols, independent of surrounding context.

| Symbol | Name | Meaning |
|---|---|---|
| N | Non-terminals | symbols that can still be rewritten (S, NP, VP, PP: names of constituents) |
| Σ | Terminals | actual words (แมว, กิน, ปลา); cannot be rewritten |
| R | Rules / productions | `A → β`, A a non-terminal, β a sequence of symbols |
| S | Start symbol | normally S (Sentence) |

"Context-free" because `A → β` can be applied whenever A appears, regardless of what surrounds A. [slide 17]

Slide 16 example grammar, for "The smart professor taught data science.":
```
S  → NP VP          NP → DT JJ NN | NN NN        VP → VB NP
DT → "the"   JJ → "smart"   NN → "professor" | "data" | "science"   VB → "taught"
```
(NP → DT JJ NN covers "the smart professor"; NP → NN NN covers "data science".) [mapping computed]

**English vs Thai grammar** [slide 18]: Thai puts the adjective **after** the noun ("แมวดำ" vs "black cat"), so the rule shapes differ.

| English | Thai |
|---|---|
| S → NP VP | S → NP VP |
| NP → Det Nom ; NP → ProperNoun | NP → N ADJ (ADJ follows N!) ; NP → N |
| Nom → Adj Nom (Adj before N) ; Nom → Noun | VP → V NP ; VP → VP PP ; PP → P NP |
| VP → Verb NP ; VP → VP PP ; PP → Prep NP | N → แมว \| ปลา ; ADJ → ดำ ; V → กิน |
| Det → the \| a ; Noun → cat \| fish ; Adj → black ; Verb → eats | |

Observation [computed]: the Thai grammar has `PP → P NP` but no lexical rule for P, so it can never actually derive a PP.

**Derivation vs parse tree** [slide 19]: a derivation is the sequence of rewrites; the parse tree is the resulting hierarchical structure. Several derivations can give the same parse tree. Slide derivation of "แมว ดำ กิน ปลา" (leftmost, expanding the leftmost non-terminal each time):
```
S => NP VP => N ADJ VP => แมว ADJ VP => แมว ดำ VP => แมว ดำ V NP => แมว ดำ กิน NP => แมว ดำ กิน ปลา
      (S→NP VP)  (NP→N ADJ)                               (VP→V NP)
Tree: S[ NP[ N(แมว) ADJ(ดำ) ]  VP[ V(กิน) NP(ปลา) ] ]
```
Note [computed]: with the slide-18 grammar the last step hides two rewrites (NP → N, N → ปลา), and the drawn tree puts ปลา directly under NP. That is only licensed after the unit production is removed (section 5, where NP → ปลา exists).

## 4. Structural ambiguity [slides 5, 20]

One sentence, several trees. "I saw the man with the telescope." (who holds the telescope, me or the man?) Slide trees:
```
Method 1 (PP + VP):                      Method 2 (PP + NP):
S                                        S
 +- NP I                                 +- NP I
 +- VP                                   +- VP
     +- VP                                   +- V saw
     |   +- V saw                            +- NP
     |   +- NP the man                           +- NP the man
     +- PP with telescope                        +- PP with telescope
```
Method 1: the PP modifies the VP (I used the telescope to see); Method 2: the PP modifies the NP "the man" (the man has the telescope). [reading-to-tree mapping: general] A grammar alone cannot choose; this motivates probabilities (section 6).

## 5. Chomsky Normal Form (CNF) [slides 21-22]

A CNF grammar allows only two rule shapes:
1. `A → B C` (exactly two non-terminals on the right)
2. `A → w` (a single terminal)

Every CFG can be converted to a CNF grammar accepting the same language, with no loss of expressiveness (slide wording; strictly this ignores the empty string [general]). CYK needs CNF. Three conversion tricks:

| # | Problem rule | Fix (slide example) |
|---|---|---|
| 1 | mixes terminal and non-terminal: `INF-VP → to VP` | new non-terminal over the word: `INF-VP → TO VP` and `TO → to` |
| 2 | **unit production** (one non-terminal on RHS): `NP → N → แมว` | replace by what N rewrites to: `NP → แมว \| ปลา` |
| 3 | RHS longer than 2: `VP → V NP PP` | split with a dummy symbol: `VP → X1 PP` and `X1 → V NP` |

Slide 22 shows textbook Fig. 18.10, grammar L1 and its CNF (lexical entries carry over unchanged):

| L1 rule | CNF result |
|---|---|
| S → NP VP | S → NP VP |
| S → Aux NP VP | S → X1 VP ; X1 → Aux NP |
| S → VP | S → book \| include \| prefer ; S → Verb NP ; S → X2 PP ; S → Verb PP ; S → VP PP |
| NP → Pronoun ; NP → Proper-Noun | NP → I \| she \| me ; NP → United \| Houston |
| NP → Det Nominal | NP → Det Nominal |
| Nominal → Noun | Nominal → book \| flight \| meal \| money |
| Nominal → Nominal Noun ; Nominal → Nominal PP | unchanged |
| VP → Verb | VP → book \| include \| prefer |
| VP → Verb NP ; VP → Verb PP ; VP → VP PP | unchanged |
| VP → Verb NP PP | VP → X2 PP ; X2 → Verb NP |
| PP → Preposition NP | PP → Preposition NP |

(`S → VP` is a unit production removed by copying every VP expansion up into S; X2 is the same dummy as in trick 3. Trick mapping: [general].)

## 6. Probabilistic CFG (PCFG) [slides 23-28]

**Idea** [slide 23]: PCFG = CFG + probabilities. It gives the same parses as the CFG but assigns each parse a probability; with several parses choose the most probable. PCFG extends CFG the way a Markov model extends a regular grammar.

- Rule format: `A → β [p]` (4.5), read as $P(A\to\beta\mid A)$ (4.6).
- **Constraint:** for each non-terminal A, the probabilities of all rules with LHS = A sum to 1.

$$P(T)=\prod_{n\in T}p\big(r(n)\big)\qquad(4.7)\quad\text{(multiply the probability of every rule used in the tree)}$$

$$\hat T(S)=\underset{T\in\tau(S)}{\arg\max}\;P(T)\qquad(4.8)\quad\tau(S)=\text{set of all possible parses of sentence }S$$

**Sample PCFG** [slide 24, textbook Fig. 4.13, food-ordering chatbot at a campus]. All LHS groups sum to 1.00 [computed, checked]:

| Rule | p | Rule | p |
|---|---|---|---|
| S → NP VP | 0.82 | Det → a / that / the / this | .12 / .03 / .75 / .10 |
| S → Aux NP VP | 0.12 | N → coffee / tea / food | 0.75 / 0.13 / 0.12 |
| S → VP | 0.06 | V → buy / pay / order | 0.41 / 0.27 / 0.32 |
| NP → Det Nom | 0.21 | Aux → do / does / can | 0.31 / 0.26 / 0.43 |
| NP → Proper-N | 0.37 | Proper-N → Starbucks / KFC | 0.63 / 0.37 |
| NP → Nom | 0.06 | Pronoun → I / you / he / she | .42 / .36 / .12 / .10 |
| NP → Pronoun | 0.36 | | |
| Nom → Noun | 0.72 | | |
| Nom → N Nom | 0.23 | | |
| Nom → Proper-N Nom | 0.05 | | |
| VP → V | 0.58 | | |
| VP → V NP | 0.36 | | |
| VP → V NP NP | 0.06 | | |

Naming inconsistency on the slide: `Nom → Noun` but the lexical rules are `N → ...`; I treat Noun = N. [computed]
Example use [computed], "I order the coffee" (one parse; treating Noun = N):
$P=0.82\times(0.36\times0.42)\times(0.36\times0.32)\times(0.21\times0.75\times0.72\times0.75)$, i.e. S→NP VP, NP→Pronoun, Pronoun→I, VP→V NP, V→order, NP→Det Nom, Det→the, Nom→Noun, N→coffee. $=0.82\times0.1512\times0.1152\times0.08505\approx 1.215\times10^{-3}$ (the slide gives no such example).

**Three PCFG assumptions** [slide 25]:
1. **Place invariance:** a rule's probability does not depend on where the subtree appears in the sentence (NP → N ADJ is the same at the start or end).
2. **Context-free (ancestor-free):** the probability of expanding a non-terminal depends only on that non-terminal, not on its parent or neighbouring nodes.
3. **Independence of rule choices:** the rule chosen at one node is independent of rules at other nodes, which is why probabilities can be multiplied.

### 6.1 Worked example: "I shot an elephant in my pajamas" [slides 26-27]

PCFG (slide 26; each LHS group sums to 1.0 [computed, checked]):
```
S  -> NP VP   [1.0]
VP -> V NP    [0.6]   VP -> VP PP   [0.4]
NP -> N       [0.5]   NP -> N ADJ   [0.3]   NP -> NP PP  [0.2]
PP -> P NP    [1.0]
```
Rules used (slide 27; lexical rules not scored, "an"/"my" absorbed into N, so only 7 rules per tree):

| Step | Parse A: PP attaches to NP (ช้างใส่ชุดนอน, "elephant in pajamas") | p | Parse B: PP attaches to VP (ฉันใส่ชุดนอน, "I in pajamas") | p |
|---|---|---|---|---|
| 1 | S → NP VP | 1.0 | S → NP VP | 1.0 |
| 2 | NP → N (I) | 0.5 | NP → N (I) | 0.5 |
| 3 | VP → V NP | 0.6 | VP → VP PP | **0.4** |
| 4 | NP → NP PP | **0.2** | VP → V NP | 0.6 |
| 5 | NP → N (Elephant) | 0.5 | NP → N (Elephant) | 0.5 |
| 6 | PP → P NP | 1.0 | PP → P NP | 1.0 |
| 7 | NP → N (Pajamas) | 0.5 | NP → N (Pajamas) | 0.5 |
| | **Product** | **0.015** | **Product** | **0.030** |

- Recomputed [computed]: A = 1.0·0.5·0.6·0.2·0.5·1.0·0.5 = **0.015**; B = 1.0·0.5·0.4·0.6·0.5·1.0·0.5 = **0.030**. The slide values are numerically right. The only difference between the trees is VP → VP PP (0.4) versus NP → NP PP (0.2), so B wins by a factor of 2: the PCFG picks the **VP attachment** (green box, 0.03).
- **Label discrepancy on slide 27:** the result boxes read "P(T_B) = 0.01500" under the Parse A card and "P(T_A) = 0.03000" under the Parse B card, i.e. the subscripts A/B are swapped relative to the card titles. The numbers match the cards; only the T_A/T_B names are crossed.
- [computed] Sentence probability = sum over all parses $=0.015+0.030=0.045$ (the PCFG also gives a probability to the string itself; the slide only compares trees).

### 6.2 Limitation and fix: lexicalized PCFG [slide 28]
Plain PCFG problems:
- Ignores actual words ("lexical independence"): "ดื่ม" (drink) and "ซื้อ" (buy) use the same VP rule probabilities although they behave differently.
- Ignores structural position: a subject NP and an object NP share the same probabilities.
- Hence PCFG often picks the wrong parse for **PP-attachment** and **coordination**, which depend on word meaning.

Fix: attach the **lexical head** to every non-terminal (N is head of NP, V of VP): rules become `VP(กิน) → V(กิน) NP(ปลา)` instead of `VP → V NP`, so the model learns that "กิน" is often followed by food and "ไป" by places. This is the idea of the Collins and Charniak parsers (1997-1999). Today: **neural span-based constituency parsers** score each span with a neural network.

## 7. Treebanks [slide 34]

A **treebank** = text corpus in which humans annotated the syntax of every sentence (annotated by hand, or parsed first and then hand-corrected). Uses: train models, gold standard for evaluation, corpus linguistics.

| Treebank | Type | Slide description |
|---|---|---|
| Penn Treebank | constituency | English (Wall Street Journal); most influential, standard benchmark for decades |
| Universal Dependencies (UD) | dependency | open data, almost 200 treebanks in 100+ languages, one relation set across languages |
| ORCHID / Thai UD | both | ORCHID (NECTEC) Thai corpus with POS tags; a Thai treebank also exists in the UD project |

**Grammar from a treebank:** instead of writing rules by hand, read the rules off the treebank and count them to get PCFG probabilities (relative-frequency / maximum-likelihood estimate):

$$P(A\to\beta)=\frac{\text{Count}(A\to\beta)}{\text{Count}(A)}$$

## 8. Dependency structure [slides 30-32]

Link **word to word** with an arrow from **head** to **dependent**, labelled with the grammatical relation. [slide 30]
- **Universal Dependencies (UD):** 37 standard relations, usable in 100+ languages. Relations shown on the slide (textbook Fig. 19.2):

  | Group | Relation: description |
  |---|---|
  | Clausal argument | NSUBJ nominal subject · OBJ direct object · IOBJ indirect object · CCOMP clausal complement |
  | Nominal modifier | NMOD nominal modifier · AMOD adjectival modifier · APPOS appositional modifier · DET determiner · CASE prepositions, postpositions and other case markers |
  | Other | CONJ conjunct · CC coordinating conjunction |

- Key properties: the main verb (e.g. "กิน") is the **root**; every word has **exactly one head** except the root; **number of arcs = number of words** (counting the ROOT → main-verb arc, as the slide's trace does, [computed]).
- Why suited to Thai (slide claim): Thai has flexible word order and no inflection, so dependency says "who did what to whom" more directly, without relying on phrase position. [general caveat: Thai basic order is fairly SVO, so "flexible" is arguable; the slide's point is that dependency does not need fixed phrase positions.]

**Formal definition** [slide 31]: a directed graph $G=(V,A)$, V = set of words (nodes), A = set of ordered pairs (directed, labelled edges). Three conditions:
1. exactly one **root** with no incoming edge;
2. every other node has exactly **one incoming edge** (one head);
3. there is a **unique path** from the root to every node (connected, no cycles).

**Projectivity:** a tree is projective if all edges can be drawn **without crossing**. Arc-standard transition parsers can build **only projective** trees; flexible-word-order languages often have non-projective structures. Slide figures:
- (19.2) "United canceled the morning flights to Houston": root → canceled; nsubj United; obj flights; flights → det the, compound morning, nmod Houston; Houston → case to. No crossings (projective, [general]).
- (19.3) "JetBlue canceled our flight this morning which was already late": the arc flight → late (acl:relcl) crosses the arc canceled → morning (obl), so it is **non-projective** [inferred from the figure; the slide gives no explanation]. Other arcs: nsubj JetBlue, obj flight, det our, det this, nsubj which, cop was, adv already.

**Constituency vs dependency, Thai table** [slide 32]:

| Aspect | Constituency (phrase structure) | Dependency |
|---|---|---|
| Basic unit | nested phrases in a hierarchy | words linked directly |
| Tree nodes | internal nodes that are not words (NP, VP, PP) | every node is a word |
| Shows well | phrase boundaries, nesting | grammatical relations (who does what) |
| Suited to | fixed word order, e.g. English | flexible order, e.g. Thai, Czech, Turkish |
| Main algorithm | CYK / chart parsing, O(n³) | transition-based, O(n) |
| Treebank | Penn Treebank | Universal Dependencies |

The two convert into each other: use **head-finding rules** to find the lexical head of each constituent, then turn a constituency tree into a dependency tree.

## 9. Parsing as search [slides 35-36]

Goal: find a tree that (1) has S as root and (2) has leaves exactly equal to the input sentence.

| | Top-down (goal-directed) | Bottom-up (data-directed) |
|---|---|---|
| Start | from S, expand rules down until the words match the input | from the input words, build larger phrases up to S |
| Pro | never builds trees that cannot reach S | always grounded in the real words, never builds trees inconsistent with the input |
| Con | may waste time on trees that contradict the input words from the start; **loops forever on left-recursive rules** such as `NP → NP PP` | may build sub-phrases that can never combine into S (wasted work) |

Slide figures: Fig. 4.9 shows a three-level top-down expansion from S (S → NP VP / Aux NP VP / VP, then NP → Det Nom or ProperN, VP → V NP or V); Fig. 4.11 shows bottom-up building for "Play the piano". **CYK uses the bottom-up approach and removes repeated work with dynamic programming.**

## 10. CYK algorithm [slides 37-43]

**Overview** [slide 37]: Cocke-Kasami-Younger; the most widely used dynamic-programming parser.
- Same principle as **Viterbi** and **minimum edit distance**: store answers to subproblems and reuse them.
- Context-freeness helps: once a span is known to be a constituent of some type, that fact is stored and reused, never re-analysed.
- Needs the grammar in **CNF**. Stores all possible parses compactly in one table.
- **Table:** upper-triangular matrix; cell [i, j] = **set of non-terminals** that can generate words i..j. The diagonal [i, i] = the category of each word (from the POS tagging lecture). Top-right cell [1, n] covers the whole sentence; **if S is in [1, n] the sentence is grammatical.**

**Four steps** [slide 38]: (1) convert the CFG to CNF (`A → B C`, `A → word`); (2) build the n × n triangular table; (3) for each cell try every split point and combine non-terminals from the two smaller sub-spans; (4) the sentence is grammatical iff S is in the top cell spanning the whole sentence.

**Cell-filling rule** [slide 39], span i..j can be split at every k with i ≤ k < j:
```
if  B ∈ table[i, k]  and  C ∈ table[k+1, j]  and the grammar has A -> B C
then add A to table[i, j]
```
Order: short spans to long spans (bottom-up); or column by column left to right, each column bottom to top, which guarantees the needed cells (left and below) are already filled. Three nested loops (j, i, k) give O(n³), times grammar size |G|.

Textbook pseudocode on the slide (Fig. 18.12). It uses **0-based fencepost indices** (word j sits in table[j-1, j]), unlike the slide's 1-based inclusive prose rule above:
```
function CKY-PARSE(words, grammar) returns table
  for j <- 1 to LENGTH(words):
    for all {A | A -> words[j] in grammar}:  table[j-1, j] <- table[j-1, j] ∪ A
    for i <- j-2 down to 0:
      for k <- i+1 to j-1:
        for all {A | A -> B C in grammar and B in table[i,k] and C in table[k,j]}:
          table[i,j] <- table[i,j] ∪ A
```

### 10.1 Worked example [slides 40-42]: "แมว ดำ กิน ปลา" (the black cat eats fish)

CNF grammar (slide 40):
```
S -> NP VP     NP -> N ADJ     VP -> V NP
NP -> แมว | ปลา     N -> แมว | ปลา     ADJ -> ดำ     V -> กิน
```
"แมว" and "ปลา" are both N and NP (a consequence of removing the unit production NP → N).

Final table (slide 41; rows i, columns j):

| | j=1 แมว | j=2 ดำ | j=3 กิน | j=4 ปลา |
|---|---|---|---|---|
| i=1 | {N, NP} | {NP} | – | **{S}** |
| i=2 | | {ADJ} | – | – |
| i=3 | | | {V} | {VP} |
| i=4 | | | | {N, NP} |

Fill sequence (slide 41, with the full split check for the empty cells added by me [computed]):

| Cell | Words | Split k | Left × right | Rule | Result |
|---|---|---|---|---|---|
| [1,2] | แมว ดำ | 1 | N ∈ [1,1] × ADJ ∈ [2,2] | NP → N ADJ | NP |
| [2,3] | ดำ กิน | 2 | ADJ × V | none | empty |
| [3,4] | กิน ปลา | 3 | V ∈ [3,3] × NP ∈ [4,4] | VP → V NP | VP |
| [1,3] | แมว ดำ กิน | 1, 2 | k=1: {N,NP} × [2,3]=∅; k=2: NP × V | none (no NP V rule) | empty |
| [2,4] | ดำ กิน ปลา | 2, 3 | k=2: ADJ × VP; k=3: [2,3]=∅ × {N,NP} | none | empty |
| [1,4] | whole | 2 | NP ∈ [1,2] × VP ∈ [3,4] | S → NP VP | **S** |

(For [1,4] the other splits k=1 and k=3 involve an empty cell, so S arrives only via k=2.) S in [1,4], so the sentence is grammatical. My Python CKY reproduces every cell. [computed]

**Recognizer to parser** [slide 42]: the basic algorithm is only a **recognizer** (yes/no grammatical). Two changes make it a parser: store **backpointers** to the cells used to build each entry, and allow the same non-terminal several times in one cell. Backpointers for this example:
```
S  @[1,4] <- NP[1,2] + VP[3,4]
NP @[1,2] <- N[1,1]  + ADJ[2,2]
VP @[3,4] <- V[3,3]  + NP[4,4]
```
Tree: S[ NP[N แมว, ADJ ดำ], VP[V กิน, NP ปลา] ], i.e. [NP แมว ดำ] is the subject and [VP กิน [NP ปลา]] the predicate.

### 10.2 Complexity [slide 43]
- Cells: n(n+1)/2 ≈ O(n²); each cell tries up to n split points, O(n); total **O(n³ · |G|)** (n = words, |G| = number of grammar rules).

| n | cells n(n+1)/2 | n³ split attempts (slide) |
|---|---|---|
| 4 (our example) | 10 | 64 |
| 10 | 55 | 1,000 |
| 20 | 210 | 8,000 |

(All six values re-computed: correct. [computed]) Note: n³ is a scale, not an exact count; the exact number of (i, k, j) split triples is (n+1)n(n−1)/6 = 10, 165, 1,330 for n = 4, 10, 20. [computed]
Slide comparison: Viterbi is O(N·T²), linear in sentence length; CYK is far more expensive because it considers every span, not just every position.

## 11. Probabilistic CYK [slide 44]

Plain CYK keeps every parse but does not choose the best; a real sentence may have dozens. Fix: each cell stores the **maximum probability** of each non-terminal instead of just present/absent.

$$\text{table}[i,j,A]=\max_{i\le k<j}\;P(A\to B\,C)\times\text{table}[i,k,B]\times\text{table}[k+1,j,C]$$

Keep the backpointer $(k,B,C)$ that attains the max. (The slide prints only k under the max; the max also ranges over rules `A → B C`. Base case $\text{table}[i,i,A]=P(A\to w_i)$ is not on the slide. [general])

Relation to Viterbi (slide): $v_t(j)=\max_i[v_{t-1}(i)\,a(i,j)]\,b_j(o_t)$ chooses the best path in a **sequence**; probabilistic CYK chooses the best way to assemble a **tree**. Same max + backpointer, different subproblem shape.

Worked check [computed, not on the slides]: probabilistic CYK on the slide-26 PCFG for "I shot an elephant in my pajamas", tokens simplified as N V N P N, lexical p = 1, unit rule NP → N folded into the word cells (NP[i,i] = 0.5):

| Cell | Entry |
|---|---|
| [2,3] shot elephant | VP = 0.6 × 1 × 0.5 = 0.30 |
| [4,5] in pajamas | PP = 1.0 × 1 × 0.5 = 0.50 |
| [3,5] elephant in pajamas | NP = 0.2 × 0.5 × 0.5 = 0.05 |
| [2,5] shot elephant in pajamas | VP via V NP = 0.6 × 0.05 = 0.03; VP via VP PP = 0.4 × 0.30 × 0.50 = **0.06** (kept) |
| [1,5] whole | S = 1.0 × 0.5 × 0.06 = **0.03** |

Result = 0.03, the same as Parse B on slide 27; the NP-attachment tree (0.015) is discarded at cell [2,5]. This matches argmax P(T).

## 12. Transition-based dependency parsing [slides 45-49]

**Configuration** (parser state) [slide 45]: **Stack** (words under consideration, starts `[ROOT]`), **Buffer** (unread words, starts with the whole sentence), **Relations** (set of dependency edges built so far). Start from the initial configuration and keep choosing a transition until the final state: stack = [ROOT] only, buffer empty; the relation set is then the dependency tree. Generic loop (textbook Fig. 19.5):
```
state <- {[root], [words], []}
while state not final:  t <- ORACLE(state);  state <- APPLY(t, state)
return state
```

**Three arc-standard operators** [slide 45] (S1 = top of stack, S2 = the one below it):

| Operator | Effect |
|---|---|
| SHIFT | move the first buffer word onto the stack |
| LEFTARC(r) | add edge S1 → S2 (top is head), then remove S2 (the lower word is the dependent) |
| RIGHTARC(r) | add edge S2 → S1 (lower is head), then remove S1 (the top word is the dependent) |

Conditions: LEFTARC cannot be applied to ROOT (ROOT cannot be a dependent); both arcs need ≥ 2 items on the stack.

**Trace** [slide 46], "เด็ก กิน ข้าว" (child eats rice). Verified by simulating the parser (output matches the slide) [computed]:

| Step | Stack | Buffer | Action | Relation added |
|---|---|---|---|---|
| 0 | [ROOT] | [เด็ก, กิน, ข้าว] | SHIFT | |
| 1 | [ROOT, เด็ก] | [กิน, ข้าว] | SHIFT | |
| 2 | [ROOT, เด็ก, กิน] | [ข้าว] | LEFTARC(nsubj) | กิน → เด็ก |
| 3 | [ROOT, กิน] | [ข้าว] | SHIFT | |
| 4 | [ROOT, กิน, ข้าว] | [ ] | RIGHTARC(obj) | กิน → ข้าว |
| 5 | [ROOT, กิน] | [ ] | RIGHTARC(root) | ROOT → กิน |
| 6 | [ROOT] | [ ] | Done | |

Result: ROOT -root→ กิน, กิน -nsubj→ เด็ก, กิน -obj→ ข้าว. **6 transitions = 2n for n = 3 words, so O(n) linear.** (Each word is shifted once and removed once. [general])

**Second trace** [slide 47, textbook Fig. 19.6], "book me the morning flight" (10 transitions = 2n for n = 5; also reproduced in simulation [computed]):

| Step | Stack | Word list | Action | Relation added |
|---|---|---|---|---|
| 0 | [root] | [book, me, the, morning, flight] | SHIFT | |
| 1 | [root, book] | [me, the, morning, flight] | SHIFT | |
| 2 | [root, book, me] | [the, morning, flight] | RIGHTARC | (book → me) |
| 3 | [root, book] | [the, morning, flight] | SHIFT | |
| 4 | [root, book, the] | [morning, flight] | SHIFT | |
| 5 | [root, book, the, morning] | [flight] | SHIFT | |
| 6 | [root, book, the, morning, flight] | [] | LEFTARC | (morning ← flight) |
| 7 | [root, book, the, flight] | [] | LEFTARC | (the ← flight) |
| 8 | [root, book, flight] | [] | RIGHTARC | (book → flight) |
| 9 | [root, book] | [] | RIGHTARC | (root → book) |
| 10 | [root] | [] | Done | |

### 12.1 Oracle and training [slide 48]
- The **oracle** decides which transition to use in each configuration; it is learned by supervised learning. But a treebank gives (sentence, tree) pairs, not (configuration, transition) pairs. Fix: **simulate the parser on the gold tree** to produce (configuration, transition) training pairs.
- **Training oracle rules:**
  - LEFTARC(r) if (S1 r S2) is in the gold tree;
  - RIGHTARC(r) if (S2 r S1) is in the gold tree **and all dependents of S1 are already attached**;
  - SHIFT otherwise.
- Why RIGHTARC needs the extra condition: it **removes** the top word from the stack; if that word still has dependents waiting in the buffer, they could never be attached. The condition forces waiting until every dependent is attached.
- **Traditional feature-based classifier:** extract features from the configuration, e.g. words and POS of s1, s2 (stack) and b1 (front of buffer); conjunctive example `s1.t ∘ s2.t = "NNS ∘ VBD"`; any classifier works, e.g. logistic regression or SVM.
- [computed] I coded this oracle rule set and it reproduces both traces above.

### 12.2 Neural transition-based parsing [slide 49]
Pass the whole sentence through an **encoder** (BiLSTM or Transformer) to get a vector per word; take the vectors of the top two stack words (s1, s2) and the first buffer word (b1); **concatenate** → **feedforward network** → **softmax** over SHIFT / LEFTARC / RIGHTARC (with label). Train with **cross-entropy** against the oracle's correct transitions. Advantages: no hand-made features, and the encoder sees the whole sentence. Basis of many modern parsers (Kiperwasser & Goldberg, 2016).

## 13. Chart vs transition parsing, and real parsers [slides 50-51]

| Aspect | Chart parsing (CYK) | Transition-based |
|---|---|---|
| Output | constituency tree (nested phrases) | dependency tree (edges between words) |
| Search | dynamic programming, explores all possibilities | greedy, one step at a time, no backtracking |
| Complexity | O(n³ · \|G\|) | O(n) linear |
| Optimality | guarantees the best parse (exact) | not guaranteed; one wrong step can propagate |
| Limitation | grammar must first be converted to CNF | arc-standard builds only projective trees |
| Suited to | complete, accurate phrase structure | high speed on large amounts of text |

**Middle path:** **graph-based dependency parsing** finds a **maximum spanning tree** over scores of all word pairs: exact optimum and handles non-projective trees, but slower than transition-based.

Real-world parsers [slide 51, descriptions paraphrased]:

| Tool | Type | Description |
|---|---|---|
| spaCy | dependency | most-used industrial Python library; fast transition-based neural parser; multilingual |
| Stanza (Stanford NLP) | dependency | full neural pipeline (tokenize → POS → parse), 70+ languages, UD standard |
| Berkeley Neural Parser | constituency | span-based neural parser: scores each span, then a modified CYK finds the best tree |
| UDPipe | dependency | trains and runs UD parsers for any language that has a treebank |
| PyThaiNLP | Thai | Thai NLP toolkit covering word segmentation, POS tagging and dependency parsing |

(The text layer mis-aligns this table's type column; the pairing above is from the image.) Trend: nearly all commercial parsers are neural and some work now uses LLMs to parse directly, but CYK and transition-based ideas are still the foundation.

## 14. Parsing evaluation [slides 52-53]

### 14.1 PARSEVAL (constituency) [slide 52]
Exact match of the whole tree is too strict to tell systems apart, so count correct **constituents**, each identified by (label, start, end). Also report **cross-brackets**: how often gold groups ((A B) C) but the system gives (A (B C)).

$$\text{Labeled Precision}=\frac{\text{correct}}{\text{system answered}}\quad\text{Labeled Recall}=\frac{\text{correct}}{\text{in gold}}\quad F_1=\frac{2PR}{P+R}$$

Slide example, "แมว ดำ กิน ปลา" (token positions 1-4):

| Constituent | Gold | System | Result |
|---|---|---|---|
| S (1-4) | yes | yes | correct |
| NP (1-2) | yes | yes | correct |
| VP (3-4) | yes | yes | correct |
| NP (4-4) | yes | no | missed |
| NP (3-4) | no | yes | extra |

System gave 4, 3 correct; gold has 4, 3 found: P = 3/4 = 0.75, R = 3/4 = 0.75, F1 = 0.75 (re-computed, correct [computed]). Toy-example oddity [general]: the system tree has both an NP and a VP over span 3-4, which needs a unary chain.

### 14.2 UAS / LAS (dependency) [slide 53]
**UAS** (unlabeled attachment score): only whether the head is right. **LAS** (labeled attachment score): head **and** label must be right. Slide example "เด็ก เห็น ผู้ชาย ด้วย กล้อง" (5 words), gold vs system:

| Word | Gold head / label | System head / label | Head ok | Label ok |
|---|---|---|---|---|
| เด็ก | เห็น / nsubj | เห็น / nsubj | yes | yes |
| เห็น | ROOT / root | ROOT / root | yes | yes |
| ผู้ชาย | เห็น / obj | เห็น / iobj | yes | no |
| ด้วย | กล้อง / case | กล้อง / case | yes | yes |
| กล้อง | เห็น / obl | ผู้ชาย / nmod | no | no |

$$\text{UAS}=\frac{\#\text{correct heads}}{\#\text{words}}=\frac45=0.80\qquad\text{LAS}=\frac{\#\text{correct head and label}}{\#\text{words}}=\frac35=0.60$$

Both re-computed, correct [computed]. (The one wrong head, กล้อง, is the same PP-attachment ambiguity as "with the telescope" in section 4. [general])

## 15. Slide issues and ambiguities (summary)

1. **Slide 27:** result boxes labelled P(T_B)=0.01500 / P(T_A)=0.03000 sit under the Parse A / Parse B cards respectively. Numbers are right per card (A = 0.015, B = 0.03); only the T_A/T_B subscripts are crossed.
2. **Slide 19:** derivation and tree skip the unit step NP → N → ปลา (grammar of slide 18 has no NP → ปลา).
3. **Slide 18:** Thai grammar has `PP → P NP` but no preposition lexicon.
4. **Slide 24:** `Nom → Noun` vs lexical `N → ...` naming mismatch; rules sum to 1 per LHS (checked).
5. **Slide 43:** "n³ tries" is a rough scale (exact split count is (n+1)n(n−1)/6).
6. **Slides 14, 51:** the text layer mis-orders table columns (re-read from images). **Slide 44:** the max in the probabilistic-CYK formula should also range over rules/B/C. **Slide 39:** prose rule is 1-based inclusive, the textbook pseudocode is 0-based fenceposts.
7. **Slide 10:** pattern 6 is printed "Direct Complement" (usually called object complement [general]).
8. Not covered on the slides: lexical/unary handling in PCFG-CYK, smoothing of PCFG counts, arc-eager or swap transitions, PCFG training with EM, anything Thai-specific beyond the examples and ORCHID/Thai UD mention.

## 16. Project relevance and practical notes

- **Not needed for the mini-project pipeline.** Stage 0 (Thai word segmentation), Stage 1 (Naive Bayes / SVM / kNN sentence classification) and Stage 2 (TF-IDF + cosine extractive summary + templates) all work on bags of words or sentence vectors. [general]
- **Parsing sits downstream of segmentation:** POS tags and parses assume a correct token sequence, so Thai parse quality is bounded by Stage 0 quality (see [1-2](1-2-tokenization.md) and [2-1](2-1-word-segmentation-pos-sequence-labeling.md)). [general]
- **Possible optional uses** [general]: (a) shallow chunking or dependency relations to pull weather phenomena, intensity and place names out of formulaic TMD sentences for the template step; (b) PP-attachment ambiguity is real in weather text (e.g. a phenomenon phrase followed by a "in the northern part of the region" phrase); (c) PyThaiNLP is listed on slide 51 as covering dependency parsing, but a Thai parser needs a trained model (UD treebank) and extra setup, so check availability before relying on it.
- **Transferable ideas:**
  - PCFG rule probability $\text{Count}(A\to\beta)/\text{Count}(A)$ is the same relative-frequency (MLE) estimate as n-gram models ([5-1](5-1-language-models-ngrams.md)) and Naive Bayes; unseen rules would need smoothing as well. [general]
  - Probabilistic CYK is Viterbi over trees (the HMM view is in 2-1).
  - PARSEVAL uses the same precision / recall / F1 as the Stage-1 classifiers (per-class F1 from the ML classification chapters).
- **Exam-style checklist:** CFG = (N, Σ, R, S); CNF shapes `A → B C` / `A → w`; the three CNF conversions; PCFG: probs per LHS sum to 1, tree prob = product of rule probs, choose argmax; CYK fills [i, j] by trying every split k and checking `A → B C`, O(n³·|G|); transition-based arc-standard: SHIFT / LEFTARC / RIGHTARC, 2n steps, projective only, oracle conditions; UAS vs LAS; PARSEVAL P/R/F1.
