import duckdb

from src.config import DATABASE_PATH, HOME_CREDIT_RAW_DIR


CSV_TO_VIEW = {
    "application_train.csv": "application_train",
    "application_test.csv": "application_test",
    "bureau.csv": "bureau",
    "bureau_balance.csv": "bureau_balance",
    "credit_card_balance.csv": "credit_card_balance",
    "installments_payments.csv": "installments_payments",
    "POS_CASH_balance.csv": "pos_cash_balance",
    "previous_application.csv": "previous_application",
    "sample_submission.csv": "sample_submission",
}


METADATA_FILES = [
    "HomeCredit_columns_description.csv",
]


def validar_archivos_raw() -> None:
    """
    Verifica que los archivos CSV esperados existan en la carpeta raw.
    """
    archivos_esperados = list(CSV_TO_VIEW.keys()) + METADATA_FILES
    archivos_faltantes = []

    for csv_name in archivos_esperados:
        csv_path = HOME_CREDIT_RAW_DIR / csv_name

        if not csv_path.exists():
            archivos_faltantes.append(csv_name)

    if archivos_faltantes:
        raise FileNotFoundError(
            "Faltan archivos CSV esperados en data/raw/home_credit: "
            + ", ".join(archivos_faltantes)
        )


def crear_vistas_raw() -> None:
    """
    Crea vistas en DuckDB sobre los archivos CSV principales de Home Credit.

    Decisión técnica:
    En raw_data se cargan las columnas como VARCHAR para evitar inferencias
    prematuras de tipos. La estandarización formal se hará en std_data.

    El archivo HomeCredit_columns_description.csv se excluye de esta carga
    porque funciona como metadata de documentación y puede requerir tratamiento
    especial de encoding.
    """
    validar_archivos_raw()

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(DATABASE_PATH)) as connection:
        connection.execute("CREATE SCHEMA IF NOT EXISTS raw_data;")

        for csv_name, view_name in CSV_TO_VIEW.items():
            csv_path = HOME_CREDIT_RAW_DIR / csv_name
            csv_path_sql = csv_path.as_posix().replace("'", "''")

            query = f"""
            CREATE OR REPLACE VIEW raw_data.{view_name} AS
            SELECT *
            FROM read_csv_auto(
                '{csv_path_sql}',
                header = true,
                all_varchar = true,
                sample_size = -1,
                null_padding = true
            );
            """

            connection.execute(query)
            print(f"Vista creada: raw_data.{view_name} -> {csv_name}")

    print("\nVistas raw_data principales creadas correctamente.")
    print(
        "Nota: HomeCredit_columns_description.csv se tratará como metadata "
        "en una etapa posterior."
    )


def main() -> None:
    crear_vistas_raw()


if __name__ == "__main__":
    main()