import duckdb

from src.config import DATABASE_PATH


def print_section(title: str) -> None:
    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


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
            "1. Distribución de flag_dificultad_pago",
            """
            SELECT
                flag_dificultad_pago,
                cantidad,
                ROUND(porcentaje * 100, 2) AS porcentaje
            FROM data_quality.perfil_target_std
            ORDER BY flag_dificultad_pago;
            """,
        )

        print_query(
            con,
            "2. Columnas con mayor porcentaje de nulos",
            """
            SELECT
                tabla,
                columna,
                tipo_dato,
                total_filas,
                nulos,
                ROUND(porcentaje_nulos * 100, 2) AS porcentaje_nulos
            FROM data_quality.perfil_nulos_std
            WHERE nulos > 0
            ORDER BY porcentaje_nulos DESC, nulos DESC
            LIMIT 25;
            """,
        )

        print_query(
            con,
            "3. Diferencias de nulos entre application_train y application_test",
            """
            SELECT
                columna,
                ROUND(porcentaje_nulos_train * 100, 2) AS pct_nulos_train,
                ROUND(porcentaje_nulos_test * 100, 2) AS pct_nulos_test,
                ROUND(diferencia_porcentaje_nulos * 100, 2) AS diferencia_pct_test_menos_train
            FROM data_quality.comparacion_nulos_train_test_std
            WHERE ABS(diferencia_porcentaje_nulos) > 0.5 / 100
            ORDER BY ABS(diferencia_porcentaje_nulos) DESC
            LIMIT 25;
            """,
        )

        print_query(
            con,
            "4. Variables numéricas con valores negativos",
            """
            SELECT
                tabla,
                columna,
                tipo_dato,
                cantidad_negativos,
                minimo,
                p25,
                mediana,
                p75,
                maximo
            FROM data_quality.perfil_numerico_std
            WHERE cantidad_negativos > 0
            ORDER BY cantidad_negativos DESC;
            """,
        )

        print_query(
            con,
            "5. Variables numéricas con ceros",
            """
            SELECT
                tabla,
                columna,
                cantidad_ceros,
                minimo,
                mediana,
                maximo
            FROM data_quality.perfil_numerico_std
            WHERE cantidad_ceros > 0
            ORDER BY cantidad_ceros DESC
            LIMIT 25;
            """,
        )

        print_query(
            con,
            "6. Resumen de montos principales",
            """
            SELECT
                tabla,
                columna,
                minimo,
                p25,
                promedio,
                mediana,
                p75,
                maximo,
                cantidad_ceros,
                cantidad_negativos
            FROM data_quality.perfil_numerico_std
            WHERE columna IN (
                'ingreso_total',
                'monto_credito',
                'monto_anualidad',
                'monto_bien',
                'score_externo_1',
                'score_externo_2',
                'score_externo_3'
            )
            ORDER BY tabla, columna;
            """,
        )

        print_query(
            con,
            "7. Categorías principales de variables relevantes",
            """
            SELECT
                tabla,
                columna,
                valor,
                cantidad,
                ROUND(porcentaje * 100, 2) AS porcentaje
            FROM data_quality.perfil_categorico_std
            WHERE columna IN (
                'tipo_contrato',
                'genero',
                'flag_tiene_auto',
                'flag_tiene_propiedad',
                'tipo_ingreso',
                'nivel_educacional',
                'estado_civil',
                'tipo_vivienda',
                'estado_asignacion'
            )
            ORDER BY tabla, columna, cantidad DESC;
            """,
        )

        print_query(
            con,
            "8. Control de asignación de cartera",
            """
            SELECT
                check_name,
                valor,
                detalle
            FROM data_quality.control_asignacion_cartera_std
            ORDER BY check_name;
            """,
        )


if __name__ == "__main__":
    main()