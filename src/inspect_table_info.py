import argparse
import re

import duckdb

from src.config import DATABASE_PATH


def validar_nombre(nombre: str) -> str:
    patron = r"^[A-Za-z_][A-Za-z0-9_]*$"

    if not re.match(patron, nombre):
        raise ValueError(f"Nombre inválido: {nombre}")

    return nombre


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Muestra información básica de una tabla en DuckDB."
    )

    parser.add_argument("schema", help="Schema de la tabla")
    parser.add_argument("table", help="Nombre de la tabla")
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        help="Cantidad de filas de muestra a mostrar",
    )

    args = parser.parse_args()

    schema = validar_nombre(args.schema)
    table = validar_nombre(args.table)

    con = duckdb.connect(DATABASE_PATH)

    nombre_completo = f"{schema}.{table}"

    total_filas = con.execute(
        f"SELECT COUNT(*) FROM {nombre_completo}"
    ).fetchone()[0]

    columnas = con.execute(
        """
        SELECT
            ordinal_position,
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = ?
          AND table_name = ?
        ORDER BY ordinal_position;
        """,
        [schema, table],
    ).fetchdf()

    print(f"\nTabla: {nombre_completo}")
    print(f"Filas: {total_filas}")
    print(f"Columnas: {len(columnas)}")

    print("\nEstructura:")
    print(columnas)

    if args.sample > 0:
        muestra = con.execute(
            f"SELECT * FROM {nombre_completo} LIMIT {args.sample}"
        ).fetchdf()

        print(f"\nMuestra ({args.sample} filas):")
        print(muestra)

    con.close()


if __name__ == "__main__":
    main()