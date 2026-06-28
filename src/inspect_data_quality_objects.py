from src.config import DATABASE_PATH
import duckdb


def main() -> None:
    query = """
    SELECT
        table_schema,
        table_name,
        table_type
    FROM information_schema.tables
    WHERE table_schema = 'data_quality'
    ORDER BY table_name;
    """

    with duckdb.connect(DATABASE_PATH) as con:
        objects = con.execute(query).fetchdf()

        print("Objetos en data_quality:")
        print(objects.to_string(index=False))

        print()
        print("Conteo de filas por tabla:")

        for table_name in objects["table_name"]:
            count = con.execute(
                f"SELECT COUNT(*) FROM data_quality.{table_name}"
            ).fetchone()[0]

            print(f"data_quality.{table_name}: {count:,} filas")


if __name__ == "__main__":
    main()