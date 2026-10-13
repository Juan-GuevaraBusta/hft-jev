# ADR-011: Veredictos del gate (PASS, FLAG, BLOCK, NEEDS_DATA) y su efecto en la ejecución

- **Estado:** Aceptado
- **Fecha:** 2026-10-13
- **Decisor:** Juan Guevara Bustamante (debate M0-05, T-109)
- **Tradeoffs:** T-015 (antes T-109)
- **Modifica:** requisito duro "gate = `PASS`" de [ADR-004](./ADR-004-decision-score-umbrales-limites-riesgo.md) §1, que pasa a "gate ∈ {`PASS`, `FLAG`}"

## Contexto

- [ADR-002](./ADR-002-research-desk-orchestration.md) propone cuatro veredictos para el Deterministic Gate; ADR-004 solo permite órdenes con `PASS`.
- El usuario quiere que un `FLAG` llegue a aprobación humana y que un `NEEDS_DATA` espere al dato y se reanude solo.

## Decisión

| Veredicto | Significado | Efecto |
|-----------|-------------|--------|
| `PASS` | Todo verificado | Sigue ADR-004: score < 0.40 rechazo en sombra; 0.40–0.75 aprobación humana; ≥ 0.75 envío automático (solo en paper) |
| `FLAG` | Dudas no bloqueantes (p. ej. contradicción menor, evidencia débil) | Cumple el requisito duro. Score < 0.40 → rechazo en sombra; score ≥ 0.40 → **siempre aprobación humana**, nunca envío automático. El memo muestra los motivos del FLAG |
| `BLOCK` | Falla una regla dura (p. ej. orden que supera `money_rules`, alerta sin fuente) | Sin orden (`execution_status: "disabled"`, `ticket: "NO_TICKET"`). El memo se publica con los motivos |
| `NEEDS_DATA` | Falta un dato obligatorio (p. ej. cartera, filing, precio) | La investigación espera en la cola `research-jobs-data-wait` y se reanuda sola (ver abajo) |

**Espera de `NEEDS_DATA`:**

1. El worker guarda el checkpoint (ADR-006), registra qué dato falta y la hora límite (**24 h** desde el primer `NEEDS_DATA`, igual que `money_rules.staleness_hours`) y envía la investigación a `research-jobs-data-wait`.
2. Un programa periódico de EventBridge Scheduler (**cada 30 min**) invoca la misma Lambda de reenvío de [ADR-010](./ADR-010-lambda-reenvio-cuota.md), con origen `data-wait` y destino `research-jobs`.
3. El worker retoma desde el paso que obtiene el dato. Ese paso es determinista y **no consume cuota de OpenRouter**. Si el dato llegó, sigue el flujo; si no, vuelve a `data-wait`.
4. Pasada la hora límite, la investigación termina como **caducada**, sin orden.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| FLAG sin orden (mantener ADR-004 sin cambios) | El usuario quiere decidir él en los casos dudosos |
| FLAG siempre a aprobación humana, aunque score < 0.40 | Llenaría la cola de aprobación con casos de baja calidad; se pierde el seguimiento en sombra |
| FLAG como PASS con penalización en el score | Permitiría envío automático con dudas abiertas |
| NEEDS_DATA termina y se relanza a mano | El usuario quiere reanudación automática |
| Vocabulario de 3 o 2 veredictos | El usuario mantiene los cuatro |

## Consecuencias

- ADR-004 §1 queda modificado: requisito duro "gate ∈ {`PASS`, `FLAG`}"; el resto de requisitos duros no cambia.
- El dashboard (M4) debe mostrar la cola de aprobación humana con los motivos del FLAG y las investigaciones en espera de datos con el dato que falta.
- Nuevos parámetros de configuración (en `config/desk.yaml` al implementar): espera máxima de `NEEDS_DATA` (24 h) y frecuencia de reintento (30 min).
- Tests requeridos: un caso por veredicto; FLAG con score ≥ 0.75 nunca envía automático; NEEDS_DATA caduca a las 24 h.

## Confianza

**Alta** en la semántica (reglas deterministas). **Media** en la espera de datos: el mecanismo reutiliza piezas probadas (Scheduler, Lambda, SQS, checkpoints), pero el paso que detecta el dato aún no existe.

## Condición de revisión

Reabrir si: (a) la cola de aprobación humana recibe tantos FLAG que se vuelve inmanejable, (b) los datos que faltan casi nunca llegan en 24 h, o (c) la calibración de ADR-004 muestra que los FLAG aprobados rinden peor que los rechazados.

## Referencias

- [ADR-002](./ADR-002-research-desk-orchestration.md), [ADR-004](./ADR-004-decision-score-umbrales-limites-riesgo.md), [ADR-006](./ADR-006-cola-sqs-worker-checkpointing.md), [ADR-010](./ADR-010-lambda-reenvio-cuota.md)
