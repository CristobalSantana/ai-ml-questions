# Spanish style

How the Spanish version of each question is written. It applies to the questions, the taxonomy names and the interface texts.

## The general rule

Write what a Spanish-speaking practitioner would say, not a word-for-word translation:

- **Natural translation, not literal.** Same meaning and same options in the same order, but Spanish sentences, not English ones in Spanish words.
- **Keep the English term when the field uses it.** Many ML terms are used in English in Spanish-speaking teams and papers (chunk, embedding, fine-tuning). Translating them reads oddly.
- **Translate when an established Spanish term exists** (alucinación, sobreajuste, olvido catastrófico).
- **Neutral Latin American Spanish.** Avoid regional words, such as the Chilean «calzar», «ficha», «chico» (for small), «quiebre de stock», «perilla» or «la gracia», or the Spanish «ordenador» or «coger».
- **Tú**, never usted, as in the interface.
- **Numbers in Spanish format:** a decimal comma (0,82) and a period for thousands (4.096). «Mil millones» is 10⁹; «un billón» is 10¹² (an English trillion).

## Terms kept in English

| Area | Terms |
|---|---|
| Retrieval | chunk, chunking, embedding, retriever, reranking, reranker, cross-encoder, bi-encoder, contextual retrieval |
| Metrics | recall, precision (the metric), F1, benchmark, baseline, skill score |
| Training | batch, dropout, weight decay, learning rate (also «tasa de aprendizaje»), data augmentation, fine-tuning |
| Networks | feature map; features, when they are representations inside a network (interpretability, normalization layers) |
| LLMs | prompt, prompting, token, logits, KV cache, prefill, decode, few-shot, zero-shot, chain of thought, in-context learning |
| Agents and safety | harness, function calling, host (in MCP), prompt injection, prompt leakage, jailbreak |
| Phenomena | prompt sensitivity, sycophancy, grokking, double descent, lost in the middle, reward hacking, specification gaming, model collapse, emergent abilities, lottery ticket hypothesis |
| Production | dataset shift, concept drift, drift, data leakage, target leakage |

## Terms translated

| English | Spanish | Not |
|---|---|---|
| passage (retrieved text) | fragmento | pasaje |
| feature (input variable in tabular or classical ML) | variable | característica, atributo |
| overfitting / underfitting | sobreajuste / subajuste | |
| hallucination | alucinación | |
| catastrophic forgetting | olvido catastrófico | |
| accuracy | exactitud | precisión (that is precision) |
| test set | conjunto de prueba | set de test |
| overconfidence | exceso de confianza | sobreconfianza |
| library (software) | biblioteca | librería |
| attention, layer, loss, weights | atención, capa, pérdida, pesos | |

When a new term comes up, look at how Spanish-speaking practitioners write it, and add it to this page so every question uses it the same way.
