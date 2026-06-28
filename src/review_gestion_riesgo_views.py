import duckdb

from src.config import DATABASE_PATH


def print_section(title: str) -> None:
    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


def print_query(con: duckdb.DuckDBPyConnection, title: str, query: str) -> None:
    print_section(title)
    df = con.execute(query).fetchdf()

    if df.empty:
        print("Sin resultados.")
    else:
        print(df.to_string(index=False))


def main() -> None:
    with duckdb.connect(DATABASE_PATH) as con:
        print_query(
            con,
            "1. Gestión de riesgo por filial",
            """
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
                margen_esperado_aproximado,
                ranking_riesgo,
                ranking_exposicion
            FROM cst_data.vw_gestion_riesgo_filial
            ORDER BY ranking_riesgo, ranking_exposicion;
            """,
        )

        print_query(
            con,
            "2. Gestión de riesgo por producto",
            """
            SELECT
                id_producto,
                nombre_producto,
                familia_producto,
                riesgo_esperado_producto,
                total_clientes,
                clientes_con_dificultad_pago,
                tasa_dificultad_pago_pct,
                exposicion_credito_total,
                monto_en_riesgo_observado,
                porcentaje_exposicion_en_riesgo,
                margen_esperado_aproximado,
                ranking_riesgo,
                ranking_exposicion
            FROM cst_data.vw_gestion_riesgo_producto
            ORDER BY ranking_riesgo, ranking_exposicion;
            """,
        )

        print_query(
            con,
            "3. Gestión de riesgo por canal",
            """
            SELECT
                id_canal,
                nombre_canal,
                tipo_canal,
                total_clientes,
                clientes_con_dificultad_pago,
                tasa_dificultad_pago_pct,
                exposicion_credito_total,
                monto_en_riesgo_observado,
                porcentaje_exposicion_en_riesgo,
                margen_esperado_aproximado,
                ranking_riesgo,
                ranking_exposicion
            FROM cst_data.vw_gestion_riesgo_canal
            ORDER BY ranking_riesgo, ranking_exposicion;
            """,
        )

        print_query(
            con,
            "4. Gestión de riesgo por segmento",
            """
            SELECT
                id_segmento,
                nombre_segmento,
                perfil_riesgo_segmento,
                rango_ingreso_estimado,
                total_clientes,
                clientes_con_dificultad_pago,
                tasa_dificultad_pago_pct,
                exposicion_credito_total,
                monto_en_riesgo_observado,
                porcentaje_exposicion_en_riesgo,
                margen_esperado_aproximado,
                ranking_riesgo,
                ranking_exposicion
            FROM cst_data.vw_gestion_riesgo_segmento
            ORDER BY ranking_riesgo, ranking_exposicion;
            """,
        )

        print_query(
            con,
            "5. Resumen ejecutivo general",
            """
            SELECT
                COUNT(*) AS total_clientes,
                SUM(flag_dificultad_pago) AS clientes_con_dificultad_pago,
                ROUND(SUM(flag_dificultad_pago) * 100.0 / COUNT(*), 2) AS tasa_dificultad_pago_pct,
                ROUND(SUM(monto_credito), 2) AS exposicion_credito_total,
                ROUND(SUM(CASE WHEN flag_dificultad_pago = 1 THEN monto_credito ELSE 0 END), 2) AS monto_en_riesgo_observado,
                ROUND(
                    SUM(CASE WHEN flag_dificultad_pago = 1 THEN monto_credito ELSE 0 END)
                    * 100.0 / NULLIF(SUM(monto_credito), 0),
                    2
                ) AS porcentaje_exposicion_en_riesgo,
                ROUND(AVG(ratio_credito_ingreso), 4) AS ratio_credito_ingreso_promedio,
                ROUND(AVG(score_promedio_externo), 4) AS score_externo_promedio
            FROM cst_data.cartera_clientes_train;
            """,
        )


if __name__ == "__main__":
    main()