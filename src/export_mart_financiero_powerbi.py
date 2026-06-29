from pathlib import Path

import duckdb

from src.config import DATABASE_PATH, EXPORTS_DIR


TABLES_TO_EXPORT = [
    "resumen_general",
    "resumen_filial",
    "resumen_producto",
    "resumen_canal",
    "resumen_segmento",
]


def main() -> None:
    output_dir = EXPORTS_DIR / "powerbi"
    output_dir.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(DATABASE_PATH)

    for table_name in TABLES_TO_EXPORT:
        full_table_name = f"mart_financiero.{table_name}"
        output_path = output_dir / f"{table_name}.csv"

        query = f"""
        COPY (
            SELECT *
            FROM {full_table_name}
        )
        TO '{output_path.as_posix()}'
        WITH (
            HEADER,
            DELIMITER ','
        );
        """

        con.execute(query)

        row_count = con.execute(
            f"SELECT COUNT(*) FROM {full_table_name};"
        ).fetchone()[0]

        print(f"Exportado: {output_path}")
        print(f"Filas: {row_count}")
        print("-" * 60)

    con.close()

    print("Exportación de mart_financiero para Power BI completada.")


if __name__ == "__main__":
    main()