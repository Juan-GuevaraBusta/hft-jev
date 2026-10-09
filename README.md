# hft-jev

Plataforma de investigación de inversiones **AI-native** (demostración de ingeniería). Arquitectura **diseñada para AWS**, despliegue previsto **solo en local** con emulación (Floci). **No es asesoría financiera** ni un sistema de trading autónomo: no hay ejecución con dinero real.

## Estado actual (honesto)

| Área | Estado |
|------|--------|
| Repositorio GitHub | **Implementado** — [Juan-GuevaraBusta/hft-jev](https://github.com/Juan-GuevaraBusta/hft-jev) |
| `master_prompt.md` + skills de agente | **Implementado** — contrato de trabajo del proyecto |
| README, `.gitignore`, backlog | **Implementado** — PR #2 |
| Verificación Fase A (docs oficiales) | **Implementado** — `docs/verification-fase-a-official-sources.md` |
| Backend, API, worker, LangGraph | **Planificado** — Fase B+ |
| Frontend (Next.js / vinext) | **Planificado** — debate Tipo 1 pendiente |
| Floci, PostgreSQL, SQS, S3 | **Planificado** — M3 |
| LangSmith, Langfuse | **Planificado** — **nube** (ADR-001); cuentas/API keys pendientes |
| LLM (demo) | **Planificado** — OpenRouter tier gratuito (ADR-001) |
| CI (`make test`, GitHub Actions) | **Planificado** |
| Diagramas de arquitectura en README (Sección 17 del master prompt) | **Planificado** — tras debates Tipo 1 y primer corte vertical |

## Fase del proyecto

- **Fase A (plan):** en curso — diagnóstico de entorno, verificación de documentación, debates Tipo 1, roadmap de PRs.
- **Fases B–E:** implementación por PRs pequeños, cada uno con compuerta de comprensión (`APRUEBO <PR-ID>`).

## Cómo clonar

```bash
git clone https://github.com/Juan-GuevaraBusta/hft-jev.git
cd hft-jev
```

No hay aún `make setup` ni `compose.yaml`. Se añadirán cuando exista el primer stack acordado.

## Documentación de referencia

- Contrato operativo: [`master_prompt.md`](./master_prompt.md)
- Tareas y milestones: [`tasks/backlog.md`](./tasks/backlog.md)

## Licencia

MIT — ver [`LICENSE`](./LICENSE).
