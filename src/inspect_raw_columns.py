from src.config import DATABASE_PATH
import duckdb


TABLES_TO_INSPECT = [
    "application_train",
    "application_test",
    "fact_asignacion_cartera",
    "dim_filial",
    "dim_sucursal",
    "dim_ejecutivo",
    "dim_producto",
    "dim_canal",
    "dim_segmento",
]


def main() -> None:
    with duckdb.connect(DATABASE_PATH) as con:
        for table_name in TABLES_TO_INSPECT:
            full_name = f"raw_data.{table_name}"

            print("=" * 80)
            print(full_name)
            print("=" * 80)

            try:
                columns = con.execute(f"DESCRIBE {full_name}").fetchdf()
                print(columns[["column_name", "column_type"]].to_string(index=False))
            except Exception as exc:
                print(f"ERROR inspeccionando {full_name}: {exc}")

            print()


if __name__ == "__main__":
    main()