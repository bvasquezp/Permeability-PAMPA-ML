# =============================================================================
#  Paso 1: Importar librerías (con nuevas adiciones)
# =============================================================================
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_validate, StratifiedKFold
from sklearn.metrics import make_scorer, recall_score, cohen_kappa_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

# =============================================================================
#  Paso 2: Cargar datos y definir atributos
# =============================================================================

# --- Configuración Inicial (MODIFICA SEGÚN NECESITES) ---
# Cambia esta ruta al archivo que quieras analizar (DM o Fingerprints)
ruta_archivo_csv = r"C:\Users\benja\Desktop\BD PAMPA\Calculos Fingerprint\Bases de datos\new_training.csv" 
columna_clase = "Actividad"

# Pega aquí la lista de atributos que quieres usar
atributos_seleccionados = [
    # Ejemplo para Fingerprints:
    'MACCSFP8', 'MACCSFP18', 'MACCSFP25', 'MACCSFP34', 'MACCSFP40',
    'MACCSFP43', 'MACCSFP47', 'MACCSFP49', 'MACCSFP50', 'MACCSFP54',
    'MACCSFP56', 'MACCSFP62', 'MACCSFP70', 'MACCSFP76', 'MACCSFP80',
    'MACCSFP84', 'MACCSFP99', 'MACCSFP112', 'MACCSFP125', 'MACCSFP145',
    'MACCSFP156', 'MACCSFP161'
]

# --- Carga y Preparación de Datos ---
try:
    df_completo = pd.read_csv(ruta_archivo_csv)
    df_completo.columns = df_completo.columns.str.strip()
    X = df_completo[atributos_seleccionados]
    y = df_completo[columna_clase]
    print(f"Datos cargados. Se usarán {X.shape[1]} atributos para {X.shape[0]} moléculas.")

    # =============================================================================
    #  Paso 3: Definir las métricas de evaluación (NUEVA SECCIÓN)
    # =============================================================================
    
    # Identificamos las etiquetas de clase (ej. 'Act-1', 'Inact-0')
    # Esto hace el código robusto sin importar cómo se llamen las clases
    labels = sorted(y.unique())
    neg_label, pos_label = labels[0], labels[1]
    print(f"Clase Positiva detectada: '{pos_label}', Clase Negativa: '{neg_label}'")

    # Creamos un diccionario con todas las métricas que queremos calcular
    scoring = {
        'Accuracy': 'accuracy',
        'BACC': 'balanced_accuracy',
        'Sensitivity': make_scorer(recall_score, pos_label=pos_label),
        'Specificity': make_scorer(recall_score, pos_label=neg_label),
        'Kappa': make_scorer(cohen_kappa_score),
        'ROC_AUC': 'roc_auc'
    }

    # =============================================================================
    #  Paso 4: Definir y Evaluar Modelos (usando cross_validate)
    # =============================================================================
    modelos = {
        "Árbol de Decisión (J48)": DecisionTreeClassifier(random_state=42),
        "Regresión Logística": LogisticRegression(max_iter=1000, random_state=42),
        "k-NN (IBk, k=5)": KNeighborsClassifier(n_neighbors=5),
        "Random Forest": RandomForestClassifier(random_state=42),
        "SVM": SVC(probability=True, random_state=42)
    }
    cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
    resultados = {}

    print("\n--- Iniciando Evaluación de Modelos ---")
    for nombre, modelo in modelos.items():
        # Usamos cross_validate para obtener todas las métricas de una vez
        scores = cross_validate(modelo, X, y, cv=cv, scoring=scoring)
        
        # Guardamos el promedio de cada métrica
        resultados[nombre] = {key: np.mean(values) for key, values in scores.items()}
        print(f"  > Evaluado: {nombre}")
    print("--- Evaluación Completada ---\n")

    # =============================================================================
    #  Paso 5: Mostrar y Guardar resultados
    # =============================================================================
    df_resultados = pd.DataFrame.from_dict(resultados, orient='index')
    # Renombramos las columnas para que se vean mejor
    df_resultados = df_resultados.rename(columns={
        'test_Accuracy': 'Accuracy', 'test_BACC': 'BACC',
        'test_Sensitivity': 'Sensitivity', 'test_Specificity': 'Specificity',
        'test_Kappa': 'Kappa', 'test_ROC_AUC': 'ROC AUC'
    })
    # Seleccionamos el orden deseado de las columnas
    columnas_ordenadas = ['Accuracy', 'BACC', 'Sensitivity', 'Specificity', 'Kappa', 'ROC AUC']
    df_resultados = df_resultados[columnas_ordenadas]


    print("📊 Tabla Comparativa de Rendimiento con todas las métricas:")
    print(df_resultados.round(3))

    nombre_archivo_salida = 'resultados_completos.csv'
    df_resultados.to_csv(nombre_archivo_salida)

    print(f"\n✅ ¡Tabla de resultados guardada exitosamente en el archivo '{nombre_archivo_salida}'!")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado durante la ejecución: {e}")