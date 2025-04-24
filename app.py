from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

@app.route('/')
def home():
    return '¡Backend con Flask, pandas y numpy funcionando en Render!'

@app.route('/procesar', methods=['POST'])
def procesar():
    data = request.get_json()
    df = pd.DataFrame(data)
    resultado = {
        "columnas": list(df.columns),
        "media": df.mean(numeric_only=True).to_dict(),
        "desviacion_estandar": df.std(numeric_only=True).to_dict(),
        "valores_nulos": df.isnull().sum().to_dict()
    }
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
