from flask import Flask, render_template, request, send_file
import pandas as pd
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'resultados'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/subir_csv', methods=['POST'])
def subir_csv():
    if 'archivo' not in request.files:
        return "No se encontró el archivo", 400

    archivo = request.files['archivo']
    if archivo.filename == '':
        return "Nombre de archivo vacío", 400

    # Guardamos el archivo temporalmente
    temp_filename = f"{uuid.uuid4().hex}.csv"
    temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
    archivo.save(temp_path)

    try:
        # Intentamos leer el archivo CSV
        df = pd.read_csv(temp_path, sep=',', encoding='utf-8', on_bad_lines='skip')

        # Verificamos las primeras filas para diagnóstico
        print("Primeras filas leídas:")
        print(df.head())  # Muestra las primeras filas para revisar

        # Verificamos si 'date' existe y la eliminamos si está presente
        if 'date' in df.columns:
            df = df.drop(columns=['date'])
            print("Columna 'date' eliminada")

        # Convertimos las columnas a valores numéricos (forzando NaN donde no sea posible)
        df = df.apply(pd.to_numeric, errors='coerce')

        # Comprobamos si hay al menos una columna numérica
        if df.select_dtypes(include=['number']).empty:
            return "No se encontraron columnas numéricas en el archivo.", 400

        # Calculamos las estadísticas: media, desviación estándar y valores nulos
        resumen = df.describe().transpose()[['mean', 'std']]
        resumen['valores_nulos'] = df.isnull().sum()

        # Restablecemos el índice y renombramos las columnas
        resumen.reset_index(inplace=True)
        resumen.columns = ['columna', 'media', 'desviacion_estandar', 'valores_nulos']

        # Guardamos el archivo de resultados
        resultado_filename = f"resumen_{uuid.uuid4().hex}.csv"
        resultado_path = os.path.join(RESULT_FOLDER, resultado_filename)
        resumen.to_csv(resultado_path, index=False)

        # Enviamos el archivo generado como descarga
        return send_file(resultado_path, as_attachment=True)

    except Exception as e:
        print(f"Ocurrió un error al procesar el archivo: {e}")
        return f"Ocurrió un error al procesar el archivo: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)



