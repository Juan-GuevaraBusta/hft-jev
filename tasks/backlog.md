# Backlog

> Mantenido por el agente; decisiones **Tipo 1** no se cierran aquí sin debate y ADR.  
> Estados: `TODO` | `IN_PROGRESS` | `BLOCKED` | `DONE`

## Milestones (referencia — orden debatible)

| ID | Milestone | Estado global |
|----|-----------|---------------|
| M0 | Requisitos, repo, linters, ADRs, verificación docs | **IN_PROGRESS** |
| M1 | Corte vertical determinista (sin LLM de pago) | TODO |
| M2 | Arnés LangGraph + LangSmith | TODO |
| M3 | Floci (SQS, S3), worker, IaC | TODO |
| M4 | Dashboard vinext/Next | TODO |
| M5 | Evals + Langfuse (+ Jev opcional) | TODO |
| M6 | CI, README arquitectura completo, demo | TODO |

## Decisiones Tipo 1 pendientes (no cerradas)

- Observabilidad: LangSmith / Langfuse — nube vs self-hosted; qué datos salen de la máquina.
- Servicios AWS del diseño vs emulación Floci vs contenedores propios.
- Cola + worker vs alternativa más simple para MVP.
- Cantidad de agentes vs funciones deterministas.
- LLM demo: OpenRouter tier gratuito (límites y privacidad por verificar).
- Frontend: vinext vs alternativas; Cloudflare (descartado / opcional / solo local).
- Herramienta IaC (Pulumi, Terraform, CDK, etc.) compatible con Floci.
- Jev (TypeSafe AI): opcional tras verificar API.

## Tareas

### M0 — Fundamentos

| ID | Título | Estado | Complejidad | Notas |
|----|--------|--------|-------------|-------|
| M0-01 | Bootstrap repo (master prompt, skills) | DONE | S | PR #1 |
| M0-02 | README mínimo, `.gitignore`, backlog esqueleto | IN_PROGRESS | S | PR-002 |
| M0-03 | Diagnóstico entorno local (Python, Node, Docker, Git) | TODO | S | Fase A §23.2 |
| M0-04 | Verificación docs: Floci, LangSmith, Langfuse, LangGraph, vinext, IaC, Jev | TODO | M | Fase A §23.3 |
| M0-05 | Debates Tipo 1 + orden aprobado | TODO | L | Fase A §23.4–5 |
| M0-06 | Plan MVP + roadmap PRs (3 entregas) | TODO | L | Fase A §23.6 |
| M0-07 | `pyproject.toml`, Ruff, pytest, Makefile mínimo | TODO | M | Tras plan aprobado |
| M0-08 | ADRs iniciales (plantilla + primeros temas cerrados) | TODO | M | Tras debates |

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
