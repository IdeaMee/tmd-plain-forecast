# ML 01 — Introduction to Machine Learning

Source: `course/slides/01 Introduction to Machine Learning.pptx` (35 slides, Parinya Sanguansat). Text from slide text; checkers boards and the scoring pie chart read from slide images.
Legend: **[slide N]** = slide number · **[general]** = general knowledge or my inference · **[computed]** = my own calculation.

**Project relevance: LOW (background).** It frames the vocabulary (task T, performance P, experience E; target function; LMS update) used throughout the ML course, and gives the course grading.

---

## 1. Course details [slides 2-4]

- Subject: Machine Learning (course code 1322308 per the folder name). Lecturer: Assoc. Prof. Parinya Sanguansat, Ph.D. (parinyasan@pim.ac.th). Material: Python.
- Scoring pie chart [slide 3]: **Classwork 20%, Project 20%, Final 20%, Attendance 10%, Exam 30%**. (Slide labels are "Classwork / Project / Final / Attn / Exam"; "Exam" vs "Final" is not explained, probably midterm vs final exam. [general])
- Reference books: two Thai books by the lecturer on AI with Machine Learning (Python edition).

## 2. What is machine learning? [slides 5-8]

- **Informal:** any computer program that improves its performance at some task through experience and/or data.
- **Formal (well-posed learning):** a program learns from experience $E$ with respect to a class of tasks $T$ and performance measure $P$ if its performance at tasks in $T$, as measured by $P$, improves with experience $E$.
- **Why use ML:** easier for us (program one learning algorithm and let the computer do the work; we need not know the problem's details); better performance (we have biases that affect our judgment).
- **When to use ML:** when we do not know much about the problem; when we have a lot of empirical data; "when we are lazy".
- **Applications:** machine perception, computer vision, NLP, syntactic pattern recognition, search engines, medical diagnosis, bioinformatics/cheminformatics, brain-machine interfaces, credit-card fraud detection, stock market analysis, DNA sequence classification, speech and handwriting recognition, object recognition, game playing, software engineering and robot locomotion.

## 3. Well-posed problems [slides 9-11]

| Problem | T (task) | P (performance) | E (experience) |
|---|---|---|---|
| Handwriting recognition | recognize and classify handwritten words in images | percent of words correctly classified | database of handwritten words with given classifications |
| Robot driving | drive on public motorways using vision sensors | average distance travelled before an error (judged by a human overseer) | sequence of images and steering commands recorded while watching a human driver |
| Checkers | play checkers | percent of games won in a world tournament | opportunity to play against itself |

Refining the problem specification asks: what experience? what exactly should be learned? how represented? which algorithm?

## 4. Designing a learning system (checkers case study) [slides 12-26]

Goal: learn to play checkers and enter a world tournament. Four design choices:

1. **Training experience:**
   - Direct (board state → correct move) vs. **indirect** (outcome of a complete game).
   - Teacher selects board states, or learner selects them.
   - Is the experience representative of the performance goal? (e.g. train playing against itself, evaluate against a world champion.)
2. **Target function:** `ChooseMove: B → M` (board → move) or `Evaluate: B → R` (board → numerical value; better boards score higher; pick the move leading to the successor with the maximal score). The slides choose **Evaluate**.
3. **Representation** of the target function: table look-up, collection of rules, neural network, polynomial function, etc. Trade-off: expressiveness (approximation accuracy) vs. number of training examples needed.
4. **Function approximation algorithm:** LMS.

**Target values** (if we play blue) [slide 19, as written]: final won board $V(b)=-100$; lost $V(b)=100$; drawn $V(b)=0$; non-final $V(b)=V(b')$ where $b'$ is the best final board reachable by optimal play. Note [general]: this sign convention is the reverse of the usual textbook one (win = +100); the slide's worked example follows the slide's convention (blue win = −100), so keep it when checking numbers.

**Linear representation** [slide 24]:

$$V'(b)=w_0+w_1\,rp(b)+w_2\,bp(b)$$

$bp(b)$ = number of blue pieces, $rp(b)$ = number of red pieces; $V$ = true target function, $V'$ = learned hypothesis, $V_{train}$ = training value. Training-value estimation rule: $V_{train}(b)\leftarrow V'(Successor(b))$.

**LMS weight update rule** [slide 25]: pick a training example $b$ at random;
1. $error(b)=V_{train}(b)-V'(b)=V'(Successor(b))-V'(b)$
2. for each board feature $f_i$: $\;w_i\leftarrow w_i+\eta\,f_i\,error(b)$, with learning rate $\eta\approx0.1$ (features: $f_0=1$, $f_1=rp(b)$, $f_2=bp(b)$).

## 5. Worked learning example [slides 27-33]

Initial weights $w_0=-10,\ w_1=75,\ w_2=-60$. Board $b_0$ has 2 red, 2 blue: $V'(b_0)=-10+75\cdot2-60\cdot2=20$. [I re-derived every number below from the piece counts on the boards.]

| Step | Boards | Error | Updates | New weights |
|---|---|---|---|---|
| $b_0\to b_1$ | $V'(b_1)=20$ | $0$ | no change | (−10, 75, −60) |
| $b_3\to b_4$ | $V'(b_3)=20$, $b_4$ has 1 red, 2 blue: $V'(b_4)=-10+75-120=-55$ | $-55-20=-75$ | $w_0{+}{=}0.1{\cdot}1{\cdot}(-75)$; $w_1{+}{=}0.1{\cdot}2{\cdot}(-75)$; $w_2{+}{=}0.1{\cdot}2{\cdot}(-75)$ | (−17.5, 60, −75) |
| $b_5\to b_6$ | with new weights $V'(b_5)=V'(b_4)=-107.5$ (1 red, 2 blue), $V'(b_6)=-167.5$ (0 red, 2 blue) | $-60$ | $w_0{+}{=}0.1{\cdot}1{\cdot}(-60)$; $w_1{+}{=}0.1{\cdot}1{\cdot}(-60)$; $w_2{+}{=}0.1{\cdot}2{\cdot}(-60)$ | (−23.5, 54, −87) |
| final $b_6$ (blue won, $V(b)=-100$) | $V'(b_6)=-197.5$ | $-100-(-197.5)=97.5$ | $w_0{+}{=}0.1{\cdot}1{\cdot}97.5$; $w_1{+}{=}0.1{\cdot}0{\cdot}97.5$; $w_2{+}{=}0.1{\cdot}2{\cdot}97.5$ | (−13.75, 54, −67.5) |

**Testing** [slide 34]: playing blue, red first; for every legal move simulate it, check the value of the resulting board, and pick the best move.

**Class work 1** [slide 35]: determine the target function for playing Tic-Tac-Toe so that it never loses (two board pictures are given).

## 6. Project relevance and practical notes

- The framing "T, P, E" is exactly how to state the project in the report: T = summarize TMD reports into plain Thai; P = classifier F1 and summary ROUGE/BERTScore; E = labeled TMD sentences. [general]
- LMS is the same incremental, error-driven weight update idea later seen in the perceptron and neural networks ([05](05-neural-networks.md)).
