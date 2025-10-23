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

## Verificación Rápida

Para verificar que tu proyecto está configurado correctamente:

```bash
python scripts/verify_setup.py
```

Este script verifica:
- ✓ Estructura de directorios correcta
- ✓ No hay datasets en ubicaciones incorrectas (venv/data/)
- ✓ .gitignore configurado correctamente
- ✓ Scripts necesarios presentes

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

## Scripts PowerShell (Windows)

Para usuarios de Windows, se incluyen scripts PowerShell para gestión avanzada de datasets:

### Merge con Deduplicación (merge_training_data.ps1)

Fusiona múltiples archivos JSONL con deduplicación automática:

```powershell
# Ver preview sin hacer cambios (dry-run)
.\scripts\merge_training_data.ps1 -DryRun

# Fusionar archivos con backups automáticos
.\scripts\merge_training_data.ps1 -SourceFiles "data\training_data.jsonl","venv\data\training_data.jsonl" -OutputFile "data\training_data.jsonl"

# Fusionar y mover archivo de venv (con confirmación)
.\scripts\merge_training_data.ps1 -SourceFiles "data\training_data.jsonl","venv\data\training_data.jsonl" -ConfirmMove
```

Características:
- ✓ Modo dry-run para preview seguro
- ✓ Backups automáticos con timestamp
- ✓ Deduplicación basada en campo 'text'
- ✓ Manejo de líneas JSON malformadas
- ✓ Log de líneas inválidas en data/training_data.invalid_lines.log

### Limpieza y Deduplicación (dedupe_clean.ps1)

Limpia y deduplica un archivo JSONL:

```powershell
# Preview de limpieza
.\scripts\dedupe_clean.ps1 -DryRun

# Limpiar con configuración por defecto
.\scripts\dedupe_clean.ps1 -InputFile "data\training_data.jsonl"

# Limpiar con opciones avanzadas
.\scripts\dedupe_clean.ps1 -InputFile "data\training_data.jsonl" -MinTextLength 20 -RemoveEmpty
```

Características:
- ✓ Elimina duplicados exactos
- ✓ Remueve textos muy cortos (configurable)
- ✓ Opción para remover entradas vacías
- ✓ Estadísticas detalladas de reducción

### Resumir Textos Largos (summarize_sumy.py)

Reduce el tamaño del dataset mediante resumen extractivo:

```bash
# Preview de reducción
python scripts/summarize_sumy.py data/training_data.jsonl --dry-run

# Reducir a tamaño objetivo
python scripts/summarize_sumy.py data/training_data.jsonl --target-size-mb 5

# Resumir con configuración personalizada
python scripts/summarize_sumy.py data/training_data.jsonl --max-sentences 3 --algorithm lsa
```

**Nota**: Requiere instalación previa:
```bash
pip install sumy nltk
python -m nltk.downloader punkt
```

Características:
- ✓ Resumen extractivo con algoritmos LSA o Luhn
- ✓ Control por tamaño objetivo o número de oraciones
- ✓ Preserva estructura JSONL original
- ✓ Backups automáticos

## Guardar Correcciones de Forma Segura

Para evitar escrituras en ubicaciones incorrectas, use el script `save_correction_safe.py`:

```bash
# Guardar una corrección
python scripts/save_correction_safe.py --text "Descripción de vacante..."

# Guardar múltiples correcciones desde archivo
python scripts/save_correction_safe.py --file corrections.txt

# Ver estadísticas del dataset
python scripts/save_correction_safe.py --stats
```

O usar como módulo en otros scripts:

```python
from scripts.save_correction_safe import save_correction, save_corrections

# Guardar una corrección
save_correction("Texto de vacante")

# Guardar múltiples
save_corrections(["Texto 1", "Texto 2", "Texto 3"])
```

Características:
- ✓ Siempre escribe en data/training_data.jsonl (ruta absoluta)
- ✓ Deduplicación automática
- ✓ Backups antes de modificar
- ✓ Thread-safe para uso concurrente
- ✓ Validación de datos

## Flujo de Trabajo Recomendado

### Para Migración desde venv/data/

Si detectaste archivos en `venv/data/training_data.jsonl`:

1. **Ejecutar dry-run del merge**:
   ```powershell
   .\scripts\merge_training_data.ps1 -DryRun
   ```

2. **Revisar el preview** y verificar conteos

3. **Ejecutar merge real**:
   ```powershell
   .\scripts\merge_training_data.ps1 -SourceFiles "data\training_data.jsonl","venv\data\training_data.jsonl" -OutputFile "data\training_data.jsonl"
   ```

4. **Validar resultado**:
   ```bash
   python scripts/dataset_manager.py validate data/training_data.jsonl
   ```

5. **Mover archivo venv** (opcional, con confirmación):
   ```powershell
   Move-Item venv\data\training_data.jsonl venv\data\training_data.jsonl.moved
   ```

### Para Mantenimiento Regular

1. **Crear backup periódico**:
   ```bash
   python scripts/dataset_manager.py backup data/training_data.jsonl
   ```

2. **Validar integridad**:
   ```bash
   python scripts/dataset_manager.py validate data/training_data.jsonl
   ```

3. **Limpiar duplicados** (si necesario):
   ```powershell
   .\scripts\dedupe_clean.ps1 -InputFile "data\training_data.jsonl"
   ```

4. **Reducir tamaño** (si excede límites):
   ```bash
   python scripts/summarize_sumy.py data/training_data.jsonl --target-size-mb 10
   ```

## Verificación del Proyecto

Ejecuta el script de verificación para asegurar que todo está correctamente configurado:

```bash
python scripts/verify_setup.py
```

Este script verifica:
- ✓ Estructura de directorios correcta
- ✓ No hay datasets en venv/data/
- ✓ .gitignore configurado
- ✓ Scripts disponibles

## Contacto

Para dudas o problemas, crear un issue en el repositorio.
