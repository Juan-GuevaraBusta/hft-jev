# Tradeoffs de arquitectura

> Registro vivo de los tradeoffs de arquitectura de hft-jev. Lo mantiene el agente y lo revisa el usuario.  
> Estados: **Decidido** (con ADR aceptado) | **Recomendado** (propuesta previa al debate, sin ADR) | **Abierto** (sin propuesta cerrada).  
> Solo lo marcado como **Decidido** es vinculante. Lo demás puede cambiar en el debate Tipo 1 (M0-05).

## 1. Tradeoffs decididos

| ID | Tema | Elección | Alternativas descartadas | Lo que ganamos | Lo que cedemos | ADR | Fecha |
|----|------|----------|--------------------------|----------------|----------------|-----|-------|
| T-001 | Proveedor LLM | OpenRouter (tier gratuito) vía `langchain-openrouter` (`ChatOpenRouter`) | Ollama local; `ChatOpenAI` + `base_url` como camino principal | Costo ~$0, poca RAM local, acceso a varios modelos | Dependencia externa, límites de uso del tier gratuito, inferencia sale de la máquina | [ADR-001](./ADR-001-llm-openrouter-observability-cloud.md) | 2026-10-09 |
| T-002 | Trazas del grafo | LangSmith SaaS (plan Developer) | LangSmith self-host en Docker (requiere licencia Enterprise y ~16 GB RAM) | Cero operación local, integración nativa con LangGraph | Tope de 5 000 trazas/mes, retención de 14 días, trazas salen de la máquina | [ADR-001](./ADR-001-llm-openrouter-observability-cloud.md) | 2026-10-09 |
| T-003 | Evals y datasets | Langfuse Cloud (plan Hobby) | Langfuse self-host en Docker Compose; prescindir de Langfuse | Cero operación local, cumple el obligatorio del `master_prompt.md` | Tope de 50 000 unidades/mes, datos salen de la máquina | [ADR-001](./ADR-001-llm-openrouter-observability-cloud.md) | 2026-10-09 |
| T-004 | Instrumentación | SDK de LangSmith y Langfuse como fuente principal | OpenRouter Broadcast como única instrumentación | Cubre nodos deterministas y el grafo completo | Hay que evitar trazas duplicadas si se activa Broadcast | [ADR-001](./ADR-001-llm-openrouter-observability-cloud.md) | 2026-10-09 |

## 2. Tradeoffs recomendados o abiertos (pendientes de debate)

| ID | Tema | Recomendación actual | Alternativas en juego | A favor | En contra / riesgo | Evidencia que haría cambiar | Estado |
|----|------|----------------------|-----------------------|---------|--------------------|-----------------------------|--------|
| T-101 | Servicios emulados en Floci | SQS (con cola de mensajes fallidos) y S3 en Floci; PostgreSQL en contenedor propio | RDS en Floci; todo en contenedores propios sin Floci | Código con SDK de AWS y `endpoint_url` configurable; PostgreSQL más simple y fiable | Paridad Floci vs AWS no verificada; Floci sin probar en Apple Silicon | Spike de Floci fallido en el Mac | Recomendado |
| T-102 | Cómputo del worker | Worker de larga duración en contenedor (ECS/Fargate en el diseño; Compose o ECS en Floci) | AWS Lambda disparada por SQS; diseño serverless puro | Sin límite de 15 min; dependencias pesadas sin arranque en frío; checkpointing de LangGraph más simple | Más infraestructura que una función; hay que gestionar el proceso | Investigaciones de pocos minutos en el spike de OpenRouter y prioridad alta a mostrar serverless | Recomendado |
| T-103 | Lambda en el MVP | No usar; opcional para tareas cortas por eventos (S3, cola de mensajes fallidos) | Lambda como pieza central | Menos alcance y complejidad | Muestra menos servicios de AWS en la demo | Requisito explícito de demo serverless | Recomendado |
| T-104 | Simulación de carga | Fuera del MVP: Floci emula APIs, no rendimiento ni escalado | Varios workers consumiendo la cola; pruebas de estrés | MVP acotado y demostrable | No demuestra comportamiento bajo carga | Requisito explícito de demo bajo carga | Abierto |
| T-105 | Cola + worker vs algo más simple | Cola + worker (flujo del `master_prompt.md` §12) | Ejecución síncrona o tarea en segundo plano en FastAPI | API no bloquea; reintentos, idempotencia y cola de mensajes fallidos | Más piezas móviles en local | Debate M0-05 | Abierto |
| T-106 | Herramienta de IaC | Pendiente | Terraform, OpenTofu, CDK (con pruebas oficiales de compatibilidad con Floci); Pulumi (sin suite oficial) | — | — | Debate M0-05 y spike con SQS + S3 | Abierto |
| T-107 | Frontend | Pendiente (vinext si se acepta el riesgo de madurez) | Next.js estándar; despliegue opcional en Cloudflare | — | — | Debate M0-05 | Abierto |

## 3. Registro de preguntas de arquitectura

Cada pregunta sobre arquitectura se añade aquí, con su respuesta resumida y el tradeoff que afecta.

| Fecha | Pregunta | Respuesta resumida | Tradeoffs relacionados | Estado |
|-------|----------|--------------------|------------------------|--------|
| 2026-10-12 | ¿El proyecto usa LangSmith, Langfuse y LangChain? Se usará OpenRouter | Sí: LangGraph, LangSmith y Langfuse son obligatorios; LangChain se usa para el cliente LLM (`ChatOpenRouter`). OpenRouter ya está aprobado | T-001, T-002, T-003, T-004 | Decidido |
| 2026-10-12 | ¿Ya está la arquitectura en Floci para simular uso pesado de AWS? | No. Hay propuesta (SQS + S3 en Floci, PostgreSQL propio) sin ADR ni código. La simulación de carga no está en el MVP | T-101, T-104, T-105, T-106 | Abierto |
| 2026-10-12 | ¿No haría falta usar Lambda? | No es obligatoria. Se recomienda worker en contenedor por duración, dependencias y checkpointing; Lambda queda opcional | T-102, T-103 | Recomendado |
