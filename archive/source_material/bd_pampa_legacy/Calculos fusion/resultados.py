import pandas as pd
import numpy as np
from sklearn.model_selection import cross_validate, StratifiedKFold
from sklearn.metrics import make_scorer, recall_score, cohen_kappa_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

# --- 1. CONFIGURACIÓN ---
ruta_dataset = r"C:\Users\benja\Desktop\BD PAMPA\Calculos fusion\combined_training.arff"

# Nuestro "equipo titular" de 8 atributos mixtos
atributos_seleccionados = [
    'Psi_e_0', 'piPC05', 'Yindex', 'Eig13_EA(dm)', 
    'MACCSFP18', 'MACCSFP65', 'B06[C-C]', 'B07[C-C]'
]
columna_clase = "Actividad"
nombre_archivo_resultados = "resultados_modelo_hibrido.txt"

# --- 2. CARGA DE DATOS ---
try:
    def cargar_arff(path):
        try:
            import arff
        except ImportError:
            raise ImportError("La librería 'liac-arff' no está instalada. Por favor, ejecuta: pip install liac-arff")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = arff.load(f)
        return pd.DataFrame(data['data'], columns=[attr[0] for attr in data['attributes']])
    
    print(f"Cargando dataset desde '{ruta_dataset}'...")
    df = cargar_arff(ruta_dataset)
    
    for col in df.columns:
        if col != columna_clase:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(inplace=True)

    X = df[atributos_seleccionados]
    y = df[columna_clase]
    print(f"Datos listos: {X.shape[0]} instancias y {X.shape[1]} atributos.")

    # --- 3. CONFIGURACIÓN DE MODELOS Y MÉTRICAS ---
    print("\nIniciando validación cruzada para 6 algoritmos...")
    modelos = {
        "SVM": SVC(random_state=42, probability=True),
        "Random Forest": RandomForestClassifier(random_state=42),
        "Árbol de Decisión (J48)": DecisionTreeClassifier(random_state=42),
        "k-NN": KNeighborsClassifier(),
        "Regresión Logística": LogisticRegression(random_state=42, max_iter=1000),
        "Naive Bayes": GaussianNB()
    }

    # Definimos las métricas, incluyendo las personalizadas
    # Asumimos que 'Act1' es la clase positiva y 'Act-1' la negativa
    scoring = {
        'accuracy': 'accuracy',
        'bacc': 'balanced_accuracy',
        'roc_auc': 'roc_auc',
        'sensitivity': make_scorer(recall_score, pos_label='Act1'),
        'specificity': make_scorer(recall_score, pos_label='Act-1'),
        'kappa': make_scorer(cohen_kappa_score)
    }
    
    cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
    resultados_finales = {}

    for nombre, modelo in modelos.items():
        scores = cross_validate(modelo, X, y, cv=cv, scoring=scoring, n_jobs=-1)
        resultados_finales[nombre] = {k: np.mean(v) for k, v in scores.items()}
        print(f"  > {nombre} evaluado.")

    # --- 4. GUARDAR RESULTADOS EN UN ARCHIVO ---
    print(f"\nGuardando resultados en el archivo '{nombre_archivo_resultados}'...")
    with open(nombre_archivo_resultados, 'w') as f:
        f.write("--- RESULTADOS DETALLADOS DEL MODELO HÍBRIDO (Promedio de 10-fold CV) ---\n")
        for nombre, metricas in resultados_finales.items():
            f.write(f"\nModelo: {nombre}\n")
            f.write("-" * 40 + "\n")
            f.write(f"  Accuracy:         {metricas['test_accuracy']:.4f}\n")
            f.write(f"  ROC AUC:          {metricas['test_roc_auc']:.4f}\n")
            f.write(f"  BACC:             {metricas['test_bacc']:.4f}\n")
            f.write(f"  Sensitivity:      {metricas['test_sensitivity']:.4f}\n")
            f.write(f"  Specificity:      {metricas['test_specificity']:.4f}\n")
            f.write(f"  Kappa:            {metricas['test_kappa']:.4f}\n")
            
    print("\n✅ ¡Éxito! El archivo de resultados ha sido creado.")

except ImportError as e:
    print(f"\n❌ ERROR: {e}")
except FileNotFoundError:
    print(f"❌ ERROR: No se encontró el archivo '{ruta_dataset}'.")
except Exception as e:
    print(f"❌ Ocurrió un error inesperado: {e}")