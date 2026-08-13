# Hallazgos (cifras reales, 6500 clientes / compras 2021)

Fuente: `outputs/*.json` generados desde Supabase.

## Limpieza

- Filas iniciales: 6500. Nulos: 0. Duplicados: 0. Id_cliente unico.
- Fechas: 2021-01-01 a 2021-12-31. Catalogos del enunciado: todos validos.
- Carga: 6500 clientes + 6500 compras en proyecto `sog2-ventas-2021` (sa-east-1).

## Estadisticas (media / mediana / moda)

| Variable | Media | Mediana | Moda |
|---|---|---|---|
| Edad | 36.31 | 36 | 18 |
| Venta_total | 206.24 | 137.35 | 98 |
| N_Compras | 5.09 | 4 | 2 |
| MontoCompra | 39.79 | 35.76 | 37.15 |
| Tiempo | 767.38 | 768 | 852 |

Edad min 18, max 79. Venta_total max 3169 (sesgo a la derecha).

## Tendencias

- Mes mayor: **Marzo** (22,994.34; 569 tx).
- Mes menor: **Noviembre** (19,779.24; 493 tx).
- Canal mas usado: **Tienda Fisica** (3,523; 140,332).
- Canal menos usado: **Navegador 4** (197; 8,142).
- Efectivo / contra entrega (MetodoPago=0): 1,207 tx (18.57%), monto 47,465.64.
- Metodo dominante: Tarjeta de credito (3,827 tx; 152,601).
- Mas boletines: **Diciembre** (262). Mas vales: **Marzo** (133).

## Segmentacion

- 26-35 y 36-45: 1,946 clientes cada uno. 18-25: mayor venta_promedio relativa junto a 26-35 (~208-213). 56+: 192.46.
- Femenino 3,128 vs Masculino 3,372. Venta promedio similar (208 vs 204).
- Boletin y vale: n=811, venta_promedio 242.57 (el mas alto).
- Sin promocion: n=3,136, venta_promedio 183.33.
- Solo vale: n=443, venta_promedio 170.66 (el mas bajo).

## Correlacion

- Edad vs venta_total: Pearson r = -0.025 (p=0.042). Relacion lineal **debil/nula** (significativa por n grande, no util).
- Genero vs metodo de pago: chi2 p=0.155. **No** hay asociacion significativa.
- Boletin vs vale: chi2=243.57, p≈6.6e-55. **Si** hay asociacion (quienes usan boletin tienden a usar vale mas de lo esperado).
