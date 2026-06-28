import duckdb

from src.config import DATABASE_PATH


def main() -> None:
    """
    Inspecciona las vistas creadas en el schema raw_data.
    """
    with duckdb.connect(str(DATABASE_PATH)) as connection:
        resultado = connection.execute(
            """
            SELECT
                table_schema,
                table_name,
                table_type
            FROM information_schema.tables
            WHERE table_schema = 'raw_data'
            ORDER BY table_name;
            """
        ).fetchdf()

    print("\nObjetos encontrados en raw_data:\n")
    print(resultado.to_string(index=False))


if __name__ == "__main__":
    main()