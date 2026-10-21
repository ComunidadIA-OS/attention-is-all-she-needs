# Política de Seguridad y Reporte Responsable

## 1. Alcance de Seguridad

El equipo de **Attention Is All She Needs (AIASN)** se toma muy en serio la seguridad de la información, la privacidad de los datos personales y la integridad algorítmica de los modelos.

Este proyecto trata con metadatos audiovisuales y procesamiento de voz y texto. Cumplimos con los principios de:
* **Privacidad por diseño (RGPD):** Procesamiento de evidencias audiovisuales efímero en memoria sin retención de plantillas biométricas persistentes.
* **Seguridad de credenciales:** Prohibición estricta de almacenar claves de API, tokens de OVHcloud o credenciales en el repositorio público (`.gitignore` verificado).
* **Cumplimiento del Reglamento Europeo de IA (RIA / REIA):** Trazabilidad de inferencias y auditoría humana (*Human-in-the-Loop*).

---

## 2. Reporte Responsable de Vulnerabilidades

Si descubres una vulnerabilidad de seguridad o una fuga accidental de credenciales:

> ⚠️ **Por favor, NO abras un Issue público en GitHub.**

Ponte en contacto directamente con el equipo mediante canal privado a través de cualquiera de las siguientes direcciones de correo electrónico:
* **Alba Camiña García:** `albacaminagarcia@gmail.com`
* **Pilar de la Fuente Diez:** `pilarfuente1992@gmail.com`
* **Rocío Jiménez Villén:** `rjvillen@gmail.com`

### Información a incluir en el reporte:
1. Descripción de la vulnerabilidad o riesgo detectado.
2. Pasos detallados para reproducir el fallo o vector de ataque.
3. Posible impacto sobre la privacidad o el sistema.
4. Sugerencia de mitigación, si la tienes.

---

## 3. Plazos de Respuesta y Divulgación Coordinada

* **Recepción y acuse de recibo:** En un plazo máximo de **48 horas**.
* **Evaluación y parche:** Se priorizará el despliegue de una corrección en rama privada antes de publicarla en `main`.
* **Divulgación coordinada:** Agradecemos y acreditamos públicamente a los investigadores que colaboren en el reporte responsable una vez subsanado el problema.
