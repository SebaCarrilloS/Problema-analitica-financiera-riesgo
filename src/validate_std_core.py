from pathlib import Path

import duckdb
import pandas as pd

from src.config import DATABASE_PATH, PROCESSED_DATA_DIR


VALIDATION_DIR = PROCESSED_DATA_DIR / "validaciones"
OUTPUT_PATH = VALIDATION_DIR / "validacion_std_core.csv"


EXPECTED_OBJECTS = {
    "application_train": "BASE TABLE",
    "application_test": "BASE TABLE",
    "fact_asignacion_cartera": "BASE TABLE",
    "dim_filial": "VIEW",
    "dim_sucursal": "VIEW",
    "dim_ejecutivo": "VIEW",
    "dim_producto": "VIEW",
    "dim_canal": "VIEW",
    "dim_segmento": "VIEW",
}


REQUIRED_COLUMNS = {
    "application_train": [
        "id_cliente",
        "flag_dificultad_pago",
        "tipo_contrato",
        "genero",
        "flag_tiene_auto",
        "flag_tiene_propiedad",
        "cantidad_hijos",
        "ingreso_total",
        "monto_credito",
        "monto_anualidad",
        "monto_bien",
        "dias_nacimiento_relativo",
        "dias_empleo_relativo",
        "tipo_ingreso",
        "nivel_educacional",
        "estado_civil",
        "tipo_vivienda",
        "ocupacion",
        "tipo_organizacion",
        "score_externo_1",
        "score_externo_2",
        "score_externo_3",
        "fecha_carga_std",
    ],
    "application_test": [
        "id_cliente",
        "tipo_contrato",
        "genero",
        "flag_tiene_auto",
        "flag_tiene_propiedad",
        "cantidad_hijos",
        "ingreso_total",
        "monto_credito",
        "monto_anualidad",
        "monto_bien",
        "dias_nacimiento_relativo",
        "dias_empleo_relativo",
        "tipo_ingreso",
        "nivel_educacional",
        "estado_civil",
        "tipo_vivienda",
        "ocupacion",
        "tipo_organizacion",
        "score_externo_1",
        "score_externo_2",
        "score_externo_3",
        "fecha_carga_std",
    ],
    "fact_asignacion_cartera": [
        "id_cliente",
        "id_filial",
        "id_sucursal",
        "id_ejecutivo",
        "id_producto",
        "id_canal",
        "id_segmento",
        "fecha_asignacion",
        "estado_asignacion",
        "fecha_carga_std",
    ],
}


def add_result(results: list[dict], check_name: str, status: str, detail: str) -> None:
    results.append(
        {
            "check_name": check_name,
            "status": status,
            "detail": detail,
        }
    )


def table_exists(con: duckdb.DuckDBPyConnection, table_name: str) -> str | None:
    query = """
    SELECT table_type
    FROM information_schema.tables
    WHERE table_schema = 'std_data'
      AND table_name = ?
    """
    row = con.execute(query, [table_name]).fetchone()
    return row[0] if row else None


def count_rows(con: duckdb.DuckDBPyConnection, full_table_name: str) -> int:
    return con.execute(f"SELECT COUNT(*) FROM {full_table_name}").fetchone()[0]


def get_columns(con: duckdb.DuckDBPyConnection, full_table_name: str) -> set[str]:
    df = con.execute(f"DESCRIBE {full_table_name}").fetchdf()
    return set(df["column_name"].tolist())


def main() -> None:
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []

    with duckdb.connect(DATABASE_PATH) as con:
        # 1. Validar existencia y tipo de objetos
        for table_name, expected_type in EXPECTED_OBJECTS.items():
            actual_type = table_exists(con, table_name)

            if actual_type is None:
                add_result(
                    results,
                    f"existe_std_data_{table_name}",
                    "ERROR",
                    f"No existe std_data.{table_name}",
                )
            elif actual_type != expected_type:
                add_result(
                    results,
                    f"tipo_objeto_std_data_{table_name}",
                    "ERROR",
                    f"std_data.{table_name} es {actual_type}, se esperaba {expected_type}",
                )
            else:
                add_result(
                    results,
                    f"tipo_objeto_std_data_{table_name}",
                    "OK",
                    f"std_data.{table_name} existe como {actual_type}",
                )

        # 2. Validar conteos entre raw y std para tablas físicas
        tables_to_compare = [
            "application_train",
            "application_test",
            "fact_asignacion_cartera",
        ]

        for table_name in tables_to_compare:
            raw_count = count_rows(con, f"raw_data.{table_name}")
            std_count = count_rows(con, f"std_data.{table_name}")

            if raw_count != std_count:
                add_result(
                    results,
                    f"conteo_filas_{table_name}",
                    "ERROR",
                    f"raw={raw_count}, std={std_count}",
                )
            else:
                add_result(
                    results,
                    f"conteo_filas_{table_name}",
                    "OK",
                    f"raw={raw_count}, std={std_count}",
                )

        # 3. Validar columnas requeridas
        for table_name, required_columns in REQUIRED_COLUMNS.items():
            actual_columns = get_columns(con, f"std_data.{table_name}")
            missing_columns = sorted(set(required_columns) - actual_columns)

            if missing_columns:
                add_result(
                    results,
                    f"columnas_requeridas_{table_name}",
                    "ERROR",
                    f"Faltan columnas: {missing_columns}",
                )
            else:
                add_result(
                    results,
                    f"columnas_requeridas_{table_name}",
                    "OK",
                    "Columnas requeridas presentes",
                )

        # 4. Validar llaves principales no nulas
        for table_name in tables_to_compare:
            null_ids = con.execute(
                f"""
                SELECT COUNT(*)
                FROM std_data.{table_name}
                WHERE id_cliente IS NULL
                """
            ).fetchone()[0]

            if null_ids > 0:
                add_result(
                    results,
                    f"id_cliente_no_nulo_{table_name}",
                    "ERROR",
                    f"id_cliente nulo en {null_ids} filas",
                )
            else:
                add_result(
                    results,
                    f"id_cliente_no_nulo_{table_name}",
                    "OK",
                    "id_cliente sin nulos",
                )

        # 5. Validar TARGET transformado
        invalid_target = con.execute(
            """
            SELECT COUNT(*)
            FROM std_data.application_train
            WHERE flag_dificultad_pago IS NULL
               OR flag_dificultad_pago NOT IN (0, 1)
            """
        ).fetchone()[0]

        if invalid_target > 0:
            add_result(
                results,
                "flag_dificultad_pago_valido",
                "ERROR",
                f"TARGET inválido o nulo en {invalid_target} filas",
            )
        else:
            add_result(
                results,
                "flag_dificultad_pago_valido",
                "OK",
                "flag_dificultad_pago contiene solo 0 y 1",
            )

        # 6. Validar duplicados de id_cliente en tablas donde esperamos unicidad
        unique_tables = [
            "application_train",
            "application_test",
            "fact_asignacion_cartera",
        ]

        for table_name in unique_tables:
            duplicated_ids = con.execute(
                f"""
                SELECT COUNT(*) - COUNT(DISTINCT id_cliente)
                FROM std_data.{table_name}
                """
            ).fetchone()[0]

            if duplicated_ids > 0:
                add_result(
                    results,
                    f"id_cliente_unico_{table_name}",
                    "ERROR",
                    f"Hay {duplicated_ids} duplicados de id_cliente",
                )
            else:
                add_result(
                    results,
                    f"id_cliente_unico_{table_name}",
                    "OK",
                    "id_cliente sin duplicados",
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
        raise SystemExit("Validación std_data finalizó con errores.")

    print("Validación std_data completada correctamente.")


if __name__ == "__main__":
    main()