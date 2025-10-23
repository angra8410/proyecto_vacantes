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

## Comandos de Referencia Rápida

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
