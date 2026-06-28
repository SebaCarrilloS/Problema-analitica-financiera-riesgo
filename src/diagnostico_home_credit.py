from pathlib import Path

import duckdb
import pandas as pd

from src.config import HOME_CREDIT_RAW_DIR, PROCESSED_DATA_DIR


ENCODINGS_CANDIDATOS = ["utf-8", "latin1", "cp1252"]

OUTPUT_DIR = PROCESSED_DATA_DIR / "diagnosticos"
OUTPUT_PATH = OUTPUT_DIR / "diagnostico_archivos_home_credit.csv"


def obtener_columnas_csv(path_csv: Path) -> tuple[list[str], str]:
    """
    Lee solo el encabezado de un CSV para obtener sus columnas.
    Prueba distintos encodings porque algunos archivos pueden no estar en UTF-8.
    """
    ultimo_error = None

    for encoding in ENCODINGS_CANDIDATOS:
        try:
            columnas = pd.read_csv(
                path_csv,
                nrows=0,
                encoding=encoding,
            ).columns.tolist()

            return columnas, encoding

        except UnicodeDecodeError as error:
            ultimo_error = error

    raise UnicodeDecodeError(
        "encoding",
        b"",
        0,
        1,
        (
            f"No fue posible leer {path_csv.name} con los encodings candidatos. "
            f"Último error: {ultimo_error}"
        ),
    )


def contar_filas_csv(path_csv: Path) -> int:
    """
    Cuenta filas usando DuckDB para evitar cargar el archivo completo en memoria.
    Si DuckDB falla por codificación, usa pandas con fallback de encoding.
    """
    query = f"""
        SELECT COUNT(*) AS total_filas
        FROM read_csv_auto('{path_csv.as_posix()}', header = true)
    """

    try:
        with duckdb.connect() as connection:
            total_filas = connection.execute(query).fetchone()[0]

        return total_filas

    except Exception:
        for encoding in ENCODINGS_CANDIDATOS:
            try:
                total = 0

                for chunk in pd.read_csv(
                    path_csv,
                    chunksize=100_000,
                    encoding=encoding,
                ):
                    total += len(chunk)

                return total

            except UnicodeDecodeError:
                continue

        raise RuntimeError(f"No fue posible contar filas del archivo: {path_csv.name}")


def diagnosticar_archivos_home_credit() -> pd.DataFrame:
    """
    Genera un inventario inicial de los archivos CSV de Home Credit.
    """
    archivos_csv = sorted(HOME_CREDIT_RAW_DIR.glob("*.csv"))

    if not archivos_csv:
        raise FileNotFoundError(
            f"No se encontraron archivos CSV en: {HOME_CREDIT_RAW_DIR}"
        )

    registros = []

    for archivo in archivos_csv:
        columnas, encoding_detectado = obtener_columnas_csv(archivo)
        total_filas = contar_filas_csv(archivo)
        tamaño_mb = archivo.stat().st_size / (1024 * 1024)

        registros.append(
            {
                "archivo": archivo.name,
                "tamaño_mb": round(tamaño_mb, 2),
                "total_filas": total_filas,
                "total_columnas": len(columnas),
                "encoding_usado": encoding_detectado,
                "primeras_columnas": ", ".join(columnas[:8]),
            }
        )

    diagnostico = pd.DataFrame(registros)

    diagnostico = diagnostico.sort_values(
        by="tamaño_mb",
        ascending=False,
    ).reset_index(drop=True)

    return diagnostico


def guardar_diagnostico(diagnostico: pd.DataFrame, output_path: Path) -> None:
    """
    Guarda el diagnóstico en formato CSV para reutilizarlo en reportes Quarto.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    diagnostico.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )


def main() -> None:
    diagnostico = diagnosticar_archivos_home_credit()

    print("\nDiagnóstico inicial de archivos Home Credit:\n")
    print(diagnostico.to_string(index=False))

    guardar_diagnostico(diagnostico, OUTPUT_PATH)

    print(f"\nDiagnóstico guardado en: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()