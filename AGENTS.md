# AGENTS.md

Instrucciones para agentes de IA que trabajan en este repositorio. El contrato operativo completo está en [`master_prompt.md`](./master_prompt.md).

## Toda operación se testea; si pasa, se commitea y se pushea

Detalle en la sección 2.10 de [`master_prompt.md`](./master_prompt.md). Tras **cada operación** que modifique el repositorio (código, tests, configuración, infraestructura o documentación):

1. Ejecuta los tests, lint y typecheck relevantes al cambio. Si la operación no tiene un test aplicable (p. ej. solo documentación), ejecuta la verificación disponible (lint de markdown, build, validación de esquema) y dilo.
2. **Si todo pasa:** revisa `git diff --staged` en busca de secretos, haz commit con Conventional Commits y haz push a la rama de trabajo, automáticamente y sin pedir confirmación.
3. **Si algo falla:** no commitees ni pushees. Corrige y vuelve al paso 1, o reporta el fallo con el comando, el código de salida y la salida relevante.
4. El autor del commit es únicamente el usuario con su cuenta de GitHub: sin trailers `Co-authored-by` ni otra atribución a agentes.
5. Nunca pushees directo a `main`, nunca uses `git reset --hard` ni force-push sin confirmación explícita (ver 2.3).

## Registro de tradeoffs de arquitectura

Después de responder **cualquier pregunta sobre arquitectura** (servicios AWS/Floci, cómputo, cola/worker, LLM, observabilidad, base de datos, IaC, frontend, contratos, etc.), actualiza [`docs/architecture-decisions/tradeoffs.md`](./docs/architecture-decisions/tradeoffs.md):

1. Añade una fila a la tabla **"3. Registro de preguntas de arquitectura"** con fecha, pregunta, respuesta resumida, tradeoffs relacionados y estado.
2. Si la respuesta introduce o cambia un tradeoff, añade o actualiza su fila en la tabla 1 (**Decidido**) o 2 (**Recomendado** / **Abierto**).
3. Solo marca **Decidido** lo que tenga un ADR aceptado en `docs/architecture-decisions/`. Una recomendación del agente no es una decisión.
4. Usa tablas en markdown y mantén los IDs (`T-0xx` decididos, `T-1xx` pendientes) estables; no reutilices IDs.
5. Al cerrar un tema con ADR, mueve su fila de la tabla 2 a la tabla 1 y enlaza el ADR.
