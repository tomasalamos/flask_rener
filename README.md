# Backend en Flask con pandas y numpy

Este backend tiene un endpoint `/procesar` que acepta datos JSON tipo lista de diccionarios y calcula media, desviación estándar y valores nulos.

## Endpoint

**POST /procesar**

**Ejemplo de input:**
```json
[
  {"sensor1": 10, "sensor2": 20},
  {"sensor1": 30, "sensor2": 40}
]
```

**Output:**
```json
{
  "columnas": ["sensor1", "sensor2"],
  "media": {"sensor1": 20.0, "sensor2": 30.0},
  "desviacion_estandar": {"sensor1": 14.14, "sensor2": 14.14},
  "valores_nulos": {"sensor1": 0, "sensor2": 0}
}
```
