# Guía de Migración de Datasets

Esta guía te ayudará a migrar de forma segura los datasets desde `venv/data/` a la ubicación oficial `data/`.

## Escenario: Tienes datos en venv/data/training_data.jsonl

### Paso 1: Verificar la situación actual

Primero, verifica que tienes los archivos en las ubicaciones esperadas:

```bash
# Verificar archivo en data/
python scripts/dataset_manager.py validate data/training_data.jsonl

# Verificar archivo en venv/data/ (si existe)
python scripts/dataset_manager.py validate venv/data/training_data.jsonl
```

### Paso 2: Crear backups de seguridad

**IMPORTANTE**: Siempre crea backups antes de cualquier operación:

```bash
# Backup del archivo principal
python scripts/dataset_manager.py backup data/training_data.jsonl

# Backup del archivo en venv (si existe)
python scripts/dataset_manager.py backup venv/data/training_data.jsonl
```

Los backups se crearán en el directorio `backups/` con un timestamp único.

### Paso 3: Fusionar y deduplicar

Ahora fusiona ambos archivos, eliminando duplicados:

```bash
python scripts/dataset_manager.py merge \
    data/training_data.jsonl \
    venv/data/training_data.jsonl \
    -o data/training_data.jsonl
```

Este comando:
- ✅ Crea backups automáticos de ambos archivos
- ✅ Lee todas las entradas de ambos archivos
- ✅ Elimina duplicados basándose en el campo `text`
- ✅ Ignora líneas JSON malformadas (con advertencias)
- ✅ Guarda el resultado en `data/training_data.jsonl`

### Paso 4: Verificar el resultado

Valida que la fusión fue exitosa:

```bash
# Ver estadísticas del archivo fusionado
python scripts/dataset_manager.py validate data/training_data.jsonl

# Contar entradas
python scripts/dataset_manager.py count data/training_data.jsonl

# Ver las últimas 5 entradas
python scripts/dataset_manager.py tail data/training_data.jsonl -n 5
```

### Paso 5: Renombrar el archivo antiguo

Una vez verificado que todo funciona, renombra el archivo en venv:

```bash
# En Linux/Mac
mv venv/data/training_data.jsonl venv/data/training_data.jsonl.moved

# En Windows PowerShell
Move-Item venv\data\training_data.jsonl venv\data\training_data.jsonl.moved -Force
```

**NO lo elimines todavía**, solo renómbralo para que no se use accidentalmente.

### Paso 6: Probar tu flujo de trabajo

Ejecuta tus scripts de entrenamiento o procesamiento para verificar que funcionan con el nuevo archivo:

```bash
# Ejemplo: si tienes un script de entrenamiento
python train_model.py

# O script de extracción
python extract_data.py
```

### Paso 7: Eliminar archivo movido (opcional)

Después de varios días de usar el nuevo archivo sin problemas, puedes eliminar el archivo renombrado:

```bash
# En Linux/Mac
rm venv/data/training_data.jsonl.moved

# En Windows PowerShell
Remove-Item venv\data\training_data.jsonl.moved
```

## Caso: Solo tienes datos en venv/data/

Si solo existe `venv/data/training_data.jsonl` y no hay archivo en `data/`:

```bash
# Crear directorio data si no existe
mkdir -p data

# Mover el archivo (con backup automático)
python scripts/dataset_manager.py backup venv/data/training_data.jsonl

# Copiar a la ubicación correcta
cp venv/data/training_data.jsonl data/training_data.jsonl

# Validar
python scripts/dataset_manager.py validate data/training_data.jsonl

# Renombrar el original
mv venv/data/training_data.jsonl venv/data/training_data.jsonl.moved
```

## Caso: Solo tienes datos en data/

¡Perfecto! Ya estás usando la ubicación correcta. Solo asegúrate de:

```bash
# Crear un backup por seguridad
python scripts/dataset_manager.py backup data/training_data.jsonl

# Validar el dataset
python scripts/dataset_manager.py validate data/training_data.jsonl
```

## Mantenimiento Regular

### Crear backups periódicos

```bash
# Antes de agregar nuevos datos
python scripts/dataset_manager.py backup data/training_data.jsonl

# Los backups se guardan con timestamp: training_data_YYYYMMDD_HHMMSS.jsonl.bak
```

### Verificar integridad

```bash
# Ejecutar validación periódicamente
python scripts/dataset_manager.py validate data/training_data.jsonl
```

### Limpiar backups antiguos

Los backups se acumulan en el directorio `backups/`. Puedes limpiar los antiguos manualmente:

```bash
# Ver backups existentes
ls -lh backups/

# Eliminar backups de más de 30 días (Linux/Mac)
find backups/ -name "*.bak" -mtime +30 -delete

# En Windows, eliminar manualmente los que no necesites
```

## Problemas Comunes

### "Archivo no encontrado"

Si recibes este error, verifica:
1. Que estás ejecutando el comando desde la raíz del proyecto
2. Que la ruta del archivo es correcta
3. Que el archivo existe: `ls -l data/training_data.jsonl`

### "Líneas malformadas"

Si el validador reporta líneas malformadas:
1. No te preocupes, el script las ignorará durante la fusión
2. Puedes ver qué líneas son con el comando `validate`
3. Revisa el archivo original si es necesario

### "Permisos denegados"

Si tienes problemas de permisos:

```bash
# Linux/Mac
chmod +x scripts/dataset_manager.py
chmod 644 data/training_data.jsonl

# Windows: Ejecuta PowerShell como Administrador
```

## Verificación Final

Checklist antes de considerar la migración completa:

- [ ] Backups creados y verificados
- [ ] Archivo fusionado validado sin errores
- [ ] Scripts de entrenamiento funcionan con el nuevo archivo
- [ ] Archivo antiguo renombrado (no eliminado aún)
- [ ] Documentación actualizada en README
- [ ] `.gitignore` configurado para ignorar `venv/` y `backups/`
- [ ] Equipo notificado de la nueva ubicación

## Soporte

Si encuentras problemas durante la migración:
1. NO elimines ningún archivo todavía
2. Revisa los backups en `backups/`
3. Crea un issue en el repositorio con los detalles del problema
4. Incluye la salida del comando que falló

## Método Alternativo: Scripts PowerShell (Windows)

Para usuarios de Windows, existe una alternativa usando scripts PowerShell con características avanzadas:

### Paso 1: Dry-Run con PowerShell

```powershell
# Desde la raíz del proyecto
.\scripts\merge_training_data.ps1 -DryRun
```

Este comando:
- Muestra los archivos que se fusionarían
- Cuenta entradas en cada archivo
- Identifica líneas malformadas
- NO hace cambios reales

**Ejemplo de salida**:
```
======================================================================
JSONL Training Data Merge Tool
======================================================================

DRY RUN MODE - No changes will be made

Configuration:
  Project Root: C:\Projects\proyecto_vacantes
  Source Files: 2
    ✓ C:\Projects\proyecto_vacantes\data\training_data.jsonl
    ✓ C:\Projects\proyecto_vacantes\venv\data\training_data.jsonl
  Output File: C:\Projects\proyecto_vacantes\data\training_data.jsonl

Analysis (Dry Run):
  Reading: C:\Projects\proyecto_vacantes\data\training_data.jsonl
    Entries: 150
  Reading: C:\Projects\proyecto_vacantes\venv\data\training_data.jsonl
    Entries: 75
    Invalid lines: 2

Summary:
  Total entries to merge: 225
  Invalid lines: 2

To execute the merge, run without -DryRun parameter
```

### Paso 2: Ejecutar Merge Real

Una vez revisado el dry-run, ejecuta el merge real:

```powershell
.\scripts\merge_training_data.ps1 -SourceFiles "data\training_data.jsonl","venv\data\training_data.jsonl" -OutputFile "data\training_data.jsonl"
```

Este comando:
- ✓ Crea backups automáticos con timestamp
- ✓ Lee y parsea ambos archivos
- ✓ Deduplica basándose en el campo 'text'
- ✓ Registra líneas malformadas en data/training_data.invalid_lines.log
- ✓ Escribe el resultado fusionado

**Ejemplo de salida**:
```
======================================================================
JSONL Training Data Merge Tool
======================================================================

Creating backups...
✓ Backup created: backups\training_data_20251023_140522.jsonl.bak
✓ Backup created: backups\training_data_20251023_140523.jsonl.bak

Reading source files...
  Processing: C:\Projects\proyecto_vacantes\data\training_data.jsonl
    Read: 150 entries
  Processing: C:\Projects\proyecto_vacantes\venv\data\training_data.jsonl
    Read: 75 entries
    Invalid lines: 2
    Duplicates removed: 25

✓ Invalid lines logged to: data\training_data.invalid_lines.log

Writing merged output...
✓ Written 200 entries to: C:\Projects\proyecto_vacantes\data\training_data.jsonl

======================================================================
Merge completed successfully!
======================================================================
  Total unique entries: 200
  Duplicates removed: 25
  Invalid lines: 1
  Output file: C:\Projects\proyecto_vacantes\data\training_data.jsonl
```

### Paso 3: Mover Archivo Antiguo (Opcional)

Para mover el archivo de venv después del merge:

```powershell
# Con confirmación interactiva
.\scripts\merge_training_data.ps1 -SourceFiles "data\training_data.jsonl","venv\data\training_data.jsonl" -ConfirmMove

# O manualmente
Move-Item venv\data\training_data.jsonl venv\data\training_data.jsonl.moved.20251023
```

### Limpieza Adicional con dedupe_clean.ps1

Si después del merge quieres limpiar aún más:

```powershell
# Preview de limpieza
.\scripts\dedupe_clean.ps1 -InputFile "data\training_data.jsonl" -DryRun

# Ejecutar limpieza (elimina textos < 10 chars y duplicados)
.\scripts\dedupe_clean.ps1 -InputFile "data\training_data.jsonl"

# Limpieza agresiva (elimina textos < 20 chars y vacíos)
.\scripts\dedupe_clean.ps1 -InputFile "data\training_data.jsonl" -MinTextLength 20 -RemoveEmpty
```

### Reducción de Tamaño con summarize_sumy.py

Si el archivo es muy grande (> 10 MB), puedes reducirlo:

```bash
# Activar venv primero
.\venv\Scripts\Activate.ps1

# Instalar dependencias (una vez)
pip install sumy nltk
python -m nltk.downloader punkt

# Preview de reducción
python scripts/summarize_sumy.py data/training_data.jsonl --dry-run

# Reducir a tamaño objetivo
python scripts/summarize_sumy.py data/training_data.jsonl --target-size-mb 5

# O con control de oraciones
python scripts/summarize_sumy.py data/training_data.jsonl --max-sentences 3
```

## Prevenir Escrituras Incorrectas

Para evitar que scripts escriban en venv/data/, usa el helper seguro:

### En Scripts Python

```python
# En lugar de usar rutas relativas:
# BAD: file_path = "training_data.jsonl"  # puede escribir en CWD incorrecto

# Usar el helper seguro:
from scripts.save_correction_safe import save_correction, get_training_data_path

# Obtener ruta correcta
correct_path = get_training_data_path()
print(f"Ruta correcta: {correct_path}")
# Output: C:\Projects\proyecto_vacantes\data\training_data.jsonl

# Guardar correcciones
save_correction("Texto de vacante")
save_corrections(["Texto 1", "Texto 2"])
```

### Desde Línea de Comandos

```bash
# Guardar una corrección
python scripts/save_correction_safe.py --text "Descripción de vacante..."

# Guardar desde archivo
python scripts/save_correction_safe.py --file corrections.txt

# Ver estadísticas
python scripts/save_correction_safe.py --stats
```

El script automáticamente:
- ✓ Usa rutas absolutas relativas al project root
- ✓ Crea backups antes de modificar
- ✓ Deduplica automáticamente
- ✓ Valida entradas JSON

## Comandos de Referencia Rápida

### Python (multiplataforma)

```bash
# Backup
python scripts/dataset_manager.py backup <archivo>

# Validar
python scripts/dataset_manager.py validate <archivo>

# Fusionar (con backups automáticos)
python scripts/dataset_manager.py merge <archivo1> <archivo2> -o <salida>

# Contar
python scripts/dataset_manager.py count <archivo>

# Ver últimas N entradas
python scripts/dataset_manager.py tail <archivo> -n <número>

# Ayuda
python scripts/dataset_manager.py --help
python scripts/dataset_manager.py <comando> --help
```

### PowerShell (Windows)

```powershell
# Merge con dry-run
.\scripts\merge_training_data.ps1 -DryRun

# Merge real
.\scripts\merge_training_data.ps1 -SourceFiles "data\training_data.jsonl","venv\data\training_data.jsonl"

# Limpieza
.\scripts\dedupe_clean.ps1 -InputFile "data\training_data.jsonl" -DryRun
.\scripts\dedupe_clean.ps1 -InputFile "data\training_data.jsonl"

# Resumen extractivo
python scripts/summarize_sumy.py data/training_data.jsonl --target-size-mb 5

# Guardar corrección segura
python scripts/save_correction_safe.py --text "Vacante..."
```

## Razón del Cambio

Esta migración previene problemas como:

❌ **Problema**: Scripts escriben en `venv/data/` porque usan `os.getcwd()` o rutas relativas
❌ **Problema**: Duplicados entre `data/` y `venv/data/`
❌ **Problema**: No hay backups antes de modificar
❌ **Problema**: Líneas JSON malformadas causan errores

✅ **Solución**: Scripts PowerShell y Python con rutas absolutas
✅ **Solución**: Deduplicación automática
✅ **Solución**: Backups con timestamp
✅ **Solución**: Manejo robusto de errores

## Revertir Cambios

Si algo sale mal, los backups están en `backups/` con timestamp:

```powershell
# Ver backups disponibles
Get-ChildItem backups\*.bak | Sort-Object LastWriteTime -Descending

# Restaurar backup
Copy-Item backups\training_data_20251023_140522.jsonl.bak data\training_data.jsonl -Force
```

```bash
# Linux/Mac
ls -lt backups/*.bak
cp backups/training_data_20251023_140522.jsonl.bak data/training_data.jsonl
```
