from src.config import DATABASE_PATH
import duckdb


def main() -> None:
    query = """
    SELECT
        table_schema,
        table_name,
        table_type
    FROM information_schema.tables
    WHERE table_schema = 'std_data'
    ORDER BY table_name;
    """

    with duckdb.connect(DATABASE_PATH) as con:
        result = con.execute(query).fetchdf()

    print(result.to_string(index=False))


if __name__ == "__main__":
    main()