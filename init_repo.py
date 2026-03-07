import os

def crear_estructura():
    # Definimos las rutas de las carpetas
    carpetas = [
        'data/raw',
        'data/processed',
        'notebooks',
        'src',
        'results/figures',
        'models'
    ]
    
    for carpeta in carpetas:
        os.makedirs(carpeta, exist_ok=True)
        # Archivo oculto para que Git reconozca la carpeta
        with open(os.path.join(carpeta, '.gitkeep'), 'w') as f:
            pass
            
    # Creamos el archivo .gitignore vital para no subir el venv a GitHub
    gitignore_content = ".venvn/\n__pycache__/\n.ipynb_checkpoints/\n*.log\n"
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
        
    # Creamos un README base
    with open('README.md', 'w') as f:
        f.write("# Permeability-PAMPA\n\nProyecto de prediccion de permeabilidad mediante Machine Learning y ensayos PAMPA.")
        
    print("Estructura de laboratorio digital creada con exito.")

if __name__ == "__main__":
    crear_estructura()