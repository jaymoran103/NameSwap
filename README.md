# NameSwap

NameSwap is a Python tool for anonymizing CSV data, replacing name strings with randomized alternatives. NameSwap maintains a map of renamings, ensuring that swaps are consistent across a data set, and cross-checking operations will peform as they would for the original data.

## Features

- **Batch Processing**: Process multiple files with a single command
- **Flexible Parsing**: Tokenizes name strings, ensuring cells containing mutliple names will handle each individually. Can be toggled off
- **Format Preservation**: Maintains CSV structure, quoting style, and delimiters
- **Smart Name Detection**: Can automatically detects name columns, in addition to manually specified headers. Matches headers regardless of capitalization.
- **Deterministic Mapping**: Supports use of seeds for consistent name replacements across runs

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/nameswap.git
cd nameswap

# Install dependencies. For a self-contained version that includes a name bank, contact me with the info below!
pip install faker
```

## Quick Start

```bash
# Basic usage: anonymize names in specific columns
python3 nameswap.py -f data.csv -c "First Name" -c "Last Name"

# Use auto-detection to find name columns
python3 nameswap.py -f data.csv --autocolumns

# Process multiple files at once
python3 nameswap.py -f file1.csv -f file2.csv -c "Name"

# Use a seed for consistent results
python3 nameswap.py -f data.csv -c "Name" -s myseed123
```

## Usage

### Basic Syntax

```bash
python3 nameswap.py [-f <file>] [-c <column>] [options]
```
### Input Flags

- `-f <file>` - Specify CSV file(s) to process (required, can use multiple times)
- `-c <column>` - Specify column(s) to anonymize (can use multiple times)
- `-p <prefix>` - Set output file prefix (default: "renamed")
- `-s <seed>` - Set seed for deterministic name generation

### Option Flags

- `--help` - Display basic help information
- `--menu` - Display detailed menu with all flags and options
- `--skip` - Skip user confirmation step before processing
- `--autocolumns` - Auto-detect columns containing "name"
- `--defaultcolumns` - Apply default column set
- `--renamewholecells` - Apply renaming to entire cells without parsing (use with caution)

## Advanced Usage

### Seed Selection

Nameswap picks names randomly by default. Using -s <seedtext> ensures a consistent queue of names to assign while processing a csv batch. If the same sequence of names is provided as input, the same name mappings will occur. This is helpful for comparing results across file batches, but relies on the same sequence of given inputs to generate consistent results. If you're interested in a version of this tool that saves mappings and config info in a local file for continued use, contact me with the information below!

### Whole Cell Renaming

By default, NameSwap parses names intelligently (handling spaces, commas, hyphens). This ensures cells containing multiple names ("Lastname, FirstName" or "Name Hypen-Ated") are handled accordingly, with syntax and contextual relationships preserved.

To disable this feature, use `--renamewholecells`. 

```bash
python3 nameswap.py -f data.csv -c "Name" --renamewholecells
```
**Note**: Use this feature with caution. This flag treats entire cells as single names, and may mean the loss of internal syntax or relationships between name components, depending on your use case.

### File Naming

Nameswap adds the prefix "renamed-" to output files by default. Using -p <prefixtext> results in output

data.csv -> prefixtext-data.csv 

The hyphen is added automatically, so a file can't be overwritten by itself, but repeated use will mean overwriting the renamed version as long as the prefix and filename remain the same.
```bash
python3 nameswap.py -f data.csv -c "Name" --skip
```
**Note**: Use this feature with caution. The confirmation step prints the files and columns set to be processed, and skipping could lead to the overwriting or problematic modification of output files. As renamed files are written as copies with a prefix, original files should be difficult to overwrite by accident.

### Skipping Confirmation

By default, NameSwap prints its configration information and waits for manual approval to execute. Using --skip makes execution happen as soon as inputs are verified, only stopping if inputs are insufficient or a file exception occurs. Use with caution if you need to keep recent outputs.

## Author

Created by Jay Moran in November 2025.
jaymorandev@gmail.com
github.com/jaymoran103
linkedin.com/in/jaymorandev