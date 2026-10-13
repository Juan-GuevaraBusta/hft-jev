# ADR-005: Floci ligero (SQS + DLQ + S3); PostgreSQL y worker como contenedores de Compose

- **Estado:** Aceptado; decisiones 2, 3 y 4 sustituidas por [ADR-008](./ADR-008-terraform-todo-en-floci.md) (2026-10-13)
- **Fecha:** 2026-10-13
- **Decisor:** Juan Guevara Bustamante (elección explícita de la opción A en el debate M0-05)
- **Tradeoffs:** T-007 (antes T-101), T-008 (antes T-102)

## Contexto

- Floci es obligatorio para emular AWS en local (`master_prompt.md` §0); se debate el cómo, no el si.
- Máquina: Apple M4, 16 GB RAM; VM de Docker con 7,75 GiB. Otros proyectos ocupan ~2,5 GiB en Docker; el usuario acepta apagarlos mientras trabaja en hft-jev.
- Requisitos del usuario para la demo: varias investigaciones en paralelo, reintento automático si una falla, demo en menos de 2 semanas.

## Criterios relevantes

| Criterio | Peso (usuario) |
|----------|----------------|
| Demostrabilidad ante el jurado | Alto (único criterio elegido) |
| RAM local baja | Alto (motivo del debate) |
| Velocidad de entrega (< 2 semanas) | Alto (implícito por el plazo) |

## Evidencia (spike 2026-10-13, en la máquina del usuario)

| Medida | Resultado |
|--------|-----------|
| Imagen | `floci/floci:latest` = Floci 2.2.0, binario nativo arm64 (~83 MB) |
| RAM en reposo | ~16 MiB |
| RAM tras crear cola + DLQ + bucket y enviar 500 mensajes | ~63 MiB |
| Arranque | ~15,6 s (el README dice ~24 ms; no se cumple en este Mac) |
| SQS + DLQ con `boto3` | El mensaje no borrado se entregó 2 veces y pasó a la DLQ (`maxReceiveCount=2`) |
| S3 con `boto3` | `create_bucket`, `put_object` y `get_object` correctos |

## Decisión

1. **Floci emula solo servicios in-process:** SQS (cola de investigaciones + DLQ) y S3 (artefactos). Se añaden otros servicios in-process solo con justificación.
2. **PostgreSQL** corre como contenedor propio de Compose, no como RDS en Floci.
3. **El worker** corre como contenedor de larga duración en Compose que consume SQS. En el diseño AWS e IaC se describe como ECS/Fargate.
4. **RDS, ECS y Lambda de Floci no se usan en el MVP**: levantan contenedores reales y suben la RAM.
5. La API y el worker esperan al healthcheck de Floci antes de arrancar (arranque medido de ~15 s).

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| B. Floci completo (worker en ECS y base en RDS dentro de Floci) | Más RAM (~1–1,5 GB estimado) y ECS/RDS emulados sin probar en el Mac; más superficie de fallo en la demo con plazo < 2 semanas |
| C. Mínimo (Floci solo S3; cola en PostgreSQL) | Pierde SQS y la DLQ, justo lo más demostrable, y los reintentos que pidió el usuario |
| D. A + perfil de demo con worker como tarea ECS en Floci | Dos perfiles que mantener; queda como extensión si sobra tiempo |

## Consecuencias

- Código con `boto3` y `endpoint_url` configurable (`http://localhost:4566` en local).
- Presupuesto de RAM estimado para el stack: ~0,6–0,8 GB (Floci medido; PostgreSQL, API y worker estimados).
- La demo muestra SQS, DLQ y S3 corriendo; ECS/Fargate y RDS se muestran en el diagrama y la IaC, sin ejecutarse.
- `docs/aws-vs-floci.md` debe documentar que ECS/RDS no se ejecutan emulados y que la paridad con AWS real no está verificada.

## Confianza

**Alta** para SQS, DLQ y S3 en esta máquina (medido). **Media** para el presupuesto total de RAM (estimado).

## Condición de revisión

Reabrir si: (a) el jurado o el usuario exige ver ECS o RDS ejecutándose (pasar a la opción D), (b) Floci falla en SQS/S3 durante el desarrollo, o (c) el stack supera ~2 GB de RAM en Docker.

## Referencias

- https://github.com/floci-io/floci/blob/main/README.md
- https://hub.docker.com/r/floci/floci
- `docs/verification-fase-a-official-sources.md` §2
