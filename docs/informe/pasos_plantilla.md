# Pasos para armar el Word / PDF con tu plantilla USAC

El texto ya esta en `docs/informe/INFORME_COMPLETO.md`. No uses Gemini para generar el informe.

1. Abre tu plantilla Word (sello USAC + tabla Nombre/Carnet).
2. Deja portada y estilos. Borra SIMIO / PlastiProduct / ERP-CRM.
3. Pon el titulo del markdown (analisis de ventas 2021 + agente conversacional).
4. Completa los 5 integrantes (nombres, apellidos, carnets) y el numero de grupo.
5. Copia `INFORME_COMPLETO.md` seccion por seccion, aplicando justificacion, titulos y tablas de tu plantilla.
6. Inserta imagenes:
   - Fig 1: `outputs/figures/01_barras_ventas_mes.png`
   - Fig 2: `outputs/figures/02_lineas_tendencia_mes.png`
   - Fig 3: `outputs/figures/03_pastel_metodo_pago.png`
   - Fig 4: `outputs/figures/08_barras_navegador.png`
   - Fig 5: `outputs/figures/07_histograma_edad.png`
   - Fig 6: `outputs/figures/04_dispersion_edad_venta.png`
   - Fig 7: `outputs/figures/05_boxplot_venta_genero.png`
   - Fig 8: `outputs/figures/06_heatmap_boletin_vale.png`
   - Fig 9: `db/schema.png` (ER de dbdiagram.io)
7. Pie de figura: “Figura n. … Fuente: elaboracion propia a partir de Supabase / ventas 2021.”
8. En Codigo, pega el link de GitHub (sin .env).
9. Exporta `SOG2-2S26_grupo#.pdf` y sube a UEDI.
10. Antes de entregar: 4 conclusiones largas, 10 recomendaciones (2 por integrante), nombres reales.
