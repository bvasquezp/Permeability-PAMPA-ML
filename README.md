# Permeability-PAMPA
Predicción de Permeabilidad Intestinal Pasiva (PAMPA) mediante Modelos QSAR y Machine Learning
Este repositorio contiene el desarrollo y la implementación de un flujo de trabajo computacional para predecir la permeabilidad intestinal pasiva utilizando modelos de Relación Cuantitativa Estructura-Actividad (QSAR). El proyecto se centra en la robustez estadística y la interpretabilidad de las predicciones, aplicadas a un cribado masivo de fármacos.

1. Resumen del Proyecto
El objetivo principal es identificar moléculas con potencial de permeabilidad intestinal óptima utilizando el ensayo PAMPA (Parallel Artificial Membrane Permeability Assay) como referencia. Se desarrolló un modelo basado en el algoritmo Random Forest, optimizado para manejar descriptores moleculares fisicoquímicos y estructurales (Fingerprints).

2. Estructura del Repositorio
data/: Conjuntos de datos de entrenamiento y validación externa.

notebooks/:

01_Curacion_Datos.ipynb: Limpieza de estructuras, estandarización de SMILES y cálculo de descriptores.

02_Modelado_Interpretabilidad.ipynb: Entrenamiento, validación cruzada y análisis de SHAP.

03_Cribado_Virtual_PAMPA.ipynb: Aplicación del modelo sobre DrugBank y filtros de Lipinski.

models/: Serialización del modelo final (.pkl).

results/: Reportes de predicción y figuras generadas (Curvas ROC, SHAP, Galería 2D).

3. Metodología
Descriptores Utilizados
Se seleccionaron 11 variables clave tras un proceso de reducción de dimensionalidad, incluyendo:

LOGPcons: Hidrofobicidad de la molécula.

MACCSFP125: Fragmentos estructurales específicos.

MW: Peso molecular (recalculado mediante RDKit).

Evaluación de Robustez
El modelo fue validado mediante:

Validación Cruzada (K-Fold) para asegurar estabilidad.

Validación Externa con un set de datos no visto por el modelo.

Dominio de Aplicabilidad mediante el cálculo de Leverage.

4. Interpretabilidad (Valores SHAP)
Para cumplir con el requisito de interpretabilidad, se utilizaron valores de SHAP (SHapley Additive exPlanations). Esto permite identificar cómo cada descriptor aumenta o disminuye la probabilidad de permeabilidad, proporcionando una base química a las decisiones del modelo de Machine Learning.

5. Resultados del Cribado Virtual
Se realizó un cribado masivo sobre 4,845 moléculas de la base de datos DrugBank. Los candidatos finales fueron filtrados mediante:

Probabilidad de permeabilidad > 0.5 (Modelo RF).

Cumplimiento de la Regla de los 5 de Lipinski (Drogabilidad).

6. Requisitos de Instalación
Es necesario contar con un entorno de Python 3.x y las siguientes librerías:

Bash

pip install rdkit scikit-learn pandas matplotlib seaborn joblib shap
