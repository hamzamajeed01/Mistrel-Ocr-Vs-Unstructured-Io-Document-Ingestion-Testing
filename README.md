# Document Ingestion Pipelines

This project provides two document ingestion pipelines for processing PDF and DOCX files:

1. **Unstructured.io Pipeline**: Uses Unstructured.io's API to extract structured content from documents
2. **Mistral OCR Pipeline**: Uses Mistral's OCR capabilities to extract text and images from documents(right now mistral does not hanlde docx files)

It also includes a document viewer to help you browse and view the processed data.

## Overview

Both pipelines perform the following general steps:
1. Scan the input directory for PDF and DOCX files
2. Process each file using their respective APIs
3. Extract structured content from the documents
4. Save the processed content in various formats
5. Display a preview of each processed document

## Features

### Unstructured.io Pipeline
- Text extraction from PDFs and DOCX files
- Chunking of text into paragraphs
- Structured JSON output
- Detailed logging

### Mistral OCR Pipeline
- Text extraction from PDFs and DOCX files
- Image extraction from documents
- Markdown generation with properly linked images
- JSON output with OCR data
- Detailed processing summary

### Document Viewer (printer.py)
- Interactive browsing of processed documents
- Colorized and formatted display of extracted content
- Side-by-side comparison of results from both pipelines
- Information about extracted images

## Requirements

- Python 3.8+
- Unstructured.io API key (for the Unstructured.io pipeline)
- Mistral API key (for the Mistral OCR pipeline)

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the project root with the following variables:

```
UNSTRUCTURED_API_KEY=your_unstructured_api_key_here
UNSTRUCTURED_API_URL=https://api.unstructuredapp.io
MISTRAL_API_KEY=your_mistral_api_key_here
```

## Directory Structure

- `Data/`: Place your PDF and DOCX files in this directory
- `unstructured_json/`: Output directory for the Unstructured.io pipeline
- `mistral_output/`: Output directory for the Mistral OCR pipeline
  - `json/`: Contains JSON output files with OCR data
  - `markdown/`: Contains markdown files with extracted text
  - `images/`: Contains extracted images from documents
  - `processed_files/`: Contains copies of processed files

## Usage

### Running the Pipelines

You can run either pipeline individually or both together using the provided script:

```bash
# Run both pipelines
python run_pipelines.py

# Run only the Unstructured.io pipeline
python run_pipelines.py --pipeline unstructured

# Run only the Mistral OCR pipeline
python run_pipelines.py --pipeline mistral
```

Alternatively, you can run each pipeline directly:

```bash
# Run the Unstructured.io pipeline
python unstructured_io_ingestion_pipeline.py

# Run the Mistral OCR pipeline
python mistrel_ocr_ingestion_pipeline.py
```

### Viewing Processed Documents

After running the pipelines, you can use the document viewer to browse and view the processed data:

```bash
# Run the document viewer in interactive mode
python printer.py

# List all available documents
python printer.py --list

# View a specific document
python printer.py --doc "document_name"
```

## Pipeline Details

### Unstructured.io Pipeline

The Unstructured.io pipeline uses the Unstructured.io API to extract structured content from documents. It processes each file and saves the extracted content as JSON files in the `unstructured_json` directory.

For more details, see [README_unstructured.md](README.md).

### Mistral OCR Pipeline

The Mistral OCR pipeline uses Mistral's OCR capabilities to extract text and images from documents. It processes each file and saves the extracted content as JSON files, markdown files, and images in the `mistral_output` directory.

For more details, see [README_mistral.md](README_mistral.md).

### Document Viewer

The document viewer (printer.py) provides an interactive way to browse and view the processed data from both pipelines. It displays the extracted text, images, and metadata in a user-friendly format.

For more details, see [README_printer.md](README_printer.md).

## Troubleshooting

- If you encounter an error about the API keys, make sure you have set the appropriate environment variables or added them to the `.env` file.
- If you encounter an error about the input directory, make sure the `Data` directory exists and contains PDF or DOCX files.
- If you encounter an error during processing, check the logs for more information.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 