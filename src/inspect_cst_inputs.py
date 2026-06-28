from src.config import DATABASE_PATH
import duckdb


TABLES_TO_INSPECT = [
    "std_data.application_train",
    "std_data.fact_asignacion_cartera",
    "std_data.dim_filial",
    "std_data.dim_sucursal",
    "std_data.dim_ejecutivo",
    "std_data.dim_producto",
    "std_data.dim_canal",
    "std_data.dim_segmento",
]


def main() -> None:
    with duckdb.connect(DATABASE_PATH) as con:
        for table_name in TABLES_TO_INSPECT:
            print("=" * 100)
            print(table_name)
            print("=" * 100)

            print("COLUMNAS:")
            columns = con.execute(f"DESCRIBE {table_name}").fetchdf()
            print(columns[["column_name", "column_type"]].to_string(index=False))

            print()
            print("MUESTRA:")
            sample = con.execute(f"SELECT * FROM {table_name} LIMIT 3").fetchdf()
            print(sample.to_string(index=False))

            print()


if __name__ == "__main__":
    main()