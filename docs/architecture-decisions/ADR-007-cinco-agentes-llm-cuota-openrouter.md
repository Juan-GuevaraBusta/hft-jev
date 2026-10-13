# ADR-007: Cinco agentes LLM, respuestas grabadas fuera de la demo y cuota agotada a la DLQ

- **Estado:** Aceptado; decisión 5 modificada por [ADR-010](./ADR-010-lambda-reenvio-cuota.md) (2026-10-13)
- **Fecha:** 2026-10-13
- **Decisor:** Juan Guevara Bustamante (elección explícita de la opción C en el debate M0-05)
- **Tradeoffs:** T-010 (antes T-108); T-112 sigue abierto en los IDs de modelo

## Contexto

- [ADR-002](./ADR-002-research-desk-orchestration.md) (Propuesto) define 5 agentes LLM, un gate determinista y un ExecutionPort determinista.
- El usuario quiere que el jurado vea un grafo multiagente, con datos públicos reales (SEC EDGAR), sin saldo en OpenRouter y con demo en menos de 2 semanas.
- Límites verificados de OpenRouter para modelos `:free`: 20 peticiones/minuto; **50 peticiones/día sin créditos** (1000/día con ≥ 10 USD comprados).

## Criterios relevantes

| Criterio | Peso (usuario) |
|----------|----------------|
| Grafo multiagente visible para el jurado | Alto (único criterio elegido) |
| Costo $0 (sin saldo en OpenRouter) | Alto |
| Demo en < 2 semanas | Alto |

## Decisión

1. **Cinco agentes LLM** con los roles del ADR-002: `event_analyst`, `evidence_researcher`, `market_impact`, `risk_contradiction`, `thesis_synthesizer`. Se confirman las decisiones 1 y 2 del ADR-002 (supervisor LangGraph, un prompt por rol en `prompts/`).
2. **Gate y ExecutionPort deterministas**, sin LLM (ADR-002, ADR-003, ADR-004).
3. **Respuestas grabadas en desarrollo y tests:** las llamadas al LLM se graban una vez y se reproducen. OpenRouter real solo se usa en la demo y en las evals oficiales (M5). La herramienta concreta se elige en la spec de implementación (Tipo 2).
4. **Sin respaldo silencioso en la demo:** si OpenRouter devuelve 429 o la cuota diaria está agotada, la investigación **falla cerrada**. No se sustituye por respuestas grabadas.
5. **Cuota agotada → DLQ → reanudar:** la investigación queda en `research-jobs-dlq` con su estado guardado en PostgreSQL ([ADR-006](./ADR-006-cola-sqs-worker-checkpointing.md), `thread_id = research_id`). Cuando la cuota se restablece, los mensajes vuelven a `research-jobs` con `StartMessageMoveTask` y el grafo retoma desde el último paso completado, sin repetir llamadas ya hechas.

## Evidencia

| Hecho | Fuente |
|-------|--------|
| Free: 20 RPM; 50 RPD sin créditos; 1000 RPD con ≥ 10 USD | [OpenRouter API limits](https://openrouter.ai/docs/api-reference/limits) |
| 429 de un modelo `:free` (`google/gemma-4-31b-it:free`) en el smoke de Langfuse | Ejecución 2026-10-13 |
| `StartMessageMoveTask` devuelve mensajes de la DLQ a la cola de origen en Floci 2.2.0 | Spike 2026-10-13 en el Mac del usuario (tarea `COMPLETED`, 1 mensaje movido) |
| El checkpointing retoma desde el último paso exitoso | [LangGraph Checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers) |

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| A. 5 agentes LLM siempre reales | ~10 investigaciones/día en total; la cuota se agota programando y la demo queda en riesgo |
| B. 5 nodos visibles, solo 2 con LLM | Tres "agentes" serían funciones; el usuario prioriza el grafo multiagente real |
| Cargar 10 USD de créditos (1000 RPD) | El usuario decide mantener costo $0 |
| Respuestas grabadas como respaldo en la demo | El usuario prefiere fallar cerrado y reanudar con memoria |

## Consecuencias

- Presupuesto: cada investigación real usa ≥ 5 peticiones; ~10 investigaciones reales al día como máximo, compartidas entre demo y evals. Las evals de M5 deben planificarse con esa cuota.
- Paralelismo real limitado por 20 RPM: unas 4 investigaciones simultáneas antes del 429.
- **Pendiente de verificar:** si el límite diario es por cuenta (sumando todos los `:free`) y a qué hora se restablece. Hasta entonces, el reenvío desde la DLQ se dispara con un comando manual; programarlo queda para cuando se conozca la hora.
- **Pendiente de diseñar:** distinguir el 429 por minuto (reintento con espera, respetando `Retry-After`) del agotamiento diario (no gastar los 3 intentos del ADR-006; ir a la DLQ).
- Las respuestas grabadas deben regrabarse al cambiar prompts o modelos; si no, los tests pasan con respuestas desfasadas.
- Datos de entrada: SEC EDGAR real en la demo (exige `User-Agent` con contacto, `config/desk.example.yaml`).

## Confianza

**Media** — el patrón está verificado (cuota, DLQ, redrive, checkpointing), pero la calidad de 5 agentes con modelos gratuitos y la gestión fina de la cuota no se han probado.

## Condición de revisión

Reabrir si: (a) la cuota impide completar la demo o las evals, (b) las evals muestran que menos agentes dan igual calidad (ADR-002, condición c), o (c) el usuario carga créditos.

## Referencias

- https://openrouter.ai/docs/api-reference/limits
- https://docs.langchain.com/oss/python/langgraph/checkpointers
- [ADR-002](./ADR-002-research-desk-orchestration.md), [ADR-006](./ADR-006-cola-sqs-worker-checkpointing.md)
