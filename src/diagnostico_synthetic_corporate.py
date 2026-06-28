from pathlib import Path

import pandas as pd

from src.config import CORPORATE_SYNTHETIC_DIR, PROCESSED_DATA_DIR


OUTPUT_DIR = PROCESSED_DATA_DIR / "diagnosticos"
OUTPUT_PATH = OUTPUT_DIR / "diagnostico_archivos_synthetic_corporate.csv"


def diagnosticar_archivo_csv(path_csv: Path) -> dict:
    """
    Genera métricas básicas para un archivo CSV sintético.
    """
    df = pd.read_csv(path_csv)

    total_nulos = int(df.isna().sum().sum())
    columnas_con_nulos = df.columns[df.isna().any()].tolist()
    tamaño_mb = path_csv.stat().st_size / (1024 * 1024)

    return {
        "archivo": path_csv.name,
        "tamaño_mb": round(tamaño_mb, 2),
        "total_filas": len(df),
        "total_columnas": len(df.columns),
        "total_nulos": total_nulos,
        "columnas_con_nulos": ", ".join(columnas_con_nulos)
        if columnas_con_nulos
        else "Sin nulos",
        "primeras_columnas": ", ".join(df.columns[:8]),
    }


def diagnosticar_datos_sinteticos() -> pd.DataFrame:
    """
    Diagnostica los archivos CSV sintéticos corporativos.
    """
    archivos_csv = sorted(CORPORATE_SYNTHETIC_DIR.glob("*.csv"))

    if not archivos_csv:
        raise FileNotFoundError(
            f"No se encontraron archivos CSV en: {CORPORATE_SYNTHETIC_DIR}"
        )

    registros = [diagnosticar_archivo_csv(path_csv) for path_csv in archivos_csv]

    diagnostico = pd.DataFrame(registros)

    diagnostico = diagnostico.sort_values(
        by="tamaño_mb",
        ascending=False,
    ).reset_index(drop=True)

    return diagnostico


def guardar_diagnostico(diagnostico: pd.DataFrame) -> None:
    """
    Guarda el diagnóstico para reutilizarlo en reportes Quarto.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    diagnostico.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8",
    )


def main() -> None:
    diagnostico = diagnosticar_datos_sinteticos()

    print("\nDiagnóstico inicial de datos sintéticos corporativos:\n")
    print(diagnostico.to_string(index=False))

    guardar_diagnostico(diagnostico)

    print(f"\nDiagnóstico guardado en: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()