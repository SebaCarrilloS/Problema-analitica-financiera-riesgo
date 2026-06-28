from pathlib import Path

import pandas as pd

from src.config import CORPORATE_SYNTHETIC_DIR, PROCESSED_DATA_DIR


OUTPUT_DIR = PROCESSED_DATA_DIR / "validaciones"
OUTPUT_PATH = OUTPUT_DIR / "validacion_synthetic_corporate.csv"


ARCHIVOS_ESPERADOS = {
    "dim_periodo": "dim_periodo.csv",
    "dim_filial": "dim_filial.csv",
    "dim_sucursal": "dim_sucursal.csv",
    "dim_ejecutivo": "dim_ejecutivo.csv",
    "dim_canal": "dim_canal.csv",
    "dim_producto": "dim_producto.csv",
    "dim_segmento": "dim_segmento.csv",
    "fact_asignacion_cartera": "fact_asignacion_cartera.csv",
    "fact_metas_mensuales": "fact_metas_mensuales.csv",
    "fact_costos_operacionales": "fact_costos_operacionales.csv",
}


COLUMNAS_REQUERIDAS = {
    "dim_periodo": ["periodo", "fecha_periodo", "anio", "mes"],
    "dim_filial": [
        "id_filial",
        "nombre_filial",
        "zona",
        "tipo_filial",
        "fecha_inicio_operacion",
        "estado_filial",
    ],
    "dim_sucursal": [
        "id_sucursal",
        "id_filial",
        "nombre_sucursal",
        "region",
        "ciudad",
        "estado_sucursal",
    ],
    "dim_ejecutivo": [
        "id_ejecutivo",
        "id_sucursal",
        "nombre_ejecutivo",
        "cargo",
        "fecha_ingreso",
        "estado_ejecutivo",
    ],
    "dim_canal": ["id_canal", "nombre_canal", "tipo_canal"],
    "dim_producto": [
        "id_producto",
        "nombre_producto",
        "familia_producto",
        "margen_esperado",
        "riesgo_esperado",
        "estado_producto",
    ],
    "dim_segmento": [
        "id_segmento",
        "nombre_segmento",
        "perfil_riesgo",
        "rango_ingreso_estimado",
    ],
    "fact_asignacion_cartera": [
        "SK_ID_CURR",
        "id_filial",
        "id_sucursal",
        "id_ejecutivo",
        "id_canal",
        "id_producto",
        "id_segmento",
        "fecha_asignacion",
        "estado_asignacion",
    ],
    "fact_metas_mensuales": [
        "periodo",
        "id_filial",
        "id_producto",
        "id_canal",
        "meta_colocacion",
        "meta_clientes",
        "meta_margen",
    ],
    "fact_costos_operacionales": [
        "periodo",
        "id_filial",
        "id_sucursal",
        "costo_personal",
        "costo_arriendo",
        "costo_operacion",
        "costo_marketing",
        "costo_total",
    ],
}


def agregar_validacion(
    registros: list[dict],
    tabla: str,
    validacion: str,
    estado: str,
    detalle: str,
) -> None:
    registros.append(
        {
            "tabla": tabla,
            "validacion": validacion,
            "estado": estado,
            "detalle": detalle,
        }
    )


def cargar_tablas() -> dict[str, pd.DataFrame | None]:
    tablas = {}

    for tabla, archivo in ARCHIVOS_ESPERADOS.items():
        path = CORPORATE_SYNTHETIC_DIR / archivo

        if not path.exists():
            tablas[tabla] = None
            continue

        tablas[tabla] = pd.read_csv(path)

    return tablas


def validar_existencia_y_estructura(
    tablas: dict[str, pd.DataFrame | None],
    registros: list[dict],
) -> None:
    for tabla, archivo in ARCHIVOS_ESPERADOS.items():
        df = tablas.get(tabla)

        if df is None:
            agregar_validacion(
                registros,
                tabla,
                "existencia_archivo",
                "ERROR",
                f"No existe el archivo esperado: {archivo}",
            )
            continue

        agregar_validacion(
            registros,
            tabla,
            "existencia_archivo",
            "OK",
            f"Archivo encontrado: {archivo}",
        )

        agregar_validacion(
            registros,
            tabla,
            "tabla_no_vacia",
            "OK" if len(df) > 0 else "ERROR",
            f"Filas encontradas: {len(df)}",
        )

        columnas = set(df.columns)

        for columna in COLUMNAS_REQUERIDAS[tabla]:
            agregar_validacion(
                registros,
                tabla,
                f"columna_requerida_{columna}",
                "OK" if columna in columnas else "ERROR",
                (
                    f"Columna {columna} presente."
                    if columna in columnas
                    else f"Columna {columna} ausente."
                ),
            )


def validar_integridad_referencial(
    tablas: dict[str, pd.DataFrame],
    registros: list[dict],
) -> None:
    dim_filial = tablas["dim_filial"]
    dim_sucursal = tablas["dim_sucursal"]
    dim_ejecutivo = tablas["dim_ejecutivo"]
    dim_canal = tablas["dim_canal"]
    dim_producto = tablas["dim_producto"]
    dim_segmento = tablas["dim_segmento"]
    dim_periodo = tablas["dim_periodo"]

    fact_asignacion = tablas["fact_asignacion_cartera"]
    fact_metas = tablas["fact_metas_mensuales"]
    fact_costos = tablas["fact_costos_operacionales"]

    validaciones_fk = [
        ("dim_sucursal", dim_sucursal, "id_filial", dim_filial, "id_filial"),
        ("dim_ejecutivo", dim_ejecutivo, "id_sucursal", dim_sucursal, "id_sucursal"),
        ("fact_asignacion_cartera", fact_asignacion, "id_filial", dim_filial, "id_filial"),
        ("fact_asignacion_cartera", fact_asignacion, "id_sucursal", dim_sucursal, "id_sucursal"),
        ("fact_asignacion_cartera", fact_asignacion, "id_ejecutivo", dim_ejecutivo, "id_ejecutivo"),
        ("fact_asignacion_cartera", fact_asignacion, "id_canal", dim_canal, "id_canal"),
        ("fact_asignacion_cartera", fact_asignacion, "id_producto", dim_producto, "id_producto"),
        ("fact_asignacion_cartera", fact_asignacion, "id_segmento", dim_segmento, "id_segmento"),
        ("fact_metas_mensuales", fact_metas, "periodo", dim_periodo, "periodo"),
        ("fact_metas_mensuales", fact_metas, "id_filial", dim_filial, "id_filial"),
        ("fact_metas_mensuales", fact_metas, "id_producto", dim_producto, "id_producto"),
        ("fact_metas_mensuales", fact_metas, "id_canal", dim_canal, "id_canal"),
        ("fact_costos_operacionales", fact_costos, "periodo", dim_periodo, "periodo"),
        ("fact_costos_operacionales", fact_costos, "id_filial", dim_filial, "id_filial"),
        ("fact_costos_operacionales", fact_costos, "id_sucursal", dim_sucursal, "id_sucursal"),
    ]

    for tabla_origen, df_origen, col_origen, df_ref, col_ref in validaciones_fk:
        total_invalidos = int((~df_origen[col_origen].isin(df_ref[col_ref])).sum())

        agregar_validacion(
            registros,
            tabla_origen,
            f"integridad_{col_origen}",
            "OK" if total_invalidos == 0 else "ERROR",
            f"Registros con {col_origen} sin referencia válida: {total_invalidos}",
        )


def validar_problemas_controlados(
    tablas: dict[str, pd.DataFrame],
    registros: list[dict],
) -> None:
    dim_sucursal = tablas["dim_sucursal"]
    dim_ejecutivo = tablas["dim_ejecutivo"]
    dim_producto = tablas["dim_producto"]

    fact_asignacion = tablas["fact_asignacion_cartera"]
    fact_metas = tablas["fact_metas_mensuales"]
    fact_costos = tablas["fact_costos_operacionales"]

    productos_sin_familia = int(dim_producto["familia_producto"].isna().sum())

    agregar_validacion(
        registros,
        "dim_producto",
        "productos_sin_familia_gerencial",
        "WARNING" if productos_sin_familia > 0 else "OK",
        f"Productos sin familia gerencial: {productos_sin_familia}",
    )

    sucursales_nombre_inconsistente = int(
        dim_sucursal["nombre_sucursal"]
        .astype(str)
        .str.contains("Suc\\.", regex=True)
        .sum()
    )

    agregar_validacion(
        registros,
        "dim_sucursal",
        "nombres_sucursal_inconsistentes",
        "WARNING" if sucursales_nombre_inconsistente > 0 else "OK",
        (
            "Sucursales con abreviatura o nombre potencialmente inconsistente: "
            f"{sucursales_nombre_inconsistente}"
        ),
    )

    asignacion_ejecutivo = fact_asignacion.merge(
        dim_ejecutivo[["id_ejecutivo", "estado_ejecutivo"]],
        on="id_ejecutivo",
        how="left",
    )

    cartera_ejecutivos_inactivos = int(
        (asignacion_ejecutivo["estado_ejecutivo"] == "Inactivo").sum()
    )

    agregar_validacion(
        registros,
        "fact_asignacion_cartera",
        "cartera_asignada_a_ejecutivos_inactivos",
        "WARNING" if cartera_ejecutivos_inactivos > 0 else "OK",
        f"Clientes asignados a ejecutivos inactivos: {cartera_ejecutivos_inactivos}",
    )

    costos_negativos = int(
        (
            (fact_costos["costo_personal"] < 0)
            | (fact_costos["costo_arriendo"] < 0)
            | (fact_costos["costo_operacion"] < 0)
            | (fact_costos["costo_marketing"] < 0)
            | (fact_costos["costo_total"] < 0)
        ).sum()
    )

    agregar_validacion(
        registros,
        "fact_costos_operacionales",
        "costos_negativos",
        "WARNING" if costos_negativos > 0 else "OK",
        f"Registros con algún costo negativo: {costos_negativos}",
    )

    periodos = tablas["dim_periodo"]["periodo"].nunique()
    filiales = tablas["dim_filial"]["id_filial"].nunique()
    productos = tablas["dim_producto"]["id_producto"].nunique()
    canales = tablas["dim_canal"]["id_canal"].nunique()

    combinaciones_esperadas = periodos * filiales * productos * canales
    combinaciones_reales = len(fact_metas)
    metas_faltantes = combinaciones_esperadas - combinaciones_reales

    agregar_validacion(
        registros,
        "fact_metas_mensuales",
        "metas_faltantes",
        "WARNING" if metas_faltantes > 0 else "OK",
        (
            f"Combinaciones esperadas={combinaciones_esperadas}; "
            f"reales={combinaciones_reales}; faltantes={metas_faltantes}"
        ),
    )


def validar_datos_sinteticos() -> pd.DataFrame:
    tablas = cargar_tablas()
    registros = []

    validar_existencia_y_estructura(tablas, registros)

    if any(df is None for df in tablas.values()):
        return pd.DataFrame(registros)

    validar_integridad_referencial(tablas, registros)
    validar_problemas_controlados(tablas, registros)

    return pd.DataFrame(registros)


def guardar_validacion(resultado: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    resultado.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8",
    )


def main() -> None:
    resultado = validar_datos_sinteticos()

    print("\nResultado de validación de datos sintéticos corporativos:\n")
    print(resultado.to_string(index=False))

    guardar_validacion(resultado)

    resumen = resultado["estado"].value_counts().to_dict()

    print("\nResumen de validación:")
    print(f"OK: {resumen.get('OK', 0)}")
    print(f"WARNING: {resumen.get('WARNING', 0)}")
    print(f"ERROR: {resumen.get('ERROR', 0)}")
    print(f"Resultado guardado en: {OUTPUT_PATH}")

    if resumen.get("ERROR", 0) > 0:
        print("\nAdvertencia: existen errores estructurales que deben corregirse.")
    elif resumen.get("WARNING", 0) > 0:
        print("\nValidación completada con advertencias esperadas/controladas.")
    else:
        print("\nValidación completada sin observaciones.")


if __name__ == "__main__":
    main()