# ADR-010: Lambda + EventBridge Scheduler para reanudar investigaciones paradas por cuota

- **Estado:** Aceptado
- **Fecha:** 2026-10-13
- **Decisor:** Juan Guevara Bustamante (debate M0-05, T-103)
- **Tradeoffs:** T-014 (antes T-103)
- **Modifica:** decisión 5 de [ADR-007](./ADR-007-cinco-agentes-llm-cuota-openrouter.md) (la cuota agotada ya no va a la DLQ general ni se reenvía con `StartMessageMoveTask`)

## Contexto

- El usuario acepta Lambda solo si resuelve un problema real. El problema: reanudar automáticamente las investigaciones paradas cuando se agota la cuota diaria de OpenRouter (ADR-007), a la hora en que se restablece.
- En la DLQ general caerían también fallos por bugs; reenviarlos a ciegas los metería en bucle y gastaría cuota.

## Evidencia

| Hecho | Fuente |
|-------|--------|
| Los límites de modelos `:free` son globales por cuenta: más claves o cuentas no dan más cuota | [OpenRouter API limits](https://openrouter.ai/docs/api-reference/limits) |
| Un 429 de límite de plataforma trae `X-RateLimit-Limit`, `X-RateLimit-Remaining` y `X-RateLimit-Reset`; `GET /api/v1/key` informa `free_model_daily_requests` | Misma fuente |
| EventBridge Scheduler con `at(...)` y `ActionAfterCompletion=DELETE` invoca una Lambda Python 3.12 a la hora fijada en Floci; el programa se borra solo | Spike 2026-10-13, Mac del usuario |
| La Lambda (contenedor real `public.ecr.aws/lambda/python:3.12`, ~49 MiB de 128 MiB) movió 4 mensajes de `research-jobs-quota-wait` a `research-jobs` 42 s después de crear el programa | Mismo spike |
| `StartMessageMoveTask` solo acepta como origen una cola configurada como DLQ (Floci lo valida igual que AWS) | Mismo spike (`InvalidParameterValue: Source queue is not configured as a dead-letter queue`) |
| Primera descarga de la imagen de Lambda: ~47 s | Mismo spike |

## Decisión

1. **Cola aparte para cuota:** cuando el worker detecta agotamiento de la cuota diaria (429 con `X-RateLimit-Remaining: 0`), envía la investigación a `research-jobs-quota-wait` y borra el mensaje original. No consume los 3 intentos de ADR-006. La DLQ `research-jobs-dlq` queda solo para fallos reales.
2. **Programa puntual:** el worker crea (o reutiliza, por nombre derivado de la hora de reset) un programa de EventBridge Scheduler `at(<X-RateLimit-Reset>)` con `ActionAfterCompletion=DELETE`.
3. **Lambda `redrive-quota-wait`:** recibe los mensajes de `quota-wait`, los envía a `research-jobs` y los borra. **No usa la clave de OpenRouter.** El grafo retoma desde el último checkpoint (ADR-006).
4. Lambda, Scheduler y la cola nueva se declaran en Terraform ([ADR-008](./ADR-008-terraform-todo-en-floci.md)).

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| B. Scheduler periódico + Lambda que consulta `GET /api/v1/key` | La Lambda necesitaría la clave de OpenRouter; consultas constantes |
| C. Sin Lambda: el worker reenvía cuando llega la hora | Resuelve el problema con menos piezas (steelman), pero mezcla responsabilidades y no muestra serverless; el usuario prefiere A |
| Todo en la misma DLQ | Los fallos por bugs se reenviarían en bucle y gastarían cuota |
| `StartMessageMoveTask` desde `quota-wait` | AWS y Floci exigen que el origen sea una DLQ |

## Consecuencias

- Si el reset llega y la cuota sigue agotada (p. ej., otra ejecución la gastó), el worker vuelve a mandar la investigación a `quota-wait` y crea otro programa; no hay bucle porque cada intento espera al siguiente reset.
- Un mensaje reenviado puede duplicarse (entrega al menos una vez); `thread_id = research_id` lo absorbe (ADR-006).
- La primera invocación de la Lambda tarda ~47 s más si su imagen no está en caché: precargarla antes de la demo.
- **Pendiente de verificar en implementación:** el formato exacto de `X-RateLimit-Reset` (epoch en ms o en s) y cómo `langchain-openrouter` expone las cabeceras del 429.

## Confianza

**Alta** para el mecanismo (Scheduler + Lambda + SQS probados en Floci). **Media** para la detección del agotamiento diario (cabeceras sin probar con un 429 real de cuota).

## Condición de revisión

Reabrir si: (a) `langchain-openrouter` no expone las cabeceras del 429 y no hay forma razonable de leerlas, (b) el usuario carga créditos (1000 peticiones/día) y la cola de cuota deja de tener sentido, o (c) Lambda en Floci falla de forma no reproducible.

## Referencias

- https://openrouter.ai/docs/api-reference/limits
- [ADR-006](./ADR-006-cola-sqs-worker-checkpointing.md), [ADR-007](./ADR-007-cinco-agentes-llm-cuota-openrouter.md), [ADR-008](./ADR-008-terraform-todo-en-floci.md)
