from flask import Flask, render_template, request, send_file
import pandas as pd
import io
import os
import uuid

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024  # 300 MB máximo para Render (o ajusta)

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

    try:
        # Guardar el archivo en una ruta temporal
        temp_filename = f"/tmp/{uuid.uuid4().hex}.csv"
        archivo.save(temp_filename)

        # Cargar el CSV desde disco temporal
        df = pd.read_csv(temp_filename, sep=',', encoding='utf-8', on_bad_lines='skip')

        # Eliminar el archivo temporal
        os.remove(temp_filename)

        # Procesar los datos como antes
        if 'date' in df.columns:
            df = df.drop(columns=['date'])

        df = df.apply(pd.to_numeric, errors='coerce')

        if df.select_dtypes(include=['number']).empty:
            return "No se encontraron columnas numéricas en el archivo.", 400

        resumen = df.describe().transpose()[['mean', 'std']]
        resumen['valores_nulos'] = df.isnull().sum()

        resumen.reset_index(inplace=True)
        resumen.columns = ['columna', 'media', 'desviacion_estandar', 'valores_nulos']

        resultado_buffer = io.BytesIO()
        resumen.to_csv(resultado_buffer, index=False)
        resultado_buffer.seek(0)

        return send_file(
            resultado_buffer, 
            as_attachment=True, 
            download_name="resumen_resultado.csv",
            mimetype="text/csv"
        )

    except Exception as e:
        return f"Ocurrió un error al procesar el archivo: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
