# ML notes — index

Course: Machine Learning (lecturer Parinya Sanguansat). Slides: `../../slides/01 ... 09 *.pptx`. Overall index: [../README.md](../README.md). Legend of provenance tags is in the README.

| # | File | What it covers | Project relevance |
|---|---|---|---|
| 01 | [01-intro-to-ml.md](01-intro-to-ml.md) | T/P/E definition of learning; checkers design; linear value function; LMS update with a full worked trace; course grading | low |
| 02 | [02-concept-learning.md](02-concept-learning.md) | EnjoySport task, hypothesis counting, general-to-specific ordering, Find-S, version spaces, Candidate Elimination, inductive bias | low |
| 03 | [03-decision-tree.md](03-decision-tree.md) | entropy, information gain, ID3 and extensions, continuous attributes, overfitting and pruning | medium (alternative classifier) |
| 04 | [04-knn.md](04-knn.md) | k-NN procedure, $L_1/L_2/L_\infty/L_p$ norms, condensed NN, k-d tree, LSH | medium-low |
| 05 | [05-neural-networks.md](05-neural-networks.md) | perceptron, delta rule, multilayer networks, backpropagation | background for RNN/Transformer |
| 06 | [06-clustering.md](06-clustering.md) | Self-Organizing Map (with a traced example), K-means, fuzzy c-means, EM, Gaussian mixture models | low-medium |
| 07 | [07-genetic-algorithms.md](07-genetic-algorithms.md) | genetic algorithm operators and examples | low |
| 08 | [08-bayesian-learning.md](08-bayesian-learning.md) | Bayes theorem, MAP/ML, Bayes optimal, **Naive Bayes and its text-categorization algorithm**, m-estimate, belief networks | **high** |
| 09 | [09-svm.md](09-svm.md) | margin, dual form, soft margin, kernels, multiclass | medium |

## Reading order for the project

1. **08** (Naive Bayes: the Stage-1 classifier) then **09** and **04** (comparison classifiers), optionally **03**.
2. **01** for the T/P/E wording of the report; **05** as the bridge to NLP 5-2 (RNN) and 7-1 (Transformer).

## Dependencies between chapters

- 08 and 09 both rely on conditional probability / optimization ideas introduced in 01 and 05 only loosely; each file is self-contained.
- 04's "non-numeric data to numeric by frequency" idea is the same as the bag-of-words vectors in NLP 4-1.
- 09's soft-margin trade-off parameter $C$ and 05's overfitting discussion address the same generalization issue.
