import pandas as pd
from collections import Counter
import re

# =============================================================================
#  CONFIGURACIÓN
# =============================================================================
archivo_resultados_raw = r"C:\Users\benja\Desktop\BD PAMPA\Calculos fusion reducida\variables_fusionadas.txt"
archivo_dataset_combinado = r"C:\Users\benja\Desktop\BD PAMPA\Calculos fusion\Combinado/combined_training.csv"
archivo_salida_reporte = "consenso_final.txt"
# =============================================================================

try:
    print(f"Cargando nombres de atributos desde '{archivo_dataset_combinado}'...")
    df_headers = pd.read_csv(archivo_dataset_combinado, sep=',', nrows=0)
    lista_nombres_atributos = df_headers.columns.tolist()
    total_columnas = len(lista_nombres_atributos)
    print(f"Se encontraron {total_columnas} nombres de atributos en total.")

    print(f"\nProcesando los índices desde '{archivo_resultados_raw}'...")
    todos_los_indices = []
    with open(archivo_resultados_raw, 'r') as f:
        for line in f:
            numeros_encontrados = re.findall(r'\d+', line)
            indices = [int(num) for num in numeros_encontrados]
            todos_los_indices.extend(indices)
    
    frecuencia_indices = Counter(todos_los_indices)
    resultados_ordenados = sorted(frecuencia_indices.items(), key=lambda item: item[1], reverse=True)

    print(f"\nGenerando reporte de diagnóstico en '{archivo_salida_reporte}'...")
    with open(archivo_salida_reporte, 'w') as f_out:
        f_out.write("--- REPORTE DE DIAGNÓSTICO DE CONSENSO (J48 + IBk) ---\n")
        f_out.write("-" * 60 + "\n")
        f_out.write(f"{'Atributo (o Índice)':<40} | {'Frecuencia':<15}\n")
        f_out.write("-" * 60 + "\n")

        if not resultados_ordenados:
            f_out.write("No se encontraron atributos seleccionados en el archivo raw.\n")
        else:
            for indice, frecuencia in resultados_ordenados:
                # Usamos un try-except para manejar cualquier índice problemático
                try:
                    # WEKA es 1-based, Python es 0-based.
                    nombre_atributo = lista_nombres_atributos[indice - 1]
                    linea_reporte = f"{nombre_atributo:<40} | {frecuencia:<15}"
                    f_out.write(linea_reporte + "\n")
                except IndexError:
                    # Si el índice no existe en la lista, lo reportamos
                    linea_reporte = f"{f'Índice Fuera de Rango: {indice}':<40} | {frecuencia:<15}"
                    f_out.write(linea_reporte + "\n")

        f_out.write("-" * 60 + "\n")

    print(f"\n✅ ¡Éxito! El reporte de diagnóstico ha sido guardado.")
    print(f"   Por favor, abre '{archivo_salida_reporte}' y comparte su contenido.")

except FileNotFoundError as e:
    print(f"❌ ERROR: No se pudo encontrar el archivo: {e.filename}")
except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")