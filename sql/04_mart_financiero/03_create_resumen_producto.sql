CREATE SCHEMA IF NOT EXISTS mart_financiero;

DROP TABLE IF EXISTS mart_financiero.resumen_producto;

CREATE TABLE mart_financiero.resumen_producto AS
SELECT
    id_producto,
    nombre_producto,
    familia_producto,
    total_clientes,
    clientes_con_dificultad_pago,
    tasa_dificultad_pago_pct,
    exposicion_credito_total,
    monto_en_riesgo_observado,
    porcentaje_exposicion_en_riesgo,
    margen_esperado_aproximado,
    ratio_credito_ingreso_promedio,
    score_externo_promedio,
    ranking_riesgo,
    ranking_exposicion
FROM cst_data.vw_gestion_riesgo_producto
ORDER BY ranking_riesgo;