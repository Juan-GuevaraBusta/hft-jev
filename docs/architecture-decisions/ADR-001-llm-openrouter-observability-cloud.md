# ADR-001: LLM OpenRouter y observabilidad en nube (LangSmith + Langfuse)

- **Estado:** Aceptado
- **Fecha:** 2026-10-09
- **Decisor:** Juan Guevara Bustamante (aprobación explícita en chat de sesión)

## Contexto

- Máquina de desarrollo con ~16 GB RAM total; self-host de LangSmith o Langfuse vía Docker Compose recomienda ~16 GiB solo para observabilidad.
- Obligatorios del proyecto: LangGraph, LangSmith y Langfuse (`master_prompt.md` §0).
- Preferencia de arranque: cuentas en nube aceptables; solo GitHub disponible al inicio; LLM vía OpenRouter tier gratuito.

## Criterios relevantes

| Criterio | Peso (usuario, implícito) |
|----------|---------------------------|
| Costo incremental ~$0 | Alto |
| RAM local baja | Alto |
| Rigor demo (trazas + evals visibles) | Alto |
| Privacidad / datos sintéticos en demo | Medio (a detallar en threat model) |
| Simplicidad operativa | Alto |

## Decisión

1. **Proveedor LLM (demo y desarrollo):** [OpenRouter](https://openrouter.ai) con modelos del **tier gratuito** cuando aplique; integración en Python vía **`langchain-openrouter`** (`ChatOpenRouter`), no `ChatOpenAI` + `base_url` como camino principal.
2. **LangSmith:** **SaaS** (plan Developer / cuenta gratuita con API key). Trazas del grafo LangGraph con `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`. **No** self-host Docker de LangSmith en la máquina de desarrollo.
3. **Langfuse:** **Langfuse Cloud** (plan Hobby u otro con API keys). Datasets, experimentos y scores vía **SDK en el worker/evals**, correlacionados con `research_id`. **No** self-host Compose en local para el MVP.
4. **OpenRouter Broadcast** hacia Langfuse/LangSmith: **no** como única instrumentación; evitar duplicar trazas si el SDK ya registra las mismas generations.
5. **Contenido enviado fuera:** inferencia (OpenRouter) + trazas (LangSmith/Langfuse). Demo y evals oficiales usan servicios reales; datos **sintéticos o públicos** etiquetados; sin secretos en payloads.

## Alternativas consideradas

| Alternativa | Por qué se descartó (MVP) |
|-------------|---------------------------|
| Self-host LangSmith + Langfuse en Docker | RAM y complejidad incompatibles con portátil 16 GB y otros stacks Docker ya activos |
| Solo Broadcast OpenRouter → Langfuse | No cubre nodos deterministas ni el grafo completo exigido para LangSmith |
| Ollama local | Menor egress pero más RAM/CPU y otro debate de calidad de demo |
| Sin Langfuse Cloud (solo LangSmith) | Viola obligatorio Langfuse del master prompt |

## Consecuencias

- Crear cuentas LangSmith y Langfuse; claves solo en `.env` (nunca en git).
- Spike pendiente: límites OpenRouter free, modelos `:free`, política de privacidad.
- Tests unitarios: trazadores mock; integración/demo: servicios cloud reales.
- Límite LangSmith Developer: 5 000 trazas base/mes — diseñar evals y demos conscientes del volumen de spans.

## Confianza

**Media** — alineado con documentación oficial; falta validación empírica OpenRouter free + cuentas creadas.

## Condición de revisión

Reabrir si: (a) spike OpenRouter free es inviable, (b) límites de trazas bloquean la demo, (c) política de datos exige 100 % egress cero (entonces valorar solo Langfuse self-host ligero o minimización extrema).

## Referencias

- `docs/verification-fase-a-official-sources.md`
- https://docs.langchain.com/oss/python/integrations/chat/openrouter
- https://docs.langchain.com/oss/python/langgraph/observability
- https://langfuse.com/integrations/gateways/openrouter
- https://openrouter.ai/docs/guides/features/broadcast
