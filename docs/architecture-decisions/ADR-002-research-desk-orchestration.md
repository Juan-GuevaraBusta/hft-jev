# ADR-002: Orquestación del desk de investigación (LangGraph + prompts de runtime)

- **Estado:** Propuesto
- **Fecha:** 2026-10-12
- **Decisor:** Pendiente de aprobación explícita del usuario

## Contexto

- Inspiración externa: hilo [GrokBot / equipo financiero](https://x.com/51bodila/status/2104605864770371757) y captura de desk «24/7» (estructura en [`docs/sources/desk-24-7-structural-extract.md`](../sources/desk-24-7-structural-extract.md)).
- [`master_prompt.md`](../../master_prompt.md) §9 ya define cinco agentes y un flujo LangGraph; §2.4 y §5 prohíben ejecución y brokers en el MVP.
- ADR-001 fija OpenRouter y observabilidad en nube; no fija topología multi-agente ni veredictos del gate.
- El usuario indicó interés en operación futura supervisada; **no** autorizada en este ADR.

## Criterios relevantes

| Criterio | Peso |
|----------|------|
| Alineación con LangGraph obligatorio | Alto |
| Trazabilidad y evals (LangSmith/Langfuse) | Alto |
| No ampliar alcance a brokers/Plaid en MVP | Alto |
| Fidelidad de handoffs entre especialistas | Medio |
| Costo de tokens (tiers por nodo) | Medio |

## Decisión (propuesta)

1. **Orquestación:** supervisor LangGraph con un prompt por rol en `prompts/agents/` e instrucciones globales en `prompts/orchestration/chief.md`. Rechazar prompt monolítico único y chat multi-bot sin grafo.
2. **Roles:** mantener los cinco agentes de §9; contrato «Signal Scout» absorbido por **Event Analyst**; no crear agentes Money & Books ni Execution Bot.
3. **Veredictos del gate:** `PASS`, `FLAG`, `BLOCK`, `NEEDS_DATA`. `PASS` publica artefacto para revisión humana; no autoriza operación.
4. **Pluma única:** Thesis Synthesizer redacta `executive_summary` y línea analítica; cita estado estructurado de otros nodos.
5. **ExecutionPort:** `execution_status: "disabled"`, `ticket: "NO_TICKET"` en todo artefacto MVP. Habilitar ejecución requiere ADR nuevo y enmienda de §2.4 y §5.
6. **Cartera:** fixture o extracto aportado por el usuario con `as_of`; sin fixture → gate puede devolver `NEEDS_DATA`. Sin lectura bancaria.
7. **Turnos 24/7:** especificados en `config/desk.example.yaml` (`night_ingest`, `morning_desk`); implementación **después** del primer corte vertical por evento.
8. **Modelos:** tiers `fast` / `mid` / `strong` con IDs OpenRouter en config; prompts no fijan marcas de modelo; tier vacío → fallo cerrado.

## Alternativas consideradas

| Alternativa | Por qué se descarta (MVP) |
|-------------|---------------------------|
| Un `prompt.md` estilo Claude Code 24/7 | Rompe LangGraph obligatorio y arnés de §6.3 |
| Seis bots en grupo (GrokBot paso 8) | Pérdida de fidelidad en handoffs («telephone game») |
| Ticket en papel + Alpaca en MVP | Fuera de alcance; contradice §5 actual |
| GrokBot completo (Plaid, TradingView) | Fuera de alcance y sin ADR de datos personales |

## Consecuencias

- Nuevos artefactos: `prompts/`, `config/desk.example.yaml`, extracto en `docs/sources/`.
- Enmienda de `master_prompt.md` §5 y §9.
- M2 (LangGraph) debe cargar prompts desde `prompts/` y desk config.
- Evals: casos con alerta sin fuente → no `PASS`; orden oversized vs `money_rules` → `BLOCK` (cuando exista gate).

## Confianza

**Media** — diseño alineado con master prompt y skills multi-agent; sin validación empírica hasta M1/M2.

## Condición de revisión

Reabrir si: (a) el usuario aprueba operación supervisada con ticket en papel, (b) spike OpenRouter impide tiers, (c) un solo agente demuestra igual calidad con menor costo en evals.

## Referencias

- [`docs/sources/desk-24-7-structural-extract.md`](../sources/desk-24-7-structural-extract.md)
- [`prompts/README.md`](../../prompts/README.md)
- [ADR-001](./ADR-001-llm-openrouter-observability-cloud.md)
