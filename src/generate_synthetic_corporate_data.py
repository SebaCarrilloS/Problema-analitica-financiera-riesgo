from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from src.config import CORPORATE_SYNTHETIC_DIR, DATABASE_PATH


RANDOM_SEED = 42
rng = np.random.default_rng(RANDOM_SEED)


@dataclass(frozen=True)
class SyntheticConfig:
    n_filiales: int = 6
    n_sucursales: int = 25
    n_ejecutivos: int = 100
    n_productos: int = 7
    n_canales: int = 5
    n_segmentos: int = 6
    n_meses: int = 24
    porcentaje_problemas_min: float = 0.03
    porcentaje_problemas_max: float = 0.07


CONFIG = SyntheticConfig()


def obtener_clientes_home_credit() -> pd.DataFrame:
    """
    Obtiene clientes desde raw_data.application_train.

    Se usa DuckDB porque Home Credit ya está disponible como vista raw.
    """
    query = """
    SELECT
        SK_ID_CURR,
        TARGET,
        AMT_INCOME_TOTAL,
        AMT_CREDIT,
        NAME_CONTRACT_TYPE
    FROM raw_data.application_train;
    """

    with duckdb.connect(str(DATABASE_PATH)) as connection:
        clientes = connection.execute(query).fetchdf()

    return clientes


def crear_periodos(n_meses: int) -> pd.DataFrame:
    """
    Crea periodos mensuales para metas y costos.
    """
    periodos = pd.date_range(
        start="2024-01-01",
        periods=n_meses,
        freq="MS",
    )

    return pd.DataFrame(
        {
            "periodo": periodos.strftime("%Y-%m"),
            "fecha_periodo": periodos,
            "anio": periodos.year,
            "mes": periodos.month,
        }
    )


def crear_dim_filial() -> pd.DataFrame:
    zonas = ["Norte", "Centro", "Sur", "Metropolitana", "Austral", "Digital"]
    tipos = ["Retail Financiero", "Banca Personas", "Mixta"]

    registros = []

    for i in range(1, CONFIG.n_filiales + 1):
        registros.append(
            {
                "id_filial": f"FIL_{i:03d}",
                "nombre_filial": f"Filial {zonas[i - 1]}",
                "zona": zonas[i - 1],
                "tipo_filial": rng.choice(tipos, p=[0.5, 0.3, 0.2]),
                "fecha_inicio_operacion": pd.Timestamp("2015-01-01")
                + pd.DateOffset(months=int(rng.integers(0, 72))),
                "estado_filial": "Activa",
            }
        )

    return pd.DataFrame(registros)


def crear_dim_sucursal(dim_filial: pd.DataFrame) -> pd.DataFrame:
    ciudades = [
        "Santiago",
        "Valparaíso",
        "Antofagasta",
        "La Serena",
        "Concepción",
        "Temuco",
        "Puerto Montt",
        "Rancagua",
        "Talca",
        "Iquique",
    ]

    registros = []

    filiales = dim_filial["id_filial"].tolist()

    for i in range(1, CONFIG.n_sucursales + 1):
        id_filial = rng.choice(filiales)
        ciudad = rng.choice(ciudades)

        registros.append(
            {
                "id_sucursal": f"SUC_{i:03d}",
                "id_filial": id_filial,
                "nombre_sucursal": f"Sucursal {ciudad} {i:02d}",
                "region": f"Región {int(rng.integers(1, 17))}",
                "ciudad": ciudad,
                "estado_sucursal": rng.choice(
                    ["Activa", "Activa", "Activa", "Inactiva"],
                    p=[0.35, 0.35, 0.2, 0.1],
                ),
            }
        )

    sucursales = pd.DataFrame(registros)

    # Problema controlado: nombres inconsistentes en algunas sucursales.
    n_problemas = max(1, int(len(sucursales) * 0.05))
    idx = rng.choice(sucursales.index, size=n_problemas, replace=False)

    for i in idx:
        nombre = sucursales.loc[i, "nombre_sucursal"]
        sucursales.loc[i, "nombre_sucursal"] = nombre.replace("Sucursal", "Suc.")

    return sucursales


def crear_dim_ejecutivo(dim_sucursal: pd.DataFrame) -> pd.DataFrame:
    nombres = [
        "Ana Torres",
        "Carlos Rivas",
        "María González",
        "Pedro Muñoz",
        "Camila Soto",
        "Javier Herrera",
        "Valentina Rojas",
        "Felipe Castillo",
        "Daniela Vega",
        "Matías Morales",
    ]

    cargos = ["Ejecutivo Comercial", "Ejecutivo Senior", "Gestor de Cartera"]

    registros = []

    sucursales = dim_sucursal["id_sucursal"].tolist()

    for i in range(1, CONFIG.n_ejecutivos + 1):
        registros.append(
            {
                "id_ejecutivo": f"EJE_{i:04d}",
                "id_sucursal": rng.choice(sucursales),
                "nombre_ejecutivo": rng.choice(nombres),
                "cargo": rng.choice(cargos, p=[0.6, 0.25, 0.15]),
                "fecha_ingreso": pd.Timestamp("2018-01-01")
                + pd.DateOffset(days=int(rng.integers(0, 1800))),
                "estado_ejecutivo": rng.choice(
                    ["Activo", "Activo", "Activo", "Inactivo"],
                    p=[0.4, 0.35, 0.15, 0.1],
                ),
            }
        )

    return pd.DataFrame(registros)


def crear_dim_canal() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id_canal": "CAN_001",
                "nombre_canal": "Sucursal",
                "tipo_canal": "Presencial",
            },
            {
                "id_canal": "CAN_002",
                "nombre_canal": "Digital",
                "tipo_canal": "Online",
            },
            {
                "id_canal": "CAN_003",
                "nombre_canal": "Call Center",
                "tipo_canal": "Remoto",
            },
            {
                "id_canal": "CAN_004",
                "nombre_canal": "Alianza Comercial",
                "tipo_canal": "Partner",
            },
            {
                "id_canal": "CAN_005",
                "nombre_canal": "Ejecutivo Terreno",
                "tipo_canal": "Presencial",
            },
        ]
    )


def crear_dim_producto() -> pd.DataFrame:
    productos = [
        ("PROD_001", "Crédito Consumo", "Créditos", 0.18, "Medio"),
        ("PROD_002", "Tarjeta Crédito", "Tarjetas", 0.22, "Alto"),
        ("PROD_003", "Crédito Automotriz", "Créditos", 0.16, "Medio"),
        ("PROD_004", "Refinanciamiento", "Normalización", 0.14, "Alto"),
        ("PROD_005", "Avance en Efectivo", "Tarjetas", 0.28, "Alto"),
        ("PROD_006", "Crédito Educación", "Créditos", 0.12, "Bajo"),
        ("PROD_007", "Compra de Cartera", "Normalización", 0.15, "Medio"),
    ]

    dim_producto = pd.DataFrame(
        productos,
        columns=[
            "id_producto",
            "nombre_producto",
            "familia_producto",
            "margen_esperado",
            "riesgo_esperado",
        ],
    )

    dim_producto["estado_producto"] = "Activo"

    # Problema controlado: algunos productos sin familia gerencial.
    idx = rng.choice(dim_producto.index, size=1, replace=False)
    dim_producto.loc[idx, "familia_producto"] = np.nan

    return dim_producto


def crear_dim_segmento() -> pd.DataFrame:
    segmentos = [
        ("SEG_001", "Masivo", "Medio", "0-500k"),
        ("SEG_002", "Medio", "Medio", "500k-1.2MM"),
        ("SEG_003", "Preferente", "Bajo", "1.2MM-2.5MM"),
        ("SEG_004", "Alto Valor", "Bajo", ">2.5MM"),
        ("SEG_005", "Riesgo Alto", "Alto", "Variable"),
        ("SEG_006", "Nuevo Cliente", "Medio", "Sin historial"),
    ]

    return pd.DataFrame(
        segmentos,
        columns=[
            "id_segmento",
            "nombre_segmento",
            "perfil_riesgo",
            "rango_ingreso_estimado",
        ],
    )


def asignar_segmento(row: pd.Series) -> str:
    """
    Asignación semi-aleatoria de segmento usando ingreso y TARGET.
    """
    ingreso = pd.to_numeric(row["AMT_INCOME_TOTAL"], errors="coerce")
    target = pd.to_numeric(row["TARGET"], errors="coerce")

    if target == 1 and rng.random() < 0.65:
        return "SEG_005"

    if pd.isna(ingreso):
        return rng.choice(["SEG_001", "SEG_006"])

    if ingreso >= 250000 and rng.random() < 0.7:
        return "SEG_004"

    if ingreso >= 150000 and rng.random() < 0.65:
        return "SEG_003"

    if ingreso >= 80000 and rng.random() < 0.6:
        return "SEG_002"

    return rng.choice(["SEG_001", "SEG_006", "SEG_002"], p=[0.55, 0.25, 0.20])


def crear_fact_asignacion_cartera(
    clientes: pd.DataFrame,
    dim_filial: pd.DataFrame,
    dim_sucursal: pd.DataFrame,
    dim_ejecutivo: pd.DataFrame,
    dim_canal: pd.DataFrame,
    dim_producto: pd.DataFrame,
) -> pd.DataFrame:
    """
    Asigna clientes reales de Home Credit a estructura corporativa sintética.
    """
    clientes_base = clientes.copy()

    clientes_base["id_segmento"] = clientes_base.apply(asignar_segmento, axis=1)

    sucursales = dim_sucursal[["id_sucursal", "id_filial"]].copy()
    ejecutivos = dim_ejecutivo[["id_ejecutivo", "id_sucursal", "estado_ejecutivo"]]

    registros = []

    for _, cliente in clientes_base.iterrows():
        sucursal = sucursales.sample(n=1, random_state=int(rng.integers(0, 1_000_000))).iloc[0]
        ejecutivos_sucursal = ejecutivos.loc[
            ejecutivos["id_sucursal"] == sucursal["id_sucursal"]
        ]

        if ejecutivos_sucursal.empty:
            ejecutivo = ejecutivos.sample(n=1, random_state=int(rng.integers(0, 1_000_000))).iloc[0]
        else:
            ejecutivo = ejecutivos_sucursal.sample(
                n=1,
                random_state=int(rng.integers(0, 1_000_000)),
            ).iloc[0]

        canal = dim_canal.sample(n=1, random_state=int(rng.integers(0, 1_000_000))).iloc[0]

        # Regla simple: clientes de mayor riesgo tienen algo más de probabilidad
        # de productos de refinanciamiento o avance.
        target = pd.to_numeric(cliente["TARGET"], errors="coerce")

        if target == 1 and rng.random() < 0.45:
            productos_candidatos = dim_producto[
                dim_producto["id_producto"].isin(["PROD_004", "PROD_005"])
            ]
        else:
            productos_candidatos = dim_producto

        producto = productos_candidatos.sample(
            n=1,
            random_state=int(rng.integers(0, 1_000_000)),
        ).iloc[0]

        registros.append(
            {
                "SK_ID_CURR": cliente["SK_ID_CURR"],
                "id_filial": sucursal["id_filial"],
                "id_sucursal": sucursal["id_sucursal"],
                "id_ejecutivo": ejecutivo["id_ejecutivo"],
                "id_canal": canal["id_canal"],
                "id_producto": producto["id_producto"],
                "id_segmento": cliente["id_segmento"],
                "fecha_asignacion": pd.Timestamp("2024-01-01")
                + pd.DateOffset(days=int(rng.integers(0, 365))),
                "estado_asignacion": rng.choice(
                    ["Activa", "Activa", "Activa", "Cerrada"],
                    p=[0.45, 0.35, 0.1, 0.1],
                ),
            }
        )

    asignacion = pd.DataFrame(registros)

    # Problema controlado:
    # algunos clientes quedan asignados a ejecutivos inactivos.
    ejecutivos_inactivos = dim_ejecutivo.loc[
        dim_ejecutivo["estado_ejecutivo"] == "Inactivo",
        "id_ejecutivo",
    ].tolist()

    if ejecutivos_inactivos:
        n_problemas = int(len(asignacion) * 0.04)
        idx = rng.choice(asignacion.index, size=n_problemas, replace=False)
        asignacion.loc[idx, "id_ejecutivo"] = rng.choice(
            ejecutivos_inactivos,
            size=n_problemas,
            replace=True,
        )

    return asignacion


def crear_fact_metas_mensuales(
    periodos: pd.DataFrame,
    dim_filial: pd.DataFrame,
    dim_producto: pd.DataFrame,
    dim_canal: pd.DataFrame,
) -> pd.DataFrame:
    registros = []

    for periodo in periodos["periodo"]:
        for id_filial in dim_filial["id_filial"]:
            for id_producto in dim_producto["id_producto"]:
                for id_canal in dim_canal["id_canal"]:
                    # Problema controlado: algunas metas faltantes.
                    if rng.random() < 0.04:
                        continue

                    meta_colocacion = int(rng.normal(180_000_000, 35_000_000))
                    meta_clientes = int(rng.normal(900, 180))
                    meta_margen = meta_colocacion * rng.uniform(0.08, 0.22)

                    registros.append(
                        {
                            "periodo": periodo,
                            "id_filial": id_filial,
                            "id_producto": id_producto,
                            "id_canal": id_canal,
                            "meta_colocacion": max(meta_colocacion, 10_000_000),
                            "meta_clientes": max(meta_clientes, 50),
                            "meta_margen": round(max(meta_margen, 1_000_000), 2),
                        }
                    )

    return pd.DataFrame(registros)


def crear_fact_costos_operacionales(
    periodos: pd.DataFrame,
    dim_sucursal: pd.DataFrame,
) -> pd.DataFrame:
    registros = []

    for periodo in periodos["periodo"]:
        for _, sucursal in dim_sucursal.iterrows():
            costo_personal = rng.normal(35_000_000, 5_000_000)
            costo_arriendo = rng.normal(12_000_000, 2_500_000)
            costo_operacion = rng.normal(8_000_000, 2_000_000)
            costo_marketing = rng.normal(4_000_000, 1_500_000)

            registros.append(
                {
                    "periodo": periodo,
                    "id_filial": sucursal["id_filial"],
                    "id_sucursal": sucursal["id_sucursal"],
                    "costo_personal": round(costo_personal, 2),
                    "costo_arriendo": round(costo_arriendo, 2),
                    "costo_operacion": round(costo_operacion, 2),
                    "costo_marketing": round(costo_marketing, 2),
                }
            )

    costos = pd.DataFrame(registros)
    costos["costo_total"] = (
        costos["costo_personal"]
        + costos["costo_arriendo"]
        + costos["costo_operacion"]
        + costos["costo_marketing"]
    )

    # Problema controlado: costos negativos inválidos.
    n_problemas = int(len(costos) * 0.03)
    idx = rng.choice(costos.index, size=n_problemas, replace=False)
    costos.loc[idx, "costo_operacion"] = -abs(costos.loc[idx, "costo_operacion"])
    costos.loc[idx, "costo_total"] = (
        costos.loc[idx, "costo_personal"]
        + costos.loc[idx, "costo_arriendo"]
        + costos.loc[idx, "costo_operacion"]
        + costos.loc[idx, "costo_marketing"]
    )

    return costos


def guardar_csv(df: pd.DataFrame, nombre_archivo: str) -> None:
    CORPORATE_SYNTHETIC_DIR.mkdir(parents=True, exist_ok=True)

    output_path = CORPORATE_SYNTHETIC_DIR / nombre_archivo

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )

    print(f"Archivo generado: {output_path} | filas={len(df)} | columnas={len(df.columns)}")


def main() -> None:
    print("Generando datos sintéticos corporativos...")

    clientes = obtener_clientes_home_credit()

    periodos = crear_periodos(CONFIG.n_meses)
    dim_filial = crear_dim_filial()
    dim_sucursal = crear_dim_sucursal(dim_filial)
    dim_ejecutivo = crear_dim_ejecutivo(dim_sucursal)
    dim_canal = crear_dim_canal()
    dim_producto = crear_dim_producto()
    dim_segmento = crear_dim_segmento()

    fact_asignacion_cartera = crear_fact_asignacion_cartera(
        clientes=clientes,
        dim_filial=dim_filial,
        dim_sucursal=dim_sucursal,
        dim_ejecutivo=dim_ejecutivo,
        dim_canal=dim_canal,
        dim_producto=dim_producto,
    )

    fact_metas_mensuales = crear_fact_metas_mensuales(
        periodos=periodos,
        dim_filial=dim_filial,
        dim_producto=dim_producto,
        dim_canal=dim_canal,
    )

    fact_costos_operacionales = crear_fact_costos_operacionales(
        periodos=periodos,
        dim_sucursal=dim_sucursal,
    )

    guardar_csv(periodos, "dim_periodo.csv")
    guardar_csv(dim_filial, "dim_filial.csv")
    guardar_csv(dim_sucursal, "dim_sucursal.csv")
    guardar_csv(dim_ejecutivo, "dim_ejecutivo.csv")
    guardar_csv(dim_canal, "dim_canal.csv")
    guardar_csv(dim_producto, "dim_producto.csv")
    guardar_csv(dim_segmento, "dim_segmento.csv")
    guardar_csv(fact_asignacion_cartera, "fact_asignacion_cartera.csv")
    guardar_csv(fact_metas_mensuales, "fact_metas_mensuales.csv")
    guardar_csv(fact_costos_operacionales, "fact_costos_operacionales.csv")

    print("\nDatos sintéticos corporativos generados correctamente.")


if __name__ == "__main__":
    main()