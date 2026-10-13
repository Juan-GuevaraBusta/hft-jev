# ADR-012: Turnos noche/mañana en el MVP, disparo por filings materiales y "reprocesar filing"

- **Estado:** Aceptado
- **Fecha:** 2026-10-13
- **Decisor:** Juan Guevara Bustamante (debate M0-05, T-110)
- **Tradeoffs:** T-016 (antes T-110)

## Contexto

- `config/desk.example.yaml` define `night_ingest` (16:30 ET, lun–vie: filings de la SEC y calendario de resultados) y `morning_desk` (09:00 ET), ambos desactivados; ADR-002 los dejaba para después del primer corte vertical.
- El usuario quiere ambos turnos en la demo, con investigaciones disparadas por filings nuevos y un tope de 3 automáticas al día.
- Cuota de OpenRouter: 50 peticiones/día, ≥ 5 por investigación ([ADR-007](./ADR-007-cinco-agentes-llm-cuota-openrouter.md)).

## Evidencia (SEC EDGAR submissions API, consultada 2026-10-13)

| Símbolo | Filings en 90 días | Materiales (8-K, 10-Q) | Resto |
|---------|--------------------|------------------------|-------|
| NVDA | 29 | 4 | 16 Form 4, 4 Form 144, otros |
| SPY | 1 | 0 | 1 NPORT-P |

Conclusión: con solo filings materiales hay ~1 evento cada 3 semanas; con todos, el ruido (Form 4) agotaría el tope.

## Decisión

1. **Ambos turnos entran en el MVP**, disparados por EventBridge Scheduler (cron en `America/New_York`):
   - `night_ingest` (16:30 ET, lun–vie): sin LLM. Descarga los filings nuevos del universo desde SEC EDGAR y guarda los **materiales** (8-K, 10-Q, 10-K) como pendientes.
   - `morning_desk` (09:00 ET): encola una investigación por filing material pendiente, **máximo 3 al día**.
2. **Solo disparan filings materiales:** 8-K, 10-Q y 10-K. Form 4, 144 y demás se ignoran.
3. **"Reprocesar filing":** acción manual (API y dashboard) que lanza el mismo flujo sobre un filing real ya publicado, como si acabara de llegar. No cuenta para el tope automático, pero sí consume cuota de OpenRouter.
4. **Universo sin cambios:** SPY y NVDA. SPY casi no genera eventos; sigue como benchmark.
5. Las peticiones a SEC EDGAR llevan `User-Agent` con contacto (`sec_contact` en `config/desk.yaml`).

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| Turnos después de la demo | El usuario los quiere en la demo |
| Disparar con Form 4 o con todos los filings | Ruido: agotaría el tope de 3/día con operaciones de directivos |
| Solo eventos reales, sin reprocesar | Alta probabilidad de una demo sin eventos |
| Lanzamiento manual libre (cualquier ticker o texto) | El usuario prefiere mantener el flujo por eventos con datos reales |
| Ampliar el universo a ~10 acciones | El usuario mantiene SPY y NVDA |

## Consecuencias

- Presupuesto diario: 3 investigaciones automáticas ≈ 15 peticiones; quedan ~35 para reprocesar, evals y reintentos.
- Los filings detectados un viernes por la noche se investigan el lunes a las 09:00 ET (no hay `morning_desk` en fin de semana); comprobar que su antigüedad no choca con `staleness_hours` (24 h) del gate, o el gate devolverá `NEEDS_DATA`/`BLOCK`. **Resolver en la spec de M1.**
- **Pendiente de verificar:** si EventBridge Scheduler en Floci puede tener SQS como destino directo (solo se probó con Lambda, [ADR-010](./ADR-010-lambda-reenvio-cuota.md)) y si respeta la zona horaria `America/New_York`.
- El calendario de resultados (`earnings_calendar`) necesita una fuente de datos aún no elegida; si no hay una gratuita, `night_ingest` cubre solo filings.

## Confianza

**Media** — el disparo y el filtro son deterministas y simples; quedan sin verificar el destino SQS del Scheduler en Floci, la zona horaria y la fuente del calendario de resultados.

## Condición de revisión

Reabrir si: (a) la frecuencia real de filings materiales deja la demo sin eventos y "reprocesar" no basta, (b) el tope de 3/día resulta insuficiente o excesivo para la cuota, o (c) no hay fuente gratuita fiable del calendario de resultados.

## Referencias

- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- `config/desk.example.yaml`
- [ADR-002](./ADR-002-research-desk-orchestration.md), [ADR-007](./ADR-007-cinco-agentes-llm-cuota-openrouter.md), [ADR-010](./ADR-010-lambda-reenvio-cuota.md), [ADR-011](./ADR-011-veredictos-gate.md)
