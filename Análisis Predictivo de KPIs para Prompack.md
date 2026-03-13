# Análisis Predictivo de KPIs para Prompack

Este repositorio contiene un script de Python diseñado para analizar el tablero de control de Prompack en Google Sheets, predecir el rendimiento futuro de los indicadores clave de rendimiento (KPIs) y confrontarlos con las metas estratégicas definidas para 2027.

## Características

*   **Extracción de Datos**: Conecta y extrae datos de múltiples pestañas históricas de un Google Sheet.
*   **Predicción de KPIs**: Utiliza un modelo de regresión lineal simple para proyectar el valor futuro de los KPIs.
*   **Confrontación con Metas**: Compara los valores predichos con las metas establecidas para 2027.
*   **Generación de Reportes**: Genera un resumen en consola y un archivo Excel con los resultados de la predicción.

## Requisitos

Para ejecutar este script, necesitarás Python 3.x y las siguientes librerías:

*   `gspread`
*   `pandas`
*   `scikit-learn`
*   `openpyxl`

Puedes instalar estas dependencias usando `pip`:

```bash
pip install -r requirements.txt
```

## Configuración

1.  **Google Sheet URL**: Asegúrate de que la URL de tu Google Sheet esté correctamente configurada en la variable `GOOGLE_SHEET_URL` dentro del script `predictive_dashboard.py`.

    ```python
    GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1GSFc-H2yxU-OFF3FqOrxVfEIcO2Wgd1eeaMBraf_YKI/edit?usp=sharing"
    ```

2.  **Permisos del Google Sheet**: El script intenta autenticarse con credenciales de servicio. Para que funcione, tu Google Sheet debe ser **público** o debes configurar una **cuenta de servicio de Google Cloud** y compartir el Google Sheet con el correo electrónico de esa cuenta de servicio. Luego, el archivo JSON de credenciales de la cuenta de servicio debe estar accesible en el entorno donde se ejecuta el script (por ejemplo, a través de la variable de entorno `GOOGLE_APPLICATION_CREDENTIALS`).

    *   **Opción 1 (Público)**: Si tu hoja de cálculo es pública (cualquiera con el enlace puede verla), `gspread` puede acceder sin configuración adicional de credenciales de servicio.
    *   **Opción 2 (Cuenta de Servicio)**: Para hojas privadas, sigue estos pasos:
        1.  Crea un proyecto en Google Cloud Console.
        2.  Habilita la API de Google Sheets y la API de Google Drive.
        3.  Crea una cuenta de servicio y descarga el archivo JSON de credenciales.
        4.  Comparte tu Google Sheet con el correo electrónico de la cuenta de servicio.
        5.  Configura la variable de entorno `GOOGLE_APPLICATION_CREDENTIALS` para que apunte a la ruta de tu archivo JSON.

3.  **Nombres de Pestañas**: Verifica que los nombres de las pestañas históricas (`HISTORICAL_SHEET_NAMES`) y la pestaña de metas (`GOALS_SHEET_NAME`) en el script coincidan con los de tu Google Sheet.

## Uso

Para ejecutar el script, simplemente navega al directorio donde guardaste `predictive_dashboard.py` y ejecuta:

```bash
python predictive_dashboard.py
```

El script imprimirá los resultados de la predicción en la consola y generará un archivo Excel llamado `predicciones_kpi_prompack.xlsx` en el mismo directorio.

## Modelos de Predicción

Actualmente, el script utiliza un modelo de **Regresión Lineal Simple** (`sklearn.linear_model.LinearRegression`) para proyectar las tendencias de los KPIs. Este modelo es adecuado para identificar tendencias lineales a partir de datos históricos. Para conjuntos de datos más complejos o con estacionalidad, se podrían explorar modelos de series de tiempo más avanzados (ej., ARIMA, Prophet).

## Contribuciones

Las contribuciones son bienvenidas. Si tienes sugerencias para mejorar el modelo de predicción, la extracción de datos o la usabilidad, no dudes en abrir un *issue* o enviar un *pull request*.

---

**Autor:** Manus AI
**Fecha:** 13 de marzo de 2026
