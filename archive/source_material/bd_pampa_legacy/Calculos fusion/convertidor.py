import pandas as pd
import os

# =============================================================================
#  CONFIGURACIÓN
# =============================================================================
# Nombre del archivo CSV que quieres convertir
nombre_archivo_csv = r"C:\Users\benja\Desktop\BD PAMPA\Calculos fusion\combined_training_set.csv"

# Nombre que tendrá el nuevo archivo ARFF
nombre_archivo_arff = "combined_training.arff"

# Nombre de tu dataset (puedes cambiarlo si quieres)
nombre_relacion = "pampa_combined_dataset"
# =============================================================================

def csv_to_arff(csv_path, arff_path, relation_name):
    """
    Convierte un archivo CSV a formato ARFF, manejando automáticamente los tipos de datos.
    """
    try:
        print(f"Cargando archivo CSV: '{csv_path}'...")
        # Intentamos detectar el separador, asumiendo coma por defecto
        try:
            df = pd.read_csv(csv_path, sep=',')
            if df.shape[1] == 1: # Si solo lee una columna, prueba con punto y coma
                 print("Detectado posible separador incorrecto, intentando con punto y coma ';'")
                 df = pd.read_csv(csv_path, sep=';')
        except Exception as e:
            print(f"Error al leer con coma, intentando con punto y coma ';'. Error original: {e}")
            df = pd.read_csv(csv_path, sep=';')

        print(f"Archivo cargado exitosamente. Dimensiones: {df.shape[0]} filas, {df.shape[1]} columnas.")

        # Abrir el archivo de salida para escribir
        with open(arff_path, 'w') as f:
            # --- 1. Escribir el encabezado ---
            f.write(f"@relation {relation_name}\n\n")

            # --- 2. Escribir las definiciones de los atributos ---
            for column in df.columns:
                # Limpiar nombres de columna para que sean compatibles con ARFF (sin espacios ni caracteres especiales)
                clean_column = column.replace(" ", "_").replace("(", "").replace(")", "").replace("[", "").replace("]", "")

                if df[column].dtype in ['int64', 'float64']:
                    f.write(f"@attribute {clean_column} numeric\n")
                else: # Tratar todo lo demás como nominal (categórico)
                    # Obtenemos los valores únicos y los formateamos para ARFF
                    unique_values = df[column].unique()
                    # Quitamos comillas para evitar problemas de formato
                    unique_values_str = ",".join([str(val).replace("'", "").replace('"', '') for val in unique_values])
                    f.write(f"@attribute {clean_column} {{{unique_values_str}}}\n")
            
            # --- 3. Escribir la sección de datos ---
            f.write("\n@data\n")
            
            # --- 4. Escribir cada fila de datos ---
            for index, row in df.iterrows():
                # Convertir cada valor de la fila a string y unirlos con comas
                line = ",".join([str(item) for item in row])
                f.write(line + "\n")

        print(f"\n✅ ¡Éxito! Archivo convertido y guardado como '{arff_path}'")

    except FileNotFoundError:
        print(f"❌ ERROR: No se pudo encontrar el archivo de entrada '{csv_path}'.")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")


# --- Ejecutar la conversión ---
if __name__ == "__main__":
    csv_to_arff(nombre_archivo_csv, nombre_archivo_arff, nombre_relacion)