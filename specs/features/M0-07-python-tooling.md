# M0-07: Python Tooling — `pyproject.toml`, Ruff, pytest y Makefile mínimo

> Issue: [#46](https://github.com/Juan-GuevaraBusta/hft-jev/issues/46)  
> Milestone: M0 (épica [#17](https://github.com/Juan-GuevaraBusta/hft-jev/issues/17))  
> Compuerta: APROBADA 2026-10-13

## Objetivo

Configurar el esqueleto del proyecto Python con gestor `uv`, linter/formatter Ruff, type checker mypy en modo `strict`, tests con pytest, y un Makefile mínimo con comandos que funcionan hoy.

## Alcance

**Incluye:**
- `pyproject.toml` con metadatos, `requires-python = ">=3.12,<3.13"`, build backend, grupo `dev`
- `uv.lock` y `.python-version`
- `backend/src/hft_jev/__init__.py` con `__version__` y `py.typed`
- `backend/tests/unit/test_smoke.py`: importa `hft_jev` y valida `__version__` (marcado `unit`)
- Configuración de Ruff, mypy, pytest, coverage en `pyproject.toml`
- `Makefile` con targets: `setup`, `lint`, `format`, `typecheck`, `test`, `test-unit`, `help`
- `.gitignore`: añadir entradas si faltan
- README: sección "Cómo ejecutar" con comandos reales; estado actualizado

**NO incluye:**
- CI/GitHub Actions (M6)
- compose/Floci (M3)
- Frontend (M4)
- pre-commit
- Código de dominio, FastAPI, LangGraph, Alpaca
- Dependencias no aprobadas

## Criterios de aceptación

1. `uv sync` instala el entorno y las dependencias de desarrollo sin error.
2. `uv sync` produce `uv.lock` commiteable.
3. `make lint` ejecuta `ruff check` y `ruff format --check` y pasa en verde.
4. `make typecheck` ejecuta `mypy --strict` y pasa en verde.
5. `make test` ejecuta pytest con cobertura y pasa en verde.
6. `make test-unit` ejecuta solo tests marcados `unit`.
7. El smoke test (`test_smoke.py`) falla antes de que exista el paquete (TDD: RED → GREEN).
8. Prueba negativa: introducir un error de tipo y un import sin usar → `make typecheck` y `make lint` FALLAN.
9. `make help` lista todos los targets con descripción.
10. `README.md` incluye "Cómo ejecutar" con los comandos reales verificados.
11. `tasks/backlog.md`: M0-07 → DONE con hash del commit y fecha.

## Comandos de verificación

```bash
# Setup limpio
rm -rf .venv && make setup
# Lint
make lint
# Type check
make typecheck
# Tests
make test
make test-unit
```

### Prueba negativa

```bash
# Introducir error temporal, verificar fallo, revertir
make lint && echo "FAIL: debió fallar" || echo "OK: lint detectó el error"
make typecheck && echo "FAIL: debió fallar" || echo "OK: mypy detectó el error"
```

## Decisiones (cerradas, no reabrir)

| Decisión | Valor |
|---|---|
| Gestor | `uv` (con `uv.lock` commiteado) |
| Python | 3.12 (`requires-python = ">=3.12,<3.13"`, `.python-version = 3.12`) |
| Type checker | mypy en modo `strict` |
| Layout | `backend/src/hft_jev/`, tests en `backend/tests/` |
| Dependencias dev | ruff, pytest, pytest-cov, mypy (ninguna otra sin preguntar) |
| Build backend | `hatchling` (propuesto por `uv init --package`, estándar, ligero) |
| Linter | Ruff con reglas `E, F, W, I, B, UP, S, N, SIM, RUF` |
| Seguridad | Bandit (S) integrado vía Ruff |
| Line length | 100 |