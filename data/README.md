# Directorio de Datos

## Contenido

Este directorio contiene los datasets de entrenamiento para el proyecto.

### Archivo Principal

- `training_data.jsonl` - Dataset principal en formato JSONL (JSON Lines)

### Formato

Cada línea debe ser un objeto JSON válido:

```json
{"text": "Contenido de la vacante o descripción"}
```

## Importante

⚠️ **Este es el ÚNICO directorio válido para datasets de entrenamiento.**

No utilices otras ubicaciones como `venv/data/` o similares.

## Uso

Para gestionar este dataset de forma segura, usa el script `scripts/dataset_manager.py`. Ver el README principal del proyecto para más detalles.
