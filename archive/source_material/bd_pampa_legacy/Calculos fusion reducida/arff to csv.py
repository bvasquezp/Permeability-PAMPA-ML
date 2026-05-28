import pandas as pd
import re

# --- CONFIGURACIÓN ---
archivos_a_convertir = {
    r"C:\Users\benja\Desktop\BD PAMPA\Calculos fusion reducida\J48_training-comb.arff": "train_final.csv",
    r"C:\Users\benja\Desktop\BD PAMPA\Calculos fusion reducida\J48_test-comb.arff": "test_final.csv",
    r"C:\Users\benja\Desktop\BD PAMPA\Calculos fusion reducida\J48_external-comb.arff": "external_final.csv"
}

# --- LÓGICA DE CONVERSIÓN Y CORRECCIÓN ---
try:
    print("--- Convirtiendo ARFF a CSV y corrigiendo duplicados... ---")
    
    for arff_file, csv_file in archivos_a_convertir.items():
        print(f"  Procesando '{arff_file}'...")
        
        with open(arff_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        header_lines = [line for line in lines if line.strip().lower().startswith('@attribute')]
        data_lines = [line for line in lines if not line.strip().startswith('@') and line.strip() != '']

        column_names = []
        indices_a_eliminar = []
        
        # Procesar encabezado para encontrar duplicados
        seen_names = set()
        for i, line in enumerate(header_lines):
            # Extraer el nombre del atributo
            match = re.match(r"@attribute\s+['\"]?([^'\"\s]+)['\"]?", line.strip(), re.IGNORECASE)
            if match:
                name = match.group(1)
                if name in seen_names:
                    indices_a_eliminar.append(i) # Guardar el índice de la columna duplicada
                else:
                    seen_names.add(name)
                    column_names.append(name)
        
        # Procesar datos para eliminar las columnas duplicadas
        corrected_data = []
        for line in data_lines:
            values = line.strip().split(',')
            # Crear una nueva lista de valores excluyendo los índices de las columnas duplicadas
            new_values = [val for i, val in enumerate(values) if i not in indices_a_eliminar]
            corrected_data.append(new_values)
            
        # Crear el DataFrame final y guardarlo como CSV
        df = pd.DataFrame(corrected_data, columns=column_names)
        df.to_csv(csv_file, index=False, sep=',')
        print(f"    > Archivo '{csv_file}' corregido y creado con {len(df.columns)} columnas.")

    print("\n✅ Conversión completada. Tus archivos CSV finales están listos y consistentes.")

except FileNotFoundError as e:
    print(f"❌ ERROR: No se encontró el archivo ARFF: {e.filename}")
except Exception as e:
    print(f"❌ Ocurrió un error: {e}")