# ADR-003: Broker Alpaca y ejecución de órdenes por umbrales de calificación

- **Estado:** Aceptado
- **Fecha:** 2026-10-12
- **Decisor:** Juan Guevara Bustamante (aprobación explícita en chat de sesión)

## Contexto

- La versión 3.0 de `master_prompt.md` prohibía la integración con brokers, las órdenes automáticas y la ejecución con dinero real. El proyecto era solo de investigación analítica.
- El usuario decide que el sistema opere desde Alpaca: la investigación debe terminar en órdenes ejecutadas.
- El resto del contexto sigue igual: todo corre en local, AWS emulado en Floci y LangGraph, LangSmith y Langfuse obligatorios.

## Criterios relevantes

| Criterio | Peso (usuario, implícito) |
|----------|---------------------------|
| Operar de verdad desde un broker | Alto |
| Autonomía del sistema cuando la confianza es alta | Alto |
| Control humano en los casos dudosos | Alto |
| Riesgo de capital acotado durante el MVP | Alto |
| Costo incremental ~$0 | Alto |

## Decisión

1. **Broker:** Alpaca, mediante su Trading API.
2. **Modo de cuenta:** paper trading en el MVP. El dinero real llega más adelante, detrás de un interruptor explícito (variable de entorno dedicada más confirmación del usuario). Si la configuración falta o es ambigua, el sistema arranca en `paper`.
3. **Enrutamiento por calificación.** Cada orden propuesta recibe un `decision_score` entre 0 y 1, calculado con código determinista:
   - Por encima de `auto_threshold`: el sistema envía la orden sin aprobación.
   - Entre `reject_threshold` y `auto_threshold`: la orden espera la aprobación del usuario.
   - Por debajo de `reject_threshold`: la orden se rechaza.
4. **Controles que nunca se saltan:** verificación determinista superada, límites de riesgo (tamaño por orden, exposición por activo, pérdida diaria, órdenes por día), kill switch, universo de activos permitido e idempotencia por identificador de cliente.
5. **Salvaguarda en `live`:** la zona de envío automático queda desactivada hasta tener evidencia de calibración del `decision_score` sobre resultados en paper. Hasta entonces, en `live` toda orden por encima de `reject_threshold` requiere aprobación humana.
6. **Separación:** el LLM nunca llama a Alpaca. Solo el módulo de ejecución determinista envía órdenes.

Detalle operativo en `master_prompt.md` §5.1.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| Sin broker (solo investigación, versión 3.0) | No cumple el objetivo de operar desde Alpaca |
| Solo paper trading, sin camino a dinero real | El usuario quiere operar con dinero real más adelante |
| Dinero real desde el inicio | Riesgo de capital sin calificación calibrada ni límites probados |
| Aprobación humana de cada orden | Menos autonomía de la deseada cuando la confianza es alta |
| Envío automático sin aprobación ni umbrales | Sin control humano en los casos dudosos |

## Consecuencias

- Crear una cuenta de Alpaca con paper trading. Las claves de paper y live van separadas y solo en `.env`, nunca en git ni en el frontend.
- Nuevas decisiones Tipo 1 por debatir: fórmula del `decision_score`, valores de los umbrales y de los límites de riesgo, y criterio de calibración para pasar a `live`.
- Nuevo módulo de ejecución con broker falso para tests y adaptador real de Alpaca para integración y demo.
- El modelo de amenazas incluye órdenes indebidas o duplicadas, activación accidental de `live` y manipulación de la calificación por inyección de prompts.
- El costo sigue en ~$0 mientras se opere en paper. En `live` el riesgo es de capital, no de nube.

## Riesgo aceptado por el usuario

Envío automático de órdenes basado en una calificación que, al inicio, no está calibrada. Mitigación: solo en paper hasta tener evidencia de calibración, con límites de riesgo y kill switch siempre activos.

## Confianza

**Media.** La política está clara, pero falta verificar la API de Alpaca (endpoints, SDK, límites de uso, horario de mercado) y definir la fórmula de la calificación.

## Condición de revisión

Reabrir si: (a) la calificación no muestra relación con los resultados en paper, (b) la API de Alpaca no permite paper trading o la idempotencia requerida, o (c) se plantea activar `live`.

## Referencias

- `master_prompt.md` §2.4, §5, §5.1, §14 y §21
- https://docs.alpaca.markets/ (a verificar)
