-- =============================================================================
-- Proyecto: Analítica Financiera y Riesgo
-- Fase 3: Creación de capa std_data
-- Archivo: sql/02_std/01_create_std_core.sql
--
-- Decisiones aplicadas:
-- 1. Alcance inicial: tablas principales.
-- 2. Enfoque mixto:
--    - Tablas físicas para datos centrales.
--    - Vistas para dimensiones pequeñas.
-- 3. Conversión mixta:
--    - CAST para llaves y campos críticos.
--    - TRY_CAST para variables analíticas.
-- 4. Nombres en español, snake_case, sin tildes.
-- =============================================================================


-- =============================================================================
-- 1. TABLA FÍSICA: std_data.application_train
-- =============================================================================

DROP TABLE IF EXISTS std_data.application_train;

CREATE TABLE std_data.application_train AS
SELECT
    CAST(SK_ID_CURR AS BIGINT) AS id_cliente,
    CAST(TARGET AS INTEGER) AS flag_dificultad_pago,

    TRIM(NAME_CONTRACT_TYPE) AS tipo_contrato,
    TRIM(CODE_GENDER) AS genero,

    CASE
        WHEN UPPER(TRIM(FLAG_OWN_CAR)) = 'Y' THEN TRUE
        WHEN UPPER(TRIM(FLAG_OWN_CAR)) = 'N' THEN FALSE
        ELSE NULL
    END AS flag_tiene_auto,

    CASE
        WHEN UPPER(TRIM(FLAG_OWN_REALTY)) = 'Y' THEN TRUE
        WHEN UPPER(TRIM(FLAG_OWN_REALTY)) = 'N' THEN FALSE
        ELSE NULL
    END AS flag_tiene_propiedad,

    TRY_CAST(CNT_CHILDREN AS INTEGER) AS cantidad_hijos,
    TRY_CAST(AMT_INCOME_TOTAL AS DOUBLE) AS ingreso_total,
    TRY_CAST(AMT_CREDIT AS DOUBLE) AS monto_credito,
    TRY_CAST(AMT_ANNUITY AS DOUBLE) AS monto_anualidad,
    TRY_CAST(AMT_GOODS_PRICE AS DOUBLE) AS monto_bien,

    TRY_CAST(DAYS_BIRTH AS INTEGER) AS dias_nacimiento_relativo,
    TRY_CAST(DAYS_EMPLOYED AS INTEGER) AS dias_empleo_relativo,
    TRY_CAST(DAYS_REGISTRATION AS DOUBLE) AS dias_registro_relativo,
    TRY_CAST(DAYS_ID_PUBLISH AS INTEGER) AS dias_publicacion_id_relativo,

    TRIM(NAME_TYPE_SUITE) AS tipo_acompanante,
    TRIM(NAME_INCOME_TYPE) AS tipo_ingreso,
    TRIM(NAME_EDUCATION_TYPE) AS nivel_educacional,
    TRIM(NAME_FAMILY_STATUS) AS estado_civil,
    TRIM(NAME_HOUSING_TYPE) AS tipo_vivienda,
    TRIM(OCCUPATION_TYPE) AS ocupacion,
    TRIM(ORGANIZATION_TYPE) AS tipo_organizacion,

    TRY_CAST(CNT_FAM_MEMBERS AS DOUBLE) AS cantidad_integrantes_familia,
    TRY_CAST(REGION_POPULATION_RELATIVE AS DOUBLE) AS poblacion_region_relativa,
    TRY_CAST(OWN_CAR_AGE AS DOUBLE) AS antiguedad_auto_anios,

    TRY_CAST(EXT_SOURCE_1 AS DOUBLE) AS score_externo_1,
    TRY_CAST(EXT_SOURCE_2 AS DOUBLE) AS score_externo_2,
    TRY_CAST(EXT_SOURCE_3 AS DOUBLE) AS score_externo_3,

    CURRENT_TIMESTAMP AS fecha_carga_std

FROM raw_data.application_train;


-- =============================================================================
-- 2. TABLA FÍSICA: std_data.application_test
-- =============================================================================

DROP TABLE IF EXISTS std_data.application_test;

CREATE TABLE std_data.application_test AS
SELECT
    CAST(SK_ID_CURR AS BIGINT) AS id_cliente,

    TRIM(NAME_CONTRACT_TYPE) AS tipo_contrato,
    TRIM(CODE_GENDER) AS genero,

    CASE
        WHEN UPPER(TRIM(FLAG_OWN_CAR)) = 'Y' THEN TRUE
        WHEN UPPER(TRIM(FLAG_OWN_CAR)) = 'N' THEN FALSE
        ELSE NULL
    END AS flag_tiene_auto,

    CASE
        WHEN UPPER(TRIM(FLAG_OWN_REALTY)) = 'Y' THEN TRUE
        WHEN UPPER(TRIM(FLAG_OWN_REALTY)) = 'N' THEN FALSE
        ELSE NULL
    END AS flag_tiene_propiedad,

    TRY_CAST(CNT_CHILDREN AS INTEGER) AS cantidad_hijos,
    TRY_CAST(AMT_INCOME_TOTAL AS DOUBLE) AS ingreso_total,
    TRY_CAST(AMT_CREDIT AS DOUBLE) AS monto_credito,
    TRY_CAST(AMT_ANNUITY AS DOUBLE) AS monto_anualidad,
    TRY_CAST(AMT_GOODS_PRICE AS DOUBLE) AS monto_bien,

    TRY_CAST(DAYS_BIRTH AS INTEGER) AS dias_nacimiento_relativo,
    TRY_CAST(DAYS_EMPLOYED AS INTEGER) AS dias_empleo_relativo,
    TRY_CAST(DAYS_REGISTRATION AS DOUBLE) AS dias_registro_relativo,
    TRY_CAST(DAYS_ID_PUBLISH AS INTEGER) AS dias_publicacion_id_relativo,

    TRIM(NAME_TYPE_SUITE) AS tipo_acompanante,
    TRIM(NAME_INCOME_TYPE) AS tipo_ingreso,
    TRIM(NAME_EDUCATION_TYPE) AS nivel_educacional,
    TRIM(NAME_FAMILY_STATUS) AS estado_civil,
    TRIM(NAME_HOUSING_TYPE) AS tipo_vivienda,
    TRIM(OCCUPATION_TYPE) AS ocupacion,
    TRIM(ORGANIZATION_TYPE) AS tipo_organizacion,

    TRY_CAST(CNT_FAM_MEMBERS AS DOUBLE) AS cantidad_integrantes_familia,
    TRY_CAST(REGION_POPULATION_RELATIVE AS DOUBLE) AS poblacion_region_relativa,
    TRY_CAST(OWN_CAR_AGE AS DOUBLE) AS antiguedad_auto_anios,

    TRY_CAST(EXT_SOURCE_1 AS DOUBLE) AS score_externo_1,
    TRY_CAST(EXT_SOURCE_2 AS DOUBLE) AS score_externo_2,
    TRY_CAST(EXT_SOURCE_3 AS DOUBLE) AS score_externo_3,

    CURRENT_TIMESTAMP AS fecha_carga_std

FROM raw_data.application_test;


-- =============================================================================
-- 3. TABLA FÍSICA: std_data.fact_asignacion_cartera
-- =============================================================================

DROP TABLE IF EXISTS std_data.fact_asignacion_cartera;

CREATE TABLE std_data.fact_asignacion_cartera AS
SELECT
    CAST(SK_ID_CURR AS BIGINT) AS id_cliente,

    TRIM(id_filial) AS id_filial,
    TRIM(id_sucursal) AS id_sucursal,
    TRIM(id_ejecutivo) AS id_ejecutivo,
    TRIM(id_producto) AS id_producto,
    TRIM(id_canal) AS id_canal,
    TRIM(id_segmento) AS id_segmento,

    TRY_CAST(fecha_asignacion AS DATE) AS fecha_asignacion,
    TRIM(estado_asignacion) AS estado_asignacion,

    CURRENT_TIMESTAMP AS fecha_carga_std

FROM raw_data.fact_asignacion_cartera;


-- =============================================================================
-- 4. VISTAS ESTANDARIZADAS: dimensiones corporativas
-- =============================================================================

CREATE OR REPLACE VIEW std_data.dim_filial AS
SELECT *
FROM raw_data.dim_filial;


CREATE OR REPLACE VIEW std_data.dim_sucursal AS
SELECT *
FROM raw_data.dim_sucursal;


CREATE OR REPLACE VIEW std_data.dim_ejecutivo AS
SELECT *
FROM raw_data.dim_ejecutivo;


CREATE OR REPLACE VIEW std_data.dim_producto AS
SELECT *
FROM raw_data.dim_producto;


CREATE OR REPLACE VIEW std_data.dim_canal AS
SELECT *
FROM raw_data.dim_canal;


CREATE OR REPLACE VIEW std_data.dim_segmento AS
SELECT *
FROM raw_data.dim_segmento;