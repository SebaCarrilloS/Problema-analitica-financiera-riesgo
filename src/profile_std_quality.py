from pathlib import Path

import duckdb
import pandas as pd

from src.config import DATABASE_PATH, PROCESSED_DATA_DIR


OUTPUT_DIR = PROCESSED_DATA_DIR / "data_quality"

TABLES_TO_PROFILE = [
    "application_train",
    "application_test",
    "fact_asignacion_cartera",
]

NUMERIC_TYPES = {
    "TINYINT",
    "SMALLINT",
    "INTEGER",
    "BIGINT",
    "HUGEINT",
    "UTINYINT",
    "USMALLINT",
    "UINTEGER",
    "UBIGINT",
    "FLOAT",
    "DOUBLE",
    "REAL",
    "DECIMAL",
}

CATEGORICAL_TYPES = {
    "VARCHAR",
    "BOOLEAN",
}


def normalize_type(column_type: str) -> str:
    return column_type.split("(")[0].upper()


def get_columns_metadata(con: duckdb.DuckDBPyConnection, table_name: str) -> pd.DataFrame:
    df = con.execute(f"DESCRIBE std_data.{table_name}").fetchdf()
    df["tipo_normalizado"] = df["column_type"].apply(normalize_type)
    return df


def save_df(
    con: duckdb.DuckDBPyConnection,
    df: pd.DataFrame,
    table_name: str,
    csv_name: str,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = OUTPUT_DIR / csv_name
    df.to_csv(csv_path, index=False, encoding="utf-8")

    con.register("tmp_df_to_save", df)
    con.execute(f"DROP TABLE IF EXISTS data_quality.{table_name}")
    con.execute(f"CREATE TABLE data_quality.{table_name} AS SELECT * FROM tmp_df_to_save")
    con.unregister("tmp_df_to_save")

    print(f"Guardado: data_quality.{table_name}")
    print(f"CSV: {csv_path}")


def build_null_profile(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    results = []

    for table_name in TABLES_TO_PROFILE:
        columns_df = get_columns_metadata(con, table_name)
        total_rows = con.execute(
            f"SELECT COUNT(*) FROM std_data.{table_name}"
        ).fetchone()[0]

        for _, row in columns_df.iterrows():
            column_name = row["column_name"]
            column_type = row["column_type"]

            null_count = con.execute(
                f"""
                SELECT COUNT(*)
                FROM std_data.{table_name}
                WHERE {column_name} IS NULL
                """
            ).fetchone()[0]

            null_pct = null_count / total_rows if total_rows > 0 else None

            results.append(
                {
                    "tabla": table_name,
                    "columna": column_name,
                    "tipo_dato": column_type,
                    "total_filas": total_rows,
                    "nulos": null_count,
                    "porcentaje_nulos": null_pct,
                }
            )

    return pd.DataFrame(results)


def build_numeric_profile(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    results = []

    for table_name in TABLES_TO_PROFILE:
        columns_df = get_columns_metadata(con, table_name)
        numeric_columns = columns_df[
            columns_df["tipo_normalizado"].isin(NUMERIC_TYPES)
        ]

        for _, row in numeric_columns.iterrows():
            column_name = row["column_name"]
            column_type = row["column_type"]

            query = f"""
            SELECT
                COUNT(*) AS total_filas,
                COUNT({column_name}) AS valores_no_nulos,
                SUM(CASE WHEN {column_name} IS NULL THEN 1 ELSE 0 END) AS nulos,
                MIN({column_name}) AS minimo,
                QUANTILE_CONT({column_name}, 0.25) AS p25,
                AVG({column_name}) AS promedio,
                MEDIAN({column_name}) AS mediana,
                QUANTILE_CONT({column_name}, 0.75) AS p75,
                MAX({column_name}) AS maximo,
                SUM(CASE WHEN {column_name} = 0 THEN 1 ELSE 0 END) AS cantidad_ceros,
                SUM(CASE WHEN {column_name} < 0 THEN 1 ELSE 0 END) AS cantidad_negativos
            FROM std_data.{table_name}
            """

            row_result = con.execute(query).fetchdf().iloc[0].to_dict()

            results.append(
                {
                    "tabla": table_name,
                    "columna": column_name,
                    "tipo_dato": column_type,
                    **row_result,
                }
            )

    return pd.DataFrame(results)


def build_categorical_profile(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    results = []

    for table_name in TABLES_TO_PROFILE:
        columns_df = get_columns_metadata(con, table_name)
        categorical_columns = columns_df[
            columns_df["tipo_normalizado"].isin(CATEGORICAL_TYPES)
        ]

        for _, row in categorical_columns.iterrows():
            column_name = row["column_name"]
            column_type = row["column_type"]

            query = f"""
            SELECT
                '{table_name}' AS tabla,
                '{column_name}' AS columna,
                '{column_type}' AS tipo_dato,
                CAST({column_name} AS VARCHAR) AS valor,
                COUNT(*) AS cantidad,
                COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () AS porcentaje
            FROM std_data.{table_name}
            GROUP BY {column_name}
            ORDER BY cantidad DESC
            LIMIT 20
            """

            df_values = con.execute(query).fetchdf()
            results.append(df_values)

    if not results:
        return pd.DataFrame(
            columns=["tabla", "columna", "tipo_dato", "valor", "cantidad", "porcentaje"]
        )

    return pd.concat(results, ignore_index=True)


def build_target_profile(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    query = """
    SELECT
        flag_dificultad_pago,
        COUNT(*) AS cantidad,
        COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () AS porcentaje
    FROM std_data.application_train
    GROUP BY flag_dificultad_pago
    ORDER BY flag_dificultad_pago
    """

    return con.execute(query).fetchdf()


def build_train_test_null_comparison(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    train_columns = set(
        con.execute("DESCRIBE std_data.application_train").fetchdf()["column_name"]
    )
    test_columns = set(
        con.execute("DESCRIBE std_data.application_test").fetchdf()["column_name"]
    )

    common_columns = sorted(
        (train_columns & test_columns) - {"fecha_carga_std"}
    )

    results = []

    train_total = con.execute(
        "SELECT COUNT(*) FROM std_data.application_train"
    ).fetchone()[0]

    test_total = con.execute(
        "SELECT COUNT(*) FROM std_data.application_test"
    ).fetchone()[0]

    for column_name in common_columns:
        train_nulls = con.execute(
            f"""
            SELECT COUNT(*)
            FROM std_data.application_train
            WHERE {column_name} IS NULL
            """
        ).fetchone()[0]

        test_nulls = con.execute(
            f"""
            SELECT COUNT(*)
            FROM std_data.application_test
            WHERE {column_name} IS NULL
            """
        ).fetchone()[0]

        train_null_pct = train_nulls / train_total if train_total > 0 else None
        test_null_pct = test_nulls / test_total if test_total > 0 else None

        results.append(
            {
                "columna": column_name,
                "nulos_train": train_nulls,
                "porcentaje_nulos_train": train_null_pct,
                "nulos_test": test_nulls,
                "porcentaje_nulos_test": test_null_pct,
                "diferencia_porcentaje_nulos": (
                    test_null_pct - train_null_pct
                    if train_null_pct is not None and test_null_pct is not None
                    else None
                ),
            }
        )

    return pd.DataFrame(results)


def build_assignment_quality(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    checks = []

    total_rows = con.execute(
        "SELECT COUNT(*) FROM std_data.fact_asignacion_cartera"
    ).fetchone()[0]

    checks.append(
        {
            "check_name": "total_filas_fact_asignacion_cartera",
            "valor": total_rows,
            "detalle": "Total de filas en asignación de cartera",
        }
    )

    missing_train_clients = con.execute(
        """
        SELECT COUNT(*)
        FROM std_data.fact_asignacion_cartera f
        LEFT JOIN std_data.application_train a
            ON f.id_cliente = a.id_cliente
        WHERE a.id_cliente IS NULL
        """
    ).fetchone()[0]

    checks.append(
        {
            "check_name": "clientes_asignados_sin_application_train",
            "valor": missing_train_clients,
            "detalle": "Clientes en cartera que no aparecen en application_train",
        }
    )

    duplicated_clients = con.execute(
        """
        SELECT COUNT(*) - COUNT(DISTINCT id_cliente)
        FROM std_data.fact_asignacion_cartera
        """
    ).fetchone()[0]

    checks.append(
        {
            "check_name": "duplicados_id_cliente_asignacion",
            "valor": duplicated_clients,
            "detalle": "Duplicados de id_cliente en fact_asignacion_cartera",
        }
    )

    null_assignment_date = con.execute(
        """
        SELECT COUNT(*)
        FROM std_data.fact_asignacion_cartera
        WHERE fecha_asignacion IS NULL
        """
    ).fetchone()[0]

    checks.append(
        {
            "check_name": "fecha_asignacion_nula",
            "valor": null_assignment_date,
            "detalle": "Filas sin fecha_asignacion válida",
        }
    )

    return pd.DataFrame(checks)


def main() -> None:
    with duckdb.connect(DATABASE_PATH) as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS data_quality")

        print("Generando perfil de nulos...")
        null_profile = build_null_profile(con)
        save_df(
            con,
            null_profile,
            "perfil_nulos_std",
            "perfil_nulos_std.csv",
        )

        print()
        print("Generando perfil numérico...")
        numeric_profile = build_numeric_profile(con)
        save_df(
            con,
            numeric_profile,
            "perfil_numerico_std",
            "perfil_numerico_std.csv",
        )

        print()
        print("Generando perfil categórico...")
        categorical_profile = build_categorical_profile(con)
        save_df(
            con,
            categorical_profile,
            "perfil_categorico_std",
            "perfil_categorico_std.csv",
        )

        print()
        print("Generando perfil de TARGET...")
        target_profile = build_target_profile(con)
        save_df(
            con,
            target_profile,
            "perfil_target_std",
            "perfil_target_std.csv",
        )

        print()
        print("Generando comparación train vs test...")
        train_test_comparison = build_train_test_null_comparison(con)
        save_df(
            con,
            train_test_comparison,
            "comparacion_nulos_train_test_std",
            "comparacion_nulos_train_test_std.csv",
        )

        print()
        print("Generando control de asignación de cartera...")
        assignment_quality = build_assignment_quality(con)
        save_df(
            con,
            assignment_quality,
            "control_asignacion_cartera_std",
            "control_asignacion_cartera_std.csv",
        )

    print()
    print("Perfilamiento de calidad std_data completado correctamente.")


if __name__ == "__main__":
    main()