CREATE SCHEMA IF NOT EXISTS mart_financiero;

DROP TABLE IF EXISTS mart_financiero.resumen_general;

CREATE TABLE mart_financiero.resumen_general AS
SELECT
    COUNT(*) AS total_clientes,

    SUM(flag_dificultad_pago) AS clientes_con_dificultad_pago,

    ROUND(
        SUM(flag_dificultad_pago) * 100.0 / COUNT(*),
        2
    ) AS tasa_dificultad_pago_pct,

    ROUND(SUM(monto_credito), 2) AS exposicion_credito_total,

    ROUND(
        SUM(
            CASE
                WHEN flag_dificultad_pago = 1 THEN monto_credito
                ELSE 0
            END
        ),
        2
    ) AS monto_en_riesgo_observado,

    ROUND(
        SUM(
            CASE
                WHEN flag_dificultad_pago = 1 THEN monto_credito
                ELSE 0
            END
        ) * 100.0 / NULLIF(SUM(monto_credito), 0),
        2
    ) AS porcentaje_exposicion_en_riesgo,

    ROUND(AVG(ratio_credito_ingreso), 4) AS ratio_credito_ingreso_promedio,

    ROUND(AVG(score_promedio_externo), 4) AS score_externo_promedio

FROM cst_data.cartera_clientes_train;