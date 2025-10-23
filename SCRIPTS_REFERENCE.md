# Scripts Quick Reference

Quick reference guide for all dataset management utilities in the proyecto_vacantes repository.

## Table of Contents
- [PowerShell Scripts (Windows)](#powershell-scripts-windows)
- [Python Scripts (Cross-platform)](#python-scripts-cross-platform)
- [Common Workflows](#common-workflows)
- [Safety Checklist](#safety-checklist)

---

## PowerShell Scripts (Windows)

### merge_training_data.ps1

**Purpose**: Merge and deduplicate multiple JSONL files

#### Basic Usage
```powershell
# Preview merge (no changes)
.\scripts\merge_training_data.ps1 -DryRun

# Execute merge with defaults
.\scripts\merge_training_data.ps1

# Specify source files
.\scripts\merge_training_data.ps1 -SourceFiles "data\training_data.jsonl","venv\data\training_data.jsonl" -OutputFile "data\training_data.jsonl"

# Merge and move venv file with confirmation
.\scripts\merge_training_data.ps1 -ConfirmMove
```

#### Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `-DryRun` | Switch | - | Preview without changes |
| `-SourceFiles` | String[] | data\, venv\data\ | Files to merge |
| `-OutputFile` | String | data\training_data.jsonl | Output file path |
| `-ConfirmMove` | Switch | - | Move venv file after merge |

#### Output
- ✅ Merged JSONL file
- 📁 Timestamped backups in `backups/`
- 📝 Invalid lines log in `data/training_data.invalid_lines.log`

---

### dedupe_clean.ps1

**Purpose**: Remove duplicates and clean JSONL file

#### Basic Usage
```powershell
# Preview cleaning (no changes)
.\scripts\dedupe_clean.ps1 -InputFile "data\training_data.jsonl" -DryRun

# Clean with defaults (removes duplicates, keeps texts >= 10 chars)
.\scripts\dedupe_clean.ps1 -InputFile "data\training_data.jsonl"

# Aggressive cleaning
.\scripts\dedupe_clean.ps1 -InputFile "data\training_data.jsonl" -MinTextLength 20 -RemoveEmpty
```

#### Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `-InputFile` | String | data\training_data.jsonl | Input file path |
| `-OutputFile` | String | (same as input) | Output file path |
| `-DryRun` | Switch | - | Preview without changes |
| `-MinTextLength` | Int | 10 | Minimum text length to keep |
| `-RemoveEmpty` | Switch | - | Remove empty/whitespace texts |

#### Output
- ✅ Cleaned JSONL file
- 📁 Timestamped backup in `backups/`
- 📊 Reduction statistics

---

## Python Scripts (Cross-platform)

### save_correction_safe.py

**Purpose**: Safely save corrections to training data (always uses correct path)

#### Basic Usage
```bash
# Save single correction
python scripts/save_correction_safe.py --text "Vacancy description here"

# Save from file (one entry per line)
python scripts/save_correction_safe.py --file corrections.txt

# View statistics
python scripts/save_correction_safe.py --stats

# Allow duplicates (no deduplication)
python scripts/save_correction_safe.py --text "Text" --allow-duplicates

# Skip backup
python scripts/save_correction_safe.py --text "Text" --no-backup
```

#### As Python Module
```python
from scripts.save_correction_safe import save_correction, save_corrections, get_training_data_path

# Get correct path
path = get_training_data_path()
print(path)  # /absolute/path/to/data/training_data.jsonl

# Save one
save_correction("Vacancy text")

# Save multiple
save_corrections(["Text 1", "Text 2", "Text 3"])
```

#### Options
| Option | Description |
|--------|-------------|
| `--text TEXT` | Single text to save |
| `--file FILE` | File with texts (one per line) |
| `--stats` | Show statistics |
| `--no-backup` | Skip backup creation |
| `--allow-duplicates` | Don't check for duplicates |

---

### dataset_manager.py

**Purpose**: Comprehensive dataset management tool

#### Commands

##### backup
```bash
python scripts/dataset_manager.py backup data/training_data.jsonl
python scripts/dataset_manager.py backup data/training_data.jsonl --backup-dir my_backups/
```

##### validate
```bash
python scripts/dataset_manager.py validate data/training_data.jsonl
```
Shows: entry count, malformed lines, text length statistics, last 3 entries

##### merge
```bash
python scripts/dataset_manager.py merge data/training_data.jsonl venv/data/training_data.jsonl -o data/training_data.jsonl
python scripts/dataset_manager.py merge file1.jsonl file2.jsonl file3.jsonl -o merged.jsonl --no-backup
```

##### count
```bash
python scripts/dataset_manager.py count data/training_data.jsonl
```

##### tail
```bash
python scripts/dataset_manager.py tail data/training_data.jsonl -n 5
python scripts/dataset_manager.py tail data/training_data.jsonl -n 10
```

---

### summarize_sumy.py

**Purpose**: Reduce file size using extractive text summarization

#### Requirements
```bash
pip install sumy nltk
python -m nltk.downloader punkt
```

#### Basic Usage
```bash
# Preview summarization (no changes)
python scripts/summarize_sumy.py data/training_data.jsonl --dry-run

# Reduce to target size
python scripts/summarize_sumy.py data/training_data.jsonl --target-size-mb 5

# Control sentence count
python scripts/summarize_sumy.py data/training_data.jsonl --max-sentences 3

# Use different algorithm
python scripts/summarize_sumy.py data/training_data.jsonl --algorithm luhn --max-sentences 2

# Skip backup
python scripts/summarize_sumy.py data/training_data.jsonl --no-backup
```

#### Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_file` | Path | required | Input JSONL file |
| `-o, --output` | Path | (same as input) | Output file |
| `--max-sentences` | Int | 3 | Sentences per summary |
| `--target-size-mb` | Float | - | Target file size |
| `--algorithm` | String | lsa | lsa or luhn |
| `--dry-run` | Flag | - | Preview only |
| `--no-backup` | Flag | - | Skip backup |

---

### verify_setup.py

**Purpose**: Verify project configuration

#### Usage
```bash
python scripts/verify_setup.py
```

#### Checks
- ✓ Directory structure (data/, scripts/)
- ✓ No datasets in wrong locations (venv/data/)
- ✓ .gitignore configured
- ✓ Required scripts present

---

## Common Workflows

### Workflow 1: First-Time Setup

```bash
# 1. Verify setup
python scripts/verify_setup.py

# 2. If all good, start using the tools
python scripts/save_correction_safe.py --stats
```

### Workflow 2: Migrate from venv/data/

```powershell
# 1. Preview merge
.\scripts\merge_training_data.ps1 -DryRun

# 2. Review output, then execute
.\scripts\merge_training_data.ps1

# 3. Validate result
python scripts/dataset_manager.py validate data/training_data.jsonl

# 4. Move old file (manual confirmation)
Move-Item venv\data\training_data.jsonl venv\data\training_data.jsonl.moved
```

### Workflow 3: Regular Maintenance

```bash
# 1. Create backup
python scripts/dataset_manager.py backup data/training_data.jsonl

# 2. Validate
python scripts/dataset_manager.py validate data/training_data.jsonl

# 3. If needed, clean duplicates
# (Use PowerShell if on Windows, Python if cross-platform)
python scripts/dataset_manager.py merge data/training_data.jsonl -o data/training_data.jsonl
```

### Workflow 4: Reduce File Size

```bash
# 1. Check current size
python scripts/save_correction_safe.py --stats

# 2. Preview reduction
python scripts/summarize_sumy.py data/training_data.jsonl --target-size-mb 5 --dry-run

# 3. Execute if satisfied
python scripts/summarize_sumy.py data/training_data.jsonl --target-size-mb 5

# 4. Validate result
python scripts/dataset_manager.py validate data/training_data.jsonl
```

### Workflow 5: Save New Corrections Safely

```python
# In your Python script
import sys
sys.path.append('.')  # if not already in path

from scripts.save_correction_safe import save_correction

# Your data extraction code here
vacancy_text = "Job description..."

# Save safely (always writes to correct location)
save_correction(vacancy_text)
```

---

## Safety Checklist

Before modifying production data:

- [ ] Run with `-DryRun` or `--dry-run` first
- [ ] Review the preview output carefully
- [ ] Verify backup creation is enabled
- [ ] Check available disk space
- [ ] Test with a small sample file first
- [ ] Document the operation in your notes
- [ ] Have a rollback plan ready

### Rollback Procedure

If something goes wrong:

```powershell
# Windows
Get-ChildItem backups\*.bak | Sort-Object LastWriteTime -Descending | Select-Object -First 5
Copy-Item backups\training_data_YYYYMMDD_HHMMSS.jsonl.bak data\training_data.jsonl -Force
```

```bash
# Linux/Mac
ls -lt backups/*.bak | head -5
cp backups/training_data_YYYYMMDD_HHMMSS.jsonl.bak data/training_data.jsonl
```

### Best Practices

1. **Always backup**: Use scripts with backup enabled (default)
2. **Use dry-run**: Preview changes before executing
3. **Validate results**: Run `validate` after modifications
4. **Keep backups**: Don't delete backups for at least 30 days
5. **Test first**: Use sample/test files before production
6. **Document changes**: Note what you did and when
7. **Check logs**: Review invalid_lines.log if present

---

## Troubleshooting

### Common Issues

**"File not found"**
- Ensure you're running from project root
- Check file path is correct
- Verify file actually exists

**"Permission denied"**
```bash
# Make scripts executable (Linux/Mac)
chmod +x scripts/*.py
```

**"Invalid JSON"**
- Check file encoding (should be UTF-8)
- Look at the invalid_lines.log
- Validate individual lines with JSON checker

**"PowerShell execution policy"**
```powershell
# Temporary bypass (current session)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**"Module not found"**
```bash
# For summarize_sumy.py
pip install sumy nltk
python -m nltk.downloader punkt
```

---

## Getting Help

### Script Help
```bash
# Python scripts
python scripts/save_correction_safe.py --help
python scripts/dataset_manager.py --help
python scripts/dataset_manager.py merge --help

# PowerShell scripts
Get-Help .\scripts\merge_training_data.ps1
Get-Help .\scripts\merge_training_data.ps1 -Examples
Get-Help .\scripts\dedupe_clean.ps1 -Detailed
```

### Documentation
- `README.md` - Main documentation with usage examples
- `MIGRATION_GUIDE.md` - Step-by-step migration instructions
- `TESTING_VALIDATION.md` - Testing report and validation
- `SCRIPTS_REFERENCE.md` - This quick reference guide

### Support
Create an issue in the repository with:
- Command you ran
- Error message
- Output from `python scripts/verify_setup.py`
- Your OS and PowerShell/Python version
