CREATE SCHEMA IF NOT EXISTS mart_financiero;

DROP TABLE IF EXISTS mart_financiero.resumen_filial;

CREATE TABLE mart_financiero.resumen_filial AS
SELECT
    id_filial,
    nombre_filial,
    zona_filial,
    total_clientes,
    clientes_con_dificultad_pago,
    tasa_dificultad_pago_pct,
    exposicion_credito_total,
    monto_en_riesgo_observado,
    porcentaje_exposicion_en_riesgo,
    ratio_credito_ingreso_promedio,
    score_externo_promedio,
    ranking_riesgo,
    ranking_exposicion
FROM cst_data.vw_gestion_riesgo_filial
ORDER BY ranking_riesgo;