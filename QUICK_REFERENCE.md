# Guía Rápida - Dataset Manager

## Comandos Más Usados

### Verificar Configuración
```bash
python scripts/verify_setup.py
```

### Antes de Modificar Datos
```bash
# Siempre crear backup primero
python scripts/dataset_manager.py backup data/training_data.jsonl
```

### Ver Estado del Dataset
```bash
# Estadísticas completas
python scripts/dataset_manager.py validate data/training_data.jsonl

# Solo contar entradas
python scripts/dataset_manager.py count data/training_data.jsonl

# Ver últimas 5 entradas
python scripts/dataset_manager.py tail data/training_data.jsonl -n 5
```

### Migración desde venv/data
```bash
# 1. Backups
python scripts/dataset_manager.py backup data/training_data.jsonl
python scripts/dataset_manager.py backup venv/data/training_data.jsonl

# 2. Fusionar y deduplicar
python scripts/dataset_manager.py merge \
    data/training_data.jsonl \
    venv/data/training_data.jsonl \
    -o data/training_data.jsonl

# 3. Verificar resultado
python scripts/dataset_manager.py validate data/training_data.jsonl

# 4. Renombrar archivo antiguo
mv venv/data/training_data.jsonl venv/data/training_data.jsonl.moved
```

### Agregar Nuevos Datos
```bash
# 1. Backup del dataset actual
python scripts/dataset_manager.py backup data/training_data.jsonl

# 2. Fusionar con nuevos datos
python scripts/dataset_manager.py merge \
    data/training_data.jsonl \
    nuevos_datos.jsonl \
    -o data/training_data.jsonl

# 3. Verificar
python scripts/dataset_manager.py validate data/training_data.jsonl
```

## Estructura de Archivos

```
proyecto_vacantes/
├── data/
│   └── training_data.jsonl          # ← Usar siempre este archivo
├── backups/                          # ← Backups automáticos (ignorado)
├── scripts/
│   ├── dataset_manager.py           # ← Herramienta principal
│   └── verify_setup.py              # ← Verificar configuración
├── .gitignore                        # ← Ignora venv/, backups/
├── README.md                         # ← Documentación completa
├── MIGRATION_GUIDE.md                # ← Guía paso a paso
└── QUICK_REFERENCE.md                # ← Este archivo
```

## Reglas de Oro

1. ✅ **SIEMPRE** usar `data/training_data.jsonl`
2. ❌ **NUNCA** usar `venv/data/`
3. 🛡️ **SIEMPRE** crear backup antes de modificar
4. 🔍 **SIEMPRE** validar después de modificar
5. 📝 Mantener backups de los últimos 7-30 días

## Formato del Dataset

Cada línea debe ser un JSON válido:

```json
{"text": "Descripción de la vacante o texto de entrenamiento"}
```

## Solución de Problemas

### "Archivo no encontrado"
→ Verifica que estás en la raíz del proyecto: `pwd`

### "Líneas malformadas"
→ El script las ignorará automáticamente y mostrará advertencias

### "Permisos denegados"
→ `chmod +x scripts/dataset_manager.py`

## Ayuda

```bash
# Ayuda general
python scripts/dataset_manager.py --help

# Ayuda de un comando específico
python scripts/dataset_manager.py backup --help
python scripts/dataset_manager.py merge --help
```

## Más Información

- `README.md` - Documentación completa
- `MIGRATION_GUIDE.md` - Guía detallada de migración
- Issues del proyecto - Para reportar problemas
