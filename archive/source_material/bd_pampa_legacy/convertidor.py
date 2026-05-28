import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = r"C:\Users\benja\Desktop\BD PAMPA\Calculos descriptores moleculares\bases de dato\training_dmm.csv"
ruta_fp_csv = r"C:\Users\benja\Desktop\BD PAMPA\Calculos Fingerprint\Bases de datos\new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")======
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")======
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")mbined_training_set.csv"
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")======
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")s tipos de datos.
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")nto y coma
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")o con punto y coma ';'")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}");'. Error original: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")filas, {df.shape[1]} columnas.")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")n ARFF (sin espacios ni caracteres especiales)
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")replace(")", "").replace("[", "").replace("]", "")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}") ARFF
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")").replace('"', '') for val in unique_values])
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")str}}}\n")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")comas
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")th}'")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")v_path}'.")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")
import pandas as pd
import sys

# --- Configuración ---
ruta_dm_csv = "training_dm.csv"
ruta_fp_csv = "new_training.csv"
nombre_salida_csv = "combined_training_set.csv"

try:
    print("--- PASO 1: Cargando archivos... ---")
    df_dm = pd.read_csv(ruta_dm_csv, sep=';')
    df_fp = pd.read_csv(ruta_fp_csv, sep=',')

    # --- PASO 2: Limpieza de columnas ---
    print("--- PASO 2: Limpiando columnas innecesarias... ---")
    
    # ¡NUEVO! Eliminamos la columna 'Serie' del dataframe de fingerprints
    if 'Serie' in df_fp.columns:
        df_fp = df_fp.drop(columns=['Serie'])
        print("  > Columna 'Serie' eliminada exitosamente.")
    
    # Verificación de consistencia
    if len(df_dm) != len(df_fp):
        print("\n❌ ¡ERROR CRÍTICO! El número de filas no coincide.")
        sys.exit()

    print("\n--- PASO 3: Combinando los datasets... ---")
    df_dm_features = df_dm.drop(columns=['Actividad'], errors='ignore')
    df_fp_features = df_fp.drop(columns=['Actividad', 'Name', 'Set'], errors='ignore')
    df_actividad = df_fp[['Actividad']]
    
    df_combined_features = pd.concat([df_dm_features.reset_index(drop=True), df_fp_features.reset_index(drop=True)], axis=1)
    df_combined_final = pd.concat([df_combined_features, df_actividad], axis=1)
    
    # Guardar el archivo final
    df_combined_final.to_csv(nombre_salida_csv, index=False, sep=';')
    
    print(f"\n✅ ¡Éxito! Archivo '{nombre_salida_csv}' guardado sin la columna 'Serie'.")

except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")