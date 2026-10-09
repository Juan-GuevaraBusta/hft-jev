# Verificación Fase A — fuentes oficiales y compatibilidad

> **Fecha de consulta:** 2026-10-09 (zona del usuario: UTC-5).  
> **Alcance:** Sección 23.3 del `master_prompt.md`. Sin ejecutar spikes en este documento salvo donde se indique.  
> **Leyenda de incertidumbre:** **Alta** = no verificado en este entorno; **Media** = documentado pero no probado aquí; **Baja** = alineado con docs oficiales y coherente con el entorno diagnosticado.

---

## 1. Resumen ejecutivo

| Tema | Conclusión preliminar para el MVP | Incertidumbre |
|------|-----------------------------------|---------------|
| **Floci** | Emulador AWS local MIT, endpoint `http://localhost:4566`; SQS (DLQ), S3, RDS y ECS documentados; IaC vía Terraform/OpenTofu/CDK con suites oficiales | Media–alta en paridad AWS real y en comportamiento en tu Mac (spike pendiente) |
| **LangSmith** | Para demo con costo ~$0: **SaaS Developer** (cuenta + API key); trazas salen de la máquina | Baja en límites del plan; media en volumen real del grafo |
| **Langfuse** | **Cloud Hobby** (50k unidades/mes) o **self-host Docker** (MIT, sin límite de unidades en OSS) encajan con “nube OK” | Baja en opciones; media en recursos RAM en Compose |
| **LangGraph** | Checkpointing producción: `PostgresSaver` (`langgraph-checkpoint-postgres`); integración trazas vía `LANGSMITH_*` | Baja |
| **vinext** | Viable en local con Node 22+; proyecto Cloudflare en desarrollo activo; gaps vs Next.js 16 documentados | Media en madurez y en dashboard del MVP |
| **IaC** | Terraform/OpenTofu/CDK **verificados** por Floci; Pulumi vía provider AWS + endpoint local, sin suite dedicada | Media en Pulumi para recursos concretos del diseño |
| **Jev (TypeSafe AI)** | API HTTP documentada (`POST /v1/systemone`); **no es LLM**; uso implica llamadas a `api.typesafe.ai` (de pago por token) | Baja en API; alta en encaje MVP sin presupuesto |

**Entorno local diagnosticado (2026-10-09):** macOS arm64, Python **3.12.15**, Node **24.12.0**, Docker **29.7.2** (daemon activo), Git/gh OK. Runtime Python del proyecto acordado: **3.12**.

---

## 2. Floci

### 2.1 Hechos verificados (fuentes)

| Hecho | Fuente |
|-------|--------|
| Repositorio activo: `floci-io/floci`; `hectorvent/floci` obsoleto | [README floci-io/floci](https://github.com/floci-io/floci/blob/main/README.md) |
| Licencia MIT; sin cuenta ni token; endpoint único `localhost:4566` | [floci.io](https://floci.io/floci/), README |
| Imagen Docker `floci/floci`; tags `latest`, versiones pinneadas (`1.5.x` en CHANGELOG) | [CHANGELOG](https://github.com/floci-io/floci/blob/main/CHANGELOG.md) — última entrada consultada: **1.5.32 (2026-07-11)** |
| Persistencia configurable: `memory`, `persistent`, `hybrid`, `wal`; bind mount `./data:/app/data` en quick start | README / docs de almacenamiento |
| **SQS:** colas standard/FIFO, **DLQ**, visibility timeout, batch, tagging (tabla de servicios) | README (services overview) |
| **S3**, **IAM**, **SQS**, **SNS**, **Lambda** (in-process), etc. | README |
| **RDS:** “Real Docker” — PostgreSQL, MySQL, MariaDB | README |
| **ECS:** “Real Docker” — clusters, task definitions, tasks, services | README |
| Terraform/OpenTofu: provider `hashicorp/aws` contra endpoint local; backend S3 + DynamoDB lock en Floci | [Terraform with Floci](https://floci.io/floci/getting-started/terraform/) |
| Suites de compatibilidad: Terraform AWS provider ~6, OpenTofu ~5, CDK v2 | [floci-compatibility-tests](https://github.com/floci-io/floci-compatibility-tests) |

### 2.2 Inferencias (no probadas en hft-jev aún)

- En **Apple Silicon**, Floci corre como contenedor; no hay en la doc consultada una garantía explícita “certified arm64” — asumir imagen multi-arch o emulación hasta `docker pull` + spike (**incertidumbre: media**).
- **Paridad con AWS real:** la propia documentación compara con LocalStack y lista servicios “Real Docker” vs “In-process”; no sustituye pruebas contra AWS (que este proyecto **no hará**) (**incertidumbre: alta** para afirmaciones de producción).
- **Fargate** como concepto de diseño AWS puede mapearse a ECS tasks en Floci; no se verificó un despliegue Fargate idéntico (**incertidumbre: media**).

### 2.3 Implicación para el diseño hft-jev

- Código con `endpoint_url` / variables de entorno apuntando a Floci.
- PostgreSQL de la app: contenedor **propio** en Compose es razonable; RDS en Floci es opcional para acercarse al diseño AWS.
- Documentar diferencias en `docs/aws-vs-floci.md` (planificado).

---

## 3. LangSmith

### 3.1 Hechos verificados

| Hecho | Fuente |
|-------|--------|
| Plan **Developer** $0/asiento: **5 000 trazas base/mes**, 1 asiento, retención base **14 días** | [Pricing LangSmith](https://www.langchain.com/pricing-langsmith) |
| Sin método de pago: tope mensual **5 000 trazas** (429 al exceder) | [Usage and billing](https://docs.langchain.com/langsmith/usage-and-billing) |
| Trazas = runs/spans; agentes con herramientas consumen muchas trazas por run | Docs + práctica documentada en billing |
| Integración LangGraph: `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY`, opcional `LANGSMITH_PROJECT` | [LangGraph observability](https://docs.langchain.com/oss/python/langgraph/observability), [Trace with LangGraph](https://docs.langchain.com/langsmith/trace-with-langgraph) |
| **Self-host Docker:** orientado a dev/test; requiere **`LANGSMITH_LICENSE_KEY`** (Enterprise); ~4 vCPU / 16 GB RAM recomendados; UI ~`localhost:1980` | [Self-hosted LangSmith](https://docs.langchain.com/langsmith/self-hosted), [helm docker-compose .env.example](https://github.com/langchain-ai/helm/blob/main/charts/langsmith/docker-compose/.env.example) |

### 3.2 Qué sale de tu máquina (SaaS)

- Payloads de **trazas** (inputs/outputs de nodos, metadatos, errores, tokens si el proveedor los expone) hacia la región LangSmith configurada.
- **Minimización:** no enviar secretos ni contenido fuente completo; usar datos sintéticos en evals; etiquetar runs de demo.

### 3.3 Si no está disponible

- Master prompt: tests con trazadores mock; **demo oficial** usa LangSmith real.
- Degradación propuesta a debatir (Tipo 1): logs locales + warning vs fallo cerrado.

**Incertidumbre:** baja en planes; media en conteo de trazas del grafo completo del MVP.

---

## 4. Langfuse

### 4.1 Hechos verificados

| Hecho | Fuente |
|-------|--------|
| **Self-host OSS:** MIT, funcionalidades core sin límite de unidades en self-host | [Self-Hosted Pricing](https://langfuse.com/pricing-self-host), [Self-host docs](https://langfuse.com/docs/deployment/self-host) |
| **Docker Compose:** oficial; recomendación ~4 cores / 16 GiB; puertos **3000** (web) y **9090** (MinIO) | [Docker Compose](https://langfuse.com/self-hosting/docker-compose) |
| Tras pull inicial, puede operar **sin llamadas salientes** (air-gap posible con mirror de imágenes) | [Handbook open source](https://langfuse.com/handbook/chapters/open-source) |
| **Cloud Hobby:** gratis, sin tarjeta; **50 000 unidades/mes**; 30 días de acceso a datos; 2 usuarios | [Cloud pricing](https://langfuse.com/pricing) |
| Límites API ingestion Hobby: p. ej. **1 000 req/min** en bucket Tracing | [API limits FAQ](https://langfuse.com/faq/all/api-limits) |

### 4.2 Qué sale de tu máquina

- **Cloud:** eventos de trazas, scores, datasets/experimentos según SDK.
- **Self-host:** solo tráfico que tú configures (p. ej. ninguno hacia Langfuse Cloud si es 100 % local).

### 4.3 Rol vs LangSmith (para debatir, no cerrado)

- **Hecho documental:** ambos pueden observar LLM/apps; el master prompt asigna LangSmith a trazas de grafo y Langfuse a datasets/experimentos/scores.
- **Inferencia:** correlación vía `research_id` en metadatos de ambos lados.

**Incertidumbre:** baja en despliegue; media en convivencia con Supabase local ya en puertos 54321+ (planificar puertos Langfuse).

---

## 5. LangGraph — persistencia y LangSmith

### 5.1 Checkpointing (hechos)

| Componente | Uso | Fuente |
|------------|-----|--------|
| `InMemorySaver` | Solo debug/tests | [Checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers) |
| `PostgresSaver` / `AsyncPostgresSaver` | Producción, historial de checkpoints | [Checkpoints reference](https://reference.langchain.com/python/langgraph/checkpoints), [checkpoint-postgres](https://github.com/langchain-ai/langgraph/tree/main/libs/checkpoint-postgres) |
| `thread_id` | Identificador de hilo; mantener &lt; 255 caracteres en Postgres | [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) |
| Setup | Llamar `.setup()` al crear tablas | checkpoint-postgres README |

### 5.2 Integración LangSmith (hechos)

- Misma variable de entorno que LangChain: `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`.
- Proyecto opcional: `LANGSMITH_PROJECT`.
- En LangChain 1.x preferir prefijo `LANGSMITH_*` frente a `LANGCHAIN_TRACING_V2` (documentación de migración / observability).

**Incertidumbre:** baja.

---

## 6. vinext (frontend)

### 6.1 Hechos verificados

| Hecho | Fuente |
|-------|--------|
| Mantenedor: **Cloudflare**; docs en [vinext.dev](https://vinext.dev/docs) | [GitHub cloudflare/vinext](https://github.com/cloudflare/vinext) |
| Reimplementa API Next.js sobre **Vite**; despliegue nativo Workers; también Node standalone / Nitro | README vinext |
| Nuevo proyecto: `pnpm create vinext-app@latest`; **Node.js 22+** requerido | [Installation](https://vinext.dev/docs/getting-started) |
| Migración: `npx vinext check`, `vinext init`; scripts paralelos `dev:vinext` sin borrar Next | [Migrating](https://vinext.dev/docs/getting-started/migrating) |
| Gaps documentados: Cache Components, PPR, optimización build-time de imágenes/fuentes incompleta | [Differences from Next.js](https://vinext.dev/docs/reference/differences) |

### 6.2 Entorno hft-jev

- Node **24.12.0** cumple requisito 22+ (**incertidumbre: baja**).
- Master prompt: todo local → Cloudflare **no requerido** para MVP; vinext local con `pnpm dev` / `vinext dev` (**debate Tipo 1 pendiente**).

**Incertidumbre:** **media** en estabilidad para dashboard de investigación completo.

---

## 7. Infraestructura como código (Floci)

### 7.1 Hechos verificados

| Herramienta | Evidencia |
|-------------|-----------|
| **Terraform** | Guía oficial Floci + módulo `compat-terraform` (init/plan/apply/destroy) |
| **OpenTofu** | Módulo `compat-opentofu` |
| **AWS CDK** | Módulo `compat-cdk` con `cdklocal` |
| **Pulumi** | No aparece en compatibility-tests; issues en `floci-io/floci` muestran uso con AWS provider y correcciones por API (p. ej. Firehose tags) — **inferencia:** viable con `aws:endpoint` / configuración equivalente al provider AWS, validar por recurso |

### 7.2 Pulumi + Python (master prompt)

- Pulumi AWS Python sigue siendo candidato para **describir** infra AWS; despliegue contra Floci = endpoint local + credenciales ficticias.
- **Incertidumbre:** media hasta spike `pulumi up` con SQS+S3 mínimos.

---

## 8. Jev (TypeSafe AI) — opcional

### 8.1 Hechos verificados

| Hecho | Fuente |
|-------|--------|
| **Jev** = modelo “System One”; decisiones estructuradas, no generación de texto | [Introduction](https://docs.typesafe.ai/introduction) |
| API: `POST https://api.typesafe.ai/v1/systemone`, modelo `jev-latest` → `jev-1.13.0` | [API reference](https://docs.typesafe.ai/api), [Models](https://docs.typesafe.ai/models) |
| Precio publicado: orden de **$0.042 / Mtok** (ver tabla en Models) | docs.typesafe.ai/models |
| No sustituye al LLM del agente ni al coding agent | [Jev with coding agents](https://docs.typesafe.ai/introduction/coding-agents) |

### 8.2 Implicación MVP

- Con **OpenRouter gratuito** y presupuesto $0, Jev **añade costo y dependencia externa** salvo mock/adaptador.
- Master prompt: interfaz `DecisionEvaluator` + mock si no se integra API real.

**Incertidumbre:** baja en documentación; **alta** en prioridad para demo.

---

## 9. OpenRouter (decisión de arranque del usuario)

No verificado en profundidad en este informe (pendiente spike): límites del tier gratuito, política de privacidad y modelos disponibles en [openrouter.ai](https://openrouter.ai). **Incertidumbre: alta** hasta consulta explícita de docs + prueba con clave.

---

## 10. Matriz rápida: obligatorio vs cómo (debate Tipo 1)

| Obligatorio | Opciones documentadas | Recomendación pre-debate |
|-------------|----------------------|---------------------------|
| LangGraph | Postgres checkpointer + grafo explícito | PostgresSaver + PG en Compose |
| LangSmith | SaaS Developer vs self-host con licencia | **Decidido:** SaaS — ver ADR-001 |
| Langfuse | Cloud Hobby vs Docker local | **Decidido:** Cloud — ver ADR-001 |
| LLM demo | OpenRouter / local / mock | **Decidido:** OpenRouter (tier free) — ver ADR-001 |
| AWS diseño | Floci + contenedores propios | SQS/S3 Floci; PG app en contenedor dedicado |
| Frontend | vinext local vs Next estándar | vinext si aceptas riesgo madurez |

---

## 11. Fuentes consultadas (índice)

- Floci: https://github.com/floci-io/floci , https://floci.io/floci/ , https://floci.io/floci/getting-started/terraform/
- LangSmith: https://www.langchain.com/pricing-langsmith , https://docs.langchain.com/langsmith/usage-and-billing , https://docs.langchain.com/langsmith/self-hosted , https://docs.langchain.com/oss/python/langgraph/observability
- Langfuse: https://langfuse.com/pricing , https://langfuse.com/pricing-self-host , https://langfuse.com/self-hosting/docker-compose
- LangGraph: https://docs.langchain.com/oss/python/langgraph/checkpointers , https://docs.langchain.com/oss/python/langgraph/persistence
- vinext: https://vinext.dev/docs , https://github.com/cloudflare/vinext
- Jev: https://docs.typesafe.ai/introduction , https://docs.typesafe.ai/api
- IaC Floci: https://github.com/floci-io/floci-compatibility-tests

---

## 12. Próximo paso (Fase A)

1. **§23.4** — Lista y orden de debates Tipo 1 (tu aprobación).
2. **§23.5** — Debates por rondas (4.3).
3. Spike acotados sugeridos: Floci SQS+DLQ en arm64; pull imagen `floci/floci:1.5.32`; OpenRouter free tier.
