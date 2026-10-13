# M1-T02: Fixtures de evento y loader de desk.yaml

> Issue: [#48](https://github.com/Juan-GuevaraBusta/hft-jev/issues/48)  
> Milestone: M1 (corte vertical determinista)  
> Compuerta: OMITIDA por el usuario 2026-10-13 (admitido una vez, §4.9.5)

## Objetivo

Validar por código el contrato del desk (`config/desk.example.yaml` → modelo
`DeskConfig` con Pydantic, solo `yaml.safe_load`) y disponer de fixtures JSON
de evento (8-K, 10-Q, 10-K + inválidas) que parseen al `FilingEvent` de M1-T01.
Suelo determinista de M2: si el YAML o el evento están mal formados, el fallo
es claro y temprano, no un comportamiento silencioso en el grafo.

## Alcance

**Incluye:**
- `backend/src/hft_jev/desk_config.py`: `DeskConfig` + `load_desk_config`.
- `backend/src/hft_jev/events.py`: STUB temporal de `FilingEvent` (excepción
  aprobada Q1; M1-T01 lo reemplaza, Refs #47).
- `backend/tests/fixtures/events/`: 3 válidas + 2 inválidas, sintéticas.
- `config/desk.example.yaml`: `enabled: true` en ambos turnos (Q4 aprobado).
- `pyproject.toml` + `uv.lock`: `pydantic>=2.12`, `pyyaml>=6.0` (Q5).

**NO incluye:** LangGraph, Floci, UI, SEC real, LLM, gate, score, FastAPI,
broker, IDs de modelo, ejecución de turnos (aquí solo se valida forma).

## Decisiones del usuario (sesión 2026-10-13)

| # | Decisión |
|---|---|
| Q1 | Stub mínimo de `FilingEvent`, etiquetado temporal, a reemplazar por T01 |
| Q2 | El modelo se llama `FilingEvent` ("FillingEvent" era errata) |
| Q3 | Reutilizar `desk_limits.max_artifacts_for_review_per_day` (=3, ADR-012); sin campo nuevo, sin Tipo 1 |
| Q4 | `night_ingest` y `morning_desk` a `enabled: true` en el ejemplo. Riesgo registrado: §9 del master prompt deja los turnos fuera del primer corte; activar los flags no implementa turnos pero cambia el contrato visible de M2 |
| Q5 | Sin pin preferido; elegidas `pydantic>=2.12`, `pyyaml>=6.0` (probadas 2.12.5 / 6.0.3) |
| Q6 | JSON sintético etiquetado (`synthetic: true` en archivo y modelo) |
| Q7 | Ambigua ("Sí" a disyuntiva) + compuerta saltada → opción (a) conservadora: placeholders `{{SEC_CONTACT_*}}` válidos como string; no se reescribe el estilo del ejemplo. Exigir email real queda diferido |
| Q8 | `extra="forbid"` en todo el documento, incluidos mapas anidados |

## Contratos

- **Válido:** YAML que tras `yaml.safe_load` pasa `DeskConfig` sin coerción
  silenciosa (`strict=True` + `extra="forbid"` en raíz y secciones).
- **Rangos (ADR-004):** porcentajes como fracción en [0, 1]; conteos enteros
  ≥ 1; `reject_threshold < auto_threshold` (0.40 / 0.75 en el ejemplo).
  Todo fallo nombra campo y valor en el mensaje.
- **Turnos:** solo `night_ingest` / `morning_desk`; cron de 5 campos;
  `local_time` HH:MM 24h. Clave extra o formato inválido falla con mensaje claro.
- **Fixtures:** `form` ∈ {8-K, 10-Q, 10-K} (ADR-012: Form 4 no dispara);
  `symbol` no vacío; `synthetic: true` obligatorio en archivo y modelo.

## Criterios de aceptación

1. `config/desk.example.yaml` carga sin error (test sobre el archivo real).
2. Campo desconocido (raíz y anidado) falla nombrando la clave.
3. Umbral/límite fuera de rango falla nombrando campo y valor.
4. `reject_threshold >= auto_threshold` falla.
5. Turno/cron/hora inválidos fallan con mensaje claro.
6. Loader llama a `yaml.safe_load` exactamente 1 vez (spy); tag
   `!!python/object` es rechazado (prueba conductual anti-`yaml.load`).
7. 3 fixtures válidas parsean a `FilingEvent`; 2 inválidas fallan.
8. `make test-unit`, `make lint`, `make typecheck` en verde.
9. `rg "yaml\.load\b" backend/src` sin `yaml.load` (solo `safe_load`).

## Comandos de verificación

```bash
make test-unit
make lint
make typecheck
rg "yaml\.load\b" backend/src hft_jev 2>/dev/null; rg "[^_]load\(" backend/src/hft_jev/desk_config.py
```

## Test que tumba el diseño

Quitar `test_loads_example_yaml_without_error` (carga del archivo real, no de
un dict copiado a mano): el loader podría validar un subconjunto y el ejemplo
—contrato de M2— dejaría de estar cubierto.
