import multiprocessing
import shlex
import time
import subprocess
import os


def parse_cmd(selection: str) -> list[int]:
    """
    Convierte una cadena de texto que representa una lista de números o rangos de números en una lista ordenada
    de números enteros únicos.

    La cadena puede contener números individuales o rangos especificados con un guion ('-').
    Los rangos son inclusivos y se expanden a una secuencia de números. Los números y rangos pueden estar separados
    por comas.

    Parámetros:
    -----------
    selection : str
        Cadena de texto con números individuales y/o rangos separados por comas. 
        Ejemplo: '1-3, 5, 7-9' representa los números 1, 2, 3, 5, 7, 8, 9.

    Salida:
    -------
    list of int
        Lista ordenada de números enteros sin duplicados.

    Ejemplo de uso:
    ---------------
    >>> parse_cmd('1-3, 5, 7-9')
    [1, 2, 3, 5, 7, 8, 9]

    Nota:
    -----
    Los números dentro de los rangos son inclusivos.
    """
    pages = set()
    parts = selection.split(',')
    
    for part in parts:
        if '-' in part:  # Rango de páginas
            start, end = map(int, part.split('-'))
            pages.update(range(start, end + 1))
        else:  # Página individual
            pages.add(int(part))
    
    return sorted(pages)

def const_cmd(input_arff: str, number_cmd: str ='1-6, 8, 11', path_weka_jar: str = 'weka.jar', file_output: str ='commandlines.txt') -> str:
    """
    Construye y guarda una serie de comandos para ejecutar distintos evaluadores de selección de atributos
    con diversos métodos de búsqueda en Weka. Los comandos se guardan en un archivo especificado por el usuario.

    Parámetros:
    -----------
    input_arff : str
        Ruta del archivo de entrada en formato ARFF.
    number_cmd : str, opcional
        Lista de números o rangos de métodos de búsqueda a incluir en los comandos.
        Ejemplo: '1-6, 8, 11' selecciona los métodos de 1 a 6, el 8 y el 11.
        Si no se proporciona, se usa el valor por defecto '1-6, 8, 11'.
    path_weka_jar : str, opcional
        Ruta al archivo `weka.jar`. Por defecto, se asume que está en el directorio actual.
    file_output : str, opcional
        Nombre del archivo donde se guardarán los comandos generados. Por defecto, 'commandlines.txt'.

    Salida:
    -------
    str
        Nombre del archivo donde se guardaron los comandos generados.

    Ejemplo de uso:
    ---------------
    >>> const_cmd('datos.arff', '1-3, 5', 'ruta/a/weka.jar', 'comandos.txt')
    'comandos.txt'

    Nota:
    -----
    La función asume que la función `parse_cmd(number_cmd)` existe y convierte el string `number_cmd`
    en una lista de números enteros correspondientes a los identificadores de los métodos de búsqueda.
    """
    cmds = {'0001': f'java -cp "{path_weka_jar}" weka.attributeSelection.WrapperSubsetEval -B "weka.classifiers.trees.J48" -F 5 -T 0.01 -R 1 -s "weka.attributeSelection.BestFirst" -i "{input_arff}"',
            '0002': f'java -cp "{path_weka_jar}" weka.attributeSelection.WrapperSubsetEval -B "weka.classifiers.trees.J48" -F 5 -T 0.01 -R 1 -s "weka.attributeSelection.GeneticSearch" -i "{input_arff}"',
            '0003': f'java -cp "{path_weka_jar}" weka.attributeSelection.WrapperSubsetEval -B "weka.classifiers.trees.J48" -F 5 -T 0.01 -R 1 -s "weka.attributeSelection.LinearForwardSelection" -i "{input_arff}"',
            '0004': f'java -cp "{path_weka_jar}" weka.attributeSelection.WrapperSubsetEval -B "weka.classifiers.trees.J48" -F 5 -T 0.01 -R 1 -s "weka.attributeSelection.RankSearch" -i "{input_arff}"',
            '0005': f'java -cp "{path_weka_jar}" weka.attributeSelection.WrapperSubsetEval -B "weka.classifiers.trees.J48" -F 5 -T 0.01 -R 1 -s "weka.attributeSelection.SubsetSizeForwardSelection" -i "{input_arff}"',
            '0006': f'java -cp "{path_weka_jar}" weka.attributeSelection.WrapperSubsetEval -B "weka.classifiers.lazy.IBk" -F 5 -T 0.01 -R 1 -s "weka.attributeSelection.BestFirst" -i "{input_arff}"',
            '0007': f'java -cp "{path_weka_jar}" weka.attributeSelection.WrapperSubsetEval -B "weka.classifiers.lazy.IBk" -F 5 -T 0.01 -R 1 -s "weka.attributeSelection.GeneticSearch" -i "{input_arff}"',
            '0008': f'java -cp "{path_weka_jar}" weka.attributeSelection.WrapperSubsetEval -B "weka.classifiers.lazy.IBk" -F 5 -T 0.01 -R 1 -s "weka.attributeSelection.LinearForwardSelection" -i "{input_arff}"',
            '0009': f'java -cp "{path_weka_jar}" weka.attributeSelection.WrapperSubsetEval -B "weka.classifiers.lazy.IBk" -F 5 -T 0.01 -R 1 -s "weka.attributeSelection.RankSearch" -i "{input_arff}"',
            '0010': f'java -cp "{path_weka_jar}" weka.attributeSelection.WrapperSubsetEval -B "weka.classifiers.lazy.IBk" -F 5 -T 0.01 -R 1 -s "weka.attributeSelection.SubsetSizeForwardSelection" -i "{input_arff}"',

            }
    with open(file_output, 'w') as f:
        f.writelines([cmds[str(ii).zfill(4)] + '\n' for ii in parse_cmd(number_cmd)])
    return file_output

def run_cmd(cmd, cmds, enum, output_file='salida.log'):
    global args, result
    print('Comienza', output_file)
    args = shlex.split(cmd)
    start_time = time.time()
    result = subprocess.run(args, check=True, capture_output=True, text=True)
    end_time = time.time()
    espaced = 15
    print(os.getcwd())
    with open(output_file, 'a') as f:
        f.write(f'=== Run information ===\n')
        f.write('Start time:'.ljust(espaced) + f'{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}\n')
        f.write('Commandline:'.ljust(espaced) + f'{cmd}') # no necesita el \n
        f.write('Evaluator:'.ljust(espaced) + f'{cmd.split('attributeSelection.')[1].split('-s')[0]}\n')
        f.write('Search:'.ljust(espaced) + f'{cmd.split(' -i')[0].split('.')[-1].split('"')[0].split()[0]}\n')
        f.write('Duration:'.ljust(espaced) +f'{(end_time-start_time)/86400:.0f} D : {(end_time-start_time)/3600:.0f} H : {(end_time-start_time)/60:.0f} M : {end_time-start_time:.2f} s\n')
        f.write('Task:'.ljust(espaced) + f'{enum+1}/{len(cmds)}\n')
        f.write(result.stdout)
        f.write('-'*60 + "\n")
        print('Termina', output_file)
    return output_file


if __name__ == '__main__':
    prueba = 4

    if prueba == 1:      # ejemplo de uso de selección de algoritmo según estilo print de impresora
        selection = '1-6, 8, 11'
        pages_to_print = parse_cmd(selection)
        print(f"Se imprimirán las páginas: {pages_to_print}")
    elif prueba == 2:    # ejemplo de uso de construcción de algoritmo seleccionado
        path_weka_jar=r"D:/Weka-3-6/weka.jar"
        input_arff=r"C:\Users\benja\Desktop\QSAR/training_final.csv"
        print("Los comandos están disponibles en el fichero " + const_cmd(path_weka_jar=path_weka_jar, input_arff=input_arff, number_cmd='1'))
    elif prueba == 3:    # ejemplo de uso de ejecución agregando información en el encabezado
        input_cmd = r"C:\Users\benja\Desktop\QSAR/training_final.csv"
        print('El resultado procesado se encuentra en el fichero ' + run_cmd(input_cmd=input_cmd, output_file='salida.log'))
    elif prueba ==4:
    ##################################
        path_weka_jar=r"D:/Weka-3-6/weka.jar"   #cambiar la ruta de weka
        input_arff=r"C:\Users\benja\Desktop\QSAR/training_final.csv"  #cambiar la ruta del fichero de entrenamiento
        ctd_nucleos = 8  #Cantidad de nucleos del procesador a utilizar
        number_cmd = '1-10' #37-39, 41-42        
    ##################################  
        print("Los comandos están disponibles en el fichero " + const_cmd(path_weka_jar=path_weka_jar, input_arff=input_arff, number_cmd=number_cmd))
        input_cmd = r'commandlines.txt'

        with multiprocessing.Pool(processes=ctd_nucleos) as pool:  # Máximo 6 procesos a la vez
            with open(input_cmd) as f:
                cmds = f.readlines()

            args = []
            for enum, cmd in enumerate(cmds):
                search = cmd.split('" -i')[0].split('.')[-1]
                tec = cmd.split('-B')[-1].split('" ')[0].split('.')[-1]
                output_file = f'{tec}_{search}.log'
                args.append((cmd, cmds, enum, output_file))

            # Usar pool.starmap para procesamiento paralelo
            pool.starmap(run_cmd, args)
