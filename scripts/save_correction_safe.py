#!/usr/bin/env python3
"""
Safe Correction Saver

This module provides a safe way to save corrections to the training data file,
ensuring that the data is always written to the correct location (data/training_data.jsonl)
and not to the venv directory or other incorrect locations.

Features:
- Always uses absolute paths relative to project root
- Validates data before writing
- Creates automatic backups
- Handles errors gracefully
- Thread-safe file operations

Usage:
    from save_correction_safe import save_correction
    
    # Save a single correction
    save_correction("Sample vacancy text here")
    
    # Save multiple corrections
    corrections = [
        "Vacancy 1 text",
        "Vacancy 2 text"
    ]
    save_corrections(corrections)
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Union, List, Dict
import threading
import shutil

# Thread lock for file operations
_file_lock = threading.Lock()


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    This function determines the project root by walking up from the script
    location until it finds the project markers (data/, scripts/, README.md).
    """
    # Start from script directory
    current_dir = Path(__file__).parent.resolve()
    
    # Walk up to find project root
    for parent in [current_dir] + list(current_dir.parents):
        # Check for project markers
        if (parent / "data").exists() and (parent / "scripts").exists():
            return parent
    
    # Fallback: assume script is in scripts/ folder
    return current_dir.parent


def get_training_data_path() -> Path:
    """
    Get the absolute path to the training data file.
    
    Returns:
        Path to data/training_data.jsonl (absolute)
    """
    project_root = get_project_root()
    return project_root / "data" / "training_data.jsonl"


def create_backup(file_path: Path) -> Path:
    """
    Create a timestamped backup of the training data file.
    
    Args:
        file_path: Path to the file to backup
    
    Returns:
        Path to the created backup file
    """
    if not file_path.exists():
        return None
    
    project_root = get_project_root()
    backup_dir = project_root / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}.bak"
    backup_path = backup_dir / backup_name
    
    shutil.copy2(file_path, backup_path)
    
    return backup_path


def validate_entry(entry: Union[str, Dict]) -> Dict:
    """
    Validate and normalize an entry.
    
    Args:
        entry: Entry to validate (string or dict)
    
    Returns:
        Normalized entry dict with 'text' field
    
    Raises:
        ValueError: If entry is invalid
    """
    if isinstance(entry, str):
        if not entry.strip():
            raise ValueError("Entry text cannot be empty")
        return {"text": entry.strip()}
    
    elif isinstance(entry, dict):
        if 'text' not in entry:
            raise ValueError("Entry dict must have 'text' field")
        if not isinstance(entry['text'], str):
            raise ValueError("Entry 'text' field must be a string")
        if not entry['text'].strip():
            raise ValueError("Entry text cannot be empty")
        return entry
    
    else:
        raise ValueError(f"Entry must be string or dict, got {type(entry)}")


def read_existing_entries(file_path: Path) -> List[Dict]:
    """
    Read existing entries from the training data file.
    
    Args:
        file_path: Path to the JSONL file
    
    Returns:
        List of existing entries
    """
    if not file_path.exists():
        return []
    
    entries = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            
            try:
                entry = json.loads(line)
                entries.append(entry)
            except json.JSONDecodeError:
                print(f"⚠ Warning: Skipping malformed line {line_num}", file=sys.stderr)
    
    return entries


def write_entries(file_path: Path, entries: List[Dict]) -> None:
    """
    Write entries to the training data file.
    
    Args:
        file_path: Path to the JSONL file
        entries: List of entries to write
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def save_correction(text: str, create_backup_flag: bool = True, deduplicate: bool = True) -> bool:
    """
    Save a single correction to the training data file.
    
    Args:
        text: Text to save
        create_backup_flag: Whether to create a backup before writing
        deduplicate: Whether to check for duplicates
    
    Returns:
        True if saved successfully, False otherwise
    """
    return save_corrections([text], create_backup_flag, deduplicate)


def save_corrections(texts: List[Union[str, Dict]], 
                     create_backup_flag: bool = True, 
                     deduplicate: bool = True) -> bool:
    """
    Save multiple corrections to the training data file.
    
    This function is thread-safe and ensures that data is always written
    to the correct location.
    
    Args:
        texts: List of texts or entry dicts to save
        create_backup_flag: Whether to create a backup before writing
        deduplicate: Whether to check for duplicates
    
    Returns:
        True if saved successfully, False otherwise
    """
    with _file_lock:
        try:
            # Get the correct path
            file_path = get_training_data_path()
            
            # Validate entries
            new_entries = []
            for text in texts:
                try:
                    entry = validate_entry(text)
                    new_entries.append(entry)
                except ValueError as e:
                    print(f"⚠ Warning: Skipping invalid entry: {e}", file=sys.stderr)
            
            if not new_entries:
                print("❌ Error: No valid entries to save", file=sys.stderr)
                return False
            
            # Read existing entries
            existing_entries = read_existing_entries(file_path)
            
            # Create backup if file exists and backup is requested
            if create_backup_flag and file_path.exists():
                backup_path = create_backup(file_path)
                if backup_path:
                    print(f"✓ Backup created: {backup_path}")
            
            # Deduplicate if requested
            if deduplicate:
                existing_texts = set(e.get('text', '').strip() for e in existing_entries)
                original_count = len(new_entries)
                new_entries = [e for e in new_entries if e['text'].strip() not in existing_texts]
                
                duplicates = original_count - len(new_entries)
                if duplicates > 0:
                    print(f"ℹ Skipped {duplicates} duplicate(s)")
            
            if not new_entries:
                print("ℹ All entries already exist, nothing to save")
                return True
            
            # Append new entries
            all_entries = existing_entries + new_entries
            
            # Write to file
            write_entries(file_path, all_entries)
            
            print(f"✓ Saved {len(new_entries)} correction(s) to: {file_path}")
            print(f"  Total entries in file: {len(all_entries)}")
            
            return True
        
        except Exception as e:
            print(f"❌ Error saving corrections: {e}", file=sys.stderr)
            return False


def get_stats() -> Dict:
    """
    Get statistics about the training data file.
    
    Returns:
        Dict with statistics
    """
    file_path = get_training_data_path()
    
    if not file_path.exists():
        return {
            'exists': False,
            'path': str(file_path),
            'entry_count': 0,
            'file_size_mb': 0
        }
    
    entries = read_existing_entries(file_path)
    file_size = file_path.stat().st_size
    
    return {
        'exists': True,
        'path': str(file_path),
        'entry_count': len(entries),
        'file_size_mb': file_size / (1024 * 1024)
    }


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Safely save corrections to training data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --text "Sample vacancy description"
  %(prog)s --file corrections.txt
  %(prog)s --stats
        """
    )
    
    parser.add_argument('--text', help='Single text to save')
    parser.add_argument('--file', type=Path, help='File with texts (one per line)')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup')
    parser.add_argument('--allow-duplicates', action='store_true', help='Allow duplicate entries')
    
    args = parser.parse_args()
    
    # Show stats
    if args.stats:
        stats = get_stats()
        print("\nTraining Data Statistics:")
        print("=" * 60)
        print(f"  Path: {stats['path']}")
        print(f"  Exists: {'Yes' if stats['exists'] else 'No'}")
        print(f"  Entries: {stats['entry_count']}")
        print(f"  Size: {stats['file_size_mb']:.2f} MB")
        return
    
    # Save text
    if args.text:
        success = save_correction(args.text, not args.no_backup, not args.allow_duplicates)
        sys.exit(0 if success else 1)
    
    # Save from file
    elif args.file:
        if not args.file.exists():
            print(f"❌ Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        
        with open(args.file, 'r', encoding='utf-8') as f:
            texts = [line.strip() for line in f if line.strip()]
        
        if not texts:
            print("❌ Error: No valid texts in file", file=sys.stderr)
            sys.exit(1)
        
        success = save_corrections(texts, not args.no_backup, not args.allow_duplicates)
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
