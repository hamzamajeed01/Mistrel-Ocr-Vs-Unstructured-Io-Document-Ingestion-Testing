#!/usr/bin/env python3
# Mistral OCR Document Ingestion Pipeline
# This script processes PDF and DOCX files using Mistral's OCR capabilities

import os
import json
import base64
import shutil
import logging
import time
import traceback
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from mistralai import Mistral, DocumentURLChunk
from mistralai.models import OCRResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mistral_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Path configuration
INPUT_DIR = Path("scanned_pdf_data")                  # Folder where the user places the PDFs/DOCX to be processed
OUTPUT_ROOT_DIR = Path("mistral_scanned_pdf_output")  # Root folder for conversion results
JSON_OUTPUT_DIR = OUTPUT_ROOT_DIR / "json"  # Folder for JSON output
MARKDOWN_OUTPUT_DIR = OUTPUT_ROOT_DIR / "markdown"  # Folder for Markdown output
IMAGES_OUTPUT_DIR = OUTPUT_ROOT_DIR / "images"  # Folder for extracted images
PROCESSED_DIR = OUTPUT_ROOT_DIR / "processed_files"  # Folder for processed files
ERROR_DIR = OUTPUT_ROOT_DIR / "error_files"  # Folder for files that failed processing

def setup_directories():
    """Create necessary directories if they don't exist"""
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_ROOT_DIR.mkdir(exist_ok=True)
    JSON_OUTPUT_DIR.mkdir(exist_ok=True)
    MARKDOWN_OUTPUT_DIR.mkdir(exist_ok=True)
    IMAGES_OUTPUT_DIR.mkdir(exist_ok=True)
    PROCESSED_DIR.mkdir(exist_ok=True)
    ERROR_DIR.mkdir(exist_ok=True)
    logger.info(f"Directories set up successfully")

def get_file_metadata(file_path: Path) -> Dict[str, Any]:
    """
    Get metadata for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file metadata
    """
    stats = file_path.stat()
    
    return {
        "filename": file_path.name,
        "extension": file_path.suffix.lower(),
        "size_bytes": stats.st_size,
        "size_human": format_file_size(stats.st_size),
        "modified_time": stats.st_mtime,
        "is_pdf": file_path.suffix.lower() == ".pdf",
        "is_docx": file_path.suffix.lower() in [".docx", ".doc"]
    }

def format_file_size(size_in_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0 or unit == 'GB':
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0

def replace_images_in_markdown(markdown_str: str, images_dict: dict) -> str:
    """
    Convert base64 encoded images in markdown to links to external images
    for better readability and organization.
    """
    for img_name, base64_str in images_dict.items():
        markdown_str = markdown_str.replace(f"![{img_name}]({img_name})", f"![{img_name}]({base64_str})")
    return markdown_str

def get_combined_markdown(ocr_response: OCRResponse) -> str:
    """
    Combine the markdown of all pages from the OCR response.
    """
    markdowns: list[str] = []
    for page in ocr_response.pages:
        image_data = {}
        for img in page.images:
            image_data[img.id] = img.image_base64
        markdowns.append(replace_images_in_markdown(page.markdown, image_data))

    return "\n\n".join(markdowns)

def process_document(file_path: Path, client: Mistral) -> bool:
    """
    Process a document using Mistral OCR.
    
    Args:
        file_path: Path to the document
        client: Mistral client
        
    Returns:
        True if processing was successful, False otherwise
    """
    try:
        # Get file metadata
        metadata = get_file_metadata(file_path)
        file_base = file_path.stem
        file_ext = file_path.suffix.lower()
        
        logger.info(f"Processing {file_path.name} ({metadata['size_human']})...")
        print(f"\n{'='*80}")
        print(f"PROCESSING: {file_path.name} ({metadata['size_human']})")
        print(f"{'='*80}")
        
        # Create output directories for this document
        doc_json_dir = JSON_OUTPUT_DIR / file_base
        doc_markdown_dir = MARKDOWN_OUTPUT_DIR / file_base
        doc_images_dir = IMAGES_OUTPUT_DIR / file_base
        
        doc_json_dir.mkdir(exist_ok=True)
        doc_markdown_dir.mkdir(exist_ok=True)
        doc_images_dir.mkdir(exist_ok=True)
        
        # Start timer
        start_time = time.time()
        
        # Read file
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        
        # Log file type information
        if file_ext == '.pdf':
            logger.info(f"Processing PDF file: {file_path.name}")
            purpose = "ocr"
        elif file_ext in ['.docx', '.doc']:
            logger.info(f"Processing DOCX file: {file_path.name}")
            purpose = "ocr"  # Using the same purpose for DOCX
        else:
            logger.warning(f"Unsupported file type: {file_ext}")
            return False
        
        # Upload file to Mistral
        print(f"Uploading file to Mistral...")
        logger.info(f"Uploading file to Mistral: {file_path.name}")
        try:
            uploaded_file = client.files.upload(
                file={
                    "file_name": file_path.name,
                    "content": file_bytes,
                },
                purpose=purpose
            )
            logger.info(f"File uploaded successfully with ID: {uploaded_file.id}")
        except Exception as e:
            logger.error(f"Error uploading file to Mistral: {str(e)}")
            print(f"ERROR: Failed to upload file to Mistral: {str(e)}")
            return False
        
        # Get signed URL
        try:
            signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
            logger.info(f"Got signed URL for file: {uploaded_file.id}")
        except Exception as e:
            logger.error(f"Error getting signed URL: {str(e)}")
            print(f"ERROR: Failed to get signed URL: {str(e)}")
            return False
        
        # Process with OCR
        print(f"Processing with Mistral OCR...")
        logger.info(f"Processing with Mistral OCR: {file_path.name}")
        try:
            ocr_response = client.ocr.process(
                document=DocumentURLChunk(document_url=signed_url.url),
                model="mistral-ocr-latest",
                include_image_base64=True
            )
            logger.info(f"OCR processing completed successfully")
        except Exception as e:
            logger.error(f"Error processing with Mistral OCR: {str(e)}")
            logger.error(traceback.format_exc())
            print(f"ERROR: Failed to process with Mistral OCR: {str(e)}")
            # Move to error directory
            error_file_path = ERROR_DIR / file_path.name
            shutil.copy2(file_path, error_file_path)
            logger.info(f"File copied to error directory: {error_file_path}")
            return False
        
        # Save OCR response as JSON
        ocr_json_path = doc_json_dir / "ocr_response.json"
        try:
            with open(ocr_json_path, "w", encoding="utf-8") as json_file:
                json.dump(ocr_response.model_dump(), json_file, indent=4, ensure_ascii=False)
            logger.info(f"OCR response saved to {ocr_json_path}")
            print(f"OCR response saved to {ocr_json_path}")
        except Exception as e:
            logger.error(f"Error saving OCR response: {str(e)}")
            print(f"ERROR: Failed to save OCR response: {str(e)}")
        
        # Process and save markdown with images
        global_counter = 1
        updated_markdown_pages = []
        
        print(f"Extracting and processing images...")
        logger.info(f"Extracting and processing images from {file_path.name}")
        
        # Log the number of pages in the response
        logger.info(f"Document has {len(ocr_response.pages)} pages")
        
        for page_idx, page in enumerate(ocr_response.pages, 1):
            updated_markdown = page.markdown
            page_images_count = 0
            
            # Log the number of images on this page
            logger.info(f"Page {page_idx} has {len(page.images)} images")
            
            for image_obj in page.images:
                # Extract base64 image data
                base64_str = image_obj.image_base64
                if base64_str.startswith("data:"):
                    base64_str = base64_str.split(",", 1)[1]
                
                try:
                    image_bytes = base64.b64decode(base64_str)
                    
                    # Determine image extension
                    ext = Path(image_obj.id).suffix if Path(image_obj.id).suffix else ".png"
                    new_image_name = f"{file_base}_page{page_idx}_img_{global_counter}{ext}"
                    global_counter += 1
                    page_images_count += 1
                    
                    # Save image
                    image_output_path = doc_images_dir / new_image_name
                    with open(image_output_path, "wb") as f:
                        f.write(image_bytes)
                    
                    # Update markdown with relative path to image
                    updated_markdown = updated_markdown.replace(
                        f"![{image_obj.id}]({image_obj.id})",
                        f"![{new_image_name}](../images/{file_base}/{new_image_name})"
                    )
                except Exception as e:
                    logger.error(f"Error processing image {image_obj.id}: {str(e)}")
                    print(f"ERROR: Failed to process image: {str(e)}")
            
            updated_markdown_pages.append(updated_markdown)
            logger.info(f"Page {page_idx}: Extracted {page_images_count} images")
        
        # Check if we have any markdown content
        if not updated_markdown_pages:
            logger.warning(f"No markdown content extracted from {file_path.name}")
            print(f"WARNING: No markdown content extracted from {file_path.name}")
        
        # Save combined markdown
        final_markdown = "\n\n".join(updated_markdown_pages)
        output_markdown_path = doc_markdown_dir / f"{file_base}.md"
        with open(output_markdown_path, "w", encoding="utf-8") as md_file:
            md_file.write(final_markdown)
        logger.info(f"Markdown saved to {output_markdown_path}")
        print(f"Markdown saved to {output_markdown_path}")
        
        # Create a summary JSON with metadata
        summary = {
            "filename": file_path.name,
            "file_type": "PDF" if metadata["is_pdf"] else "DOCX/DOC",
            "file_size": metadata["size_human"],
            "processing_time": f"{time.time() - start_time:.2f} seconds",
            "pages": len(ocr_response.pages),
            "total_images": global_counter - 1,
            "json_path": str(ocr_json_path),
            "markdown_path": str(output_markdown_path),
            "images_dir": str(doc_images_dir)
        }
        
        summary_path = doc_json_dir / "summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4)
        
        # End timer
        elapsed_time = time.time() - start_time
        logger.info(f"Document processed in {elapsed_time:.2f} seconds")
        print(f"Document processed in {elapsed_time:.2f} seconds")
        print(f"{'='*80}\n")
        
        # Move processed file to processed directory
        processed_file_path = PROCESSED_DIR / file_path.name
        shutil.copy2(file_path, processed_file_path)
        logger.info(f"File copied to {processed_file_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error processing {file_path.name}: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"ERROR: Failed to process {file_path.name}: {str(e)}")
        
        # Move to error directory
        try:
            error_file_path = ERROR_DIR / file_path.name
            shutil.copy2(file_path, error_file_path)
            logger.info(f"File copied to error directory: {error_file_path}")
        except Exception as copy_error:
            logger.error(f"Error copying file to error directory: {str(copy_error)}")
        
        return False

def display_processing_summary(successful_files: List[Path], failed_files: List[Path]):
    """Display a summary of the processing results"""
    print(f"\n{'='*80}")
    print(f"PROCESSING SUMMARY")
    print(f"{'='*80}")
    print(f"Total files processed: {len(successful_files) + len(failed_files)}")
    print(f"Successfully processed: {len(successful_files)}")
    print(f"Failed to process: {len(failed_files)}")
    
    # Count file types
    pdf_success = sum(1 for f in successful_files if f.suffix.lower() == '.pdf')
    docx_success = sum(1 for f in successful_files if f.suffix.lower() in ['.docx', '.doc'])
    pdf_failed = sum(1 for f in failed_files if f.suffix.lower() == '.pdf')
    docx_failed = sum(1 for f in failed_files if f.suffix.lower() in ['.docx', '.doc'])
    
    print(f"\nPDF files: {pdf_success + pdf_failed} total, {pdf_success} successful, {pdf_failed} failed")
    print(f"DOCX files: {docx_success + docx_failed} total, {docx_success} successful, {docx_failed} failed")
    
    if successful_files:
        print(f"\nSuccessfully processed files:")
        for i, file in enumerate(successful_files, 1):
            print(f"  {i}. {file.name}")
    
    if failed_files:
        print(f"\nFailed to process files:")
        for i, file in enumerate(failed_files, 1):
            print(f"  {i}. {file.name}")
    
    print(f"\nOutput directories:")
    print(f"  - JSON: {JSON_OUTPUT_DIR}")
    print(f"  - Markdown: {MARKDOWN_OUTPUT_DIR}")
    print(f"  - Images: {IMAGES_OUTPUT_DIR}")
    print(f"  - Processed files: {PROCESSED_DIR}")
    print(f"  - Error files: {ERROR_DIR}")
    print(f"{'='*80}")
    
    # Log the summary
    logger.info(f"Processing summary: {len(successful_files)} successful, {len(failed_files)} failed")
    logger.info(f"PDF files: {pdf_success}/{pdf_success + pdf_failed} successful")
    logger.info(f"DOCX files: {docx_success}/{docx_success + docx_failed} successful")

def main():
    """Main function to run the Mistral OCR document ingestion pipeline"""
    print(f"{'='*80}")
    print(f"MISTRAL OCR DOCUMENT INGESTION PIPELINE")
    print(f"{'='*80}")
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        logger.error("MISTRAL_API_KEY not found in environment variables")
        print("Error: MISTRAL_API_KEY not found in environment variables")
        print("Please set the MISTRAL_API_KEY environment variable or create a .env file")
        return
    
    # Initialize Mistral client
    client = Mistral(api_key=api_key)
    print(f"Initialized Mistral client with API key: {api_key[:4]}...")
    logger.info(f"Initialized Mistral client with API key: {api_key[:4]}...")
    
    # Setup directories
    setup_directories()
    
    # Get list of files to process
    pdf_files = list(INPUT_DIR.glob("*.pdf"))
    docx_files = list(INPUT_DIR.glob("*.docx")) + list(INPUT_DIR.glob("*.doc"))
    all_files = pdf_files + docx_files
    
    if not all_files:
        logger.warning("No PDF or DOCX files found in the input directory")
        print(f"No PDF or DOCX files found in {INPUT_DIR}")
        return
    
    logger.info(f"Found {len(all_files)} files to process: {len(pdf_files)} PDFs, {len(docx_files)} DOCX/DOC")
    print(f"Found {len(all_files)} files to process:")
    print(f"  - PDF files: {len(pdf_files)}")
    print(f"  - DOCX/DOC files: {len(docx_files)}")
    
    for i, file in enumerate(all_files, 1):
        metadata = get_file_metadata(file)
        print(f"  {i}. {file.name} ({metadata['size_human']})")
    
    print(f"\nStarting processing...")
    logger.info("Starting document processing")
    
    # Process files
    successful_files = []
    failed_files = []
    
    # Process PDFs first
    if pdf_files:
        print(f"\nProcessing PDF files...")
        logger.info(f"Processing {len(pdf_files)} PDF files")
        for file in pdf_files:
            success = process_document(file, client)
            if success:
                successful_files.append(file)
            else:
                failed_files.append(file)
    
    # Then process DOCX files
    if docx_files:
        print(f"\nProcessing DOCX/DOC files...")
        logger.info(f"Processing {len(docx_files)} DOCX/DOC files")
        for file in docx_files:
            success = process_document(file, client)
            if success:
                successful_files.append(file)
            else:
                failed_files.append(file)
    
    # Display summary
    display_processing_summary(successful_files, failed_files)
    logger.info("Document processing completed")

if __name__ == "__main__":
    main()
