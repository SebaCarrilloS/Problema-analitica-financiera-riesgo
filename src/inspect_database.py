from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "database" / "financiera.duckdb"


def main() -> None:
    """
    Inspecciona los schemas principales creados en la base DuckDB.
    """
    expected_schemas = [
        "raw_data",
        "std_data",
        "cst_data",
        "mart_financiero",
        "data_quality",
    ]

    with duckdb.connect(str(DATABASE_PATH)) as connection:
        schemas = connection.execute(
            """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name IN (
                'raw_data',
                'std_data',
                'cst_data',
                'mart_financiero',
                'data_quality'
            )
            ORDER BY schema_name;
            """
        ).fetchall()

    found_schemas = [row[0] for row in schemas]

    print("Schemas encontrados en DuckDB:")
    for schema in found_schemas:
        print(f"- {schema}")

    missing_schemas = sorted(set(expected_schemas) - set(found_schemas))

    if missing_schemas:
        raise RuntimeError(f"Faltan schemas esperados: {missing_schemas}")

    print("Validación OK: todos los schemas esperados existen.")


if __name__ == "__main__":
    main()