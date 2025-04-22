# Levy Export Parser Documentation

## Overview

The Levy Export Parser is a utility for parsing levy export files in various formats. It supports automatic format detection and extraction of levy data from TXT, XLS, XLSX, XML, CSV, and JSON files.

## Features

- **Format Auto-Detection**: Automatically detects the format of the input file based on file extension and content analysis.
- **Multi-Format Support**: Parses levy data from various file formats including:
  - Text files (TXT)
  - Excel files (XLS, XLSX)
  - XML files
  - CSV files
  - JSON files
- **Flexible Parsing**: Accommodates various data structures and header formats within each file type.
- **Year Detection**: Automatically detects the levy year from file metadata when available.
- **Linked Levy Codes**: Properly handles levy codes with linked codes (e.g., "123/456").
- **Error Handling**: Robust error handling with detailed logging for better troubleshooting.
- **Standardized Output**: Returns a consistent data structure regardless of the input format.

## Usage

### Basic Example

```python
from utils.levy_export_parser import LevyExportParser

# Parse a levy export file
data = LevyExportParser.parse_file("path/to/levy_export.xlsx")

# Get number of records
print(f"Found {len(data)} records")

# Get years in the data
print(f"Years: {data.get_years()}")

# Get tax districts in the data
print(f"Districts: {data.get_tax_districts()}")

# Access the first record
if data.records:
    record = data.records[0]
    print(f"Levy Code: {record['levy_cd']}")
    print(f"Levy Rate: {record['levy_rate']}")
    print(f"Levy Amount: {record['levy_amount']}")
```

### Format Detection

```python
from utils.levy_export_parser import LevyExportParser, LevyExportFormat

# Detect the format of a file
format = LevyExportParser.detect_format("path/to/levy_export.csv")
print(f"Detected format: {format.name}")  # Output: CSV

# Check if the format is supported
if format != LevyExportFormat.UNKNOWN:
    data = LevyExportParser.parse_file("path/to/levy_export.csv")
else:
    print("Unsupported file format")
```

### Handling Different Formats

The parser automatically handles different file formats:

```python
# Parse files of different formats
txt_data = LevyExportParser.parse_file("levy_data.txt")
xlsx_data = LevyExportParser.parse_file("levy_data.xlsx")
csv_data = LevyExportParser.parse_file("levy_data.csv")
json_data = LevyExportParser.parse_file("levy_data.json")
```

## Data Model

### LevyExportData

The `LevyExportData` class is a container for the parsed levy data:

- `records`: List of `LevyRecord` objects containing the parsed levy records
- `metadata`: Dictionary containing metadata about the export (e.g., format, year)
- `get_years()`: Returns a list of years found in the records
- `get_tax_districts()`: Returns a list of unique tax district IDs
- `get_levy_codes()`: Returns a list of unique levy codes

### LevyRecord

The `LevyRecord` class represents a single levy record:

- `data`: Dictionary containing the record data
- `__getitem__(key)`: Access record data with dictionary syntax (e.g., `record['levy_cd']`)
- `get(key, default)`: Get a value with a default if not found

Record fields include:

- `tax_district_id`: Tax district identifier
- `levy_cd`: Levy code
- `levy_cd_linked`: Linked levy code (if applicable)
- `levy_rate`: Levy rate value
- `levy_amount`: Levy amount value
- `assessed_value`: Assessed value
- `year`: Tax year
- `source`: Source format (e.g., 'txt', 'xlsx', 'csv')

## Format-Specific Considerations

### TXT Files

Text files are expected to be in a fixed-width or space-separated format with columns for levy code, rate, amount, and value. Headers are automatically detected.

### Excel Files (XLS/XLSX)

Excel files can have various structures. The parser tries to:

1. Find a header row containing levy code, rate, amount, and value columns
2. Extract the year from metadata rows
3. Parse data rows according to the detected column structure

### CSV Files

CSV files are parsed with automatic dialect detection. Headers are mapped to standard field names.

### JSON Files

JSON files can have various structures:

1. An object with a `records` or `levies` array
2. An array of levy records
3. Metadata can be included in a `metadata` object

### XML Files

XML files are parsed using ElementTree, with support for various element naming conventions.

## Error Handling

The parser includes comprehensive error handling and logging:

```python
import logging
logging.basicConfig(level=logging.INFO)

try:
    data = LevyExportParser.parse_file("path/to/file.xlsx")
except ValueError as e:
    print(f"Invalid file format: {e}")
except Exception as e:
    print(f"Error parsing file: {e}")
```

## Best Practices

1. **File Validation**: Always validate that the file exists before parsing
2. **Error Handling**: Wrap parsing code in try-except blocks to handle potential errors
3. **Logging**: Enable logging to get more detailed information about the parsing process
4. **Format Detection**: Use the format detection method to check if a file format is supported before parsing
5. **Data Validation**: Validate the parsed data before using it (e.g., check if records were found)
