# Backlog

> Mantenido por el agente; decisiones **Tipo 1** no se cierran aquí sin debate y ADR.  
> Estados: `TODO` | `IN_PROGRESS` | `BLOCKED` | `DONE`

## Milestones (referencia — orden debatible)

GitHub: milestones **M0–M6** creados; épicas y sub-issues en [manifest](./github-backlog-manifest.json). Issues Alpaca **#5–#16** sin milestone (fuera de este backlog).

| ID | Milestone | Épica GitHub | Estado global |
|----|-----------|--------------|---------------|
| M0 | Requisitos, repo, linters, ADRs, verificación docs | [#17](https://github.com/Juan-GuevaraBusta/hft-jev/issues/17) | **IN_PROGRESS** |
| M1 | Corte vertical determinista (sin LLM de pago) | [#18](https://github.com/Juan-GuevaraBusta/hft-jev/issues/18) | TODO |
| M2 | Arnés LangGraph + LangSmith (cargar `prompts/` y `config/desk.yaml`) | [#19](https://github.com/Juan-GuevaraBusta/hft-jev/issues/19) | TODO |
| M3 | Floci (SQS, S3), worker, IaC | [#20](https://github.com/Juan-GuevaraBusta/hft-jev/issues/20) | TODO |
| M4 | Dashboard vinext/Next | [#21](https://github.com/Juan-GuevaraBusta/hft-jev/issues/21) | TODO |
| M5 | Evals + Langfuse (+ Jev opcional) | [#22](https://github.com/Juan-GuevaraBusta/hft-jev/issues/22) | TODO |
| M6 | CI, README arquitectura completo, demo | [#23](https://github.com/Juan-GuevaraBusta/hft-jev/issues/23) | TODO |

## Decisiones Tipo 1

### Cerradas (ADR)

- **LLM + observabilidad (nube):** OpenRouter + LangSmith Cloud + Langfuse Cloud — [ADR-001](../docs/architecture-decisions/ADR-001-llm-openrouter-observability-cloud.md) (2026-10-09).
- **`decision_score`, umbrales y límites de riesgo:** requisitos duros + suma ponderada versionada, umbrales 0.40 / 0.75 en paper, seguimiento en sombra, límites porcentuales, criterio de calibración para `live` — [ADR-004](../docs/architecture-decisions/ADR-004-decision-score-umbrales-limites-riesgo.md) (2026-10-13).
- **Floci y cómputo:** Floci ligero (SQS + DLQ + S3); PostgreSQL y worker como contenedores de Compose; ECS/Fargate y RDS solo en diseño e IaC — [ADR-005](../docs/architecture-decisions/ADR-005-floci-ligero-servicios-y-computo.md) (2026-10-13).
- **Ejecución de investigaciones:** SQS + worker con checkpointing de LangGraph en PostgreSQL; 3 intentos antes de la DLQ — [ADR-006](../docs/architecture-decisions/ADR-006-cola-sqs-worker-checkpointing.md) (2026-10-13).
- **Agentes y cuota LLM:** 5 agentes LLM; respuestas grabadas fuera de la demo; sin saldo en OpenRouter (50 peticiones/día); cuota agotada a la DLQ y reanudación — [ADR-007](../docs/architecture-decisions/ADR-007-cinco-agentes-llm-cuota-openrouter.md) (2026-10-13).
- **IaC y despliegue:** Terraform; todo en Floci también en desarrollo (SQS + DLQ, S3, RDS, worker en ECS Fargate); sustituye parte de ADR-005 — [ADR-008](../docs/architecture-decisions/ADR-008-terraform-todo-en-floci.md) (2026-10-13).
- **Frontend:** vinext 1.1, solo local; sin Cloudflare en el MVP — [ADR-009](../docs/architecture-decisions/ADR-009-frontend-vinext-local.md) (2026-10-13).
- **Lambda:** solo para reanudar investigaciones paradas por cuota (cola `quota-wait` + Scheduler puntual + Lambda) — [ADR-010](../docs/architecture-decisions/ADR-010-lambda-reenvio-cuota.md) (2026-10-13).
- **Plazo:** demo M0–M6 en menos de 2 semanas. Decisión del usuario, riesgo aceptado: demo incompleta o con piezas sin pulir (2026-10-13).

### Pendientes (no cerradas)

- Spike OpenRouter free: IDs de modelo por tier, si el límite diario es por cuenta y a qué hora se restablece (corto: 50 peticiones/día).
- Jev (TypeSafe AI): opcional tras verificar API.

## Tareas

### M0 — Fundamentos

| ID | Título | Estado | Complejidad | Notas |
|----|--------|--------|-------------|-------|
| M0-01 | Bootstrap repo (master prompt, skills) | DONE | S | PR #1 |
| M0-02 | README mínimo, `.gitignore`, backlog esqueleto | DONE | S | PR #2 |
| M0-03 | Diagnóstico entorno local (Python 3.12, Node, Docker, Git) | DONE | S | Informe en chat + §2 del doc de verificación |
| M0-04 | Verificación docs: Floci, LangSmith, Langfuse, LangGraph, vinext, IaC, Jev | DONE | M | `docs/verification-fase-a-official-sources.md` (PR-003) |
| M0-05 | Debates Tipo 1 + orden aprobado | TODO | L | [#24](https://github.com/Juan-GuevaraBusta/hft-jev/issues/24) |
| M0-06 | Plan MVP + roadmap PRs (3 entregas) | TODO | L | [#37](https://github.com/Juan-GuevaraBusta/hft-jev/issues/37) |
| M0-07 | `pyproject.toml`, Ruff, pytest, Makefile mínimo | DONE | M | [#46](https://github.com/Juan-GuevaraBusta/hft-jev/issues/46) — commit `f34051e`, 2026-10-13 |
| M0-08 | ADRs iniciales (plantilla + primeros temas cerrados) | TODO | M | [#38](https://github.com/Juan-GuevaraBusta/hft-jev/issues/38) |
| M0-09 | Contrato desk: `prompts/`, `config/desk.example.yaml`, extracto fuentes, ADR-002 (Propuesto), delta §5/§9 | DONE | M | 2026-10-12 |

### Plantilla de tarea (futuras entradas)

```text
ID:
Título:
Justificación:
Dependencias:
Componentes:
Criterios de aceptación:
Tests requeridos:
Comando de verificación:
Complejidad: S|M|L
Estado:
Decisiones Tipo 1:
Preguntas críticas compuerta:
```
