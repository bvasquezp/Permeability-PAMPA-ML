import pandas as pd
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.svm import SVC
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# --- 1. CONFIGURACIÓN ---
ruta_dataset = r"C:\Users\benja\Desktop\BD PAMPA\Calculos fusion\combined_training.arff"

atributos_seleccionados = [
    'MW', 'stdMW', 'F04[C-F]', 'F06[N-N]', 'F06[O-O]', 'piPC05', 'Yindex',
    'F09[C-S]', 'F09[N-N]', 'F09[N-O]', 'CIC1', 'F10[C-F]', 'F10[N-N]',
    'SM5_X', 'MDEC-44', 'SM1_Dz(p)', 'phLevel1', 'phLevel3', 's1_size',
    's1_phSize', 's3_phSize', 's34_size','MW', 'stdMW', 'F04[C-F]', 'F06[N-N]', 'F06[O-O]', 'piPC05', 'Yindex',
    'F09[C-S]', 'F09[N-N]', 'F09[N-O]', 'CIC1', 'F10[C-F]', 'F10[N-N]',
    'SM5_X', 'MDEC-44', 'SM1_Dz(p)', 'phLevel1', 'phLevel3', 's1_size',
    's1_phSize', 's3_phSize', 's34_size'
]
columna_clase = "Actividad"

# --- 2. CARGA DE DATOS ---
try:
    def cargar_arff(path):
        try:
            import arff
        except ImportError:
            raise ImportError("La librería 'liac-arff' no está instalada. Ejecuta: pip install liac-arff")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = arff.load(f)
        df = pd.DataFrame(data['data'], columns=[attr[0] for attr in data['attributes']])
        
        # Convertir y limpiar datos
        for col in df.columns:
            if col != columna_clase:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(inplace=True)
        return df

    print(f"Cargando datos desde '{ruta_dataset}'...")
    df_completo = cargar_arff(ruta_dataset)
    X = df_completo[atributos_seleccionados]
    y = df_completo[columna_clase]
    print(f"Datos cargados para la optimización: {X.shape[0]} moléculas.")

    # --- 3. DEFINIR GRID DE HIPERPARÁMETROS ---
    param_grid = {
        'C': [0.1, 1, 10, 100, 1000],
        'gamma': [1, 0.1, 0.01, 0.001, 'scale'],
        'kernel': ['rbf']
    }

    # --- 4. CONFIGURAR Y EJECUTAR GRIDSEARCHCV ---
    print("\n--- Iniciando búsqueda de hiperparámetros para el modelo híbrido... ---")
    
    cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
    grid_search = GridSearchCV(SVC(probability=True, random_state=42), 
                               param_grid, 
                               cv=cv, 
                               scoring='roc_auc', 
                               n_jobs=-1,
                               verbose=2) # verbose=2 para más detalle del progreso
    grid_search.fit(X, y)

    print("\n--- ¡Búsqueda completada! ---")

    # --- 5. MOSTRAR RESULTADOS DE LA OPTIMIZACIÓN ---
    print("\n🏆 Mejores Hiperparámetros Encontrados para el Modelo Híbrido:")
    print(grid_search.best_params_)
    print(f"\n📈 Mejor puntuación ROC AUC (híbrido optimizado): {grid_search.best_score_:.4f}")
    print(f"(Resultado anterior sin tunear: 0.7429)")

except Exception as e:
    print(f"\n❌ Ocurrió un error inesperado: {e}")