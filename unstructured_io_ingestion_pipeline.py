#!/usr/bin/env python3
# Document Ingestion Pipeline using Unstructured.io
# This script processes PDF and DOCX files and extracts structured content

import os
import json
import logging
import time
from dotenv import load_dotenv
from pathlib import Path

from unstructured_ingest.v2.pipeline.pipeline import Pipeline
from unstructured_ingest.v2.interfaces import ProcessorConfig
from unstructured_ingest.v2.processes.connectors.local import (
    LocalIndexerConfig, 
    LocalDownloaderConfig, 
    LocalConnectionConfig, 
    LocalUploaderConfig
)
from unstructured_ingest.v2.processes.partitioner import PartitionerConfig
from unstructured_ingest.v2.processes.filter import FiltererConfig
from unstructured_ingest.v2.processes.chunker import ChunkerConfig

# Import utility functions
from utils import (
    ensure_directory,
    get_file_metadata,
    extract_text_from_json,
    summarize_document_collection,
    save_document_texts
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_directories():
    """Create necessary directories if they don't exist"""
    # Create output directory for processed JSON files
    output_dir = ensure_directory("unstructured_json")
    logger.info(f"Output directory set to: {output_dir}")
    return str(output_dir)

def run_ingestion_pipeline(input_dir, output_dir, api_key):
    """Run the document ingestion pipeline"""
    logger.info(f"Starting document ingestion pipeline")
    logger.info(f"Processing documents from: {input_dir}")
    
    # Get list of files to process
    input_files = [f for f in os.listdir(input_dir) 
                  if os.path.isfile(os.path.join(input_dir, f)) and 
                  (f.lower().endswith('.pdf') or f.lower().endswith('.docx') or f.lower().endswith('.doc'))]
    
    logger.info(f"Found {len(input_files)} files to process")
    
    # Print file information
    for i, file_name in enumerate(input_files, 1):
        file_path = os.path.join(input_dir, file_name)
        metadata = get_file_metadata(file_path)
        logger.info(f"File {i}: {file_name} ({metadata['size_human']})")
    
    # Start timer
    start_time = time.time()
    
    pipeline = Pipeline.from_configs(
        context=ProcessorConfig(),
        indexer_config=LocalIndexerConfig(input_path=input_dir),
        downloader_config=LocalDownloaderConfig(),
        source_connection_config=LocalConnectionConfig(),
        filterer_config=FiltererConfig(
            file_glob=["*.pdf", "*.docx", "*.doc"],
            max_file_size=10485760  # 10MB max file size
        ),
        partitioner_config=PartitionerConfig(
            partition_by_api=True,
            api_key=api_key,
            partition_endpoint="https://api.unstructuredapp.io",
            strategy="auto",
            additional_partition_args={
                "split_pdf_page": True,
                "split_pdf_allow_failed": True,
                "split_pdf_concurrency_level": 15,
            }
        ),
        chunker_config=ChunkerConfig(
            chunking_strategy="by_paragraph",  # Chunk by paragraph for better context
            chunk_max_characters=500,
            chunk_multipage_sections=True
        ),
        uploader_config=LocalUploaderConfig(output_dir=output_dir)
    )
    
    logger.info("Running pipeline...")
    pipeline.run()
    
    # End timer
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Pipeline execution completed in {elapsed_time:.2f} seconds")
    
    return True

def display_processed_files(output_dir):
    """Display the content of processed JSON files"""
    logger.info(f"Displaying processed files from: {output_dir}")
    
    documents_texts = []
    file_count = 0
    
    # Get collection summary
    summary = summarize_document_collection(output_dir)
    logger.info(f"Document Collection Summary:")
    logger.info(f"Total files: {summary['total_files']}")
    logger.info(f"PDF files: {summary['pdf_count']}")
    logger.info(f"DOCX/DOC files: {summary['docx_count']}")
    logger.info(f"Total size: {summary['total_size']}")
    
    for file_name in os.listdir(output_dir):
        if file_name.endswith('.json'):
            file_path = os.path.join(output_dir, file_name)
            file_count += 1
            
            logger.info(f"Reading file {file_count}: {file_name}")
            
            try:
                # Extract text from the JSON file
                text_content = extract_text_from_json(file_path)
                
                # Format the document text with a header
                original_filename = file_name.replace('.json', '')
                document_text = f'Document {file_count}: {original_filename}\n{text_content}'
                documents_texts.append(document_text)
                
                # Print a preview of the document
                preview = text_content[:500] + "..." if len(text_content) > 500 else text_content
                logger.info(f"Document {file_count} Preview:\n{preview}\n{'='*80}")
                
            except Exception as e:
                logger.error(f"Error processing file {file_name}: {str(e)}")
    
    logger.info(f"Total processed documents: {file_count}")
    return documents_texts

def main():
    """Main function to run the document ingestion pipeline"""
    print("="*80)
    print("DOCUMENT INGESTION PIPELINE")
    print("="*80)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("UNSTRUCTURED_API_KEY")
    if not api_key:
        logger.error("UNSTRUCTURED_API_KEY not found in environment variables")
        print("Error: UNSTRUCTURED_API_KEY not found in environment variables")
        print("Please set the UNSTRUCTURED_API_KEY environment variable or create a .env file")
        return
    
    # Setup directories
    output_dir = setup_directories()
    
    # Set input directory to the Data folder
    input_dir = "Data"
    if not os.path.exists(input_dir):
        logger.error(f"Input directory '{input_dir}' not found")
        print(f"Error: Input directory '{input_dir}' not found")
        return
    
    print(f"Processing documents from: {input_dir}")
    print(f"Output directory: {output_dir}")
    print("-"*80)
    
    # Run the ingestion pipeline
    try:
        success = run_ingestion_pipeline(input_dir, output_dir, api_key)
        
        if success:
            print("-"*80)
            print("Pipeline execution completed successfully")
            print("Displaying processed files...")
            
            # Display processed files
            documents_texts = display_processed_files(output_dir)
            
            # Save the documents texts to a file
            output_file = "documents_texts.txt"
            if save_document_texts(documents_texts, output_file):
                logger.info(f"Document texts saved to: {output_file}")
                print(f"Document texts saved to: {output_file}")
            
            print("-"*80)
            print("Document ingestion pipeline completed successfully")
            print("="*80)
    except Exception as e:
        logger.error(f"Error running ingestion pipeline: {str(e)}")
        print(f"Error running ingestion pipeline: {str(e)}")

if __name__ == "__main__":
    main()
