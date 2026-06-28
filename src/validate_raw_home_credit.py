import duckdb
import pandas as pd

from src.config import DATABASE_PATH, PROCESSED_DATA_DIR
from src.load_raw_home_credit_views import CSV_TO_VIEW


DIAGNOSTICO_PATH = (
    PROCESSED_DATA_DIR / "diagnosticos" / "diagnostico_archivos_home_credit.csv"
)

OUTPUT_DIR = PROCESSED_DATA_DIR / "validaciones"
OUTPUT_PATH = OUTPUT_DIR / "validacion_raw_home_credit.csv"


COLUMNAS_REQUERIDAS = {
    "application_train": ["SK_ID_CURR", "TARGET"],
    "application_test": ["SK_ID_CURR"],
    "bureau": ["SK_ID_CURR", "SK_ID_BUREAU"],
    "bureau_balance": ["SK_ID_BUREAU"],
    "credit_card_balance": ["SK_ID_CURR", "SK_ID_PREV"],
    "installments_payments": ["SK_ID_CURR", "SK_ID_PREV"],
    "pos_cash_balance": ["SK_ID_CURR", "SK_ID_PREV"],
    "previous_application": ["SK_ID_CURR", "SK_ID_PREV"],
    "sample_submission": ["SK_ID_CURR", "TARGET"],
}


COLUMNAS_UNICAS_ESPERADAS = {
    "application_train": "SK_ID_CURR",
    "application_test": "SK_ID_CURR",
    "bureau": "SK_ID_BUREAU",
    "previous_application": "SK_ID_PREV",
    "sample_submission": "SK_ID_CURR",
}


def obtener_vistas_raw(connection: duckdb.DuckDBPyConnection) -> set[str]:
    """
    Obtiene las vistas existentes en el schema raw_data.
    """
    resultado = connection.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'raw_data'
          AND table_type = 'VIEW';
        """
    ).fetchdf()

    return set(resultado["table_name"].tolist())


def obtener_columnas(connection: duckdb.DuckDBPyConnection, vista: str) -> list[str]:
    """
    Obtiene columnas de una vista raw_data.
    """
    resultado = connection.execute(
        f"SELECT * FROM raw_data.{vista} LIMIT 0"
    ).fetchdf()

    return resultado.columns.tolist()


def contar_filas(connection: duckdb.DuckDBPyConnection, vista: str) -> int:
    """
    Cuenta filas de una vista raw_data.
    """
    return connection.execute(
        f"SELECT COUNT(*) FROM raw_data.{vista}"
    ).fetchone()[0]


def contar_duplicados_llave(
    connection: duckdb.DuckDBPyConnection,
    vista: str,
    columna_llave: str,
) -> int:
    """
    Cuenta duplicados de una llave cuando se espera unicidad.
    """
    query = f"""
    SELECT
        COUNT(*) - COUNT(DISTINCT {columna_llave}) AS duplicados
    FROM raw_data.{vista};
    """

    return connection.execute(query).fetchone()[0]


def cargar_diagnostico() -> pd.DataFrame:
    """
    Carga el diagnóstico inicial generado previamente.
    """
    if not DIAGNOSTICO_PATH.exists():
        raise FileNotFoundError(
            "No existe el diagnóstico inicial. Ejecuta primero: "
            ".\\.venv\\Scripts\\python.exe -m src.diagnostico_home_credit"
        )

    return pd.read_csv(DIAGNOSTICO_PATH)


def validar_raw_data() -> pd.DataFrame:
    """
    Ejecuta validaciones intermedias sobre las vistas raw_data de Home Credit.
    """
    diagnostico = cargar_diagnostico()

    registros = []

    with duckdb.connect(str(DATABASE_PATH)) as connection:
        vistas_existentes = obtener_vistas_raw(connection)

        for archivo_csv, vista in CSV_TO_VIEW.items():
            existe_vista = vista in vistas_existentes

            fila_diag = diagnostico.loc[diagnostico["archivo"] == archivo_csv]

            filas_esperadas = (
                int(fila_diag["total_filas"].iloc[0])
                if not fila_diag.empty
                else None
            )

            columnas_esperadas = (
                int(fila_diag["total_columnas"].iloc[0])
                if not fila_diag.empty
                else None
            )

            if not existe_vista:
                registros.append(
                    {
                        "vista": vista,
                        "archivo_origen": archivo_csv,
                        "validacion": "existencia_vista",
                        "estado": "ERROR",
                        "detalle": "La vista no existe en raw_data.",
                    }
                )
                continue

            columnas = obtener_columnas(connection, vista)
            total_filas = contar_filas(connection, vista)

            estado_conteo_filas = (
                "OK" if filas_esperadas == total_filas else "ERROR"
            )

            estado_conteo_columnas = (
                "OK" if columnas_esperadas == len(columnas) else "ERROR"
            )

            registros.append(
                {
                    "vista": vista,
                    "archivo_origen": archivo_csv,
                    "validacion": "conteo_filas",
                    "estado": estado_conteo_filas,
                    "detalle": (
                        f"Filas DuckDB={total_filas}; "
                        f"filas diagnóstico={filas_esperadas}"
                    ),
                }
            )

            registros.append(
                {
                    "vista": vista,
                    "archivo_origen": archivo_csv,
                    "validacion": "conteo_columnas",
                    "estado": estado_conteo_columnas,
                    "detalle": (
                        f"Columnas DuckDB={len(columnas)}; "
                        f"columnas diagnóstico={columnas_esperadas}"
                    ),
                }
            )

            if total_filas == 0:
                registros.append(
                    {
                        "vista": vista,
                        "archivo_origen": archivo_csv,
                        "validacion": "vista_no_vacia",
                        "estado": "ERROR",
                        "detalle": "La vista no contiene filas.",
                    }
                )
            else:
                registros.append(
                    {
                        "vista": vista,
                        "archivo_origen": archivo_csv,
                        "validacion": "vista_no_vacia",
                        "estado": "OK",
                        "detalle": f"La vista contiene {total_filas} filas.",
                    }
                )

            columnas_requeridas = COLUMNAS_REQUERIDAS.get(vista, [])

            for columna in columnas_requeridas:
                estado_columna = "OK" if columna in columnas else "ERROR"

                registros.append(
                    {
                        "vista": vista,
                        "archivo_origen": archivo_csv,
                        "validacion": f"columna_requerida_{columna}",
                        "estado": estado_columna,
                        "detalle": (
                            f"Columna {columna} presente."
                            if estado_columna == "OK"
                            else f"Columna {columna} ausente."
                        ),
                    }
                )

            if vista == "application_train":
                registros.append(
                    {
                        "vista": vista,
                        "archivo_origen": archivo_csv,
                        "validacion": "target_en_train",
                        "estado": "OK" if "TARGET" in columnas else "ERROR",
                        "detalle": "TARGET debe existir en application_train.",
                    }
                )

            if vista == "application_test":
                registros.append(
                    {
                        "vista": vista,
                        "archivo_origen": archivo_csv,
                        "validacion": "target_ausente_en_test",
                        "estado": "OK" if "TARGET" not in columnas else "ERROR",
                        "detalle": "TARGET no debe existir en application_test.",
                    }
                )

            if vista in COLUMNAS_UNICAS_ESPERADAS:
                columna_llave = COLUMNAS_UNICAS_ESPERADAS[vista]

                if columna_llave in columnas:
                    duplicados = contar_duplicados_llave(
                        connection,
                        vista,
                        columna_llave,
                    )

                    registros.append(
                        {
                            "vista": vista,
                            "archivo_origen": archivo_csv,
                            "validacion": f"duplicados_{columna_llave}",
                            "estado": "OK" if duplicados == 0 else "ERROR",
                            "detalle": (
                                f"Duplicados detectados en {columna_llave}: "
                                f"{duplicados}"
                            ),
                        }
                    )

    return pd.DataFrame(registros)


def guardar_resultado_validacion(resultado: pd.DataFrame) -> None:
    """
    Guarda el resultado de validación para documentación posterior.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    resultado.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8",
    )


def main() -> None:
    resultado = validar_raw_data()

    print("\nResultado de validación raw_data:\n")
    print(resultado.to_string(index=False))

    guardar_resultado_validacion(resultado)

    errores = resultado.loc[resultado["estado"] == "ERROR"]

    print(f"\nValidaciones ejecutadas: {len(resultado)}")
    print(f"Errores detectados: {len(errores)}")
    print(f"Resultado guardado en: {OUTPUT_PATH}")

    if not errores.empty:
        print("\nAdvertencia: existen validaciones con ERROR. Revisar detalle.")


if __name__ == "__main__":
    main()