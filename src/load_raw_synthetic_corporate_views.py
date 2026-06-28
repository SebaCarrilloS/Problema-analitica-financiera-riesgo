import duckdb

from src.config import CORPORATE_SYNTHETIC_DIR, DATABASE_PATH


CSV_TO_VIEW = {
    "dim_periodo.csv": "dim_periodo",
    "dim_filial.csv": "dim_filial",
    "dim_sucursal.csv": "dim_sucursal",
    "dim_ejecutivo.csv": "dim_ejecutivo",
    "dim_canal.csv": "dim_canal",
    "dim_producto.csv": "dim_producto",
    "dim_segmento.csv": "dim_segmento",
    "fact_asignacion_cartera.csv": "fact_asignacion_cartera",
    "fact_metas_mensuales.csv": "fact_metas_mensuales",
    "fact_costos_operacionales.csv": "fact_costos_operacionales",
}


def validar_archivos_sinteticos() -> None:
    """
    Verifica que todos los archivos CSV sintéticos esperados existan.
    """
    archivos_faltantes = []

    for csv_name in CSV_TO_VIEW:
        csv_path = CORPORATE_SYNTHETIC_DIR / csv_name

        if not csv_path.exists():
            archivos_faltantes.append(csv_name)

    if archivos_faltantes:
        raise FileNotFoundError(
            "Faltan archivos CSV sintéticos esperados en data/synthetic/corporate: "
            + ", ".join(archivos_faltantes)
        )


def crear_vistas_raw_sinteticas() -> None:
    """
    Crea vistas en DuckDB sobre los archivos sintéticos corporativos.

    Decisión técnica:
    Igual que con Home Credit, en raw_data se cargan las columnas como VARCHAR.
    La tipificación formal se hará después en std_data.
    """
    validar_archivos_sinteticos()

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(DATABASE_PATH)) as connection:
        connection.execute("CREATE SCHEMA IF NOT EXISTS raw_data;")

        for csv_name, view_name in CSV_TO_VIEW.items():
            csv_path = CORPORATE_SYNTHETIC_DIR / csv_name
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

    print("\nVistas raw_data sintéticas creadas correctamente.")


def main() -> None:
    crear_vistas_raw_sinteticas()


if __name__ == "__main__":
    main()