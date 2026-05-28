import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, roc_auc_score, cohen_kappa_score, recall_score
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# --- 1. CONFIGURACIÓN ---
# ¡CAMBIO CLAVE! Ahora usamos los archivos CSV para todo.
ruta_entrenamiento = r"C:\Users\benja\Desktop\BD PAMPA\Calculos fusion\Combinado\combined_training.csv"
ruta_prueba = r"C:\Users\benja\Desktop\BD PAMPA\Calculos fusion\Combinado\fusion_test_set.csv"
ruta_externa = r"C:\Users\benja\Desktop\BD PAMPA\Calculos fusion\Combinado/fusion_external_set.csv"

# --- Atributos y Clase ---
atributos_seleccionados = [
    'MW', 'stdMW', 'F04[C-F]', 'F06[N-N]', 'F06[O-O]', 'piPC05', 'Yindex',
    'F09[C-S]', 'F09[N-N]', 'F09[N-O]', 'CIC1', 'F10[C-F]', 'F10[N-N]',
    'SM5_X', 'MDEC-44', 'SM1_Dz(p)', 'phLevel1', 'phLevel3', 's1_size',
    's1_phSize', 's3_phSize', 's34_size'
]
columna_clase = "Actividad"
nombre_archivo_reporte = "REPORTE_FINAL_DEL_PROYECTO.txt"

# --- 2. Lógica de Carga y Ejecución ---
try:
    # --- Función de Carga Simplificada ---
    def cargar_csv(path):
        # Asumimos separador de coma, que es el formato correcto de nuestros archivos combinados.
        return pd.read_csv(path, sep=',')

    # --- Cargar Todos los Datos ---
    print("Cargando todos los datasets (formato CSV)...")
    df_train = cargar_csv(ruta_entrenamiento)
    df_test = cargar_csv(ruta_prueba)
    df_external = cargar_csv(ruta_externa)
    
    X_train, y_train = df_train[atributos_seleccionados], df_train[columna_clase]
    X_test, y_test = df_test[atributos_seleccionados], df_test[columna_clase]
    X_external, y_external = df_external[atributos_seleccionados], df_external[columna_clase]
    print("Datasets cargados correctamente.")

    # --- PASO 1: OPTIMIZACIÓN DEL MODELO ---
    param_grid = {'n_estimators': [100, 200, 300], 'max_features': ['sqrt', 'log2'],
                  'max_depth': [10, 20, None], 'min_samples_split': [2, 5]}
    
    print("\n--- Iniciando optimización del modelo (GridSearchCV)... ---")
    cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
    grid_search = GridSearchCV(RandomForestClassifier(random_state=42), 
                               param_grid, cv=cv, scoring='roc_auc', n_jobs=-1, verbose=1)
    grid_search.fit(X_train, y_train)
    
    parametros_optimos = grid_search.best_params_
    modelo_final = grid_search.best_estimator_
    print("--- Optimización completada. ---")

    # --- PASO 2: VALIDACIÓN FINAL SOBRE PRUEBA Y EXTERNO ---
    print("\n--- Entrenando modelo final y evaluando sobre datos no vistos... ---")
    
    with open(nombre_archivo_reporte, 'w') as f:
        f.write("--- REPORTE DE VALIDACIÓN FINAL DEL PROYECTO ---\n")
        f.write(f"Modelo: Random Forest\n")
        f.write(f"Atributos de Consenso: {len(atributos_seleccionados)}\n")
        f.write("\n--- Hiperparámetros Óptimos Encontrados ---\n")
        f.write(str(parametros_optimos) + "\n")
        
        for nombre_set, X_eval, y_eval in [("Prueba Interna (Test Set)", X_test, y_test), 
                                           ("Prueba Externa (External Set)", X_external, y_external)]:
            
            y_pred = modelo_final.predict(X_eval)
            y_proba = modelo_final.predict_proba(X_eval)[:, 1]

            f.write(f"\n--- Resultados en: {nombre_set} ---\n")
            f.write("-" * 40 + "\n")
            f.write(f"  Accuracy:         {accuracy_score(y_eval, y_pred):.4f}\n")
            f.write(f"  ROC AUC:          {roc_auc_score(y_eval, y_proba):.4f}\n")
            f.write(f"  BACC:             {balanced_accuracy_score(y_eval, y_pred):.4f}\n")
            f.write(f"  Sensitivity:      {recall_score(y_eval, y_pred, pos_label='Act1'):.4f}\n")
            f.write(f"  Specificity:      {recall_score(y_eval, y_pred, pos_label='Act-1'):.4f}\n")
            f.write(f"  Kappa:            {cohen_kappa_score(y_eval, y_pred):.4f}\n")
    
    print(f"\n✅ ¡PROYECTO COMPLETADO! Revisa el archivo '{nombre_archivo_reporte}' para ver los resultados finales.")

except FileNotFoundError as e:
    print(f"\n❌ ERROR: No se pudo encontrar el archivo: {e.filename}. Asegúrate de que los tres archivos CSV combinados (training, test, external) estén en la misma carpeta.")
except Exception as e:
    print(f"\n❌ Ocurrió un error inesperado: {e}")