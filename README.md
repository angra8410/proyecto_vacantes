# Proyecto Vacantes

Este proyecto gestiona datasets de entrenamiento para modelos de análisis de vacantes laborales.

## Estructura del Proyecto

```
proyecto_vacantes/
├── data/                          # Directorio principal para datasets
│   └── training_data.jsonl       # Dataset principal de entrenamiento
├── backups/                       # Backups automáticos (ignorado en git)
├── scripts/                       # Scripts de utilidad
│   └── dataset_manager.py        # Gestor de datasets
└── README.md                     # Este archivo
```

## Gestión de Datasets

### Ubicación Oficial

**IMPORTANTE**: El único directorio válido para datasets de entrenamiento es `data/` en la raíz del proyecto.

❌ **NO usar**: `venv/data/` o cualquier otra ubicación
✅ **Usar siempre**: `data/training_data.jsonl`

### Formato del Dataset

Los datos deben estar en formato JSONL (JSON Lines), con una entrada por línea:

```json
{"text": "Descripción de la vacante o texto de entrenamiento"}
```

### Gestión Segura de Archivos

Para gestionar los datasets de forma segura, utilice el script `scripts/dataset_manager.py`:

#### Crear Backup

```bash
python scripts/dataset_manager.py backup data/training_data.jsonl
```

Esto creará un backup con timestamp en el directorio `backups/`.

#### Validar Dataset

```bash
python scripts/dataset_manager.py validate data/training_data.jsonl
```

Muestra estadísticas del dataset, entradas malformadas y últimas entradas válidas.

#### Fusionar y Deduplicar

```bash
python scripts/dataset_manager.py merge data/training_data.jsonl venv/data/training_data.jsonl -o data/training_data.jsonl
```

Este comando:
1. Crea backups automáticos de ambos archivos
2. Lee y parsea ambos archivos
3. Elimina duplicados basándose en el campo `text`
4. Ignora líneas malformadas (con advertencias)
5. Guarda el resultado en el archivo de salida

#### Contar Entradas

```bash
python scripts/dataset_manager.py count data/training_data.jsonl
```

Muestra el número total de entradas válidas.

#### Ver Últimas Entradas

```bash
python scripts/dataset_manager.py tail data/training_data.jsonl -n 5
```

Muestra las últimas N entradas del dataset.

### Procedimiento de Migración desde venv/data

Si tienes datos en `venv/data/training_data.jsonl`, sigue estos pasos:

1. **Crear backups de seguridad**:
   ```bash
   python scripts/dataset_manager.py backup data/training_data.jsonl
   python scripts/dataset_manager.py backup venv/data/training_data.jsonl
   ```

2. **Validar ambos archivos**:
   ```bash
   python scripts/dataset_manager.py validate data/training_data.jsonl
   python scripts/dataset_manager.py validate venv/data/training_data.jsonl
   ```

3. **Fusionar y deduplicar**:
   ```bash
   python scripts/dataset_manager.py merge data/training_data.jsonl venv/data/training_data.jsonl -o data/training_data.jsonl
   ```

4. **Verificar el resultado**:
   ```bash
   python scripts/dataset_manager.py validate data/training_data.jsonl
   python scripts/dataset_manager.py tail data/training_data.jsonl -n 3
   ```

5. **Renombrar el archivo antiguo** (no eliminarlo inmediatamente):
   ```bash
   mv venv/data/training_data.jsonl venv/data/training_data.jsonl.moved
   ```

6. **Después de verificar que todo funciona**, puedes eliminar el archivo movido.

## Riesgos y Precauciones

⚠️ **ADVERTENCIAS**:

- Siempre crear backups antes de modificar datasets
- Verificar que estás en el directorio correcto del proyecto
- No eliminar archivos hasta verificar que la migración fue exitosa
- Las entradas JSON malformadas se ignoran durante la fusión (se registran advertencias)
- Los backups automáticos se crean en `backups/` con timestamp

## Scripts de Extracción y Entrenamiento

Asegúrate de que todos los scripts del proyecto:
- Lean datos de `data/training_data.jsonl`
- Escriban nuevos datos en `data/training_data.jsonl`
- NO usen rutas en `venv/data/`

## Contribución

Al agregar nuevos scripts o funcionalidades:
1. Usar siempre la ruta `data/training_data.jsonl`
2. Implementar manejo de errores para archivos malformados
3. Crear backups antes de modificaciones destructivas
4. Documentar cambios en este README

## Contacto

Para dudas o problemas, crear un issue en el repositorio.
