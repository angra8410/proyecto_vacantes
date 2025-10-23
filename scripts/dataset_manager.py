#!/usr/bin/env python3
"""
Dataset Manager - Herramienta para gestión segura de datasets JSONL

Funcionalidades:
- Crear backups con timestamp
- Validar contenido de datasets
- Fusionar y deduplicar múltiples datasets
- Contar entradas válidas
- Mostrar últimas entradas
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
import shutil


def create_backup(file_path: Path, backup_dir: Path = None) -> Path:
    """
    Crea un backup del archivo con timestamp.
    
    Args:
        file_path: Ruta del archivo a respaldar
        backup_dir: Directorio donde guardar el backup (default: backups/)
    
    Returns:
        Ruta del archivo de backup creado
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
    
    if backup_dir is None:
        backup_dir = Path("backups")
    
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}.bak"
    backup_path = backup_dir / backup_name
    
    shutil.copy2(file_path, backup_path)
    print(f"✓ Backup creado: {backup_path}")
    
    return backup_path


def read_jsonl(file_path: Path) -> tuple[List[Dict], List[int]]:
    """
    Lee un archivo JSONL y retorna las entradas válidas y números de línea malformadas.
    
    Args:
        file_path: Ruta del archivo JSONL
    
    Returns:
        Tupla de (lista de entradas válidas, lista de números de línea malformadas)
    """
    entries = []
    malformed_lines = []
    
    if not file_path.exists():
        return entries, malformed_lines
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            
            try:
                entry = json.loads(line)
                entries.append(entry)
            except json.JSONDecodeError:
                malformed_lines.append(line_num)
    
    return entries, malformed_lines


def write_jsonl(file_path: Path, entries: List[Dict]) -> None:
    """
    Escribe entradas a un archivo JSONL.
    
    Args:
        file_path: Ruta del archivo de salida
        entries: Lista de diccionarios a escribir
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def validate_dataset(file_path: Path) -> None:
    """
    Valida y muestra estadísticas de un dataset.
    
    Args:
        file_path: Ruta del archivo a validar
    """
    print(f"\n📊 Validando: {file_path}")
    print("=" * 60)
    
    if not file_path.exists():
        print(f"❌ Archivo no encontrado: {file_path}")
        return
    
    entries, malformed_lines = read_jsonl(file_path)
    
    print(f"✓ Entradas válidas: {len(entries)}")
    
    if malformed_lines:
        print(f"⚠ Líneas malformadas: {len(malformed_lines)}")
        print(f"  Líneas: {malformed_lines[:10]}" + 
              (f" ... y {len(malformed_lines) - 10} más" if len(malformed_lines) > 10 else ""))
    else:
        print("✓ No hay líneas malformadas")
    
    # Mostrar estadísticas del campo 'text'
    if entries:
        text_lengths = [len(entry.get('text', '')) for entry in entries]
        avg_length = sum(text_lengths) / len(text_lengths)
        print(f"\n📝 Estadísticas del campo 'text':")
        print(f"  - Longitud promedio: {avg_length:.0f} caracteres")
        print(f"  - Longitud mínima: {min(text_lengths)} caracteres")
        print(f"  - Longitud máxima: {max(text_lengths)} caracteres")
        
        # Mostrar últimas 3 entradas
        print(f"\n📄 Últimas 3 entradas:")
        for i, entry in enumerate(entries[-3:], start=1):
            text_preview = entry.get('text', '')[:80]
            if len(entry.get('text', '')) > 80:
                text_preview += "..."
            print(f"  {i}. {text_preview}")
    else:
        print("\n⚠ No hay entradas válidas en el archivo")


def merge_datasets(input_files: List[Path], output_file: Path, create_backups: bool = True) -> None:
    """
    Fusiona múltiples datasets, eliminando duplicados.
    
    Args:
        input_files: Lista de archivos a fusionar
        output_file: Archivo de salida
        create_backups: Si se deben crear backups automáticamente
    """
    print("\n🔄 Fusionando datasets...")
    print("=" * 60)
    
    # Crear backups si se solicita
    if create_backups:
        for file_path in input_files:
            if file_path.exists():
                try:
                    create_backup(file_path)
                except Exception as e:
                    print(f"⚠ No se pudo crear backup de {file_path}: {e}")
    
    # Leer todas las entradas
    all_entries = []
    seen_texts: Set[str] = set()
    total_malformed = 0
    
    for file_path in input_files:
        print(f"\n📖 Leyendo: {file_path}")
        
        if not file_path.exists():
            print(f"  ⚠ Archivo no encontrado, omitiendo...")
            continue
        
        entries, malformed_lines = read_jsonl(file_path)
        
        print(f"  ✓ Entradas leídas: {len(entries)}")
        
        if malformed_lines:
            print(f"  ⚠ Líneas malformadas ignoradas: {len(malformed_lines)}")
            total_malformed += len(malformed_lines)
        
        # Deduplicar basándose en el campo 'text'
        duplicates = 0
        for entry in entries:
            text = entry.get('text', '')
            if text and text not in seen_texts:
                seen_texts.add(text)
                all_entries.append(entry)
            else:
                duplicates += 1
        
        if duplicates > 0:
            print(f"  🔍 Duplicados encontrados: {duplicates}")
    
    # Escribir resultado
    print(f"\n💾 Escribiendo resultado a: {output_file}")
    write_jsonl(output_file, all_entries)
    
    print(f"\n✅ Fusión completada:")
    print(f"  - Total de entradas únicas: {len(all_entries)}")
    print(f"  - Líneas malformadas ignoradas: {total_malformed}")
    print(f"  - Archivo de salida: {output_file}")


def count_entries(file_path: Path) -> None:
    """
    Cuenta y muestra el número de entradas válidas.
    
    Args:
        file_path: Ruta del archivo a contar
    """
    if not file_path.exists():
        print(f"❌ Archivo no encontrado: {file_path}")
        return
    
    entries, malformed_lines = read_jsonl(file_path)
    
    print(f"\n📊 {file_path}")
    print(f"  Entradas válidas: {len(entries)}")
    if malformed_lines:
        print(f"  Líneas malformadas: {len(malformed_lines)}")


def show_tail(file_path: Path, n: int = 5) -> None:
    """
    Muestra las últimas N entradas del dataset.
    
    Args:
        file_path: Ruta del archivo
        n: Número de entradas a mostrar
    """
    if not file_path.exists():
        print(f"❌ Archivo no encontrado: {file_path}")
        return
    
    entries, _ = read_jsonl(file_path)
    
    if not entries:
        print(f"\n⚠ No hay entradas en {file_path}")
        return
    
    print(f"\n📄 Últimas {min(n, len(entries))} entradas de {file_path}:")
    print("=" * 60)
    
    for i, entry in enumerate(entries[-n:], start=1):
        print(f"\n[{i}]")
        print(json.dumps(entry, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="Gestor de datasets JSONL para proyecto_vacantes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s backup data/training_data.jsonl
  %(prog)s validate data/training_data.jsonl
  %(prog)s merge data/training_data.jsonl venv/data/training_data.jsonl -o data/training_data.jsonl
  %(prog)s count data/training_data.jsonl
  %(prog)s tail data/training_data.jsonl -n 3
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Comando: backup
    backup_parser = subparsers.add_parser('backup', help='Crear backup de un dataset')
    backup_parser.add_argument('file', type=Path, help='Archivo a respaldar')
    backup_parser.add_argument('--backup-dir', type=Path, default=Path('backups'),
                              help='Directorio para backups (default: backups/)')
    
    # Comando: validate
    validate_parser = subparsers.add_parser('validate', help='Validar un dataset')
    validate_parser.add_argument('file', type=Path, help='Archivo a validar')
    
    # Comando: merge
    merge_parser = subparsers.add_parser('merge', help='Fusionar y deduplicar datasets')
    merge_parser.add_argument('files', type=Path, nargs='+', help='Archivos a fusionar')
    merge_parser.add_argument('-o', '--output', type=Path, required=True,
                            help='Archivo de salida')
    merge_parser.add_argument('--no-backup', action='store_true',
                            help='No crear backups automáticamente')
    
    # Comando: count
    count_parser = subparsers.add_parser('count', help='Contar entradas')
    count_parser.add_argument('file', type=Path, help='Archivo a contar')
    
    # Comando: tail
    tail_parser = subparsers.add_parser('tail', help='Mostrar últimas entradas')
    tail_parser.add_argument('file', type=Path, help='Archivo a mostrar')
    tail_parser.add_argument('-n', type=int, default=5, help='Número de entradas (default: 5)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'backup':
            create_backup(args.file, args.backup_dir)
        
        elif args.command == 'validate':
            validate_dataset(args.file)
        
        elif args.command == 'merge':
            merge_datasets(args.files, args.output, not args.no_backup)
        
        elif args.command == 'count':
            count_entries(args.file)
        
        elif args.command == 'tail':
            show_tail(args.file, args.n)
    
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
