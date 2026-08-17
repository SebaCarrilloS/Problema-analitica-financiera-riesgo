# Reproducción del proyecto

Esta guía describe los pasos generales para reproducir el proyecto **Analítica Financiera de Riesgo y Rentabilidad** desde un entorno local.

El proyecto integra Python, SQL, DuckDB, Quarto, Machine Learning y Power BI.

---

## 1. Requisitos previos

Se requiere tener instalado:

- Python 3.12
- Git
- Quarto
- Power BI Desktop
- Visual Studio Code
- Extensión de Python para VS Code
- Extensión de Quarto para VS Code

---

## 2. Clonar el repositorio

```powershell
git clone <URL_DEL_REPOSITORIO>
cd analitica-financiera-riesgo
```

---

## 3. Crear entorno virtual

Desde la raíz del proyecto:

```powershell
py -3.12 -m venv .venv
```

Activar el entorno:

```powershell
.venv\Scripts\Activate.ps1
```

Actualizar `pip`:

```powershell
py -m pip install --upgrade pip
```

Instalar dependencias:

```powershell
py -m pip install -r requirements.txt
```

---

## 4. Estructura esperada del proyecto

La estructura general del repositorio es:

```text
analitica-financiera-riesgo/
│
├── data/
│   └── database/
│
├── docs/
│
├── models/
│
├── powerbi/
│
├── reports/
│   ├── docs/
│   └── tables/
│
├── sql/
│
├── src/
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## 5. Crear schemas en DuckDB

El proyecto utiliza DuckDB como base analítica local.

Para crear los schemas principales:

```powershell
py -m src.sql_runner
```

El archivo SQL principal de administración se encuentra en:

```text
sql/00_admin/00_create_schemas.sql
```

Los schemas esperados son:

```text
raw_data
std_data
cst_data
mart_financiero
data_quality
```

---

## 6. Datos fuente

El proyecto usa datos financieros y crediticios procesados localmente.

La base DuckDB principal se ubica en:

```text
data/database/financiera.duckdb
```

Los datos crudos o archivos fuente deben ubicarse en la carpeta correspondiente dentro de:

```text
data/
```

Dependiendo del entorno, algunos archivos fuente pueden no estar incluidos en Git por tamaño, privacidad o configuración del `.gitignore`.

---

## 7. Capas analíticas

El flujo de datos sigue una arquitectura por capas:

```text
raw_data
  ↓
std_data
  ↓
cst_data
  ↓
mart_financiero
```

### `raw_data`

Contiene los datos originales o vistas sobre archivos fuente.

### `std_data`

Estandariza columnas, tipos y formatos.

### `cst_data`

Contiene datos curados y enriquecidos.

### `mart_financiero`

Contiene tablas listas para análisis, dashboard y scoring.

---

## 8. Documentos Quarto

El proyecto está documentado mediante archivos Quarto ubicados en:

```text
docs/
```

Documentos principales:

```text
docs/00_fase_0_alcance_proyecto.qmd
docs/01_diagnostico_datos.qmd
docs/02_calidad_datos.qmd
docs/03_mart_financiero.qmd
docs/04_mart_financiero_consumo.qmd
docs/05_documentacion_powerbi.qmd
docs/06_modelo_riesgo_ml.qmd
docs/07_interpretabilidad_modelo.qmd
docs/08_scoring_operativo.qmd
```

Para renderizar un documento específico:

```powershell
quarto render docs\06_modelo_riesgo_ml.qmd
```

Para renderizar otro documento, reemplazar el nombre del archivo.

Los HTML generados se guardan en:

```text
reports/docs/
```

---

## 9. Modelo predictivo

El modelo final se guarda en:

```text
models/modelo_riesgo_xgboost.joblib
```

La configuración del modelo se guarda en:

```text
models/configuracion_modelo_riesgo.json
```

Las métricas de validación final se guardan en:

```text
models/metricas_validacion_final.csv
```

Documento principal del modelo:

```text
docs/06_modelo_riesgo_ml.qmd
```

---

## 10. Interpretabilidad SHAP

La interpretabilidad global del modelo se documenta en:

```text
docs/07_interpretabilidad_modelo.qmd
```

Tablas exportadas:

```text
reports/tables/importancia_shap_variables_originales.csv
reports/tables/importancia_shap_variables_transformadas.csv
```

---

## 11. Scoring operativo

El scoring operativo se genera en:

```text
docs/08_scoring_operativo.qmd
```

La tabla principal exportada es:

```text
reports/tables/scoring_riesgo_clientes.csv
```

También se generan tablas resumen para Power BI:

```text
reports/tables/resumen_scoring.csv
reports/tables/resumen_banda_riesgo.csv
```

La tabla estructurada en DuckDB queda en:

```text
mart_financiero.scoring_riesgo_clientes
```

---

## 12. Power BI

El dashboard principal se encuentra en:

```text
powerbi/dashboard_riesgo_financiero.pbix
```

El dashboard utiliza tablas resumen para mantener un modelo liviano y orientado a reporting ejecutivo.

Tablas principales utilizadas:

```text
Resumen General
Resumen Producto
Resumen Segmento
Resumen Filial
Resumen Canal
Resumen Scoring
Resumen Banda Riesgo
```

La página principal integra:

- KPIs observados de cartera;
- tasa de dificultad de pago;
- métricas predictivas de scoring;
- distribución de clientes por banda de riesgo;
- análisis por producto y segmento.

---

## 13. Flujo general de reproducción

Orden recomendado:

```text
1. Clonar repositorio.
2. Crear entorno virtual.
3. Instalar dependencias.
4. Crear schemas DuckDB.
5. Cargar o conectar datos fuente.
6. Ejecutar scripts de transformación.
7. Construir capas std, cst y mart.
8. Renderizar documentos Quarto.
9. Entrenar o cargar modelo predictivo.
10. Ejecutar interpretabilidad SHAP.
11. Generar scoring operativo.
12. Exportar tablas resumen.
13. Abrir dashboard Power BI.
14. Actualizar fuentes si corresponde.
```

---

## 14. Comandos útiles

Ver estado de Git:

```powershell
git status
```

Agregar cambios:

```powershell
git add .
```

Crear commit:

```powershell
git commit -m "Mensaje del commit"
```

Ejecutar runner SQL:

```powershell
py -m src.sql_runner
```

Renderizar documento Quarto:

```powershell
quarto render docs\08_scoring_operativo.qmd
```

---

## 15. Consideraciones

- Algunos archivos pesados pueden no estar versionados.
- La base DuckDB puede cambiar localmente durante la ejecución del proyecto.
- Power BI consume archivos exportados y tablas resumen, no una conexión productiva en tiempo real.
- El modelo fue desarrollado como proyecto de portafolio, no como sistema productivo regulatorio.
- Las interpretaciones SHAP representan asociaciones aprendidas por el modelo, no causalidad.

---

## 16. Resultado esperado

Al completar la reproducción, deberían existir:

```text
data/database/financiera.duckdb
models/modelo_riesgo_xgboost.joblib
models/configuracion_modelo_riesgo.json
models/metricas_validacion_final.csv
reports/tables/scoring_riesgo_clientes.csv
reports/tables/resumen_scoring.csv
reports/tables/resumen_banda_riesgo.csv
powerbi/dashboard_riesgo_financiero.pbix
```

Y deberían poder renderizarse los documentos Quarto principales en:

```text
reports/docs/
```