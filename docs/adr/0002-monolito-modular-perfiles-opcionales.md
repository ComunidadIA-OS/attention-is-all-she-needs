# 0002. Monolito modular desacoplado (`[core]`, `[local-ai]`, `[gpu]`) frente a microservicios

* **Fecha:** 2026-10-17
* **Estado:** Aceptada
* **Decisores:** Equipo AIASN (Pilar de la Fuente Diez, Rocío Jiménez Villén, Alba Camiña García)
* **Directriz de referencia:** Bases Oficiales Art. 10 y Montse Guàrdia (`1:24:50`)

---

## Contexto y Problema

El software debe ejecutarse tanto en portátiles ligeros de analistas, activistas y periodistas (sin tarjeta gráfica dedicada) como en los servidores con $2 \times \text{NVIDIA V100}$ de OVHcloud. Además, el Artículo 10 de las Bases exige que la solución sea *«agnóstica al modelo y libre de ataduras tecnológicas»*. Desplegar una malla compleja de microservicios distribuidos con Docker Compose, colas RabbitMQ o Kubernetes generaría una sobrecarga operativa inasumible en el plazo del reto y dispararía el consumo energético en reposo.

## Opciones Consideradas

1. **Opción A (Arquitectura de Microservicios Distribuidos):** Un contenedor para Whisper, otro para YOLO, otro para la base de datos y otro para el frontend, comunicados vía gRPC/REST. *(Descartada por alta latencia, complejidad de despliegue y costes ocultos de mantenimiento según advirtió Montse Guàrdia).*
2. **Opción B (Monolito Modular con Inyección de Dependencias y Extras en `pyproject.toml`):** Paquete único en Python (`aiasn`) organizado en submódulos desacoplados (`aiasn/core`, `aiasn/audio`, `aiasn/vision`, `aiasn/connectors`), con adaptadores intercambiables que implementan interfaces abstractas y extras opcionales de instalación.

## Decisión Adoptada

Se adopta la **Opción B**. Se configuran tres perfiles de instalación en `pyproject.toml`:
* `pip install -e ".[analysis]"`: Motor determinista + SQLite/Parquet + cliente HTTP para AI Endpoints de OVHcloud (coste computacional $< 0,01\text{ €/h}$).
* `pip install -e ".[ai]"`: Motor + inferencia local ligera en CPU.
* `pip install -e ".[all]"`: Stack completo para instancias V100 con PyTorch, Ultralytics, InsightFace y EasyOCR.

## Consecuencias

* **Positivas:**
  * Arranque en frío en menos de 5 segundos en entornos locales de analista.
  * Portabilidad total sin necesidad de orquestadores de contenedores pesados.
  * Cumplimiento íntegro del principio de independencia de proveedores del Artículo 10.
* **Compromisos asumidos:**
  * El código de los módulos opcionales debe emplear importaciones diferidas (*lazy imports*) para no lanzar error si una dependencia de GPU no está instalada en el perfil ligero.
