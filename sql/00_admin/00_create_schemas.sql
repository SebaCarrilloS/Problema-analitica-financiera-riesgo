-- ============================================================
-- Proyecto: Analítica Financiera de Riesgo y Rentabilidad
-- Archivo: 00_create_schemas.sql
-- Objetivo: Crear los schemas principales de la arquitectura analítica
-- Motor: DuckDB
-- ============================================================

CREATE SCHEMA IF NOT EXISTS raw_data;

CREATE SCHEMA IF NOT EXISTS std_data;

CREATE SCHEMA IF NOT EXISTS cst_data;

CREATE SCHEMA IF NOT EXISTS mart_financiero;

CREATE SCHEMA IF NOT EXISTS data_quality;