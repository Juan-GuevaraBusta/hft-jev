# AGENTS.md

Instrucciones para agentes de IA que trabajan en este repositorio. El contrato operativo completo está en [`master_prompt.md`](./master_prompt.md).

## Registro de tradeoffs de arquitectura

Después de responder **cualquier pregunta sobre arquitectura** (servicios AWS/Floci, cómputo, cola/worker, LLM, observabilidad, base de datos, IaC, frontend, contratos, etc.), actualiza [`docs/architecture-decisions/tradeoffs.md`](./docs/architecture-decisions/tradeoffs.md):

1. Añade una fila a la tabla **"3. Registro de preguntas de arquitectura"** con fecha, pregunta, respuesta resumida, tradeoffs relacionados y estado.
2. Si la respuesta introduce o cambia un tradeoff, añade o actualiza su fila en la tabla 1 (**Decidido**) o 2 (**Recomendado** / **Abierto**).
3. Solo marca **Decidido** lo que tenga un ADR aceptado en `docs/architecture-decisions/`. Una recomendación del agente no es una decisión.
4. Usa tablas en markdown y mantén los IDs (`T-0xx` decididos, `T-1xx` pendientes) estables; no reutilices IDs.
5. Al cerrar un tema con ADR, mueve su fila de la tabla 2 a la tabla 1 y enlaza el ADR.
