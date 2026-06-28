import argparse
from pathlib import Path

import duckdb

from src.config import DATABASE_PATH, PROJECT_ROOT


def resolve_sql_path(sql_file: str) -> Path:
    path = Path(sql_file)

    if not path.is_absolute():
        path = PROJECT_ROOT / path

    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo SQL: {path}")

    if path.suffix.lower() != ".sql":
        raise ValueError(f"El archivo no parece ser SQL: {path}")

    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ejecuta un archivo SQL sobre la base DuckDB del proyecto."
    )
    parser.add_argument(
        "sql_file",
        help="Ruta del archivo SQL a ejecutar, relativa a la raíz del proyecto.",
    )

    args = parser.parse_args()
    sql_path = resolve_sql_path(args.sql_file)

    sql_text = sql_path.read_text(encoding="utf-8")

    print(f"Base de datos: {DATABASE_PATH}")
    print(f"Archivo SQL: {sql_path}")

    with duckdb.connect(DATABASE_PATH) as con:
        con.execute(sql_text)

    print("SQL ejecutado correctamente.")


if __name__ == "__main__":
    main()