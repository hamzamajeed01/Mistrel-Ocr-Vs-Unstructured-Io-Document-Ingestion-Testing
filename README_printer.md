# Document Viewer (printer.py)

This tool helps you view processed document data from both the Unstructured.io and Mistral OCR pipelines in a user-friendly way. It provides a side-by-side comparison of the content extracted by each pipeline.

## Features

- **Interactive Interface**: Browse and select documents to view
- **Colorized Output**: Easy-to-read colorized text output
- **Formatted Display**: Well-formatted tables and sections
- **Document Comparison**: View data from both pipelines side by side
- **Complete Content Display**: Shows both Unstructured.io and Mistral OCR content for each document
- **Markdown Display**: Clearly displays Mistral's markdown content
- **Image Information**: View details about extracted images

## Requirements

- Python 3.8+
- colorama
- tabulate

These dependencies are included in the main requirements.txt file.

## Usage

### Interactive Mode

The default mode is interactive, allowing you to browse and select documents:

```bash
python printer.py
```

This will:
1. Display a list of all available processed documents
2. Allow you to select a document by number or name
3. Display the processed data from both pipelines for the selected document

### Command Line Options

You can also use command line options:

```bash
# List all available documents
python printer.py --list

# View a specific document
python printer.py --doc "document_name"
```

## Output Format

For each document, the viewer displays:

### Unstructured.io Data
- Extracted text organized by elements
- Element types (Title, Text, etc.)

### Mistral OCR Data
- Document summary (filename, size, pages, etc.)
- Extracted text in markdown format (complete content)
- List of extracted images with sizes

## Example

```bash
# Run the document viewer
python printer.py

# Select a document by number
> 1

# Or select a document by name
> NIPS-2017-attention-is-all-you-need-Paper

# Exit the viewer
> q
```

## Content Comparison

The viewer is designed to show content from both pipelines for easy comparison:

1. **Document Selection**: Choose a document that has been processed by either or both pipelines
2. **Content Comparison**: View the content extracted by both pipelines side by side
3. **Complete Display**: Both Unstructured.io and Mistral OCR content are displayed, even if one is empty

This makes it easy to compare the quality and completeness of the extraction performed by each pipeline.

## Troubleshooting

- If you don't see any documents listed, make sure you've run at least one of the pipelines first.
- If you encounter errors viewing a document, check that the document was processed successfully.
- If colorized output doesn't display correctly, make sure you're using a terminal that supports ANSI colors. 