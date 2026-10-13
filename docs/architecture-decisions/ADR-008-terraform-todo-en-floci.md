# ADR-008: Terraform como IaC y toda la infraestructura desplegada en Floci (incluidos ECS y RDS)

- **Estado:** Aceptado
- **Fecha:** 2026-10-13
- **Decisor:** Juan Guevara Bustamante (debate M0-05, T-106)
- **Tradeoffs:** T-011 (antes T-106), T-012 (sustituye a T-007 y T-008)
- **Sustituye:** decisiones 2, 3 y 4 de [ADR-005](./ADR-005-floci-ligero-servicios-y-computo.md). Siguen vigentes sus decisiones 1 (SQS + DLQ + S3) y 5 (esperar al healthcheck de Floci).

## Contexto

- El usuario tiene experiencia en Terraform, prefiere HCL y prioriza la fiabilidad con Floci.
- El usuario pide desplegar todo en Floci, incluidos ECS y RDS, lo que reabre ADR-005 por su condición de revisión (a).
- ADR-005 descartó ECS y RDS por RAM estimada (~1–1,5 GB). Un spike posterior midió mucho menos.

## Evidencia (spike 2026-10-13, Terraform 1.5.7 + `hashicorp/aws ~> 6.0` contra Floci 2.2.0, Mac M4)

| Medida | Resultado |
|--------|-----------|
| Recursos | SQS + DLQ (`redrive_policy`), S3, VPC, subnet, RDS PostgreSQL, clúster ECS, task definition Fargate y servicio ECS: 9 recursos creados y destruidos sin errores |
| Tiempos | `apply` 130 s (RDS 1 min 47 s); `destroy` 99 s |
| RDS | Contenedor real `postgres:16-alpine`, ~32 MiB en reposo, `pg_isready` OK; Floci lo expone vía proxy en el puerto 7001 de su IP en la red de Docker |
| ECS Fargate | Contenedor real, ~4,6 MiB, límite de 512 MiB de la task definition aplicado; Floci inyecta `AWS_ENDPOINT_URL=http://localhost.floci.io:4566` y credenciales de prueba |
| Conectividad desde la tarea ECS | Floci (SQS/S3) OK, proxy de RDS OK, internet (`openrouter.ai:443`) OK |
| RAM de Floci | ~140 MiB con RDS y ECS activos (16 MiB en reposo sin ellos) |
| Fidelidad | Floci rechaza una subnet inexistente igual que AWS (`The subnet ID ... does not exist`); hay que declarar VPC y subnet |
| Requisitos de Floci | Montar `/var/run/docker.sock` y ejecutar como `-u root` para servicios con Docker real |

## Decisión

1. **Terraform** (HCL, provider `hashicorp/aws ~> 6.0`) describe toda la infraestructura y la despliega contra Floci con `endpoints` locales.
2. **Todo se despliega en Floci, también en desarrollo:** SQS + DLQ, S3, VPC/subnet, **RDS PostgreSQL** (base de la app y checkpoints de LangGraph, ADR-006) y **el worker como servicio ECS Fargate**.
3. Floci corre con el socket de Docker montado y la consola web desactivada (`FLOCI_SERVICES_UI_ENABLED=false`) para ahorrar RAM.
4. **Decisión del usuario, riesgo aceptado:** ciclo de desarrollo lento. Cada cambio del worker exige reconstruir la imagen y redesplegar la tarea ECS; crear RDS tarda ~2 min. El agente recomendaba Compose en desarrollo y Floci completo solo en un perfil de demo.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| D. Compose en desarrollo + perfil de demo con todo en Floci | Recomendación del agente; el usuario prefiere una sola forma de ejecutar el sistema |
| A. Mantener ADR-005 (ECS y RDS solo en diseño) | El spike mostró que la RAM no es un obstáculo y el usuario quiere verlos ejecutándose |
| OpenTofu | Mismo HCL; el usuario elige Terraform |
| CDK / Pulumi | Sin experiencia del usuario; Pulumi sin suite oficial de compatibilidad con Floci |

## Consecuencias

- **Pendiente de verificar antes de M3:**
  - Si RDS en Floci es accesible desde el Mac (fuera de Docker) para migraciones y tests; si no, ejecutarlos dentro de la red de Docker.
  - Si ECS en Floci usa una imagen construida localmente sin registro (o si hace falta ECR en Floci).
- Las investigaciones dependen de que la tarea ECS esté corriendo: el healthcheck y los logs de la tarea deben ser visibles (`docker logs` o CloudWatch Logs de Floci).
- Terraform 1.5.7 instalado es la última versión con licencia MPL; actualizar a 1.6+ implica licencia BSL. Decidir al montar M3 (Tipo 2).
- `docs/aws-vs-floci.md` debe documentar el proxy de RDS (puerto 7001), la inyección de `AWS_ENDPOINT_URL` y que Fargate se emula con contenedores Docker.

## Confianza

**Media-alta** — todos los recursos funcionaron en el spike; quedan sin verificar el acceso a RDS desde el host y las imágenes locales en ECS.

## Condición de revisión

Reabrir si: (a) el ciclo de desarrollo lento pone en riesgo el plazo de 2 semanas (pasar a la opción D), (b) RDS o ECS de Floci fallan de forma no reproducible, o (c) el stack supera ~2 GB de RAM en Docker.

## Referencias

- https://floci.io/floci/getting-started/terraform/
- https://github.com/floci-io/floci/blob/main/README.md
- [ADR-005](./ADR-005-floci-ligero-servicios-y-computo.md), [ADR-006](./ADR-006-cola-sqs-worker-checkpointing.md)
