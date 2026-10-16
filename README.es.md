# Preguntas IA/ML

[English](README.md) · **Español**

Preguntas de opción múltiple gratuitas para aprender inteligencia artificial y machine learning, de lo básico a temas de investigación. Cada alternativa explica por qué es correcta o incorrecta, y cada pregunta cita sus fuentes.

**Pruébalo: https://ai-ml-questions.strangemachines.workers.dev/#es**

- 103 preguntas en inglés y en español, en 8 contenidos y tres niveles.
- Modo estudio, con la explicación después de cada respuesta, o modo examen, con el resultado al final.
- Sin cuenta y sin cookies. Una vez cargado funciona sin conexión, y se puede instalar en el teléfono.

**Versión alfa.** Las preguntas son borradores que todavía no revisa una persona. Si encuentras un error, usa el enlace «Reportar un error» bajo la pregunta o [abre un issue](https://github.com/CristobalSantana/ai-ml-questions/issues).

## Contenidos

| Contenido | Por ejemplo |
|---|---|
| Machine learning tradicional | Sesgo y varianza, gradient boosting, procesos gaussianos, dataset shift, Q-learning |
| Redes neuronales | Backpropagation, optimizadores, LSTM, mixture of experts, PINN, KAN |
| Transformers y LLMs | Atención, la ventana de contexto y la KV cache, prompting, LoRA, RLHF |
| Retrieval y RAG | BM25, embeddings, HNSW, chunking, reranking, evaluación de RAG |
| Visión por computador | Convolución, detección, segmentación, ViT, CLIP |
| Agentes, harness y fenómenos | Uso de herramientas, MCP, prompt injection, double descent, grokking, sycophancy |
| Evaluación e IA responsable | Precision y recall, calibración, LLM como juez, equidad, privacidad |
| Papers clave | Del perceptrón (1958) a FlashAttention (2022) |

## Cómo se hacen las preguntas

Cada pregunta sigue reglas de redacción que evitan que la respuesta se note en cómo está escrita, declara su nivel en la taxonomía de Bloom y recibe una dificultad estimada con una rúbrica que después se calibrará con respuestas reales. Un validador revisa el formato y las reglas, y un segundo modelo revisa los hechos, las fuentes y la traducción antes de que una persona apruebe la pregunta. El detalle está en [`docs/`](docs/README.md), en inglés.

## Probarlo en tu computadora

```bash
pip install jsonschema
python scripts/validate.py                    # revisa las preguntas
python scripts/build_site.py --include-drafts # genera site/data
python -m http.server 8000 --directory site   # luego abre http://localhost:8000
```

## Repositorio

| Ruta | Contenido |
|---|---|
| `questions/` | Las preguntas, un archivo JSON por área |
| `taxonomy.json` | Contenidos, áreas y subtemas, en inglés y en español |
| `schema/` | El formato de una pregunta |
| `scripts/` | El validador y el generador del sitio |
| `prompts/` | Prompts para generar y revisar preguntas |
| `site/` | El sitio |
| `docs/` | La documentación completa, en inglés |

## Licencia

Las preguntas están bajo [CC BY-SA 4.0](LICENSE-QUESTIONS): puedes reutilizarlas si citas la fuente y compartes con la misma licencia. El código está bajo [MIT](LICENSE), y las fuentes tipográficas bajo la SIL Open Font License.

Si el sitio te sirve, puedes apoyarlo en [Ko-fi](https://ko-fi.com/strangemachines).
