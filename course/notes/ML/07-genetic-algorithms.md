# ML 07 — Genetic Algorithms

Source: `course/slides/07 Genetic Algorithms.pptx` (23 slides, lecturer Parinya Sanguansat). Text from the PDF export; all diagrams (word-guess table, crossover/mutation bit strings, flowchart, TSP drawing) read from slide images. There are no formulas on the slides except the polynomial and the sum of squared errors.
Legend: **[slide N]** = taken from the slide · **[computed]** = my own calculation or check of a slide example · **[general]** = general knowledge or my inference, not on the slides.

**Project relevance: LOW-MEDIUM (background).** GA is not part of the planned pipeline. It could be used for hyperparameter or feature-subset search (Section 11). [general]

---

## 1. Key ideas

- A **genetic algorithm (GA)** searches for good solutions by imitating biological evolution: keep a *population* of candidate solutions, score each with a *fitness* function, keep the better ones, and create new candidates by *crossover* and *mutation*. [slides 4, 15]
- Invented by John Holland (1975), made popular by John Koza (1992). [slide 4]
- Variation comes from **mutation** (random changes) and **sexual reproduction** (offspring get characteristics from each parent). "Better adapted" offspring are more likely to survive, so later generations get better. [slide 4]
- Slide 15's summary: start with a large population of randomly generated attempted solutions; repeatedly evaluate, keep the best subset, generate a new population from it; stop when satisfactory or out of time. The slide's claim: in general the best technique is sexual reproduction (crossover) combined with a small probability of mutation.

## 2. Biological vocabulary mapped to GA [slides 5-6]

| Term | Slide definition | GA meaning |
|---|---|---|
| Gene | basic instruction for building an organism; codes a specific feature (e.g. eye colour); set of possible alleles | one element of the encoded solution |
| Chromosome | a sequence of genes that represents a solution | one candidate solution (e.g. a bit string) |
| Genome | full set of chromosomes; the genome of one individual is its **genotype** | (slides assume one chromosome per organism, slide 8) |
| Population | the chromosomes available to test; set of competing individuals | current set of candidates |
| Genotype | the "blueprint" (genes and chromosomes); changed by genetic operators (mutation, recombination); immutable for an individual (no Lamarckian evolution) | the encoded string |
| Phenotype | what the organism actually is like; **selection operates on phenotypes** (survival of the fittest) | the decoded solution and its measured quality |

Slide 6 example: you might have genes to be tall but never grow tall (poor diet). Likewise "genes" describe a *possible* solution without actually being the solution.

## 3. What GA is good for [slide 7]

Noisy environments; searching (the space of hypotheses); optimization (maximization, minimization, genetic programming); parallelized computing. (Keywords only, no detail on slides.)

**Asexual vs. sexual reproduction** [slide 8]
- Asexual: each solution has **one parent**; the only source of variation is mutation.
- Sexual: each solution has **two parents**; assuming one chromosome per organism, offspring get a new chromosome by crossover of parts of each parent's chromosome.

## 4. Encoding (representation) [slide 9]

| Representation | Slide example |
|---|---|
| Bit strings | `0101 ... 1100` |
| Real numbers | `43.2 -33.1 ... 0.0 89.2` |
| Permutations of elements | `E11 E3 E7 ... E1 E15` |
| Lists of rules | `R1 R2 R3 ... R22 R23` |
| Program elements | genetic programming |

**Rule-encoding example** [slide 9]: $(\text{Outlook}=\text{Overcast}\lor\text{Rain})\land(\text{Wind}=\text{Strong})$ is encoded as Outlook `011`, Wind `10`, with "Yes = 1, No = 0, Don't care = all 1".
The attributes (Outlook, Wind) come from the PlayTennis data used in [02](02-concept-learning.md), [03](03-decision-tree.md) and [08](08-bayesian-learning.md). Reading [general, inferred]: one bit per attribute value, in the order (Sunny, Overcast, Rain) and (Strong, Weak). So `011` allows Overcast and Rain but not Sunny; `10` allows Strong only. The whole rule would be the concatenation `011 10` (the slide does not show a target-class bit).

## 5. GA operations [slides 10-13]

Three operations: **selection** (keep the best), **crossover** (mimics recombination; part of the genetic material is swapped between chromosomes, typically producing an offspring), **mutation** (pick a random locus = gene position with some probability and alter the information there; "the intuitive mechanism for the preservation of variety in the population"). [slide 10]

### Selection [slide 11]
- **Keep the top rank:** sort the population by fitness, *keep* the top part, *kill* the rest (diagram labelled Keep / Kill / Fitness / Population).
- **Roulette wheel:** "not only the top rank", i.e. weaker individuals still have a chance. The slide shows only a pie chart with unequal slices, no numbers or formula.
- [general] Fitness-proportionate (roulette) probability: $P(h_i)=\dfrac{f(h_i)}{\sum_j f(h_j)}$ (needs non-negative fitness; for an error to minimise, convert first, e.g. $1/(1+\text{error})$). Illustration, made-up fitnesses (5, 3, 2, 1), total 11: [computed] 0.4545, 0.2727, 0.1818, 0.0909.

### Crossover [slide 12]
Parents used for all three examples: `11101001000` and `00001010101`.

| Type | Idea | Result on slide [verified by recomputation] |
|---|---|---|
| Single-point | cut at one position, swap the tails (blue string `11111000000` marks the cut after bit 5) | `11101010101`, `00001001000` |
| Two-point | cut at two positions, swap the middle segment (blue `00111110000`: bits 3-7 swapped) | `11001011000`, `00101000101` |
| Uniform | every bit chosen independently from either parent (blue mask `10011010011`: 1 = bit taken from parent 1 for child 1) | `10001000100`, `01101011001` |

All six offspring strings match my recomputation. [computed]

### Mutation [slide 13]
- **Point mutation:** flip one bit: `11101001000` → `11101011000` (bit 7: 0 → 1). [computed check: matches]
- **Swap mutation:** exchange two genes: `11101001000` → `11100011000` (bits 5 and 7 swapped: 1,0 → 0,1). [computed check: matches]

## 6. Fitness [slide 14]

- Fitness = a measure of goodness or badness of a solution: **maximize the goodness** or **minimize the badness**.
- "Normally in pattern recognition": test with a **validation set**; use **mean square error (MSE)**.

## 7. GA flowchart [slide 16]

Initialization → Fitness Evaluation → Selection → Crossover → Mutation → **Terminate?** — **No**: loop back to Fitness Evaluation; **Yes**: output Solutions.

## 8. The simple GA algorithm [slide 17]

`GA(Fitness, Fitness_threshold, p, r, m)`

1. **Initialize:** $P \leftarrow$ $p$ random hypotheses
2. **Evaluate:** for each $h\in P$ compute $\text{Fitness}(h)$
3. **While** $\max_h \text{Fitness}(h) < \text{Fitness\_threshold}$:
   1. **Select:** probabilistically select $(1-r)p$ members of $P$ to add to $P_s$
   2. **Crossover:** probabilistically select $rp/2$ pairs of hypotheses from $P$
   3. **Mutate:** invert a randomly selected bit in $mp$ random members of $P_s$
   4. **Update:** $P \leftarrow P_s$
   5. **Evaluate:** for each $h\in P$ compute $\text{Fitness}(h)$
4. **Return** the hypothesis in $P$ with the highest fitness.

The slide does not define the parameters. Standard meaning (Mitchell, *Machine Learning*, ch. 9) [general]:
- $p$ = population size; $r$ = fraction of the population replaced by crossover each generation; $m$ = mutation rate (fraction of members mutated); $P_s$ = the next generation being built.
- Each selected pair produces **two** offspring, which are added to $P_s$ (the slide omits this).
- Size check [computed]: $(1-r)p + 2\cdot\frac{rp}{2} = p$, so the population size stays constant. Example with made-up $p=100,\ r=0.6,\ m=0.05$: 40 survivors, 30 pairs → 60 children, 5 members mutated.

### How does GA work? [slide 18]
"Monotonically": select the best-fitting, so better individuals can be formed from the best parents by crossover, mutation etc.; "the worst case is the best of the old generation".
Caveat [general]: this guarantee only holds if the best individual is always carried over unchanged (**elitism**). The slide-17 algorithm selects *probabilistically*, so the current best can be lost; the "keep the top rank" selection of slide 11 does give elitism.

## 9. Worked example 1: word guess [slides 2-3]

Target string `THAILAND` (8 letters).
- **Brute force** [slide 2]: enumerate every string `AAAAAAAA`, `AAAAAAAB`, ..., `ZZZZZZZZ` until the target appears. Number of candidates over A-Z: $26^8 = 208{,}827{,}064{,}576$ (about $2.1\times10^{11}$). [computed] (The slide shows three enumeration panels; in the third, the last letters become bold `D`, `ND`, `AND`. I did not rely on that detail.)
- **GA** [slide 3]: a table of successive best strings, converging to the target:

| Gen | String | Letters matching target position-wise [computed] |
|---|---|---|
| 1 | `TBRLICNU` | 2 |
| 2 | `TFEMLPNU` | 3 |
| 3 | `TRANIAPD` | 4 |
| 4 | `THPINAPD` | 5 |
| 5 | `THPILAPD` | 6 |
| 6 | `THUILAND` | 7 |
| 7 | `THAILAND` | 8 |

  The match count rises by exactly one per row. The slide does not state its fitness function; the number of matching letters is the natural choice. [general] The grey shading on the slide marks some correct letters but is not fully consistent with position-wise matching (e.g. the `N` at position 7 of row 1 matches but is unshaded), so I rely on my count, not the shading.

## 10. Worked examples 2 and 3

### GA for curve fitting [slides 19-20]
- Data: many $(x,y)$ points, e.g. $(1.0, 4.1), (3.1, 9.5), (-5.2, 8.6), \dots$ Fit a polynomial of degree up to 5:

$$y = ax^5+bx^4+cx^3+dx^2+ex+f$$

- **Genes** $a,b,c,d,e,f$; **chromosome** = array $[a,b,c,d,e,f]$.
- **Fitness** = $\sum_{\text{data points}}(\text{actual } y-\text{predicted } y)^2$; **the lowest sum is the best fit** (so "fitness" here is really a badness to minimise).

**Algorithm** [slide 20]:
1. Create 100 six-element arrays of random numbers.
2. Repeat 500 times:
   1. For each of the 100 arrays compute its badness using all data points.
   2. Keep the 10 best arrays, discard the other 90.
   3. From each kept array generate 9 new arrays: pick a random element of the six, pick a random floating-point number between 0 and 2, multiply that element by it.
3. After all 500 trials, pick the best array as the final answer.

Checks and notes:
- Population size stays 100: $10 + 10\times 9 = 100$. Fitness evaluations: $100\times500=50{,}000$ (each over all data points). [computed]
- This variant uses **mutation only** (no crossover), i.e. the asexual case of slide 8. [general observation]
- Pitfall [general]: multiplying by a factor cannot change a gene that is exactly 0 and cannot change its sign by itself (factor is in [0, 2]).
- Illustration with the slide's three listed points only [computed]: chromosome $[0,0,0,0,2,2]$ ($y=2x+2$) predicts 4.0, 8.2, -8.4, squared errors 0.01, 1.69, 289.0, so SSE = 290.7. Mutating gene $e$ by factor 0.8 gives $[0,0,0,0,1.6,2]$ with predictions 3.6, 6.96, -6.32 and SSE = 229.308, an improvement, so that child would rank higher.

### GA for the Traveling Salesperson Problem (TSP) [slides 21-23]
- **Genes** = node numbers 1, 2, 3, ...; **chromosome** = the sequence of nodes, e.g. $[2,3,1,4,\dots]$; **fitness** = distance from the beginning to the end (tour length; shorter is better, my reading [general]). [slide 22]
- **Selection:** keep the top rank (10%). [slide 22]
- **Slide 21** has no text, only a hand-drawn figure (my reading from the image): 7 cities A-G, two tours `DEFGCAB` (black) and `DCBAGFE` (red), cut after the 4th gene (`DEFG|CAB` and `DCBA|GFE`). Swapping the tails gives `DEFG GFE`, which is **crossed out**. [computed] It is invalid because G, F, E repeat and A, B, C are missing; the other child `DCBA CAB` would repeat C, A, B. Point: ordinary single-point crossover breaks permutations, so a permutation-safe crossover is needed.
- **Swap mutation** [slide 22]: `1 2 3 4 5 6` → `1 4 3 2 5 6` (positions 2 and 4 exchanged). [computed check: matches]
- **Cycle crossover** [slides 22-23]: parents `1 2 3 4 5 6` and `6 4 3 2 1 5` give offspring `1 4 3 2 5 6` and `6 2 3 4 1 5`. The slide shows only boxes and arrows; the procedure below is my reconstruction, which reproduces both offspring [computed]:
  1. Start at position 1 of parent A (value 1). Parent B has 6 there; find 6 in A (position 6). B has 5 at position 6; find 5 in A (position 5). B has 1 at position 5, which is the starting value, so the cycle closes. Cycle positions = {1, 6, 5}.
  2. Child 1 = A's values at the cycle positions, B's values elsewhere → `1 4 3 2 5 6`.
  3. Child 2 = B's values at the cycle positions, A's values elsewhere → `6 2 3 4 1 5`.
  Both children are valid permutations (no repeated city).

## 11. Project relevance and practical notes

All items below are [general], not from the slides.

- **Hyperparameter search:** chromosome = (k for kNN, C and $\gamma$ for SVM, TF-IDF options, n-gram range, ...), fitness = validation F1. For a handful of hyperparameters, grid or random search is simpler and usually enough; GA pays off only for large discrete spaces.
- **Feature selection (Stage 1):** a bit string with one bit per candidate word or feature (1 = use it); fitness = cross-validated F1 of Naive Bayes / SVM / kNN ([08](08-bayesian-learning.md), [09](09-svm.md), [04](04-knn.md)). Cost: every fitness evaluation trains a classifier.
- **Sentence subset (Stage 2):** an extractive summary can be encoded as a bit string over sentences, but the planned TF-IDF + cosine ranking with top-k is simpler; GA would need a fitness (e.g. coverage minus length penalty) that is itself well-defined.
- Slide 14's remark that fitness is "tested by validation set" implies **overfitting to the validation set**: report the final score on a separate test set (same three-split discipline as NLP 5-1).
- Practical settings: use elitism, fix the random seed, cache fitness values of repeated chromosomes, keep mutation probability small (slide 15), and stop at a fixed generation budget or fitness threshold (slide 17).
- Encoding choice matters: bit strings for subsets (slide 9), real-valued genes for continuous parameters (curve-fitting slide), permutations need special operators (TSP slides).
