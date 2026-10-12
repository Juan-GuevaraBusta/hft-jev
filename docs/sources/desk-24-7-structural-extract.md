# Extracto estructural: desk de investigación 24/7 (referencias externas)

> Documento de procedencia para hft-jev. **No** contiene el texto de prompts de terceros. Describe patrones adoptados o rechazados en palabras propias.

## Procedencia

| Fuente | URL / medio | Uso en hft-jev |
|--------|-------------|----------------|
| Hilo GrokBot (equipo financiero en 10 pasos) | [x.com/51bodila/status/2104605864770371757](https://x.com/51bodila/status/2104605864770371757) | Contrato por rol (trabajo, fuentes, salida, handoff, test); veredictos `PASS` / `BLOCK` / `NEEDS_DATA`; alerta ≠ orden |
| Captura de correo «24/7 Trading Team» | Imagen adjunta en sesión de diseño (2026-10-12); remitente citado «Alex Jane Street» | Solo **estructura** operativa (turnos, jefe de desk, aprobación humana, tiers de modelo); **no** se replica el prompt XML ni nombres de modelo concretos |
| Contrato del repositorio | [`master_prompt.md`](../../master_prompt.md) | Precede a cualquier prompt de runtime; prohíbe brokers y ejecución en el MVP |

## Patrones estructurales adoptados (desk 24/7, foto)

1. **Turno nocturno (ingesta):** recopilar filings y calendario de earnings del universo configurado; escribir en almacén de evidencia; **no** publicar memo al usuario.
2. **Turno de mañana (desk):** hora fija en `America/New_York` (p. ej. 09:00); rankear novedades y consumir lo dejado por la noche; disparar el mismo grafo de investigación que un evento puntual.
3. **Jefe de desk (una pluma):** un solo agente redacta el resumen ejecutivo y la línea de decisión; no parafrasea a ciegas a los especialistas — cita su salida estructurada del estado del grafo.
4. **Compuerta antes de «listo»:** sin cifra con fuente y periodo, sin reglas de riesgo cargadas o con cartera obsoleta → no hay `PASS`.
5. **Aprobación humana:** el humano revisa el artefacto; en el MVP no hay ticket ni broker.
6. **Tiers de modelo:** tareas baratas vs. profundas usan `fast` / `mid` / `strong` en config (OpenRouter, ADR-001), no marcas de modelo fijas en el texto del prompt.

## Patrones adoptados (hilo GrokBot)

1. **Ficha de bot:** cada rol declara trabajo, fuentes permitidas, formato de salida, siguiente consumidor y un test que puede fallar.
2. **Signal Scout como contrato, no como sexto agente:** verificación de alerta/noticia → `CONFIRMED` | `UNCONFIRMED` | `NO_RELEVANT_NEWS`; enlaces a fuente primaria; la alerta de precio no es instrucción de compra.
3. **Risk como código + prosa:** aritmética de límites y exposición en módulo determinista; el analista de riesgo en prosa aporta contraargumentos e invalidación.
4. **Chief / memo único:** un memo corto con quién verificó qué; conflictos y datos faltantes visibles.
5. **Execution explícitamente separado:** en hft-jev el puerto `ExecutionPort` permanece `disabled` y responde `NO_TICKET` hasta un ADR futuro.

## Exclusiones explícitas (no implementar en este corte)

- Integración Plaid, Mercury, Xero, Robinhood, Alpaca u otros conectores de dinero real.
- TradingView, webhooks de alerta y relays con API keys en alertas.
- Chat grupal de seis bots sin grafo (pérdida de fidelidad en handoffs).
- Un único `prompt.md` monolítico que reemplace LangGraph.
- Copiar o commitear el master prompt de la captura de correo.
- Órdenes, cantidades, sides o campos de broker en el `ResearchArtifact` del MVP.

## Mapeo a artefactos del repo

| Idea externa | Artefacto hft-jev |
|--------------|-------------------|
| Chief Bot | [`prompts/orchestration/chief.md`](../../prompts/orchestration/chief.md) + nodo Thesis Synthesizer |
| Signal Scout | Contrato en [`prompts/agents/event_analyst.md`](../../prompts/agents/event_analyst.md) |
| Analyst / filings | [`prompts/agents/evidence_researcher.md`](../../prompts/agents/evidence_researcher.md) |
| Risk Manager (veredicto) | Módulo Deterministic Gate (planificado) + [`config/desk.example.yaml`](../../config/desk.example.yaml) |
| Money & Books, Execution Bot | **No** son agentes; cartera vía fixture; `execution_status: disabled` |
| Llaves `{{UNIVERSE}}`, horarios, riesgo | `config/desk.example.yaml` |

## Estado de turnos 24/7

Especificados aquí y en ADR-002 propuesto; **fuera del primer corte vertical** (un solo flujo por evento de mercado). Ver [`tasks/backlog.md`](../../tasks/backlog.md).
