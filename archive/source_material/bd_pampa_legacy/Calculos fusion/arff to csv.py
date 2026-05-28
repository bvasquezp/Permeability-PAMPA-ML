import pandas as pd

# --- Esta es una función robusta para leer archivos ARFF ---
def cargar_arff(path):
    try:
        import arff
    except ImportError:
        raise ImportError("La librería 'liac-arff' no está instalada. Ejecuta: pip install liac-arff")
    
    with open(path, 'r', encoding='utf-8') as f:
        data = arff.load(f)
    
    # Manejar nombres de columna duplicados, como 'F09[N-N]'
    column_names = [attr[0] for attr in data['attributes']]
    df = pd.DataFrame(data['data'], columns=column_names)
    
    # Limpiar duplicados si existen, manteniendo la primera instancia
    df = df.loc[:,~df.columns.duplicated()]
    return df

# --- CONFIGURACIÓN ---
archivos_a_convertir = {
    r"C:\Users\benja\Desktop\BD PAMPA\Calculos fusion reducida\J48_training-comb.arff": "train_final.csv",
    r"C:\Users\benja\Desktop\BD PAMPA\Calculos fusion reducida\J48_test-comb.arff": "test_final.csv",
    r"C:\Users\benja\Desktop\BD PAMPA\Calculos fusion reducida\J48_test-comb.arff": "external_final.csv"
}

# --- LÓGICA DE CONVERSIÓN ---
try:
    print("--- Convirtiendo los archivos ARFF definitivos a CSV... ---")
    for arff_file, csv_file in archivos_a_convertir.items():
        print(f"  Procesando '{arff_file}'...")
        df = cargar_arff(arff_file)
        df.to_csv(csv_file, index=False, sep=',')
        print(f"    > Archivo '{csv_file}' creado con éxito.")
    
    print("\n✅ Conversión completada. Tus archivos CSV finales están listos.")

except FileNotFoundError as e:
    print(f"❌ ERROR: No se encontró el archivo ARFF: {e.filename}")
except Exception as e:
    print(f"❌ Ocurrió un error: {e}")