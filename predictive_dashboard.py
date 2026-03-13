
import gspread
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

# --- Configuración --- #
# URL del Google Sheet (asegúrate de que sea público o que la cuenta de servicio tenga acceso)
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1GSFc-H2yxU-OFF3FqOrxVfEIcO2Wgd1eeaMBraf_YKI/edit?usp=sharing"

# Nombre de las pestañas con datos históricos (de más antiguo a más reciente)
HISTORICAL_SHEET_NAMES = ["Ene_26", "Feb_26", "Mar_26"]
# Nombre de la pestaña con las metas
GOALS_SHEET_NAME = "Metas_2026"

# Columnas clave para el análisis
KPI_COLUMN = "KPI"
VALUE_COLUMN = "mar-26" # Columna que contiene el valor actual del KPI en las hojas históricas
GOAL_COLUMN = "2027" # Columna que contiene la meta para 2027 en la hoja de metas

# --- Autenticación con Google Sheets (requiere archivo de credenciales) ---
# Para GitHub, se recomienda usar variables de entorno para las credenciales
# o configurar GitHub Actions para la autenticación.
# Por simplicidad para este script, asumimos que el sheet es público o que las credenciales
# se manejarán externamente (ej. gspread.service_account() si tienes un archivo JSON)
# Para un sheet público, no se necesita autenticación explícita con gspread.open_by_url
# Si el sheet es privado, necesitarás configurar gspread.service_account() o gspread.oauth()
# gc = gspread.service_account(filename='path/to/your/credentials.json')
# spreadsheet = gc.open_by_url(GOOGLE_SHEET_URL)

# Para este ejemplo, si el sheet es público, podemos intentar abrirlo directamente
try:
    gc = gspread.service_account() # Intenta autenticar con credenciales por defecto (ej. variables de entorno)
    spreadsheet = gc.open_by_url(GOOGLE_SHEET_URL)
except Exception as e:
    print(f"Error de autenticación o acceso al Google Sheet: {e}")
    print("Asegúrate de que el Google Sheet sea público o que las credenciales estén configuradas correctamente.")
    exit()

# --- Función para extraer datos de una pestaña --- #
def get_sheet_data(sheet_name):
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_values()
        df = pd.DataFrame(data[6:], columns=data[5]) # Asumiendo que los encabezados están en la fila 6 (índice 5)
        return df
    except gspread.exceptions.WorksheetNotFound:
        print(f"Error: La pestaña '{sheet_name}' no fue encontrada.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error al leer la pestaña '{sheet_name}': {e}")
        return pd.DataFrame()

# --- Extracción de datos históricos --- #
historical_data = []
for sheet_name in HISTORICAL_SHEET_NAMES:
    df_sheet = get_sheet_data(sheet_name)
    if not df_sheet.empty:
        # Limpiar y convertir datos relevantes
        df_sheet = df_sheet[[KPI_COLUMN, VALUE_COLUMN]].copy()
        df_sheet.columns = [KPI_COLUMN, "Valor"]
        df_sheet["Mes"] = sheet_name.split('_')[0] # Extraer el mes del nombre de la pestaña
        historical_data.append(df_sheet)

if not historical_data:
    print("No se pudieron cargar datos históricos. Terminando el script.")
    exit()

full_historical_df = pd.concat(historical_data, ignore_index=True)

# Convertir valores a numéricos, manejando errores
full_historical_df["Valor"] = pd.to_numeric(full_historical_df["Valor"].str.replace(',', ''), errors='coerce')
full_historical_df.dropna(subset=["Valor"], inplace=True)

# --- Extracción de metas --- #
goals_df = get_sheet_data(GOALS_SHEET_NAME)
if goals_df.empty:
    print("No se pudieron cargar las metas. Terminando el script.")
    exit()

goals_df = goals_df[[KPI_COLUMN, GOAL_COLUMN]].copy()
goals_df.columns = [KPI_COLUMN, "Meta_2027"]
# Convertir metas a numéricos, manejando errores
goals_df["Meta_2027"] = pd.to_numeric(goals_df["Meta_2027"].str.replace(',', ''), errors='coerce')
goals_df.dropna(subset=["Meta_2027"], inplace=True)

# --- Predicción y Confrontación --- #
results = []

# Asignar un índice numérico a los meses para el modelo de regresión
month_to_num = {month: i for i, month in enumerate(HISTORICAL_SHEET_NAMES)}
full_historical_df["Mes_Num"] = full_historical_df["Mes"].map(month_to_num)

for kpi in full_historical_df[KPI_COLUMN].unique():
    kpi_data = full_historical_df[full_historical_df[KPI_COLUMN] == kpi].sort_values(by="Mes_Num")

    if len(kpi_data) >= 2: # Necesitamos al menos 2 puntos para una regresión lineal simple
        X = kpi_data[["Mes_Num"]].values
        y = kpi_data["Valor"].values

        model = LinearRegression()
        model.fit(X, y)

        # Predecir el valor para un futuro (ej. 12 meses después del último mes histórico)
        # Esto es una simplificación; para 2027 necesitaríamos más contexto de tiempo
        # Para este ejemplo, asumimos que el último mes histórico es Mar_26 (índice 2)
        # y queremos predecir para un punto futuro que represente 2027.
        # Esto es una aproximación y debería ajustarse según la granularidad de los datos y la meta.
        # Si el último mes es Mar_26 (índice 2), y queremos predecir para 2027 (aprox 12 meses después de Dic_26)
        # podríamos predecir para un 'Mes_Num' futuro, por ejemplo, 12 meses después del último mes registrado.
        last_month_num = kpi_data["Mes_Num"].max()
        # Asumimos que 2027 está a 'n' pasos del último mes histórico. Ajustar 'future_steps' según la meta de 2027.
        # Por ejemplo, si Mar_26 es el mes 2, y queremos predecir para Dic_27, serían 21 meses más (2 + 21 = 23)
        # Esto es una simplificación, el cálculo exacto de 'future_month_num' dependerá de cómo se definan los 'Mes_Num'
        # y la fecha exacta de la meta 2027.
        # Para una predicción simple, usaremos un punto futuro arbitrario, ej. 10 pasos adelante.
        future_month_num = last_month_num + 10 # Esto es un placeholder, ajustar según la lógica de tiempo real
        predicted_value = model.predict(np.array([[future_month_num]]))[0]

        # Confrontar con la meta de 2027
        kpi_goal = goals_df[goals_df[KPI_COLUMN] == kpi]["Meta_2027"]
        if not kpi_goal.empty:
            goal = kpi_goal.iloc[0]
            status = "Cumple" if predicted_value >= goal else "No Cumple"
            results.append({
                "KPI": kpi,
                "Último Valor Histórico": kpi_data["Valor"].iloc[-1],
                "Valor Predicho (2027)": predicted_value,
                "Meta (2027)": goal,
                "Estado Predicción": status
            })
        else:
            results.append({
                "KPI": kpi,
                "Último Valor Histórico": kpi_data["Valor"].iloc[-1],
                "Valor Predicho (2027)": predicted_value,
                "Meta (2027)": "N/A",
                "Estado Predicción": "Meta no encontrada"
            })
    elif len(kpi_data) == 1:
        results.append({
            "KPI": kpi,
            "Último Valor Histórico": kpi_data["Valor"].iloc[-1],
            "Valor Predicho (2027)": "No hay suficientes datos para predecir",
            "Meta (2027)": goals_df[goals_df[KPI_COLUMN] == kpi]["Meta_2027"].iloc[0] if not goals_df[goals_df[KPI_COLUMN] == kpi].empty else "N/A",
            "Estado Predicción": "N/A"
        })
    else:
        results.append({
            "KPI": kpi,
            "Último Valor Histórico": "N/A",
            "Valor Predicho (2027)": "No hay datos históricos",
            "Meta (2027)": goals_df[goals_df[KPI_COLUMN] == kpi]["Meta_2027"].iloc[0] if not goals_df[goals_df[KPI_COLUMN] == kpi].empty else "N/A",
            "Estado Predicción": "N/A"
        })

results_df = pd.DataFrame(results)
print("\n--- Resultados de Predicción y Confrontación con Metas ---")
print(results_df.to_markdown(index=False))

# --- Guardar resultados en un archivo Excel (opcional) ---
output_excel_path = "/home/ubuntu/predicciones_kpi_prompack.xlsx"
with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
    results_df.to_excel(writer, sheet_name='Predicciones KPI', index=False)
    print(f"\nResultados guardados en: {output_excel_path}")

