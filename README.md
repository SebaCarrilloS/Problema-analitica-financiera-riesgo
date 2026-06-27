# Analítica Financiera de Riesgo y Rentabilidad

Proyecto avanzado de portafolio orientado a la construcción de una solución analítica para control de gestión financiero, riesgo crediticio, rentabilidad y desempeño operacional.

El proyecto simula el caso de una organización financiera con múltiples filiales, productos, canales comerciales, sucursales, ejecutivos y segmentos de clientes. La gerencia necesita una capa analítica confiable para monitorear desempeño, detectar deterioro de cartera, evaluar cumplimiento de metas y apoyar decisiones estratégicas.

## Objetivo del proyecto

Construir una solución analítica reproducible que permita consolidar, limpiar, transformar, modelar y analizar información financiera y operacional, integrando SQL, Python, DuckDB, Quarto, Machine Learning y Power BI.

## Componentes principales

- Modelamiento de datos por capas.
- Validaciones de calidad de datos.
- SQL avanzado con DuckDB.
- Análisis financiero y control de gestión.
- Modelo de Machine Learning para predicción de mora.
- Reportes reproducibles con Quarto.
- Tablas finales para dashboard ejecutivo en Power BI.
- Uso de Git y GitHub como práctica profesional de versionamiento.

## Arquitectura analítica

El proyecto simula una arquitectura tipo data warehouse local utilizando DuckDB:

```text
raw_data
→ std_data
→ cst_data
→ mart_financiero
→ data_quality