# Prompts de runtime (grafo LangGraph)

Los prompts de esta carpeta gobiernan la **ejecución** del desk de investigación. No sustituyen ni modifican [`master_prompt.md`](../master_prompt.md) (contrato de construcción, secciones 0–4).

## Precedencia

1. `master_prompt.md` — reglas inviolables (sin órdenes, sin brokers en MVP, evidencia honesta).
2. `config/desk.yaml` (copia local de `desk.example.yaml`) — universo, horarios, reglas de riesgo, IDs de modelo OpenRouter por tier.
3. `prompts/orchestration/chief.md` — orquestación del run (objetivo, orden de fases, veredictos, entrega).
4. `prompts/agents/*.md` — system prompts por nodo del grafo.

Si un prompt de agente contradice el chief o el master prompt, gana el nivel superior.

## Mapa rol → nodo LangGraph

| Archivo | Nodo / rol en §9 | Tier LLM típico (config) |
|---------|------------------|---------------------------|
| `agents/event_analyst.md` | Event Analyst (contrato Signal Scout) | `fast` o `mid` |
| `agents/evidence_researcher.md` | Evidence Researcher | `mid` |
| `agents/market_impact.md` | Market Impact Analyst | `mid` |
| `agents/risk_contradiction.md` | Risk and Contradiction Analyst | `strong` |
| `agents/thesis_synthesizer.md` | Thesis Synthesizer (pluma única del memo) | `strong` |
| `orchestration/chief.md` | Instrucciones globales del supervisor / run | — |

Nodos **no** LLM (código): Validate Input, Deterministic Gate, ExecutionPort (`disabled`).

## Salida estructurada

Cada agente escribe en el estado del grafo (JSON/Pydantic). El Thesis Synthesizer es la **única** pluma del `executive_summary` y de la línea de decisión para revisión humana. No reescribir campos de otros nodos: referenciarlos por clave de estado.

## Veredictos (gate determinista)

| Veredicto | Significado |
|-----------|-------------|
| `PASS` | Artefacto publicable para revisión humana; **no** autoriza operación |
| `FLAG` | Contradicción material o cifra no verificable; revisión humana obligatoria |
| `BLOCK` | Regla de riesgo o política incumplida |
| `NEEDS_DATA` | Falta figura, fuente, periodo, cartera o regla configurada |

## Versionado

Al cambiar un prompt, registrar en Langfuse el identificador de versión (commit o hash) usado en evals. Ver ADR-001.

## Referencias

- Extracto de fuentes externas: [`docs/sources/desk-24-7-structural-extract.md`](../docs/sources/desk-24-7-structural-extract.md)
- ADR propuesto: [`docs/architecture-decisions/ADR-002-research-desk-orchestration.md`](../docs/architecture-decisions/ADR-002-research-desk-orchestration.md)
