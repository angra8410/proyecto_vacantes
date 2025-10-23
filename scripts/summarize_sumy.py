#!/usr/bin/env python3
"""
Extractive Text Summarization Tool

This script provides extractive summarization for JSONL training data files,
reducing file size while preserving key information. It uses the sumy library
for summarization.

Features:
- Extractive summarization using LSA or Luhn algorithms
- Preserves original JSONL structure
- Automatic backups before modification
- Target size or sentence count control
- Dry-run mode for preview

Requirements:
    pip install sumy nltk

Usage:
    python summarize_sumy.py data/training_data.jsonl --target-size-mb 5
    python summarize_sumy.py data/training_data.jsonl --max-sentences 3 --dry-run
"""

import json
import sys
import argparse
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import shutil

# Check for required libraries
try:
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lsa import LsaSummarizer
    from sumy.summarizers.luhn import LuhnSummarizer
    from sumy.nlp.stemmers import Stemmer
    from sumy.utils import get_stop_words
except ImportError:
    print("Error: Required libraries not found.")
    print("Please install: pip install sumy nltk")
    print("\nAfter installing sumy, you may need to download NLTK data:")
    print("  python -m nltk.downloader punkt")
    sys.exit(1)


def get_project_root() -> Path:
    """Get the project root directory."""
    # Assume script is in scripts/ folder
    script_dir = Path(__file__).parent
    return script_dir.parent


def create_backup(file_path: Path) -> Path:
    """Create a timestamped backup of the file."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    project_root = get_project_root()
    backup_dir = project_root / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}.bak"
    backup_path = backup_dir / backup_name
    
    shutil.copy2(file_path, backup_path)
    print(f"✓ Backup created: {backup_path}")
    
    return backup_path


def read_jsonl(file_path: Path) -> List[Dict]:
    """Read JSONL file and return valid entries."""
    entries = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            
            try:
                entry = json.loads(line)
                entries.append(entry)
            except json.JSONDecodeError as e:
                print(f"⚠ Warning: Skipping malformed line {line_num}: {e}")
    
    return entries


def write_jsonl(file_path: Path, entries: List[Dict]) -> None:
    """Write entries to JSONL file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def get_file_size_mb(file_path: Path) -> float:
    """Get file size in megabytes."""
    return file_path.stat().st_size / (1024 * 1024)


def summarize_text(text: str, max_sentences: int = 3, algorithm: str = 'lsa', language: str = 'english') -> str:
    """
    Summarize text using extractive summarization.
    
    Args:
        text: Input text to summarize
        max_sentences: Maximum number of sentences in summary
        algorithm: 'lsa' or 'luhn'
        language: Language for tokenization
    
    Returns:
        Summarized text
    """
    if not text or len(text.strip()) < 50:
        return text
    
    try:
        # Create parser and tokenizer
        parser = PlaintextParser.from_string(text, Tokenizer(language))
        
        # Choose summarizer
        stemmer = Stemmer(language)
        if algorithm == 'lsa':
            summarizer = LsaSummarizer(stemmer)
        else:
            summarizer = LuhnSummarizer(stemmer)
        
        summarizer.stop_words = get_stop_words(language)
        
        # Generate summary
        summary_sentences = summarizer(parser.document, max_sentences)
        summary = ' '.join([str(sentence) for sentence in summary_sentences])
        
        return summary if summary else text
    
    except Exception as e:
        print(f"⚠ Warning: Summarization failed: {e}")
        return text


def summarize_entries(entries: List[Dict], max_sentences: int = 3, algorithm: str = 'lsa') -> List[Dict]:
    """
    Apply summarization to all entries.
    
    Args:
        entries: List of JSONL entries
        max_sentences: Maximum sentences per summary
        algorithm: Summarization algorithm
    
    Returns:
        List of entries with summarized text
    """
    summarized = []
    
    for i, entry in enumerate(entries, start=1):
        if 'text' not in entry:
            summarized.append(entry)
            continue
        
        original_text = entry['text']
        summarized_text = summarize_text(original_text, max_sentences, algorithm)
        
        # Create new entry with summarized text
        new_entry = entry.copy()
        new_entry['text'] = summarized_text
        summarized.append(new_entry)
        
        if i % 10 == 0 or i == len(entries):
            print(f"  Progress: {i}/{len(entries)} entries processed", end='\r')
    
    print()  # New line after progress
    return summarized


def calculate_compression_stats(original_entries: List[Dict], summarized_entries: List[Dict]) -> Dict:
    """Calculate compression statistics."""
    original_chars = sum(len(e.get('text', '')) for e in original_entries)
    summarized_chars = sum(len(e.get('text', '')) for e in summarized_entries)
    
    compression_ratio = (1 - summarized_chars / original_chars) * 100 if original_chars > 0 else 0
    
    return {
        'original_chars': original_chars,
        'summarized_chars': summarized_chars,
        'compression_ratio': compression_ratio
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extractive summarization for JSONL training data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data/training_data.jsonl --target-size-mb 5
  %(prog)s data/training_data.jsonl --max-sentences 3 --dry-run
  %(prog)s data/training_data.jsonl --algorithm luhn --max-sentences 2

Algorithms:
  lsa  - Latent Semantic Analysis (default, usually better)
  luhn - Luhn algorithm (faster, simpler)
        """
    )
    
    parser.add_argument('input_file', type=Path, help='Input JSONL file')
    parser.add_argument('-o', '--output', type=Path, help='Output file (default: overwrite input)')
    parser.add_argument('--max-sentences', type=int, default=3,
                       help='Maximum sentences per summary (default: 3)')
    parser.add_argument('--target-size-mb', type=float,
                       help='Target file size in MB (overrides max-sentences)')
    parser.add_argument('--algorithm', choices=['lsa', 'luhn'], default='lsa',
                       help='Summarization algorithm (default: lsa)')
    parser.add_argument('--language', default='english',
                       help='Language for tokenization (default: english)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview without making changes')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip creating backup')
    
    args = parser.parse_args()
    
    # Resolve paths
    if not args.input_file.is_absolute():
        args.input_file = get_project_root() / args.input_file
    
    if args.output:
        if not args.output.is_absolute():
            args.output = get_project_root() / args.output
    else:
        args.output = args.input_file
    
    # Header
    print("=" * 70)
    print("Extractive Text Summarization Tool")
    print("=" * 70)
    print()
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print()
    
    # Check input file
    if not args.input_file.exists():
        print(f"❌ Error: Input file not found: {args.input_file}")
        sys.exit(1)
    
    # Display configuration
    print("Configuration:")
    print(f"  Input file: {args.input_file}")
    print(f"  Output file: {args.output}")
    print(f"  Algorithm: {args.algorithm}")
    print(f"  Max sentences: {args.max_sentences}")
    if args.target_size_mb:
        print(f"  Target size: {args.target_size_mb} MB")
    print()
    
    # Read entries
    print("Reading input file...")
    original_entries = read_jsonl(args.input_file)
    original_size_mb = get_file_size_mb(args.input_file)
    
    print(f"  Entries: {len(original_entries)}")
    print(f"  Original size: {original_size_mb:.2f} MB")
    print()
    
    # Adjust max_sentences based on target size
    max_sentences = args.max_sentences
    if args.target_size_mb and original_size_mb > args.target_size_mb:
        # Estimate sentences needed
        size_ratio = args.target_size_mb / original_size_mb
        max_sentences = max(1, int(args.max_sentences * size_ratio))
        print(f"ℹ Adjusted max sentences to {max_sentences} to reach target size")
        print()
    
    # Summarize
    print("Summarizing entries...")
    summarized_entries = summarize_entries(original_entries, max_sentences, args.algorithm)
    print()
    
    # Calculate stats
    stats = calculate_compression_stats(original_entries, summarized_entries)
    
    print("Statistics:")
    print(f"  Original characters: {stats['original_chars']:,}")
    print(f"  Summarized characters: {stats['summarized_chars']:,}")
    print(f"  Compression: {stats['compression_ratio']:.1f}%")
    print()
    
    # Estimate output size
    estimated_size_mb = original_size_mb * (stats['summarized_chars'] / stats['original_chars'])
    print(f"Estimated output size: {estimated_size_mb:.2f} MB")
    print()
    
    # Dry run: stop here
    if args.dry_run:
        print("Dry run complete. Run without --dry-run to apply changes.")
        sys.exit(0)
    
    # Create backup
    if not args.no_backup and args.output == args.input_file:
        print("Creating backup...")
        create_backup(args.input_file)
        print()
    
    # Write output
    print("Writing output file...")
    write_jsonl(args.output, summarized_entries)
    
    final_size_mb = get_file_size_mb(args.output)
    print(f"✓ Output written: {args.output}")
    print(f"  Final size: {final_size_mb:.2f} MB")
    print()
    
    print("=" * 70)
    print("✅ Summarization completed successfully!")
    print("=" * 70)


if __name__ == '__main__':
    main()
