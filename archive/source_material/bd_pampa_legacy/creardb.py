import pandas as pd
import numpy as np
import sys
import warnings
from sklearn.feature_selection import VarianceThreshold, RFE
from sklearn.ensemble import RandomForestClassifier

# --- 0. Configuración ---
print("--- Iniciando 'Fábrica de Datos' (Objetivo: 76 atributos) ---")
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# --- Rutas de ENTRADA (Los archivos maestros grandes) ---
ruta_entrenamiento_completo = r"C:\Users\benja\Desktop\QSAR/train.csv"
ruta_prueba_completo = r"C:\Users\benja\Desktop\QSAR/test.csv"
ruta_externa_completo = r"C:\Users\benja\Desktop\QSAR/external.csv"

# --- Rutas de SALIDA (Los archivos finales limpios) ---
ruta_salida_train = r"C:\Users\benja\Desktop\QSAR/train_final_76.csv"
ruta_salida_test  = r"C:\Users\benja\Desktop\QSAR/test_final_76.csv"
ruta_salida_external = r"C:\Users\benja\Desktop\QSAR/external_final_76.csv"

# --- Configuración de Clases ---
COLUMNA_CLASE = "Actividad"
COLUMNAS_METADATOS = ["Actividad", "serie"] # Columnas a eliminar de X

try:
    # --- 1. Carga y Limpieza de Datos ---
    print("\n[Paso 1: Cargando y Limpiando Datos Maestros]...")
    df_train_full = pd.read_csv(ruta_entrenamiento_completo)
    df_test_full = pd.read_csv(ruta_prueba_completo)
    df_external_full = pd.read_csv(ruta_externa_completo)

    y_train_full = df_train_full[COLUMNA_CLASE]
    print(f"  > Archivo 'train.csv' cargado: {df_train_full.shape[0]} filas, {df_train_full.shape[1]} columnas.")
    
    X_train_full = df_train_full.drop(columns=COLUMNAS_METADATOS, errors='ignore')
    print(f"  > Columnas de atributos (X) listas: {X_train_full.shape[1]} columnas.")

    # --- 2. Preprocesamiento (Varianza Cero) ---
    print("\n[Paso 2: Preprocesamiento (Varianza Cero)]...")
    features_originales = X_train_full.columns
    selector_var = VarianceThreshold(threshold=0.0)
    X_train_filtrado = selector_var.fit_transform(X_train_full)
    features_filtradas = features_originales[selector_var.get_support()]
    X_train_preprocesado = pd.DataFrame(X_train_filtrado, columns=features_filtradas)
    print(f"  > Atributos restantes tras Varianza Cero: {len(features_filtradas)}")

    # --- 3. Selección con RFE (a 100) ---
    print("\n[Paso 3: Selección de Características (RFE a 100)]...")
    print("  > (Esto puede tardar varios minutos)...")
    estimator_rfe = RandomForestClassifier(random_state=42, n_jobs=-1)
    selector_rfe = RFE(estimator=estimator_rfe, n_features_to_select=100, step=0.1)
    selector_rfe.fit(X_train_preprocesado, y_train_full)

    features_rfe = features_filtradas[selector_rfe.support_]
    X_train_rfe = X_train_preprocesado[features_rfe]
    print(f"  > ¡RFE completado! Se seleccionaron {len(features_rfe)} atributos.")

    # --- 4. Eliminación de Correlación (a 76) ---
    print("\n[Paso 4: Eliminación de Correlación (Spearman > 0.8)]...")
    corr_matrix = X_train_rfe.corr(method='spearman').abs()
    upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    umbral_corr = 0.8
    columnas_a_eliminar = [column for column in upper_tri.columns if any(upper_tri[column] > umbral_corr)]
    
    # --- ¡ESTA ES LA LISTA FINAL Y CORRECTA! ---
    lista_final_76_atributos = X_train_rfe.drop(columns=columnas_a_eliminar).columns.tolist()
    
    print(f"  > De los 100 atributos RFE, se eliminaron {len(columnas_a_eliminar)}.")
    print(f"\n  > ¡Proceso completado! Se obtuvo un conjunto final de {len(lista_final_76_atributos)} descriptores.")

    # --- 5. Guardar los Archivos Finales ---
    print("\n[Paso 5: Guardando las bases de datos finales]...")
    columnas_a_guardar = lista_final_76_atributos + [COLUMNA_CLASE]
    print(f"  > Se guardarán {len(lista_final_76_atributos)} atributos + 1 columna de clase.")

    # Filtrar y guardar TRAIN
    df_train_full[columnas_a_guardar].to_csv(ruta_salida_train, index=False)
    print(f"    > ¡Éxito! Archivo '{ruta_salida_train.split('/')[-1]}' creado.")
    
    # Filtrar y guardar TEST
    df_test_full[columnas_a_guardar].to_csv(ruta_salida_test, index=False)
    print(f"    > ¡Éxito! Archivo '{ruta_salida_test.split('/')[-1]}' creado.")
    
    # Filtrar y guardar EXTERNAL
    df_external_full[columnas_a_guardar].to_csv(ruta_salida_external, index=False)
    print(f"    > ¡Éxito! Archivo '{ruta_salida_external.split('/')[-1]}' creado.")

    print("\n--- 'Fábrica de Datos' Completada ---")

except Exception as e:
    print(f"\n--- ❌ ERROR CRÍTICO ---")
    print(f"Error: {e}")
    sys.exit()