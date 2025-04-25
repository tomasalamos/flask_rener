from flask import Flask, render_template, request, send_file
import pandas as pd
import io
import uuid

app = Flask(__name__)

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
        # Leemos el archivo directamente en memoria (sin guardarlo en el servidor)
        df = pd.read_csv(archivo, sep=',', encoding='utf-8', on_bad_lines='skip')

        # Verificamos si 'date' existe y la eliminamos si está presente
        if 'date' in df.columns:
            df = df.drop(columns=['date'])

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

        # Crear un buffer en memoria para el CSV de resultados
        resultado_buffer = io.BytesIO()
        resumen.to_csv(resultado_buffer, index=False)
        resultado_buffer.seek(0)

        # Enviamos el archivo generado como descarga
        return send_file(
            resultado_buffer, 
            as_attachment=True, 
            download_name="resumen_resultado.csv",  # Nombre del archivo para descargar
            mimetype="text/csv"  # Tipo MIME
        )

    except Exception as e:
        return f"Ocurrió un error al procesar el archivo: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)

