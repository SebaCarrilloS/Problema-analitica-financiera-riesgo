-- =============================================================================
-- Proyecto: Analítica Financiera y Riesgo
-- Fase 3: Vistas ejecutivas sobre cst_data
-- Archivo: sql/03_cst/02_create_vistas_gestion_riesgo.sql
--
-- Objetivo:
-- Crear vistas ejecutivas de riesgo y gestión sobre la tabla curada
-- cst_data.cartera_clientes_train.
--
-- Estas vistas todavía no son mart_financiero final.
-- Son resúmenes analíticos intermedios para explorar negocio.
-- =============================================================================


-- =============================================================================
-- 1. Riesgo y gestión por filial
-- =============================================================================

CREATE OR REPLACE VIEW cst_data.vw_gestion_riesgo_filial AS
SELECT
    id_filial,
    nombre_filial,
    zona_filial,
    tipo_filial,
    estado_filial,

    COUNT(*) AS total_clientes,
    SUM(CASE WHEN estado_asignacion = 'Activa' THEN 1 ELSE 0 END) AS clientes_activos,
    SUM(flag_dificultad_pago) AS clientes_con_dificultad_pago,

    ROUND(SUM(flag_dificultad_pago) * 100.0 / NULLIF(COUNT(*), 0), 2) AS tasa_dificultad_pago_pct,

    ROUND(SUM(monto_credito), 2) AS exposicion_credito_total,
    ROUND(AVG(monto_credito), 2) AS monto_credito_promedio,

    ROUND(
        SUM(CASE WHEN flag_dificultad_pago = 1 THEN monto_credito ELSE 0 END),
        2
    ) AS monto_en_riesgo_observado,

    ROUND(
        SUM(CASE WHEN flag_dificultad_pago = 1 THEN monto_credito ELSE 0 END)
        * 100.0 / NULLIF(SUM(monto_credito), 0),
        2
    ) AS porcentaje_exposicion_en_riesgo,

    ROUND(AVG(ratio_credito_ingreso), 4) AS ratio_credito_ingreso_promedio,
    ROUND(AVG(ratio_anualidad_ingreso), 4) AS ratio_anualidad_ingreso_promedio,
    ROUND(AVG(score_promedio_externo), 4) AS score_externo_promedio,

    ROUND(
        SUM(monto_credito * COALESCE(margen_esperado_producto, 0)),
        2
    ) AS margen_esperado_aproximado,

    DENSE_RANK() OVER (
        ORDER BY SUM(flag_dificultad_pago) * 1.0 / NULLIF(COUNT(*), 0) DESC
    ) AS ranking_riesgo,

    DENSE_RANK() OVER (
        ORDER BY SUM(monto_credito) DESC
    ) AS ranking_exposicion

FROM cst_data.cartera_clientes_train
GROUP BY
    id_filial,
    nombre_filial,
    zona_filial,
    tipo_filial,
    estado_filial;


-- =============================================================================
-- 2. Riesgo y gestión por producto
-- =============================================================================

CREATE OR REPLACE VIEW cst_data.vw_gestion_riesgo_producto AS
SELECT
    id_producto,
    nombre_producto,
    familia_producto,
    riesgo_esperado_producto,
    estado_producto,

    COUNT(*) AS total_clientes,
    SUM(CASE WHEN estado_asignacion = 'Activa' THEN 1 ELSE 0 END) AS clientes_activos,
    SUM(flag_dificultad_pago) AS clientes_con_dificultad_pago,

    ROUND(SUM(flag_dificultad_pago) * 100.0 / NULLIF(COUNT(*), 0), 2) AS tasa_dificultad_pago_pct,

    ROUND(SUM(monto_credito), 2) AS exposicion_credito_total,
    ROUND(AVG(monto_credito), 2) AS monto_credito_promedio,

    ROUND(
        SUM(CASE WHEN flag_dificultad_pago = 1 THEN monto_credito ELSE 0 END),
        2
    ) AS monto_en_riesgo_observado,

    ROUND(
        SUM(CASE WHEN flag_dificultad_pago = 1 THEN monto_credito ELSE 0 END)
        * 100.0 / NULLIF(SUM(monto_credito), 0),
        2
    ) AS porcentaje_exposicion_en_riesgo,

    ROUND(AVG(ratio_credito_ingreso), 4) AS ratio_credito_ingreso_promedio,
    ROUND(AVG(ratio_anualidad_ingreso), 4) AS ratio_anualidad_ingreso_promedio,
    ROUND(AVG(score_promedio_externo), 4) AS score_externo_promedio,

    ROUND(AVG(margen_esperado_producto), 4) AS margen_esperado_promedio,

    ROUND(
        SUM(monto_credito * COALESCE(margen_esperado_producto, 0)),
        2
    ) AS margen_esperado_aproximado,

    DENSE_RANK() OVER (
        ORDER BY SUM(flag_dificultad_pago) * 1.0 / NULLIF(COUNT(*), 0) DESC
    ) AS ranking_riesgo,

    DENSE_RANK() OVER (
        ORDER BY SUM(monto_credito) DESC
    ) AS ranking_exposicion

FROM cst_data.cartera_clientes_train
GROUP BY
    id_producto,
    nombre_producto,
    familia_producto,
    riesgo_esperado_producto,
    estado_producto;


-- =============================================================================
-- 3. Riesgo y gestión por canal
-- =============================================================================

CREATE OR REPLACE VIEW cst_data.vw_gestion_riesgo_canal AS
SELECT
    id_canal,
    nombre_canal,
    tipo_canal,

    COUNT(*) AS total_clientes,
    SUM(CASE WHEN estado_asignacion = 'Activa' THEN 1 ELSE 0 END) AS clientes_activos,
    SUM(flag_dificultad_pago) AS clientes_con_dificultad_pago,

    ROUND(SUM(flag_dificultad_pago) * 100.0 / NULLIF(COUNT(*), 0), 2) AS tasa_dificultad_pago_pct,

    ROUND(SUM(monto_credito), 2) AS exposicion_credito_total,
    ROUND(AVG(monto_credito), 2) AS monto_credito_promedio,

    ROUND(
        SUM(CASE WHEN flag_dificultad_pago = 1 THEN monto_credito ELSE 0 END),
        2
    ) AS monto_en_riesgo_observado,

    ROUND(
        SUM(CASE WHEN flag_dificultad_pago = 1 THEN monto_credito ELSE 0 END)
        * 100.0 / NULLIF(SUM(monto_credito), 0),
        2
    ) AS porcentaje_exposicion_en_riesgo,

    ROUND(AVG(ratio_credito_ingreso), 4) AS ratio_credito_ingreso_promedio,
    ROUND(AVG(ratio_anualidad_ingreso), 4) AS ratio_anualidad_ingreso_promedio,
    ROUND(AVG(score_promedio_externo), 4) AS score_externo_promedio,

    ROUND(
        SUM(monto_credito * COALESCE(margen_esperado_producto, 0)),
        2
    ) AS margen_esperado_aproximado,

    DENSE_RANK() OVER (
        ORDER BY SUM(flag_dificultad_pago) * 1.0 / NULLIF(COUNT(*), 0) DESC
    ) AS ranking_riesgo,

    DENSE_RANK() OVER (
        ORDER BY SUM(monto_credito) DESC
    ) AS ranking_exposicion

FROM cst_data.cartera_clientes_train
GROUP BY
    id_canal,
    nombre_canal,
    tipo_canal;


-- =============================================================================
-- 4. Riesgo y gestión por segmento
-- =============================================================================

CREATE OR REPLACE VIEW cst_data.vw_gestion_riesgo_segmento AS
SELECT
    id_segmento,
    nombre_segmento,
    perfil_riesgo_segmento,
    rango_ingreso_estimado,

    COUNT(*) AS total_clientes,
    SUM(CASE WHEN estado_asignacion = 'Activa' THEN 1 ELSE 0 END) AS clientes_activos,
    SUM(flag_dificultad_pago) AS clientes_con_dificultad_pago,

    ROUND(SUM(flag_dificultad_pago) * 100.0 / NULLIF(COUNT(*), 0), 2) AS tasa_dificultad_pago_pct,

    ROUND(SUM(monto_credito), 2) AS exposicion_credito_total,
    ROUND(AVG(monto_credito), 2) AS monto_credito_promedio,

    ROUND(
        SUM(CASE WHEN flag_dificultad_pago = 1 THEN monto_credito ELSE 0 END),
        2
    ) AS monto_en_riesgo_observado,

    ROUND(
        SUM(CASE WHEN flag_dificultad_pago = 1 THEN monto_credito ELSE 0 END)
        * 100.0 / NULLIF(SUM(monto_credito), 0),
        2
    ) AS porcentaje_exposicion_en_riesgo,

    ROUND(AVG(ratio_credito_ingreso), 4) AS ratio_credito_ingreso_promedio,
    ROUND(AVG(ratio_anualidad_ingreso), 4) AS ratio_anualidad_ingreso_promedio,
    ROUND(AVG(score_promedio_externo), 4) AS score_externo_promedio,

    ROUND(
        SUM(monto_credito * COALESCE(margen_esperado_producto, 0)),
        2
    ) AS margen_esperado_aproximado,

    DENSE_RANK() OVER (
        ORDER BY SUM(flag_dificultad_pago) * 1.0 / NULLIF(COUNT(*), 0) DESC
    ) AS ranking_riesgo,

    DENSE_RANK() OVER (
        ORDER BY SUM(monto_credito) DESC
    ) AS ranking_exposicion

FROM cst_data.cartera_clientes_train
GROUP BY
    id_segmento,
    nombre_segmento,
    perfil_riesgo_segmento,
    rango_ingreso_estimado;