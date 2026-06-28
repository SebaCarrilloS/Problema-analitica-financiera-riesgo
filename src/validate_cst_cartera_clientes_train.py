import duckdb
import pandas as pd

from src.config import DATABASE_PATH, PROCESSED_DATA_DIR


VALIDATION_DIR = PROCESSED_DATA_DIR / "validaciones"
OUTPUT_PATH = VALIDATION_DIR / "validacion_cst_cartera_clientes_train.csv"


REQUIRED_COLUMNS = [
    "id_cliente",
    "flag_dificultad_pago",
    "estado_riesgo_observado",
    "edad_anios",
    "grupo_edad",
    "antiguedad_laboral_anios",
    "flag_empleo_valor_especial",
    "ratio_credito_ingreso",
    "ratio_anualidad_ingreso",
    "ratio_credito_bien",
    "score_promedio_externo",
    "cantidad_scores_disponibles",
    "id_filial",
    "nombre_filial",
    "id_sucursal",
    "nombre_sucursal",
    "id_ejecutivo",
    "nombre_ejecutivo",
    "id_producto",
    "nombre_producto",
    "familia_producto",
    "id_canal",
    "nombre_canal",
    "id_segmento",
    "nombre_segmento",
    "fecha_carga_cst",
]


def add_result(results: list[dict], check_name: str, status: str, detail: str) -> None:
    results.append(
        {
            "check_name": check_name,
            "status": status,
            "detail": detail,
        }
    )


def main() -> None:
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []

    with duckdb.connect(DATABASE_PATH) as con:
        # 1. Existe tabla
        table_exists = con.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'cst_data'
              AND table_name = 'cartera_clientes_train'
            """
        ).fetchone()[0]

        if table_exists == 0:
            add_result(
                results,
                "existe_cst_cartera_clientes_train",
                "ERROR",
                "No existe cst_data.cartera_clientes_train",
            )

            df = pd.DataFrame(results)
            df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
            print(df.to_string(index=False))
            raise SystemExit("Validación finalizó con errores.")

        add_result(
            results,
            "existe_cst_cartera_clientes_train",
            "OK",
            "Existe cst_data.cartera_clientes_train",
        )

        # 2. Conteo de filas vs application_train
        std_count = con.execute(
            "SELECT COUNT(*) FROM std_data.application_train"
        ).fetchone()[0]

        cst_count = con.execute(
            "SELECT COUNT(*) FROM cst_data.cartera_clientes_train"
        ).fetchone()[0]

        if std_count != cst_count:
            add_result(
                results,
                "conteo_filas_vs_application_train",
                "ERROR",
                f"std_data.application_train={std_count}, cst_data.cartera_clientes_train={cst_count}",
            )
        else:
            add_result(
                results,
                "conteo_filas_vs_application_train",
                "OK",
                f"Ambas tablas tienen {cst_count} filas",
            )

        # 3. Duplicados de cliente
        duplicate_clients = con.execute(
            """
            SELECT COUNT(*) - COUNT(DISTINCT id_cliente)
            FROM cst_data.cartera_clientes_train
            """
        ).fetchone()[0]

        if duplicate_clients > 0:
            add_result(
                results,
                "id_cliente_unico",
                "ERROR",
                f"Hay {duplicate_clients} duplicados de id_cliente",
            )
        else:
            add_result(
                results,
                "id_cliente_unico",
                "OK",
                "id_cliente sin duplicados",
            )

        # 4. Columnas requeridas
        columns = con.execute(
            "DESCRIBE cst_data.cartera_clientes_train"
        ).fetchdf()["column_name"].tolist()

        missing_columns = sorted(set(REQUIRED_COLUMNS) - set(columns))

        if missing_columns:
            add_result(
                results,
                "columnas_requeridas",
                "ERROR",
                f"Faltan columnas: {missing_columns}",
            )
        else:
            add_result(
                results,
                "columnas_requeridas",
                "OK",
                "Columnas requeridas presentes",
            )

        # 5. Clientes sin asignación corporativa
        missing_assignment = con.execute(
            """
            SELECT COUNT(*)
            FROM cst_data.cartera_clientes_train
            WHERE id_filial IS NULL
               OR id_sucursal IS NULL
               OR id_ejecutivo IS NULL
               OR id_producto IS NULL
               OR id_canal IS NULL
               OR id_segmento IS NULL
            """
        ).fetchone()[0]

        if missing_assignment > 0:
            add_result(
                results,
                "clientes_sin_asignacion_completa",
                "ERROR",
                f"{missing_assignment} clientes sin asignación corporativa completa",
            )
        else:
            add_result(
                results,
                "clientes_sin_asignacion_completa",
                "OK",
                "Todos los clientes tienen asignación corporativa completa",
            )

        # 6. Cruce con dimensiones
        dimension_checks = {
            "filial": "nombre_filial",
            "sucursal": "nombre_sucursal",
            "ejecutivo": "nombre_ejecutivo",
            "producto": "nombre_producto",
            "canal": "nombre_canal",
            "segmento": "nombre_segmento",
        }

        for dimension_name, column_name in dimension_checks.items():
            missing_dimension = con.execute(
                f"""
                SELECT COUNT(*)
                FROM cst_data.cartera_clientes_train
                WHERE {column_name} IS NULL
                """
            ).fetchone()[0]

            if missing_dimension > 0:
                add_result(
                    results,
                    f"cruce_dim_{dimension_name}",
                    "ERROR",
                    f"{missing_dimension} filas sin {column_name}",
                )
            else:
                add_result(
                    results,
                    f"cruce_dim_{dimension_name}",
                    "OK",
                    f"Cruce con dimensión {dimension_name} completo",
                )

        # 7. TARGET válido
        invalid_target = con.execute(
            """
            SELECT COUNT(*)
            FROM cst_data.cartera_clientes_train
            WHERE flag_dificultad_pago NOT IN (0, 1)
               OR flag_dificultad_pago IS NULL
            """
        ).fetchone()[0]

        if invalid_target > 0:
            add_result(
                results,
                "flag_dificultad_pago_valido",
                "ERROR",
                f"{invalid_target} filas con flag_dificultad_pago inválido",
            )
        else:
            add_result(
                results,
                "flag_dificultad_pago_valido",
                "OK",
                "flag_dificultad_pago contiene solo 0 y 1",
            )

        # 8. Edad razonable
        invalid_age = con.execute(
            """
            SELECT COUNT(*)
            FROM cst_data.cartera_clientes_train
            WHERE edad_anios IS NULL
               OR edad_anios < 18
               OR edad_anios > 100
            """
        ).fetchone()[0]

        if invalid_age > 0:
            add_result(
                results,
                "edad_anios_rango",
                "WARNING",
                f"{invalid_age} filas con edad nula o fuera de rango 18-100",
            )
        else:
            add_result(
                results,
                "edad_anios_rango",
                "OK",
                "edad_anios dentro de rango 18-100",
            )

        # 9. Tratamiento del valor especial de empleo
        untreated_special_employment = con.execute(
            """
            SELECT COUNT(*)
            FROM cst_data.cartera_clientes_train
            WHERE flag_empleo_valor_especial = TRUE
              AND antiguedad_laboral_anios IS NOT NULL
            """
        ).fetchone()[0]

        if untreated_special_employment > 0:
            add_result(
                results,
                "tratamiento_empleo_valor_especial",
                "ERROR",
                f"{untreated_special_employment} filas con valor especial de empleo no tratado",
            )
        else:
            add_result(
                results,
                "tratamiento_empleo_valor_especial",
                "OK",
                "Valor especial de empleo tratado correctamente",
            )

        # 10. Ratios negativos
        negative_ratios = con.execute(
            """
            SELECT COUNT(*)
            FROM cst_data.cartera_clientes_train
            WHERE ratio_credito_ingreso < 0
               OR ratio_anualidad_ingreso < 0
               OR ratio_credito_bien < 0
            """
        ).fetchone()[0]

        if negative_ratios > 0:
            add_result(
                results,
                "ratios_no_negativos",
                "ERROR",
                f"{negative_ratios} filas con ratios negativos",
            )
        else:
            add_result(
                results,
                "ratios_no_negativos",
                "OK",
                "Ratios financieros sin valores negativos",
            )

        # 11. Score promedio externo dentro de rango 0-1
        invalid_score_avg = con.execute(
            """
            SELECT COUNT(*)
            FROM cst_data.cartera_clientes_train
            WHERE score_promedio_externo IS NOT NULL
              AND (
                    score_promedio_externo < 0
                 OR score_promedio_externo > 1
              )
            """
        ).fetchone()[0]

        if invalid_score_avg > 0:
            add_result(
                results,
                "score_promedio_externo_rango",
                "ERROR",
                f"{invalid_score_avg} filas con score_promedio_externo fuera de rango 0-1",
            )
        else:
            add_result(
                results,
                "score_promedio_externo_rango",
                "OK",
                "score_promedio_externo dentro de rango 0-1",
            )

        # 12. Familias de producto sin información
        product_family_missing = con.execute(
            """
            SELECT COUNT(*)
            FROM cst_data.cartera_clientes_train
            WHERE familia_producto = 'Sin informacion'
            """
        ).fetchone()[0]

        if product_family_missing > 0:
            add_result(
                results,
                "familia_producto_sin_informacion",
                "WARNING",
                f"{product_family_missing} filas con familia_producto = 'Sin informacion'",
            )
        else:
            add_result(
                results,
                "familia_producto_sin_informacion",
                "OK",
                "familia_producto informada en todas las filas",
            )

    df_results = pd.DataFrame(results)
    df_results.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print(df_results.to_string(index=False))
    print()
    print(f"Validación guardada en: {OUTPUT_PATH}")

    error_count = (df_results["status"] == "ERROR").sum()
    warning_count = (df_results["status"] == "WARNING").sum()

    print()
    print(f"Errores: {error_count}")
    print(f"Warnings: {warning_count}")

    if error_count > 0:
        raise SystemExit("Validación cst_data finalizó con errores.")

    print("Validación cst_data completada correctamente.")


if __name__ == "__main__":
    main()