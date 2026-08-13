# Pasos para armar el Word / PDF con tu plantilla USAC

Hazlo en este orden. No pidas a Gemini que “diseñe” la portada: ya la tienes.

1. Abre tu plantilla Word (la de sello USAC + tabla Nombre/Carnet).
2. Cambia el titulo a: INFORME TECNICO — ANALISIS DE VENTAS ONLINE 2021 Y AGENTE CONVERSACIONAL PARA LA EXPANSION A SUCURSAL FISICA.
3. Completa la tabla de integrantes. Quita filas vacias o llena las 5.
4. Fecha al pie: la de entrega (en la plantilla aparecia jueves 12 de agosto de 2026).
5. Borra el texto de SIMIO / PlastiProduct / ERP-CRM. Deja solo portada y estilos.
6. Abre Gemini, pega el contenido de `docs/informe/PROMPT_GEMINI.md` (el bloque desde “Eres un redactor…”).
7. Copia la respuesta de Gemini al Word, seccion por seccion, aplicando tus estilos (titulos, justificacion, tablas).
8. Donde Gemini dejo `[ESPACIO PARA FIGURA n]`, Insertar > Imagen y usa:
   - Fig 1: `outputs/figures/01_barras_ventas_mes.png`
   - Fig 2: `outputs/figures/02_lineas_tendencia_mes.png`
   - Fig 3: `outputs/figures/03_pastel_metodo_pago.png`
   - Fig 4: `outputs/figures/08_barras_navegador.png`
   - Fig 5: `outputs/figures/07_histograma_edad.png`
   - Fig 6: `outputs/figures/04_dispersion_edad_venta.png`
   - Fig 7: `outputs/figures/05_boxplot_venta_genero.png`
   - Fig 8: `outputs/figures/06_heatmap_boletin_vale.png`
   - Fig 9: exporta el ER desde https://dbdiagram.io pegando `db/schema.dbml`
9. Pie de cada figura: “Figura n. … Fuente: elaboracion propia a partir de Supabase / ventas 2021.”
10. Anexa el link de GitHub y, si piden codigo en el PDF, captura de la estructura de carpetas (sin .env).
11. Exporta a PDF con nombre `SOG2-2S26_grupo#.pdf` y sube a UEDI.
12. Revisa que cada conclusion tenga >=20 lineas y que haya 10 recomendaciones (2 por integrante).
