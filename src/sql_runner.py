from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "database" / "financiera.duckdb"
SQL_PATH = PROJECT_ROOT / "sql" / "00_admin" / "00_create_schemas.sql"


def run_sql_file(sql_path: Path, database_path: Path) -> None:
    """
    Ejecuta un archivo SQL sobre una base DuckDB local.

    Parameters
    ----------
    sql_path:
        Ruta del archivo SQL a ejecutar.
    database_path:
        Ruta de la base DuckDB.
    """
    if not sql_path.exists():
        raise FileNotFoundError(f"No existe el archivo SQL: {sql_path}")

    database_path.parent.mkdir(parents=True, exist_ok=True)

    sql_script = sql_path.read_text(encoding="utf-8")

    with duckdb.connect(str(database_path)) as connection:
        connection.execute(sql_script)

    print("Schemas creados correctamente en DuckDB.")
    print(f"Base DuckDB: {database_path}")
    print(f"Script ejecutado: {sql_path}")


if __name__ == "__main__":
    run_sql_file(SQL_PATH, DATABASE_PATH)