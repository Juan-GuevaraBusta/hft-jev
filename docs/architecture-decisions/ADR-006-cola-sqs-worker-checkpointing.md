# ADR-006: Investigaciones vía SQS + worker, con checkpointing de LangGraph en PostgreSQL

- **Estado:** Aceptado
- **Fecha:** 2026-10-13
- **Decisor:** Juan Guevara Bustamante (elección explícita de la opción A en el debate M0-05)
- **Tradeoffs:** T-009 (antes T-105)

## Contexto

- Requisitos del usuario: varias investigaciones en paralelo con la UI respondiendo; reintento automático que retome desde el último paso; demostrabilidad como criterio principal; demo en menos de 2 semanas.
- [ADR-005](./ADR-005-floci-ligero-servicios-y-computo.md) ya dispone SQS + DLQ en Floci, PostgreSQL y un worker en Compose.

## Decisión

1. La API valida la petición, crea el registro de la investigación (`research_id`) en PostgreSQL, encola un mensaje en SQS (`research-jobs`) y responde de inmediato.
2. El worker consume SQS y ejecuta el grafo LangGraph compilado con `PostgresSaver` (`langgraph-checkpoint-postgres`), usando `thread_id = research_id` y `durability="sync"`.
3. Reintentos: SQS reentrega el mensaje si el worker no lo borra. Tras **3 recepciones** (`maxReceiveCount=3`) el mensaje pasa a la DLQ (`research-jobs-dlq`) y la investigación queda marcada como fallida.
4. Al reintentar, el worker invoca el grafo con el mismo `thread_id`: LangGraph retoma desde el último checkpoint y no repite los nodos que ya terminaron.
5. El worker borra el mensaje solo cuando la investigación termina (éxito o fallo definitivo registrado).

## Evidencia

| Hecho | Fuente |
|-------|--------|
| SQS + DLQ con `maxReceiveCount` funciona en Floci en este Mac | Spike 2026-10-13 ([ADR-005](./ADR-005-floci-ligero-servicios-y-computo.md)) |
| Los checkpointers dan tolerancia a fallos: si un nodo falla, se retoma desde el último paso exitoso; los nodos exitosos del mismo super-step no se repiten (*pending writes*) | [LangGraph Checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers) |
| Solo `durability="sync"` garantiza que cada checkpoint se escribe antes del siguiente paso; `exit` y `async` pueden perder estado si el proceso se cae | [LangGraph Checkpointers · Durability modes](https://docs.langchain.com/oss/python/langgraph/checkpointers) |
| `PostgresSaver` exige `thread_id` < 255 caracteres y `setup()` para crear tablas | [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) |

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| A sin checkpointing | Cada reintento repite la investigación entera: más llamadas a OpenRouter (cuota gratuita) y no cumple "retomar desde el último paso" |
| B. Tarea en segundo plano de FastAPI | Paralelismo limitado al proceso de la API; si el proceso se cae, la investigación se pierde; poco demostrable |
| C. Cola en PostgreSQL (`SKIP LOCKED`) | Reintentos y DLQ hay que programarlos; no demuestra servicios AWS |

## Consecuencias

- **Entrega al menos una vez:** SQS estándar puede entregar un mensaje dos veces. Usar `research_id` como `thread_id` hace que una entrega duplicada retome el mismo hilo en vez de crear otra investigación; los efectos externos (p. ej. órdenes de Alpaca, ADR-003) deben ser idempotentes por `research_id`.
- **Visibility timeout:** debe superar la duración máxima de una investigación, o el worker debe extenderlo mientras trabaja (`ChangeMessageVisibility`). Si no, SQS reentrega a otro worker a mitad de la ejecución. Valor exacto pendiente del spike de OpenRouter.
- Dependencia nueva: `langgraph-checkpoint-postgres` (y `psycopg`).
- Los checkpoints crecen con el tiempo: definir limpieza de hilos antiguos más adelante.
- Tests: unitarios con `InMemorySaver`; integración con PostgreSQL + Floci.

## Confianza

**Alta** para el patrón (SQS + DLQ medido; checkpointing documentado oficialmente). **Media** para el visibility timeout y la idempotencia de efectos externos (sin implementar aún).

## Condición de revisión

Reabrir si: (a) el checkpointing con `durability="sync"` añade una latencia que rompe la demo, (b) las investigaciones duran más de lo que se puede gestionar con visibility timeout, o (c) se exige orden estricto (pasar a cola FIFO).

## Referencias

- https://docs.langchain.com/oss/python/langgraph/checkpointers
- https://docs.langchain.com/oss/python/langgraph/persistence
- [ADR-005](./ADR-005-floci-ligero-servicios-y-computo.md)
