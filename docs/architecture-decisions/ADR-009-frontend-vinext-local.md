# ADR-009: Frontend con vinext, solo en local (sin Cloudflare en el MVP)

- **Estado:** Aceptado
- **Fecha:** 2026-10-13
- **Decisor:** Juan Guevara Bustamante (debate M0-05, T-107)
- **Tradeoffs:** T-013 (antes T-107)

## Contexto

- `master_prompt.md` §7.4 deja abierto vinext frente a alternativas y si desplegar en Cloudflare.
- El usuario tiene experiencia con vinext, prioriza la velocidad de entrega (demo en < 2 semanas) y quiere todo en local.
- El backend corre en Floci en el Mac ([ADR-008](./ADR-008-terraform-todo-en-floci.md)): un frontend en Cloudflare no podría llegar a él.

## Evidencia

| Hecho | Fuente |
|-------|--------|
| vinext 1.1.0 publicado el 2026-10-08; Next.js 16.4.0; Vite 8.3.4 | `npm view` (2026-10-13) |
| vinext requiere Node 22+; el Mac tiene Node 24.12.0 | `docs/verification-fase-a-official-sources.md`; `node --version` |

## Decisión

1. Dashboard con **vinext 1.1**, ejecutado en local.
2. **Cloudflare fuera del MVP:** nada depende de él.
3. Las pantallas se definen al empezar M4.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| Next.js 16 estándar | Más maduro, pero el usuario no lo ha usado; la experiencia previa pesa más para la velocidad |
| React + Vite sin framework | Más simple, pero sin estructura de rutas y datos; el usuario ya domina vinext |
| Despliegue en Cloudflare | El backend local en Floci no sería accesible; sin valor para la demo |

## Consecuencias

- Los huecos de vinext frente a Next.js 16 pueden aparecer en M4; si bloquean algo, se valora cambiar a Next.js estándar (misma API de rutas).
- El frontend llama a la API local; la configuración de CORS y la URL de la API van por variables de entorno.

## Confianza

**Media-alta** — experiencia previa del usuario y versión 1.x; las pantallas aún no están definidas.

## Condición de revisión

Reabrir si: (a) un hueco de vinext bloquea una pantalla de la demo, o (b) se decide exponer la demo fuera del Mac.

## Referencias

- https://www.npmjs.com/package/vinext
- `docs/verification-fase-a-official-sources.md`
