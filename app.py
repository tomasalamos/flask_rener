from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import os
import csv

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
        # Leer archivo CSV en modo streaming línea por línea
        csv_reader = csv.DictReader((line.decode('utf-8') for line in file.stream))
        filas = []

        for i, row in enumerate(csv_reader):
            filas.append(row)
            if i % 100000 == 0:
                print(f"Leyendo fila {i}")  # Debug opcional

        df = pd.DataFrame(filas)

        # Intentar convertir columnas numéricas
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='ignore')

        resumen = {
            "columnas": list(df.columns),
            "media": df.mean(numeric_only=True).to_dict(),
            "desviacion_estandar": df.std(numeric_only=True).to_dict(),
            "valores_nulos": df.isnull().sum().to_dict()
        }

        return jsonify(resumen)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
