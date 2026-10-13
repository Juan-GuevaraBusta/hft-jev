# ADR-004: Fórmula de `decision_score`, umbrales y límites de riesgo

- **Estado:** Aceptado
- **Fecha:** 2026-10-13
- **Decisor:** Juan Guevara Bustamante (aprobación explícita en chat de sesión)
- **Relacionado:** [ADR-003](./ADR-003-broker-alpaca-ejecucion-por-umbrales.md), `master_prompt.md` §5.1 y §10, issue [#24](https://github.com/Juan-GuevaraBusta/hft-jev/issues/24) (M0-05)

## Contexto

- ADR-003 decidió enrutar cada orden propuesta según un `decision_score` determinista entre 0 y 1, pero dejó abiertos la fórmula, los umbrales, los límites de riesgo y el criterio de calibración para pasar a `live`.
- Mientras esos valores sean `null` en `config/desk.example.yaml`, el `ExecutionPort` falla cerrado y M1 no puede cerrar el corte vertical.
- El `decision_score` **no** mide la probabilidad de ganar dinero. Mide qué tan respaldada está la orden propuesta: evidencia, verificación, contradicciones y frescura. Solo los resultados en paper dirán si un score alto predice un mejor resultado.

## Criterios relevantes

| Criterio | Peso |
|----------|------|
| Determinista, reproducible y testeable (§5.1) | Alto |
| Resistente a inyección de prompts: el LLM no fija su propio score | Alto |
| Un fallo grave nunca se compensa con otras señales fuertes | Alto |
| Generar datos para calibrar en todo el rango de score | Alto |
| Explicable en el artefacto y en las trazas | Medio |

## Decisión

### 1. Fórmula: requisitos duros + suma ponderada versionada

**Requisitos duros.** Si cualquiera falla, `decision_score = 0` y no se propone orden:

- Veredicto del Deterministic Gate = `PASS`.
- Señal del Event Analyst = `CONFIRMED`.
- Cero contradicciones materiales sin resolver.
- Datos dentro de `money_rules.staleness_hours`.
- Activo dentro del universo permitido (`universe.symbols`).

**Componentes.** Si todos los requisitos pasan, `decision_score = Σ peso_i × componente_i`, con pesos que suman 1 y componentes normalizados a [0, 1]:

| Componente | Fuente determinista | Normalización inicial |
|------------|---------------------|-----------------------|
| Fuerza de la evidencia | Fuentes primarias independientes (Evidence Researcher), ponderadas por tipo de fuente | `min(fuentes_primarias / 2, 1)` |
| Cobertura de verificación | Afirmaciones y cifras verificadas por el gate | `verificadas / totales` |
| Contradicciones no materiales | Contradicciones menores abiertas (Risk Analyst + gate) | Decrece con cada una |
| Frescura | Antigüedad del dato frente a `staleness_hours` | Decae linealmente con la edad |

- Pesos iniciales iguales. Los pesos exactos y la normalización se fijan en la spec de M1.
- La fórmula lleva `score_version`. Cada orden registra la versión con la que se calificó. Cambiar pesos o componentes sube la versión.
- La confianza auto-declarada por un LLM **nunca** es entrada del score.

### 2. Umbrales iniciales (paper)

| Parámetro | Valor |
|-----------|-------|
| `reject_threshold` | 0.40 |
| `auto_threshold` | 0.75 |

En `live` sigue vigente ADR-003 punto 5: sin envío automático hasta cumplir el criterio de calibración.

### 3. Seguimiento en sombra

Toda orden rechazada por score se registra con su score, `score_version` y precio de referencia, **sin enviarse**. Se evalúa a `desk_limits.review_horizon_trading_days` (20 días hábiles). Así hay datos en las tres zonas de score sin arriesgar capital.

### 4. Límites de riesgo (porcentaje del capital de la cuenta)

| Límite | Valor | Efecto al excederse |
|--------|-------|---------------------|
| Tamaño máximo por orden | 2% | Orden rechazada |
| Exposición máxima por activo | 5% | Orden rechazada |
| Pérdida diaria máxima | 1% | Kill switch del día: no se envían más órdenes hasta la siguiente sesión |
| Órdenes por día | 5 | Orden rechazada |
| Reserva mínima de caja | 20% | Orden rechazada |

Los límites se expresan en porcentaje para no depender del capital inicial de la cuenta paper (pendiente de verificar en la documentación de Alpaca).

### 5. Criterio de calibración para considerar `live`

Todas estas condiciones, además del interruptor explícito y la confirmación del usuario de ADR-003:

- Al menos **50 órdenes resueltas** en paper (enviadas o en sombra) al horizonte de 20 días hábiles.
- **Relación monótona** del resultado frente a `benchmark` (SPY): tramo automático > tramo de aprobación humana > tramo de rechazos en sombra.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| Solo suma ponderada | Compensatoria: mucha evidencia podría tapar una contradicción grave |
| Tabla de reglas por tramos | Demasiado gruesa; muchas órdenes empatarían |
| Confianza auto-declarada del LLM | No determinista e inyectable; contradice ADR-003 |
| Modelo entrenado sobre resultados | Sin datos todavía; es el paso posterior a la calibración |
| Umbrales 0.50 / 0.85 | Casi sin órdenes automáticas: no habría datos de esa zona |
| Umbrales 0.30 / 0.65 | Más ruido y más órdenes de baja calidad en paper |
| Rechazar sin seguimiento | Sesgo de selección: imposible saber si los scores bajos salen peor |
| Criterio de 100 órdenes | Más robusto, pero demasiado lento con el universo actual |

## Consecuencias

- `config/desk.example.yaml` recibe los umbrales y límites de esta decisión.
- La spec de M1 define pesos, normalización y tests numéricos del score, de los requisitos duros y de cada límite.
- El artefacto y la traza de cada orden incluyen `decision_score`, `score_version`, umbrales vigentes, ruta tomada y, si aplica, el registro en sombra.
- Hace falta un proceso que evalúe las órdenes y los registros en sombra al horizonte de 20 días.

## Riesgo aceptado por el usuario

Pesos sin calibrar al inicio, que pueden enviar órdenes malas en paper. Mitigación: solo paper, límites de riesgo y kill switch siempre activos. La calibración tardará meses por el universo pequeño (SPY, NVDA), el máximo de 5 órdenes por día y el horizonte de 20 días; 50 resultados es una muestra pequeña.

## Confianza

**Media.** La estructura es sólida y testeable; los valores numéricos son una primera estimación sin evidencia empírica.

## Condición de revisión

Reabrir si: (a) tras 50 órdenes resueltas no hay relación monótona, (b) casi todas las órdenes caen en una sola zona de score, (c) se alcanza a menudo el kill switch diario, o (d) se amplía el universo de activos.
