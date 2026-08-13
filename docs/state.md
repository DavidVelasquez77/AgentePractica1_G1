# Sistemas Organizacionales y Gerenciales 2

## Índice

3. [Enunciado de la Práctica](#3-enunciado-de-la-práctica)
   - 3.1 Descripción del problema a resolver
   - 3.2 Alcance de la práctica
   - 3.3 Requerimientos técnicos
4. [Entregables](#4-entregables)
5. [Recursos y herramientas a utilizar](#5-recursos-y-herramientas-a-utilizar)
6. [Rúbrica de Calificación](#6-rúbrica-de-calificación)
   - 7.1 Requisitos para optar a la calificación
   - 7.2 Resumen de Puntuaciones
   - Detalle de la Calificación
   - Comentarios Generales

---

## 3. Enunciado de la Práctica

### 3.1 Descripción del problema a resolver

Siendo un analista de datos Junior el cual trabaja para una empresa que desde sus inicios ha realizado ventas online, la empresa desea expandir su alcance a una sucursal física, a su vez también han decidido que una inteligencia artificial le entreguen los datos según sea solicitado.

Esto con el fin de mejorar la búsqueda de los análisis y obtener los resultados de forma directa sin demorarse demasiado tiempo. Para este análisis se otorgará la información de las ventas online del año 2021 en un archivo `.csv` que contendrá los siguientes campos:

- Id_cliente
- Edad
- Genero
- Venta_total
- N_Compras
- FechaCompra
- MontoCompra
- MetodoPago
- Tiempo
- Navegador
- Boletín
- Vale

**Donde:**

- **Venta_total, MontoCompra:** Tipo dato decimal
- **FechaCompra:** Tipo dato Fecha
- **Genero**
  - 1: Femenino
  - 0: Masculino
- **MetodoPago**
  - 0: Efectivo
  - 1: Tarjeta de Crédito
  - 2: Tarjeta de Débito
- **Navegador**
  - 0: Tienda Física
  - 1: Navegador 1
  - 2: Navegador 2
  - 3: Navegador 3
  - 4: Navegador 4
- **Boletín**
  - 1: Sí
  - 0: No
- **Vale**
  - 1: Sí
  - 0: No

### 3.2 Alcance de la práctica

**1. Preparación de datos:**

a. Extraer los datos del archivo `.csv`.
b. Verificar si hay valores faltantes o duplicados y decidir cómo manejarlos.
c. Asegurarse de que los tipos de datos sean correctos para cada columna.
d. Cargar los datos a una base de datos SQL en la nube.

**2. Análisis exploratorio:**

a. Obtener los datos de la base de datos.
b. Calcular estadísticas básicas (media, mediana, moda) para las variables numéricas.
c. Crear visualizaciones para mostrar la distribución de ventas por mes, método de pago, navegador, Boletín y Vale.

**3. Análisis de tendencias:**

a. Determinar los meses con mayores y menores ventas.
b. Identificar el navegador más preferido y el menos popular.
c. Identificar total de ventas fueron pagadas contra entrega o con pago en efectivo.
d. Identificar los meses donde se usaron más boletines y vales.

**4. Segmentación de clientes:**

a. Agrupar a los clientes por edad y analizar sus patrones de compra.
b. Comparar el comportamiento de compra entre géneros.
c. Agrupar los clientes por boletín y vales y analizar sus patrones de compra.

**5. Análisis de correlación:**

a. Investigar si existe una relación entre el total de la venta y la edad del cliente.
b. Examinar si hay una correlación entre el género del cliente y el método de pago preferido.
c. Investigar si existe una correlación entre los clientes que utilizan boletines y vales.

**6. Visualización de datos:**

a. Crear al menos siete gráficos diferentes (por ejemplo, gráfico de barras, gráfico de dispersión, gráfico de líneas) para representar los hallazgos más importantes.

**7. Conclusiones y recomendaciones:**

a. Basándose en el análisis realizado, proporcionar al menos cuatro conclusiones clave sobre las ventas y el comportamiento de los clientes (mín. 20 líneas cada conclusión).
b. Sugerir dos acciones concretas por estudiante que la empresa podría tomar para mejorar sus ventas o la satisfacción del cliente.

**8. Responder a las preguntas:**

a. ¿Cómo podrían los insights obtenidos ayudar a diferenciarse de la competencia?
b. ¿Qué decisiones estratégicas podrían tomarse basándose en este análisis para aumentar las ventas y la satisfacción del cliente?
c. ¿Cómo podría este análisis de datos ayudar a la empresa a ahorrar costos o mejorar la eficiencia operativa?
d. ¿Qué datos adicionales recomendarían para obtener insights aún más valiosos en el futuro?
e. ¿Implementar una Chat conversacional de IA afectaría a la empresa para que entregue el análisis de los datos a futuro?

> **Nota:** Los puntos del 2 al 6, el chat de IA debe ser capaz de entregar los resultados según se soliciten.

### 3.3 Requerimientos técnicos

- Base de datos relacional implementada en la nube.
- Cualquier lenguaje de análisis de datos como Python o R.
- Google ADK para crear el agente de IA conversacional.
- Crear un MCPServer que se integre al IA conversacional de Google ADK.
- Usar cualquier modelo de IA (GPT, Claude, Gemini, Llama, etc.)
  - **Consejo:** Si van a usar Gemini usar las versiones Flash o Flash-lite las cuales están optimizadas para alta velocidad y son de uso gratuito (con límite de tokens).

---

## 4. Entregables

Se debe entregar un documento PDF presentable de acuerdo con un informe final como lo representa su puesto de analista de datos Junior, con el nombre:

```
SOG2-2S26_grupo#.pdf
```

El cual debe contener:

| Tipo | Descripción |
|---|---|
| **Presentación** | Documento presentable, bien redactado de acuerdo con un informe final conforme a su puesto de analista Junior. |
| **Planificación** | ¿Cómo se dividieron las tareas entre los miembros del equipo? ¿Qué herramientas y tecnologías decidieron utilizar y por qué? ¿Cómo establecieron los plazos para cada fase del proyecto? |
| **Proceso de análisis** | Describa el enfoque paso a paso que siguieron para limpiar y preparar los datos. Explique las decisiones tomadas durante el análisis exploratorio de datos. Detalle los desafíos encontrados durante el análisis y cómo los superaron. |
| **Metodología** | Explique cómo seleccionaron las visualizaciones más apropiadas para sus hallazgos. |
| **Conclusiones, recomendaciones, respuestas** | Se encuentran estas secciones según como fue solicitado. |
| **Diagrama** | Diagrama de la base de datos |
| **Código** | Código utilizado para su implementación |

---

## 5. Recursos y herramientas a utilizar

- **Plataformas:** GitHub (para repositorio), UEDI (para entrega).

---

## 6. Rúbrica de Calificación

### 7.1 Requisitos para optar a la calificación

| Tema | Descripción | Cumple (Sí/No) |
|---|---|---|
| Entrega | Debe entregarse el documento PDF en UEDI en tiempo. | |
| Copias | Copias parciales/totales tendrá nota de 0 y será reportación al catedrático de la sección y a la escuela de ciencias y sistemas. | |
| Grupos | La práctica será realizada en grupo los cuales serán definidos durante la lectura de dicha práctica. | |
| Base de datos | Utilizó una base de datos relacional y se encuentra implementada en la nube. | |
| Herramientas | Utilizó una herramienta para realizar el análisis de datos como Python o R. | |
| Penalizaciones | - No utilizar una base de datos relacional (-20%)<br>- No implementar la base de datos en la nube (-20%)<br>- Entrega tarde (-100%) | |

### 7.2 Resumen de Puntuaciones

| Área | Puntos Totales | Puntos Obtenidos |
|---|---|---|
| **1. Habilidades** | | |
| Utiliza herramientas de análisis de datos. | 30 | |
| Aplica herramientas actuales de IA para el análisis de datos. | 30 | |
| **Sub-Total Habilidades** | **60** | |
| **2. Conocimiento** | | |
| Analiza de forma coherente la información proporcionada con lo solicitado. | 20 | |
| Presenta un documento PDF tipo informe final con todos los puntos solicitados. | 20 | |
| **Sub-Total Conocimiento** | **40** | |
| **TOTAL** | **100** | |

### Detalle de la Calificación

La rúbrica de calificación será compartida días antes del día de calificación.

### Comentarios Generales

*Apartado para comentar si hubo algún inconveniente durante la calificación o comentario.*

---