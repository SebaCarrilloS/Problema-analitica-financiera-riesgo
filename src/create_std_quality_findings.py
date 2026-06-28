import duckdb
import pandas as pd

from src.config import DATABASE_PATH, PROCESSED_DATA_DIR


OUTPUT_DIR = PROCESSED_DATA_DIR / "data_quality"
OUTPUT_PATH = OUTPUT_DIR / "hallazgos_calidad_std.csv"


def build_findings() -> pd.DataFrame:
    findings = [
        {
            "id_hallazgo": "STD_QA_001",
            "tabla": "application_train",
            "columna": "flag_dificultad_pago",
            "tipo_hallazgo": "desbalance_clase_objetivo",
            "severidad": "ALTA",
            "descripcion": "La variable objetivo presenta fuerte desbalance: la clase 1 representa cerca del 8% de los casos.",
            "evidencia": "flag_dificultad_pago=0: 91.93%; flag_dificultad_pago=1: 8.07%",
            "impacto_potencial": "Puede afectar el entrenamiento y evaluación del modelo de riesgo si se usa accuracy como métrica principal.",
            "tratamiento_futuro": "Usar métricas adecuadas para clases desbalanceadas: AUC, recall, precision, F1, matriz de confusión, lift y análisis por umbrales.",
            "estado": "documentado",
        },
        {
            "id_hallazgo": "STD_QA_002",
            "tabla": "application_train, application_test",
            "columna": "antiguedad_auto_anios",
            "tipo_hallazgo": "nulos_altos",
            "severidad": "MEDIA",
            "descripcion": "La columna antiguedad_auto_anios tiene cerca de 66% de nulos en train y test.",
            "evidencia": "application_train: 65.99%; application_test: 66.29%",
            "impacto_potencial": "La ausencia puede estar explicada por clientes sin auto, por lo que imputar directamente podría introducir sesgo.",
            "tratamiento_futuro": "Tratar junto con flag_tiene_auto. Evaluar creación de indicador cliente_sin_auto y mantener nulo cuando no corresponda antigüedad.",
            "estado": "documentado",
        },
        {
            "id_hallazgo": "STD_QA_003",
            "tabla": "application_train, application_test",
            "columna": "score_externo_1",
            "tipo_hallazgo": "nulos_altos_y_diferencia_train_test",
            "severidad": "ALTA",
            "descripcion": "score_externo_1 tiene alto porcentaje de nulos y una diferencia relevante entre train y test.",
            "evidencia": "application_train: 56.38%; application_test: 42.12%; diferencia test-train: -14.26 puntos porcentuales",
            "impacto_potencial": "Puede afectar el modelo predictivo y generar diferencias de comportamiento entre entrenamiento y scoring.",
            "tratamiento_futuro": "Evaluar imputación, creación de flag_score_externo_1_nulo y comparación de desempeño con y sin esta variable.",
            "estado": "documentado",
        },
        {
            "id_hallazgo": "STD_QA_004",
            "tabla": "application_train, application_test",
            "columna": "ocupacion",
            "tipo_hallazgo": "nulos_relevantes",
            "severidad": "MEDIA",
            "descripcion": "La columna ocupacion tiene alrededor de 31% a 32% de nulos.",
            "evidencia": "application_train: 31.35%; application_test: 32.01%",
            "impacto_potencial": "Puede limitar análisis por perfil laboral y afectar modelos que usen variables ocupacionales.",
            "tratamiento_futuro": "Evaluar categoría 'Sin informacion' o flag_ocupacion_informada antes de usarla en análisis o ML.",
            "estado": "documentado",
        },
        {
            "id_hallazgo": "STD_QA_005",
            "tabla": "application_train, application_test",
            "columna": "score_externo_3",
            "tipo_hallazgo": "nulos_relevantes",
            "severidad": "MEDIA",
            "descripcion": "score_externo_3 presenta nulos relevantes, aunque menores que score_externo_1.",
            "evidencia": "application_train: 19.83%; application_test: 17.78%",
            "impacto_potencial": "Puede requerir tratamiento específico si se usa como variable predictiva.",
            "tratamiento_futuro": "Evaluar imputación, flag de nulidad y relevancia predictiva en fase de ML.",
            "estado": "documentado",
        },
        {
            "id_hallazgo": "STD_QA_006",
            "tabla": "application_train, application_test",
            "columna": "dias_empleo_relativo",
            "tipo_hallazgo": "valor_especial",
            "severidad": "ALTA",
            "descripcion": "La columna dias_empleo_relativo contiene el valor especial 365243, que no representa una antigüedad laboral real.",
            "evidencia": "maximo observado en train y test: 365243",
            "impacto_potencial": "Si se convierte directamente a años, genera antigüedades laborales imposibles y distorsiona análisis y modelos.",
            "tratamiento_futuro": "En cst_data, tratar 365243 como valor especial, convertirlo a NULL o crear flag_empleo_valor_especial.",
            "estado": "documentado",
        },
        {
            "id_hallazgo": "STD_QA_007",
            "tabla": "application_train",
            "columna": "ingreso_total",
            "tipo_hallazgo": "outlier",
            "severidad": "MEDIA",
            "descripcion": "ingreso_total presenta un valor máximo extremadamente alto en application_train.",
            "evidencia": "maximo application_train: 117000000; mediana application_train: 147150",
            "impacto_potencial": "Puede distorsionar promedios, ratios financieros, escalamiento de variables y visualizaciones.",
            "tratamiento_futuro": "Evaluar percentiles altos, winsorización, log-transform o tramos de ingreso para análisis y ML.",
            "estado": "documentado",
        },
        {
            "id_hallazgo": "STD_QA_008",
            "tabla": "application_train",
            "columna": "genero",
            "tipo_hallazgo": "categoria_rara",
            "severidad": "BAJA",
            "descripcion": "La variable genero contiene una categoría poco frecuente llamada XNA.",
            "evidencia": "genero=XNA: 4 casos en application_train",
            "impacto_potencial": "Puede generar categorías residuales de muy baja frecuencia en análisis y modelos.",
            "tratamiento_futuro": "Evaluar agrupación como 'Sin informacion' u 'Otro' en cst_data.",
            "estado": "documentado",
        },
        {
            "id_hallazgo": "STD_QA_009",
            "tabla": "application_train",
            "columna": "estado_civil",
            "tipo_hallazgo": "categoria_rara",
            "severidad": "BAJA",
            "descripcion": "La variable estado_civil contiene la categoría Unknown con muy baja frecuencia.",
            "evidencia": "estado_civil=Unknown: 2 casos en application_train",
            "impacto_potencial": "Puede requerir agrupación en una categoría de información no especificada.",
            "tratamiento_futuro": "Evaluar tratamiento como 'Sin informacion' en cst_data.",
            "estado": "documentado",
        },
        {
            "id_hallazgo": "STD_QA_010",
            "tabla": "fact_asignacion_cartera",
            "columna": "id_cliente, fecha_asignacion, estado_asignacion",
            "tipo_hallazgo": "control_integridad_correcto",
            "severidad": "INFORMATIVA",
            "descripcion": "La asignación de cartera no presenta problemas estructurales relevantes en los controles aplicados.",
            "evidencia": "clientes sin application_train: 0; duplicados id_cliente: 0; fecha_asignacion nula: 0; total filas: 307511",
            "impacto_potencial": "La tabla puente puede usarse como base confiable para conectar riesgo crediticio con estructura corporativa.",
            "tratamiento_futuro": "Mantener controles en futuras regeneraciones de datos sintéticos.",
            "estado": "documentado",
        },
    ]

    return pd.DataFrame(findings)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    findings = build_findings()
    findings.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    with duckdb.connect(DATABASE_PATH) as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS data_quality")
        con.register("tmp_hallazgos_calidad_std", findings)
        con.execute("DROP TABLE IF EXISTS data_quality.hallazgos_calidad_std")
        con.execute(
            """
            CREATE TABLE data_quality.hallazgos_calidad_std AS
            SELECT *
            FROM tmp_hallazgos_calidad_std
            """
        )
        con.unregister("tmp_hallazgos_calidad_std")

    print("Tabla creada: data_quality.hallazgos_calidad_std")
    print(f"CSV creado: {OUTPUT_PATH}")
    print()
    print(findings[["id_hallazgo", "severidad", "tabla", "columna", "tipo_hallazgo"]].to_string(index=False))


if __name__ == "__main__":
    main()