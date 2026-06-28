from src.config import DATABASE_PATH
import duckdb


def main() -> None:
    query = """
    SELECT
        table_schema,
        table_name,
        table_type
    FROM information_schema.tables
    WHERE table_schema = 'cst_data'
    ORDER BY table_name;
    """

    with duckdb.connect(DATABASE_PATH) as con:
        objects = con.execute(query).fetchdf()

        print("Objetos en cst_data:")
        print(objects.to_string(index=False))

        print()
        print("Conteo de filas por objeto:")

        for table_name in objects["table_name"]:
            count = con.execute(
                f"SELECT COUNT(*) FROM cst_data.{table_name}"
            ).fetchone()[0]

            print(f"cst_data.{table_name}: {count:,} filas")


if __name__ == "__main__":
    main()