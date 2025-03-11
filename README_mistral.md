# Mistral OCR Document Ingestion Pipeline(right now API handles only pdf ,images not docx)

This project provides a document ingestion pipeline using Mistral's OCR capabilities to process PDF and DOCX files, extract text and images, and save the results in structured formats.

## Overview

The pipeline performs the following steps:
1. Scans the input directory for PDF and DOCX files
2. Processes each file using Mistral's OCR API
3. Extracts text content and images from the documents
4. Saves the processed content as JSON files
5. Generates markdown files with properly linked images
6. Extracts and saves all images from the documents
7. Provides a detailed processing summary

## Features

- **Text Extraction**: Extracts text content from PDFs and DOCX files
- **Image Extraction**: Extracts images embedded in documents
- **Markdown Generation**: Creates markdown files with properly formatted text and image links
- **JSON Output**: Saves structured OCR data in JSON format
- **Detailed Logging**: Provides comprehensive logging of the processing steps
- **Processing Summary**: Generates a summary of the processing results

## Requirements

- Python 3.8+
- Mistral API key (get one at https://console.mistral.ai/api-keys)

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
MISTRAL_API_KEY=your_api_key_here
```

## Directory Structure

- `Data/`: Place your PDF and DOCX files in this directory
- `mistral_output/`: Root directory for all output files
  - `json/`: Contains JSON output files with OCR data
  - `markdown/`: Contains markdown files with extracted text
  - `images/`: Contains extracted images from documents
  - `processed_files/`: Contains copies of processed files

## Usage

1. Place your PDF and DOCX files in the `Data` directory
2. Run the ingestion pipeline:
   ```
   python mistrel_ocr_ingestion_pipeline.py
   ```
3. Check the output in the `mistral_output` directory

## Output Structure

For each processed document, the pipeline creates:

1. **JSON Output**:
   - `ocr_response.json`: The full OCR response from Mistral
   - `summary.json`: A summary of the processing results

2. **Markdown Output**:
   - `[filename].md`: A markdown file with the extracted text and image links

3. **Images Output**:
   - All extracted images saved with organized naming

## Example

```python
# Run the Mistral OCR document ingestion pipeline
python mistrel_ocr_ingestion_pipeline.py
```

## Processing Steps

1. **Setup**: Creates necessary directories and initializes the Mistral client
2. **File Discovery**: Scans the input directory for PDF and DOCX files
3. **Processing**: For each file:
   - Uploads the file to Mistral
   - Processes it with OCR
   - Extracts text and images
   - Saves the results in the appropriate formats
4. **Summary**: Displays a summary of the processing results

## Troubleshooting

- If you encounter an error about the API key, make sure you have set the `MISTRAL_API_KEY` environment variable or added it to the `.env` file.
- If you encounter an error about the input directory, make sure the `Data` directory exists and contains PDF or DOCX files.
- If you encounter an error during processing, check the logs for more information.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 