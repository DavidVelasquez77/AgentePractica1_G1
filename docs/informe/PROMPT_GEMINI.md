# Prompt para Gemini (informe Word, estilo USAC)

Copia TODO el bloque siguiente a Gemini (Flash o Pro). Luego pega el texto en tu plantilla Word. Donde veas `[ESPACIO PARA FIGURA n]` deja un salto de página o un recuadro y inserta el PNG indicado desde `outputs/figures/`.

Reemplaza `[GRUPO]`, nombres y carnets. Fecha de portada: jueves 12 de agosto de 2026 (o la de entrega).

---

Eres un redactor académico de la Universidad de San Carlos de Guatemala, Facultad de Ingeniería, Escuela de Ciencias y Sistemas. Escribes el informe final de un analista de datos junior para el curso SISTEMAS ORGANIZACIONALES Y GERENCIALES 2, Práctica 1, segundo semestre 2026.

ESTILO (obligatorio, igual a la plantilla Word del estudiante):
- Español formal, tono de informe técnico profesional (no coloquial, no marketing).
- Portada centrada: Universidad San Carlos de Guatemala / Facultad de Ingeniería / Escuela de Ciencias y Sistemas / SISTEMAS ORGANIZACIONALES Y GERENCIALES 2 (gris). Luego el sello institucional (el usuario ya lo tiene; no lo describas). Título en mayúsculas y negrita. Tabla de dos columnas: Nombre y Apellido | Carnet. Fecha al pie.
- Cuerpo: títulos numerados en negro, subtítulos en negrita. Párrafos justificados, largos y densos. Tablas con encabezado negro y texto blanco cuando describas tablas. Sin emojis. Sin inglés innecesario.
- NO uses el contenido viejo de SIMIO AEROSPACE ni PlastiProduct/ERP/CRM. Esta práctica es análisis de ventas online 2021 + sucursal física + chat de IA.
- NO inventes cifras. Usa SOLO las que te doy. Puedes redondear a 2 decimales en prosa.
- Donde indique [ESPACIO PARA FIGURA n: archivo] deja exactamente esa etiqueta en una línea sola, centrada, para que el estudiante inserte la imagen. No generes descripciones tipo “aquí iría un gráfico” de más de 2 líneas; la figura habla sola y luego un pie de figura.
- Cada una de las 4 conclusiones debe tener MÍNIMO 20 líneas de párrafo (líneas de informe, ~80-90 caracteres). Es un requisito de la rúbrica.
- 2 recomendaciones concretas POR estudiante (5 integrantes = 10 acciones), atribuidas por nombre.
- Responde las 5 preguntas 8a–8e con análisis de negocio, no con relleno.

PORTADA — título:
INFORME TÉCNICO — ANÁLISIS DE VENTAS ONLINE 2021 Y AGENTE CONVERSACIONAL PARA LA EXPANSIÓN A SUCURSAL FÍSICA

Integrantes (completa lo que falte; no inventes apellidos si no están):
- Enner Esaí Mendizabal Castro | 202302220
- Emilio [APELLIDOS] | [CARNET]
- Vela [NOMBRE COMPLETO] | 202307705
- Helado [NOMBRE COMPLETO] | [CARNET]
- Brandon [APELLIDOS] | [CARNET]
Grupo: [GRUPO]
Archivo de entrega: SOG2-2S26_grupo[GRUPO].pdf

ESTRUCTURA DEL DOCUMENTO (respeta este orden; son los entregables):

1. Resumen ejecutivo (1 página). Problema: empresa 100% online 2021 quiere sucursal física y un chat de IA que entregue análisis bajo demanda. Solución: ETL Python, PostgreSQL en Supabase (nube), análisis 2–6, MCP Server + Google ADK con Gemini 3.5 Flash-Lite.

2. Presentación / contexto del analista junior y del dataset.

3. Planificación
   3.1 División de tareas (usar el plan de trabajo real, no digas que una sola persona hizo todo):
   - Emilio: líder, redacción del PDF, planificación, metodología, 4 conclusiones, 5 preguntas, consolidar 10 recomendaciones.
   - Enner: ingeniero de datos y cloud. ETL, tipos, BD relacional en la nube, diagrama ER (DBML / dbdiagram.io).
   - Vela: Google ADK, MCP Server, conexión del LLM, chat que responde puntos 2–6.
   - Helado: segmentación, correlación, ≥7 gráficos.
   - Brandon: conexión a BD, estadística descriptiva, tendencias (meses, navegadores, efectivo, boletines/vales).
   3.2 Herramientas y por qué: Python (pandas, scipy, seaborn), Supabase PostgreSQL (BD relacional cloud, evita -20% y -20%), Google ADK + MCP (requisito técnico), Gemini 3.5 Flash-Lite (rápido, function calling, consejo del enunciado de usar Flash/Flash-lite), GitHub, dbdiagram.io.
   3.3 Plazos: Fase 1 bloqueante Enner (ETL+BD). Fase 2 paralela Brandon+Helado. Fase 3 Vela (ADK+MCP). Fase 4 Emilio cierra el PDF.

4. Proceso de análisis
   4.1 Limpieza: CSV `venta_online_c.csv`, separador `;`, 6500 filas. 0 nulos, 0 duplicados, Id_cliente único. Fechas DD.MM.YY → date. Decimales Venta_total y MontoCompra. Catálogos 0/1/2/4 según enunciado. Decisión: no imputar porque no había huecos; no borrar filas. Carga a `clientes` + `compras` + 3 catálogos en Supabase proyecto sog2-ventas-2021 región sa-east-1. RLS activo; análisis por DATABASE_URL.
   4.2 Decisiones de EDA: unir catálogos para no reportar códigos crudos; usar MontoCompra para series mensuales (evento) y Venta_total para valor del cliente; rangos de edad 18-25, 26-35, 36-45, 46-55, 56+. Efectivo/contra entrega = MetodoPago 0.
   4.3 Desafíos: (1) host directo de Postgres solo IPv6; se usó pooler de sesión IPv4. (2) CSV con `;` y fechas europeas. (3) Google ADK exige mcp 1.x, no 2.x. (4) Distinguir Venta_total vs MontoCompra.

5. Metodología de visualización: barras para comparar categorías (mes, navegador); líneas para tendencia temporal; pastel para composición de método de pago; dispersión para edad vs venta; boxplot para distribución por género; heatmap para cruce boletin×vale; histograma para forma de la edad. Criterio: una pregunta del enunciado = un tipo de gráfico.

6. Resultados
   Inserta estas cifras en prosa y tablas.

   Estadísticos (n=6500):
   Edad media 36.31, mediana 36, moda 18, min 18, max 79.
   Venta_total media 206.24, mediana 137.35, moda 98 (sesgo derecho).
   N_Compras media 5.09, mediana 4, moda 2.
   MontoCompra media 39.79, mediana 35.76.
   Tiempo media 767.38.

   Mes mayor ventas: marzo 22,994.34 (569 tx). Mes menor: noviembre 19,779.24 (493 tx). Diciembre 22,778.09 (577 tx, más transacciones pero no el mayor monto).

   Navegador/canal: Tienda Física 3523 (140,332.26) más popular. Navegador 4 197 (8,142.10) menos popular. Navegador 1 1273, Navegador 2 847, Navegador 3 660.

   Pago: crédito 3827 tx / 152,601.47; débito 1466 / 58,548.74; efectivo 1207 / 47,465.64 (18.57% de transacciones).

   Boletín: 2921 sí vs 3579 no. Vale: 1254 sí vs 5246 no. Mes con más boletines: diciembre (262). Mes con más vales: marzo (133).

   Edad: 18-25 n=1249 venta_promedio 207.82; 26-35 n=1946 / 212.66; 36-45 n=1946 / 204.70; 46-55 n=1013 / 199.63; 56+ n=346 / 192.46.

   Género: femenino 3128 venta_promedio 208.16; masculino 3372 / 204.46.

   Promo: Boletín y vale n=811 venta_promedio 242.57; solo boletín 2110 / 233.80; sin promoción 3136 / 183.33; solo vale 443 / 170.66.

   Correlación edad-venta: Pearson r=-0.025, p=0.042; Spearman rho=-0.030, p=0.016. Relación lineal débil/nula (p bajo por n grande).
   Género vs método de pago: chi²=3.73, p=0.155. No significativo.
   Boletín vs vale: chi²=243.57, p=6.57e-55. Asociación fuerte.

   Figuras (insertar en este orden, con pie de figura):
   [ESPACIO PARA FIGURA 1: outputs/figures/01_barras_ventas_mes.png]
   [ESPACIO PARA FIGURA 2: outputs/figures/02_lineas_tendencia_mes.png]
   [ESPACIO PARA FIGURA 3: outputs/figures/03_pastel_metodo_pago.png]
   [ESPACIO PARA FIGURA 4: outputs/figures/08_barras_navegador.png]
   [ESPACIO PARA FIGURA 5: outputs/figures/07_histograma_edad.png]
   [ESPACIO PARA FIGURA 6: outputs/figures/04_dispersion_edad_venta.png]
   [ESPACIO PARA FIGURA 7: outputs/figures/05_boxplot_venta_genero.png]
   [ESPACIO PARA FIGURA 8: outputs/figures/06_heatmap_boletin_vale.png]

7. Conclusiones (4, cada una ≥20 líneas). Temas sugeridos:
   C1: Estacionalidad (marzo pico, noviembre valle) y qué implica para inventario de la sucursal física.
   C2: Tienda Física ya es el canal #1 en un dataset “online”: la sucursal no parte de cero; Navegador 4 es marginal.
   C3: Tarjeta de crédito domina; efectivo es 18.6% — la sucursal debe aceptar efectivo sin convertirlo en el foco.
   C4: Promociones combinadas (boletín+vale) marcan el segmento de mayor valor; edad y género casi no diferencian el ticket. Correlación edad-venta nula; asociación boletín-vale sí.

8. Recomendaciones (2 por estudiante, concretas, medibles):
   Enner: (1) pipeline ETL+calidad mensual en Supabase. (2) vista/dashboard SQL de stock vs mes pico.
   Vela: (1) poner el chat ADK en el flujo de gerencia. (2) logs de preguntas frecuentes para priorizar reportes.
   Helado: (1) campaña boletín+vale al segmento 26-35. (2) no gastar en personalización por edad (correlación nula).
   Brandon: (1) plan comercial de marzo y contención de noviembre. (2) no invertir en Navegador 4; reforzar Tienda Física + Navegador 1.
   Emilio: (1) KPI gerencial unificado (ticket, mix de pago, uso de vale). (2) protocolo de caja en sucursal para el 18.6% efectivo.

9. Respuestas 8a–8e (un apartado cada una, 1 página c/u aprox.):
   a) Diferenciación: mix canal físico ya presente + IA que responde en segundos con cifras de 2021.
   b) Decisiones: calendario comercial marzo/noviembre; mix de pago; pack boletín+vale; no segmentar por edad para ticket.
   c) Costos: no subsidiar Navegador 4; no personalizar por edad; chat reduce horas de analista en consultas repetidas.
   d) Datos futuros: SKU, sucursal vs web, NPS, costo de adquisición, horario, ciudad, inventario.
   e) El chat SÍ cambia la entrega futura: consulta bajo demanda de puntos 2–6 vía MCP; no reemplaza el informe, acelera operación. Riesgo: alucinación si no se usan tools (aquí se forzó tool-use).

10. Diagrama de base de datos
    [ESPACIO PARA FIGURA 9: export PNG de dbdiagram.io pegando db/schema.dbml]
    Tablas: catalogo_genero, catalogo_metodo_pago, catalogo_navegador, clientes, compras.

11. Código
    Repositorio GitHub del grupo. Mencionar carpetas 01_preparacion … 06_visualizacion, mcp_server, agent, supabase/migrations, run_all.py. No pegues secretos ni .env. Puedes citar la estructura de carpetas en un recuadro de código.

Al final, no agregues “espero haberte ayudado”. Cierra con la tabla de rúbrica 7.2 en blanco (puntos totales 30+30+20+20=100) para que el catedrático la llene.
