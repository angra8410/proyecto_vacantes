# Directorio de Datos

## Contenido

Este directorio contiene los datasets de entrenamiento para el proyecto.

### Archivos

- `training_data.jsonl` - Dataset principal en formato JSONL (JSON Lines)
- `training_data.example.jsonl` - Archivo de ejemplo con formato correcto

### Formato

Cada línea debe ser un objeto JSON válido:

```json
{"text": "Contenido de la vacante o descripción"}
```

Ver `training_data.example.jsonl` para ejemplos completos.

## Importante

⚠️ **Este es el ÚNICO directorio válido para datasets de entrenamiento.**

No utilices otras ubicaciones como `venv/data/` o similares.

## Uso

Para gestionar este dataset de forma segura, usa el script `scripts/dataset_manager.py`. Ver el README principal del proyecto para más detalles.
