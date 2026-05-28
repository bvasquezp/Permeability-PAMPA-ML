# =============================================================================
#  Paso 1: Importar librerías
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

# --- Configuración para Descriptores Moleculares ---
ruta_archivo_csv = r"C:\Users\benja\Desktop\BD PAMPA\Calculos descriptores moleculares\training_dm.csv"
columna_clase = "Actividad"

# Lista con los 5 descriptores moleculares de consenso
atributos_seleccionados = [
    'LOGPcons',
    'piPC05',
    'CATS2D_07_AP',
    'B06[C-C]',
    'Eig12_EA(dm)'
]

# --- Carga y Preparación de Datos ---
try:
    df_completo = pd.read_csv(ruta_archivo_csv)
    df_completo.columns = df_completo.columns.str.strip()
    X = df_completo[atributos_seleccionados]
    y = df_completo[columna_clase]
    print(f"Datos cargados. Se usarán {X.shape[1]} atributos para {X.shape[0]} moléculas.")

    # =============================================================================
    #  Paso 3: Definir las métricas de evaluación
    # =============================================================================
    labels = sorted(y.unique())
    neg_label, pos_label = labels[0], labels[1]
    print(f"Clase Positiva detectada: '{pos_label}', Clase Negativa: '{neg_label}'")

    scoring = {
        'Accuracy': 'accuracy',
        'BACC': 'balanced_accuracy',
        'Sensitivity': make_scorer(recall_score, pos_label=pos_label),
        'Specificity': make_scorer(recall_score, pos_label=neg_label),
        'Kappa': make_scorer(cohen_kappa_score),
        'ROC_AUC': 'roc_auc'
    }

    # =============================================================================
    #  Paso 4: Definir y Evaluar Modelos
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

    print("\n--- Iniciando Evaluación de Modelos (Descriptores Moleculares) ---")
    for nombre, modelo in modelos.items():
        scores = cross_validate(modelo, X, y, cv=cv, scoring=scoring)
        resultados[nombre] = {key: np.mean(values) for key, values in scores.items()}
        print(f"  > Evaluado: {nombre}")
    print("--- Evaluación Completada ---\n")

    # =============================================================================
    #  Paso 5: Mostrar y Guardar resultados
    # =============================================================================
    df_resultados = pd.DataFrame.from_dict(resultados, orient='index')
    df_resultados = df_resultados.rename(columns={
        'test_Accuracy': 'Accuracy', 'test_BACC': 'BACC',
        'test_Sensitivity': 'Sensitivity', 'test_Specificity': 'Specificity',
        'test_Kappa': 'Kappa', 'test_ROC_AUC': 'ROC AUC'
    })
    columnas_ordenadas = ['Accuracy', 'BACC', 'Sensitivity', 'Specificity', 'Kappa', 'ROC AUC']
    df_resultados = df_resultados[columnas_ordenadas]

    print("📊 Tabla Comparativa de Rendimiento (Descriptores Moleculares):")
    print(df_resultados.round(3))

    nombre_archivo_salida = 'resultados_completos_dm.csv'
    df_resultados.to_csv(nombre_archivo_salida)

    print(f"\n✅ ¡Tabla de resultados guardada exitosamente en el archivo '{nombre_archivo_salida}'!")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado durante la ejecución: {e}")