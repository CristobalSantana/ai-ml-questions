# Question bank

What the bank contains and how it is organized.

## Principles

- **Learning is the goal.** Every option explains why it is right or wrong, and a hard question requires reasoning, not recalling an obscure fact.
- **No clues in the wording.** You get a question right by knowing the answer, not by how the options are written ([Writing rules](writing-rules.md)).
- **Stable knowledge first.** Most of the bank comes from what does not change: math, classical models, papers, architectures and established definitions. What does change is marked and has a review date.
- **Everything has a source.** A paper, a book, official documentation, a post or a reproducible experiment.
- **Strange Machines is a layer on top.** Questions that come from the posts and from [ml-toy-experiments](https://github.com/CristobalSantana/ml-toy-experiments) carry `collection: "strange-machines"` and link to the post or the experiment.
- **Free and without accounts.** The site does not need to know who is answering.

## Target composition

| Stability (`stability`) | What it includes | Share of the bank | Review |
|---|---|---|---|
| `stable` | Math, classical ML, papers, architectures, established definitions | ~80% | Only if someone reports a mistake |
| `slow` | Good practices and decision criteria: RAG or fine-tuning, sparse or dense | ~15% | Every year (`review_by`) |
| `volatile` | Tools, products, specific vector databases, newly described phenomena | ~5% | Every 6 months (`review_by`) |

The `strange-machines` collection cuts across these classes: any of its questions can have any stability.

## Areas and topics

17 areas and 203 subtopics, in [`taxonomy.json`](../taxonomy.json). Each question belongs to one area and one subtopic.

The site does not show the 17 areas: the filters and the results use 8 **topics** that group them.

| Topic (en · es) | Areas | Includes, for example |
|---|---|---|
| Classical machine learning · Machine learning tradicional | `math`, `ml-foundations`, `classical-ml`, `probabilistic`, `production`, `rl` | Linear algebra, bias and variance, gradient boosting, Bayesian ML, dataset shift, Q-learning |
| Neural networks · Redes neuronales | `deep-learning`, `architectures` | Backpropagation, optimizers, CNNs, GANs, diffusion, PINNs, KANs |
| Transformers & LLMs · Transformers y LLMs | `llm`, `adaptation` | Attention, context window, determinism, prompting, LoRA, RLHF |
| Retrieval & RAG · Retrieval y RAG | `retrieval` | BM25, sparse and dense vectors, HNSW, vector databases |
| Computer vision · Visión por computador | `vision` | Convolution, detection, segmentation, ViT, CLIP |
| Agents, harness & phenomena · Agentes, harness y fenómenos | `agents`, `phenomena` | Tools, ReAct, MCP, double descent, grokking, sycophancy |
| Evaluation & responsible AI · Evaluación e IA responsable | `evaluation`, `responsible` | Precision and recall, calibration, SHAP, fairness, privacy |
| Landmark papers · Papers clave | `papers` | From the perceptron (1958) to KAN (2024) |

- **Topics are only presentation.** They live in `groups`, inside `taxonomy.json`, and questions store their area and subtopic, not their topic. Regrouping means editing that list and rebuilding the site: no question is touched and no statistics are lost.
- The validator requires each area to belong to exactly one topic.
- Quiz sampling uses the areas ([Website](site.md#quiz-rules)), so regrouping does not change which questions come up either.
- `rl` stayed in classical machine learning because its foundations (MDPs, Q-learning, policy gradients) predate LLMs. RLHF and DPO are in `adaptation`, under Transformers & LLMs, next to prompting and fine-tuning.

| Area | Subtopics | Includes, for example |
|---|---|---|
| `math` · Math for ML | 9 | Linear algebra, SVD, Bayes, MLE and MAP, entropy and KL |
| `ml-foundations` · ML foundations | 10 | Bias and variance, regularization, cross-validation, class imbalance |
| `classical-ml` · Classical models | 13 | Regression, SVMs, trees, gradient boosting, clustering, PCA |
| `evaluation` · Metrics and evaluation | 11 | Precision and recall, ROC and PR, calibration, skill scores, evaluation harnesses |
| `deep-learning` · Neural networks and training | 12 | Backpropagation, optimizers, normalization, residual connections |
| `architectures` · Architectures | 17 | CNNs, RNNs, VAEs, GANs, transformers, diffusion, GNNs, SSMs, PINNs, FNOs, KANs |
| `llm` · Transformers and LLMs | 13 | Tokenization, attention, scaling laws, decoding, determinism, KV cache |
| `adaptation` · Adaptation and alignment | 10 | Prompting, fine-tuning, LoRA, RLHF, DPO, distillation |
| `retrieval` · Retrieval, embeddings and RAG | 11 | BM25, sparse and dense vectors, HNSW, vector databases, reranking |
| `agents` · Agents and harness | 9 | Tools, the ReAct loop, memory, harnesses, prompt injection, MCP |
| `probabilistic` · Bayesian ML and uncertainty | 10 | Bayesian inference, MCMC, variational inference, Gaussian processes, conformal prediction |
| `production` · ML in production | 9 | Dataset shift, drift detection, leakage, monitoring, serving |
| `vision` · Computer vision | 10 | Convolution, detection, segmentation, ViT, CLIP |
| `rl` · Reinforcement learning | 8 | MDPs, Q-learning, policy gradients, PPO, reward design |
| `responsible` · Interpretability, fairness and safety | 7 | SHAP, mechanistic interpretability, fairness, privacy |
| `papers` · Landmark papers | 28 | From the perceptron (1958) and Attention Is All You Need (2017) to KAN (2024) |
| `phenomena` · AI phenomena | 16 | Double descent, grokking, hallucination, sycophancy, model collapse |

Adding a subtopic means editing `taxonomy.json`. Area and subtopic ids never change afterwards, because questions refer to them.

## Size and goals

There are 51 cells (17 areas × 3 levels). Today there are 103 questions, about 2 per cell, all still marked `llm_draft`.

- **First batch (done, October 2026):** the context window and prompting, in the subtopics `llm/context-kv-cache`, `adaptation/prompting`, `adaptation/choosing-adaptation`, `agents/memory-context`, `agents/agent-security` (prompt injection), `phenomena/prompt-sensitivity` and `phenomena/in-context-learning`. It shipped together with questions from the other areas, and the bank went from 22 to 103 questions.
- **Launch:** about 10 questions per cell, around 500 in total.
- **Long term:** about 35 per cell, around 1,800. Large areas (architectures, LLMs, papers) can have more and small ones (RL, interpretability) fewer.

The current 103 questions cover the 17 areas, the three levels, the three stability classes and the five Bloom levels, in English and Spanish.
