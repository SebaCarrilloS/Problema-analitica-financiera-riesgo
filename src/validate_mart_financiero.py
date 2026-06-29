from pathlib import Path

import duckdb
import pandas as pd

from src.config import DATABASE_PATH, PROCESSED_DATA_DIR


EXPECTED_TABLES = {
    "resumen_general": {
        "expected_rows": 1,
        "required_columns": [
            "total_clientes",
            "clientes_con_dificultad_pago",
            "tasa_dificultad_pago_pct",
            "exposicion_credito_total",
            "monto_en_riesgo_observado",
            "porcentaje_exposicion_en_riesgo",
            "ratio_credito_ingreso_promedio",
            "score_externo_promedio",
        ],
    },
    "resumen_filial": {
        "expected_rows": 6,
        "required_columns": [
            "id_filial",
            "nombre_filial",
            "zona_filial",
            "total_clientes",
            "clientes_con_dificultad_pago",
            "tasa_dificultad_pago_pct",
            "exposicion_credito_total",
            "monto_en_riesgo_observado",
            "porcentaje_exposicion_en_riesgo",
            "ranking_riesgo",
            "ranking_exposicion",
        ],
    },
    "resumen_producto": {
        "expected_rows": 7,
        "required_columns": [
            "id_producto",
            "nombre_producto",
            "familia_producto",
            "total_clientes",
            "clientes_con_dificultad_pago",
            "tasa_dificultad_pago_pct",
            "exposicion_credito_total",
            "monto_en_riesgo_observado",
            "porcentaje_exposicion_en_riesgo",
            "margen_esperado_aproximado",
            "ranking_riesgo",
            "ranking_exposicion",
        ],
    },
    "resumen_canal": {
        "expected_rows": 5,
        "required_columns": [
            "id_canal",
            "nombre_canal",
            "tipo_canal",
            "total_clientes",
            "clientes_con_dificultad_pago",
            "tasa_dificultad_pago_pct",
            "exposicion_credito_total",
            "monto_en_riesgo_observado",
            "porcentaje_exposicion_en_riesgo",
            "ranking_riesgo",
            "ranking_exposicion",
        ],
    },
    "resumen_segmento": {
        "expected_rows": 6,
        "required_columns": [
            "id_segmento",
            "nombre_segmento",
            "perfil_riesgo_segmento",
            "total_clientes",
            "clientes_con_dificultad_pago",
            "tasa_dificultad_pago_pct",
            "exposicion_credito_total",
            "monto_en_riesgo_observado",
            "porcentaje_exposicion_en_riesgo",
            "ranking_riesgo",
            "ranking_exposicion",
        ],
    },
}


def add_result(results, table_name, validation, status, detail):
    results.append(
        {
            "table_name": table_name,
            "validation": validation,
            "status": status,
            "detail": detail,
        }
    )


def table_exists(con, table_name: str) -> bool:
    query = """
    SELECT COUNT(*)
    FROM information_schema.tables
    WHERE table_schema = 'mart_financiero'
      AND table_name = ?;
    """

    return con.execute(query, [table_name]).fetchone()[0] == 1


def get_columns(con, table_name: str) -> list[str]:
    query = """
    SELECT column_name
    FROM information_schema.columns
    WHERE table_schema = 'mart_financiero'
      AND table_name = ?
    ORDER BY ordinal_position;
    """

    return con.execute(query, [table_name]).fetchdf()["column_name"].tolist()


def main() -> None:
    con = duckdb.connect(DATABASE_PATH)
    results = []

    for table_name, rules in EXPECTED_TABLES.items():
        full_name = f"mart_financiero.{table_name}"

        if not table_exists(con, table_name):
            add_result(
                results,
                table_name,
                "existencia_tabla",
                "ERROR",
                f"No existe la tabla {full_name}",
            )
            continue

        add_result(
            results,
            table_name,
            "existencia_tabla",
            "OK",
            f"Existe la tabla {full_name}",
        )

        row_count = con.execute(
            f"SELECT COUNT(*) FROM {full_name};"
        ).fetchone()[0]

        expected_rows = rules["expected_rows"]

        if row_count == expected_rows:
            add_result(
                results,
                table_name,
                "cantidad_filas",
                "OK",
                f"Filas esperadas: {expected_rows}. Filas reales: {row_count}",
            )
        else:
            add_result(
                results,
                table_name,
                "cantidad_filas",
                "ERROR",
                f"Filas esperadas: {expected_rows}. Filas reales: {row_count}",
            )

        columns = get_columns(con, table_name)
        missing_columns = [
            col for col in rules["required_columns"] if col not in columns
        ]

        if not missing_columns:
            add_result(
                results,
                table_name,
                "columnas_requeridas",
                "OK",
                "Todas las columnas requeridas existen",
            )
        else:
            add_result(
                results,
                table_name,
                "columnas_requeridas",
                "ERROR",
                f"Columnas faltantes: {missing_columns}",
            )

        tasas_invalidas = con.execute(
            f"""
            SELECT COUNT(*)
            FROM {full_name}
            WHERE tasa_dificultad_pago_pct < 0
               OR tasa_dificultad_pago_pct > 100;
            """
        ).fetchone()[0]

        if tasas_invalidas == 0:
            add_result(
                results,
                table_name,
                "rango_tasa_dificultad",
                "OK",
                "Todas las tasas están entre 0 y 100",
            )
        else:
            add_result(
                results,
                table_name,
                "rango_tasa_dificultad",
                "ERROR",
                f"Filas con tasa fuera de rango: {tasas_invalidas}",
            )

        exposiciones_negativas = con.execute(
            f"""
            SELECT COUNT(*)
            FROM {full_name}
            WHERE exposicion_credito_total < 0
               OR monto_en_riesgo_observado < 0;
            """
        ).fetchone()[0]

        if exposiciones_negativas == 0:
            add_result(
                results,
                table_name,
                "montos_no_negativos",
                "OK",
                "No hay exposiciones ni montos en riesgo negativos",
            )
        else:
            add_result(
                results,
                table_name,
                "montos_no_negativos",
                "ERROR",
                f"Filas con montos negativos: {exposiciones_negativas}",
            )

    con.close()

    output_dir = PROCESSED_DATA_DIR / "validaciones"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "validacion_mart_financiero.csv"

    validation_df = pd.DataFrame(results)
    validation_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(validation_df)
    print(f"\nValidación guardada en: {output_path}")

    errors = validation_df[validation_df["status"] == "ERROR"]

    print(f"\nValidaciones ejecutadas: {len(validation_df)}")
    print(f"Errores detectados: {len(errors)}")

    if len(errors) > 0:
        raise SystemExit("Validación finalizada con errores.")

    print("Validación mart_financiero completada correctamente.")


if __name__ == "__main__":
    main()