from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# Permitir archivos de hasta 500 MB
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/procesar", methods=["POST"])
def procesar_json():
    data = request.get_json()
    df = pd.DataFrame(data)
    resumen = {
        "columnas": list(df.columns),
        "media": df.mean(numeric_only=True).to_dict(),
        "desviacion_estandar": df.std(numeric_only=True).to_dict(),
        "valores_nulos": df.isnull().sum().to_dict()
    }
    return jsonify(resumen)

@app.route("/subir_csv", methods=["POST"])
def subir_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    try:
        # Leer por chunks para evitar consumir demasiada memoria
        chunk_size = 100000  # Lee 100,000 filas por vez
        suma = {}
        suma_cuadrados = {}
        conteo = {}
        nulos = {}
        columnas = None

        for chunk in pd.read_csv(file, chunksize=chunk_size):
            if columnas is None:
                columnas = list(chunk.columns)

            for col in chunk.select_dtypes(include=np.number).columns:
                suma[col] = suma.get(col, 0) + chunk[col].sum()
                suma_cuadrados[col] = suma_cuadrados.get(col, 0) + (chunk[col] ** 2).sum()
                conteo[col] = conteo.get(col, 0) + chunk[col].count()

            for col in chunk.columns:
                nulos[col] = nulos.get(col, 0) + chunk[col].isnull().sum()

        # Calcular estadísticas sin cargar todo el archivo en RAM
        media = {col: suma[col] / conteo[col] for col in suma}
        std = {
            col: np.sqrt((suma_cuadrados[col] / conteo[col]) - (media[col] ** 2))
            for col in suma
        }

        resumen = {
            "columnas": columnas,
            "media": media,
            "desviacion_estandar": std,
            "valores_nulos": nulos
        }

        return jsonify(resumen)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

