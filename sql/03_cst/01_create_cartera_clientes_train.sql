-- =============================================================================
-- Proyecto: Analítica Financiera y Riesgo
-- Fase 3: Creación de capa cst_data
-- Archivo: sql/03_cst/01_create_cartera_clientes_train.sql
--
-- Objetivo:
-- Crear una tabla curada e integrada de cartera de clientes de entrenamiento,
-- uniendo información crediticia, asignación de cartera y dimensiones corporativas.
--
-- Decisiones aplicadas:
-- 1. cst_data integrada cliente + cartera corporativa.
-- 2. Tabla física principal.
-- 3. Tratamiento analítico de problemas conocidos.
-- 4. Variables derivadas listas para análisis, KPIs y ML.
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS cst_data;

DROP TABLE IF EXISTS cst_data.cartera_clientes_train;

CREATE TABLE cst_data.cartera_clientes_train AS
WITH clientes_base AS (
    SELECT
        id_cliente,
        flag_dificultad_pago,

        tipo_contrato,

        CASE
            WHEN genero = 'XNA' OR genero IS NULL THEN 'Sin informacion'
            ELSE genero
        END AS genero_limpio,

        flag_tiene_auto,
        flag_tiene_propiedad,
        cantidad_hijos,
        ingreso_total,
        monto_credito,
        monto_anualidad,
        monto_bien,

        dias_nacimiento_relativo,
        dias_empleo_relativo,
        dias_registro_relativo,
        dias_publicacion_id_relativo,

        tipo_acompanante,
        tipo_ingreso,
        nivel_educacional,

        CASE
            WHEN estado_civil = 'Unknown' OR estado_civil IS NULL THEN 'Sin informacion'
            ELSE estado_civil
        END AS estado_civil_limpio,

        tipo_vivienda,

        COALESCE(NULLIF(TRIM(ocupacion), ''), 'Sin informacion') AS ocupacion_limpia,

        tipo_organizacion,
        cantidad_integrantes_familia,
        poblacion_region_relativa,
        antiguedad_auto_anios,

        score_externo_1,
        score_externo_2,
        score_externo_3,

        fecha_carga_std

    FROM std_data.application_train
),

clientes_curados AS (
    SELECT
        *,

        ROUND(ABS(dias_nacimiento_relativo) / 365.25, 2) AS edad_anios,

        CASE
            WHEN ROUND(ABS(dias_nacimiento_relativo) / 365.25, 2) < 25 THEN 'Menor a 25'
            WHEN ROUND(ABS(dias_nacimiento_relativo) / 365.25, 2) < 35 THEN '25 a 34'
            WHEN ROUND(ABS(dias_nacimiento_relativo) / 365.25, 2) < 45 THEN '35 a 44'
            WHEN ROUND(ABS(dias_nacimiento_relativo) / 365.25, 2) < 55 THEN '45 a 54'
            WHEN ROUND(ABS(dias_nacimiento_relativo) / 365.25, 2) < 65 THEN '55 a 64'
            ELSE '65 o mas'
        END AS grupo_edad,

        CASE
            WHEN dias_empleo_relativo = 365243 THEN TRUE
            ELSE FALSE
        END AS flag_empleo_valor_especial,

        CASE
            WHEN dias_empleo_relativo = 365243 THEN NULL
            WHEN dias_empleo_relativo IS NULL THEN NULL
            WHEN dias_empleo_relativo <= 0 THEN ROUND(ABS(dias_empleo_relativo) / 365.25, 2)
            ELSE NULL
        END AS antiguedad_laboral_anios,

        CASE
            WHEN ingreso_total IS NULL THEN 'Sin informacion'
            WHEN ingreso_total < 100000 THEN 'Menor a 100k'
            WHEN ingreso_total < 200000 THEN '100k a 199k'
            WHEN ingreso_total < 400000 THEN '200k a 399k'
            WHEN ingreso_total < 800000 THEN '400k a 799k'
            ELSE '800k o mas'
        END AS tramo_ingreso,

        CASE
            WHEN monto_credito IS NULL THEN 'Sin informacion'
            WHEN monto_credito < 200000 THEN 'Menor a 200k'
            WHEN monto_credito < 500000 THEN '200k a 499k'
            WHEN monto_credito < 1000000 THEN '500k a 999k'
            WHEN monto_credito < 2000000 THEN '1MM a 1.99MM'
            ELSE '2MM o mas'
        END AS tramo_monto_credito,

        CASE
            WHEN ingreso_total IS NOT NULL AND ingreso_total > 0
                THEN ROUND(monto_credito / ingreso_total, 4)
            ELSE NULL
        END AS ratio_credito_ingreso,

        CASE
            WHEN ingreso_total IS NOT NULL AND ingreso_total > 0
                THEN ROUND(monto_anualidad / ingreso_total, 4)
            ELSE NULL
        END AS ratio_anualidad_ingreso,

        CASE
            WHEN monto_bien IS NOT NULL AND monto_bien > 0
                THEN ROUND(monto_credito / monto_bien, 4)
            ELSE NULL
        END AS ratio_credito_bien,

        CASE WHEN score_externo_1 IS NULL THEN TRUE ELSE FALSE END AS flag_score_externo_1_nulo,
        CASE WHEN score_externo_2 IS NULL THEN TRUE ELSE FALSE END AS flag_score_externo_2_nulo,
        CASE WHEN score_externo_3 IS NULL THEN TRUE ELSE FALSE END AS flag_score_externo_3_nulo,

        (
            CASE WHEN score_externo_1 IS NOT NULL THEN 1 ELSE 0 END
          + CASE WHEN score_externo_2 IS NOT NULL THEN 1 ELSE 0 END
          + CASE WHEN score_externo_3 IS NOT NULL THEN 1 ELSE 0 END
        ) AS cantidad_scores_disponibles,

        CASE
            WHEN (
                CASE WHEN score_externo_1 IS NOT NULL THEN 1 ELSE 0 END
              + CASE WHEN score_externo_2 IS NOT NULL THEN 1 ELSE 0 END
              + CASE WHEN score_externo_3 IS NOT NULL THEN 1 ELSE 0 END
            ) = 0 THEN NULL
            ELSE ROUND(
                (
                    COALESCE(score_externo_1, 0)
                  + COALESCE(score_externo_2, 0)
                  + COALESCE(score_externo_3, 0)
                )
                /
                (
                    CASE WHEN score_externo_1 IS NOT NULL THEN 1 ELSE 0 END
                  + CASE WHEN score_externo_2 IS NOT NULL THEN 1 ELSE 0 END
                  + CASE WHEN score_externo_3 IS NOT NULL THEN 1 ELSE 0 END
                ),
                6
            )
        END AS score_promedio_externo,

        CASE
            WHEN flag_dificultad_pago = 1 THEN 'Con dificultad de pago'
            WHEN flag_dificultad_pago = 0 THEN 'Sin dificultad de pago'
            ELSE 'Sin informacion'
        END AS estado_riesgo_observado

    FROM clientes_base
)

SELECT
    c.id_cliente,
    c.flag_dificultad_pago,
    c.estado_riesgo_observado,

    c.tipo_contrato,
    c.genero_limpio,
    c.estado_civil_limpio,
    c.tipo_ingreso,
    c.nivel_educacional,
    c.tipo_vivienda,
    c.ocupacion_limpia,
    c.tipo_organizacion,
    c.tipo_acompanante,

    c.flag_tiene_auto,
    c.flag_tiene_propiedad,
    c.cantidad_hijos,
    c.cantidad_integrantes_familia,

    c.ingreso_total,
    c.monto_credito,
    c.monto_anualidad,
    c.monto_bien,

    c.edad_anios,
    c.grupo_edad,
    c.antiguedad_laboral_anios,
    c.flag_empleo_valor_especial,
    c.antiguedad_auto_anios,

    c.tramo_ingreso,
    c.tramo_monto_credito,
    c.ratio_credito_ingreso,
    c.ratio_anualidad_ingreso,
    c.ratio_credito_bien,

    c.score_externo_1,
    c.score_externo_2,
    c.score_externo_3,
    c.score_promedio_externo,
    c.cantidad_scores_disponibles,
    c.flag_score_externo_1_nulo,
    c.flag_score_externo_2_nulo,
    c.flag_score_externo_3_nulo,

    c.poblacion_region_relativa,

    a.fecha_asignacion,
    a.estado_asignacion,

    a.id_filial,
    f.nombre_filial,
    f.zona AS zona_filial,
    f.tipo_filial,
    TRY_CAST(f.fecha_inicio_operacion AS DATE) AS fecha_inicio_operacion_filial,
    f.estado_filial,

    a.id_sucursal,
    s.nombre_sucursal,
    s.region AS region_sucursal,
    s.ciudad AS ciudad_sucursal,
    s.estado_sucursal,

    a.id_ejecutivo,
    e.nombre_ejecutivo,
    e.cargo AS cargo_ejecutivo,
    TRY_CAST(e.fecha_ingreso AS DATE) AS fecha_ingreso_ejecutivo,
    e.estado_ejecutivo,

    a.id_producto,
    p.nombre_producto,
    COALESCE(NULLIF(TRIM(p.familia_producto), ''), 'Sin informacion') AS familia_producto,
    TRY_CAST(p.margen_esperado AS DOUBLE) AS margen_esperado_producto,
    p.riesgo_esperado AS riesgo_esperado_producto,
    p.estado_producto,

    a.id_canal,
    ca.nombre_canal,
    ca.tipo_canal,

    a.id_segmento,
    sg.nombre_segmento,
    sg.perfil_riesgo AS perfil_riesgo_segmento,
    sg.rango_ingreso_estimado,

    CURRENT_TIMESTAMP AS fecha_carga_cst

FROM clientes_curados c
LEFT JOIN std_data.fact_asignacion_cartera a
    ON c.id_cliente = a.id_cliente
LEFT JOIN std_data.dim_filial f
    ON a.id_filial = f.id_filial
LEFT JOIN std_data.dim_sucursal s
    ON a.id_sucursal = s.id_sucursal
LEFT JOIN std_data.dim_ejecutivo e
    ON a.id_ejecutivo = e.id_ejecutivo
LEFT JOIN std_data.dim_producto p
    ON a.id_producto = p.id_producto
LEFT JOIN std_data.dim_canal ca
    ON a.id_canal = ca.id_canal
LEFT JOIN std_data.dim_segmento sg
    ON a.id_segmento = sg.id_segmento;