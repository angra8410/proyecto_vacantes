#!/usr/bin/env python3
"""
Script de verificación de configuración del proyecto.

Verifica que:
- La estructura de directorios es correcta
- No hay datasets en ubicaciones incorrectas
- El .gitignore está configurado correctamente
"""

import sys
from pathlib import Path
from typing import List, Tuple


def check_directory_structure() -> List[str]:
    """Verifica que la estructura de directorios sea correcta."""
    issues = []
    
    # Verificar que existe el directorio data/
    data_dir = Path("data")
    if not data_dir.exists():
        issues.append("❌ Directorio 'data/' no existe")
    elif not data_dir.is_dir():
        issues.append("❌ 'data/' existe pero no es un directorio")
    else:
        print("✓ Directorio 'data/' existe")
    
    # Verificar que existe el directorio scripts/
    scripts_dir = Path("scripts")
    if not scripts_dir.exists():
        issues.append("❌ Directorio 'scripts/' no existe")
    else:
        print("✓ Directorio 'scripts/' existe")
    
    return issues


def check_wrong_locations() -> List[str]:
    """Verifica que no haya datasets en ubicaciones incorrectas."""
    issues = []
    
    # Buscar training_data.jsonl en venv/
    venv_data = Path("venv/data/training_data.jsonl")
    if venv_data.exists():
        issues.append("⚠ ADVERTENCIA: Encontrado 'venv/data/training_data.jsonl' - debe moverse a 'data/'")
    else:
        print("✓ No hay datasets en 'venv/data/'")
    
    return issues


def check_gitignore() -> List[str]:
    """Verifica que .gitignore esté configurado correctamente."""
    issues = []
    
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        issues.append("❌ Archivo '.gitignore' no existe")
        return issues
    
    print("✓ Archivo '.gitignore' existe")
    
    # Verificar que contiene las entradas importantes
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_patterns = ['venv/', 'backups/', '*.bak']
    missing = []
    
    for pattern in required_patterns:
        if pattern not in content:
            missing.append(pattern)
    
    if missing:
        issues.append(f"⚠ .gitignore no contiene: {', '.join(missing)}")
    else:
        print("✓ .gitignore contiene patrones requeridos (venv/, backups/, *.bak)")
    
    return issues


def check_dataset_file() -> List[str]:
    """Verifica el estado del dataset principal."""
    issues = []
    
    dataset_path = Path("data/training_data.jsonl")
    
    if not dataset_path.exists():
        print("ℹ Dataset principal 'data/training_data.jsonl' no existe (aún no creado)")
    else:
        print(f"✓ Dataset principal existe: {dataset_path}")
        
        # Verificar que no está vacío
        size = dataset_path.stat().st_size
        if size == 0:
            issues.append("⚠ Dataset principal está vacío")
        else:
            print(f"  Tamaño: {size:,} bytes")
    
    return issues


def check_scripts() -> List[str]:
    """Verifica que los scripts necesarios existan."""
    issues = []
    
    dataset_manager = Path("scripts/dataset_manager.py")
    if not dataset_manager.exists():
        issues.append("❌ Script 'scripts/dataset_manager.py' no existe")
    else:
        print("✓ Script 'dataset_manager.py' existe")
        
        # Verificar que es ejecutable (en Unix)
        if hasattr(dataset_manager.stat(), 'st_mode'):
            import stat
            if not dataset_manager.stat().st_mode & stat.S_IXUSR:
                issues.append("⚠ 'dataset_manager.py' no tiene permisos de ejecución")
    
    return issues


def main():
    """Ejecuta todas las verificaciones."""
    print("=" * 60)
    print("Verificación de Configuración del Proyecto")
    print("=" * 60)
    print()
    
    all_issues = []
    
    # Verificar estructura de directorios
    print("📁 Verificando estructura de directorios...")
    all_issues.extend(check_directory_structure())
    print()
    
    # Verificar ubicaciones incorrectas
    print("🔍 Verificando ubicaciones incorrectas...")
    all_issues.extend(check_wrong_locations())
    print()
    
    # Verificar .gitignore
    print("📝 Verificando .gitignore...")
    all_issues.extend(check_gitignore())
    print()
    
    # Verificar dataset principal
    print("📊 Verificando dataset principal...")
    all_issues.extend(check_dataset_file())
    print()
    
    # Verificar scripts
    print("🔧 Verificando scripts...")
    all_issues.extend(check_scripts())
    print()
    
    # Resumen
    print("=" * 60)
    if all_issues:
        print("⚠ Se encontraron problemas:")
        print()
        for issue in all_issues:
            print(f"  {issue}")
        print()
        print("Consulta el README.md y MIGRATION_GUIDE.md para más información.")
        sys.exit(1)
    else:
        print("✅ Configuración del proyecto verificada correctamente")
        print()
        print("Todo está en orden. Puedes comenzar a trabajar con los datasets.")
        sys.exit(0)


if __name__ == '__main__':
    main()
