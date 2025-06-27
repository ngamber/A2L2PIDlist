# A2L to PID List Converter

A Python-based tool for converting A2L (ASAM MCD-2 MC) files to PID lists for automotive tuning applications.

## Features

- **Robust A2L Parsing**: Uses the `pya2l` library for standards-compliant A2L file parsing
- **Fallback Support**: Falls back to manual parsing if pya2l fails
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Batch Processing**: Process multiple A2L files at once
- **Virtual Environment Support**: Can work with Python virtual environments
- **Dry-Run Mode**: Preview operations without executing
- **Automatic Dependency Management**: Automatically installs required dependencies

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

### Quick Start

1. Clone or download this repository
2. Run the processor (dependencies will be installed automatically):
   ```bash
   python run.py --dry-run
   ```

### Manual Installation

If you prefer to install dependencies manually:

```bash
pip install -r requirements.txt
```

Or install pya2l directly:

```bash
pip install pya2l>=0.1.10
```

## Usage

### Basic Usage

```bash
# Process all A2L files in the input directory
python run.py

# Preview what would be processed (dry-run mode)
python run.py --dry-run

# Use custom directories
python run.py --input-dir /path/to/a2l/files --output-dir /path/to/output

# Use custom template file
python run.py --template custom_pidlist.csv
```

### Advanced Usage

```bash
# Use with virtual environment
python run.py --venv ./venv

# Combine multiple options
python run.py --input-dir data/ --output-dir results/ --template custom.csv --dry-run
```

### Direct Script Usage

You can also use the a2l2pid.py script directly:

```bash
python a2l2pid.py input_file.a2l pidlist.csv output_file.csv
```

## File Structure

```
A2L2PIDlist/
├── run.py              # Main wrapper script
├── a2l2pid.py          # Core A2L processing script
├── requirements.txt    # Python dependencies
├── pidlist.csv         # Template PID list
├── input/              # Directory for A2L files (auto-created)
├── output/             # Directory for output CSV files
└── README.md           # This file
```

## How It Works

1. **A2L Parsing**: The script uses `pya2l` to parse A2L files into a structured format
2. **Data Extraction**: Extracts measurements and characteristics with their addresses, units, and limits
3. **Template Matching**: Matches extracted data with entries in the template CSV file
4. **Output Generation**: Creates CSV files compatible with tuning software

## Template CSV Format

The template CSV file should contain the following columns:

- `Name`: Parameter name to match in A2L file
- `Unit`: Measurement unit
- `Equation`: Conversion equation
- `Format`: Display format
- `Address`: Memory address (populated from A2L)
- `Length`: Data length
- `Signed`: Whether the value is signed
- `ProgMin`/`ProgMax`: Programming limits
- `WarnMin`/`WarnMax`: Warning limits
- `Smoothing`: Smoothing factor
- `Enabled`: Whether parameter is enabled
- `Tabs`: Tab assignment
- `Assign To`: Assignment information

## Improvements Over Original

The new pya2l-based implementation provides several advantages over the original manual parsing:

### Robust Parsing
- **Standards Compliant**: Full ASAM MCD-2 MC standard support
- **Error Handling**: Better error messages and recovery
- **Complex Structures**: Handles nested and complex A2L structures

### Enhanced Data Extraction
- **Rich Metadata**: Extracts units, limits, data types, and descriptions
- **Multiple Sources**: Processes both measurements and characteristics
- **Flexible Addressing**: Handles various address formats and locations

### Reliability
- **Fallback Support**: Falls back to original parsing if pya2l fails
- **Input Validation**: Validates files and paths before processing
- **Progress Reporting**: Clear progress indication and error reporting

## Troubleshooting

### Common Issues

1. **pya2l Installation Fails**
   ```bash
   # Try upgrading pip first
   python -m pip install --upgrade pip
   pip install pya2l>=0.1.10
   ```

2. **A2L File Not Parsing**
   - The script will automatically fall back to manual parsing
   - Check the console output for specific error messages

3. **No Matches Found**
   - Verify that parameter names in the template CSV match those in the A2L file
   - Check that the A2L file contains the expected measurements/characteristics

### Debug Mode

For detailed debugging, run the a2l2pid.py script directly:

```bash
python a2l2pid.py your_file.a2l pidlist.csv output.csv
```

This will show detailed parsing information and any errors encountered.

## Contributing

1. Create a feature branch
2. Make your changes
3. Test with various A2L files
4. Submit a pull request

## License

This project is open source. Please check the repository for license details.

## Changelog

### v2.0.0 (pya2l Integration)
- Integrated pya2l library for robust A2L parsing
- Added fallback to original parsing method
- Enhanced error handling and reporting
- Improved data extraction with metadata support
- Added automatic dependency management
- Maintained backward compatibility

### v1.0.0 (Original)
- Basic A2L parsing with manual state machine
- CSV template matching
- Batch processing support
