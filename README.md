# AI/ML Questions

**English** · [Español](README.es.md)

Free multiple-choice questions for learning artificial intelligence and machine learning, from the basics to research topics. Every option explains why it is right or wrong, and every question cites its sources.

**Try it: https://ai-ml-questions.strangemachines.workers.dev/**

- 103 questions in English and Spanish, in 8 topics and three levels.
- Study mode, with the explanation after each answer, or exam mode, with the results at the end.
- No account and no cookies. Once loaded it works offline, and it can be installed on a phone.

**Alpha version.** The questions are drafts that a person has not reviewed yet. If you find a mistake, use the "Report a mistake" link under the question or [open an issue](https://github.com/CristobalSantana/ai-ml-questions/issues).

## Topics

| Topic | For example |
|---|---|
| Classical machine learning | Bias and variance, gradient boosting, Gaussian processes, dataset shift, Q-learning |
| Neural networks | Backpropagation, optimizers, LSTMs, mixture of experts, PINNs, KANs |
| Transformers & LLMs | Attention, the context window and KV cache, prompting, LoRA, RLHF |
| Retrieval & RAG | BM25, embeddings, HNSW, chunking, reranking, RAG evaluation |
| Computer vision | Convolution, detection, segmentation, ViT, CLIP |
| Agents, harness & phenomena | Tool use, MCP, prompt injection, double descent, grokking, sycophancy |
| Evaluation & responsible AI | Precision and recall, calibration, LLM-as-judge, fairness, privacy |
| Landmark papers | From the perceptron (1958) to FlashAttention (2022) |

## How the questions are made

Each question follows item-writing rules that keep the answer from showing in the wording, states its level in Bloom's taxonomy, and gets an estimated difficulty from a rubric that real answers will later calibrate. A validator checks the format and the rules, and a second model checks facts, sources and the translation before a person approves the question. The details are in [`docs/`](docs/README.md).

## Run it locally

```bash
pip install jsonschema
python scripts/validate.py                    # checks the questions
python scripts/build_site.py --include-drafts # builds site/data
python -m http.server 8000 --directory site   # then open http://localhost:8000
```

## Repository

| Path | Contents |
|---|---|
| `questions/` | The questions, one JSON file per area |
| `taxonomy.json` | Topics, areas and subtopics, in English and Spanish |
| `schema/` | The format of a question |
| `scripts/` | The validator and the site builder |
| `prompts/` | Prompts for generating and reviewing questions |
| `site/` | The website |
| `docs/` | The full documentation |

## License

The questions are under [CC BY-SA 4.0](LICENSE-QUESTIONS): you can reuse them if you credit the source and share under the same license. The code is under [MIT](LICENSE), and the fonts under the SIL Open Font License.

If the site helps you, you can support it on [Ko-fi](https://ko-fi.com/strangemachines).
