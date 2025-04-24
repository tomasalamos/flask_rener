from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

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
        df = pd.read_csv(file)
        resumen = {
            "columnas": list(df.columns),
            "media": df.mean(numeric_only=True).to_dict(),
            "desviacion_estandar": df.std(numeric_only=True).to_dict(),
            "valores_nulos": df.isnull().sum().to_dict()
        }
        return jsonify(resumen)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
