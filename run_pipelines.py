#!/usr/bin/env python3
# Script to run document ingestion pipelines

import os
import sys
import argparse
from dotenv import load_dotenv

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"{title}")
    print("=" * 80)

def check_environment():
    """Check if the environment is properly set up"""
    # Load environment variables
    load_dotenv()
    
    # Check for Unstructured.io API key
    unstructured_api_key = os.getenv("UNSTRUCTURED_API_KEY")
    if not unstructured_api_key:
        print("Warning: UNSTRUCTURED_API_KEY not found in environment variables")
        print("The Unstructured.io pipeline will not work without this key")
    
    # Check for Mistral API key
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    if not mistral_api_key:
        print("Warning: MISTRAL_API_KEY not found in environment variables")
        print("The Mistral OCR pipeline will not work without this key")
    
    # Check for Data directory
    if not os.path.exists("Data"):
        print("Warning: Data directory not found")
        print("Creating Data directory...")
        os.makedirs("Data")
    
    # Check if Data directory has files
    pdf_files = [f for f in os.listdir("Data") if f.lower().endswith(".pdf")]
    docx_files = [f for f in os.listdir("Data") if f.lower().endswith((".docx", ".doc"))]
    
    if not pdf_files and not docx_files:
        print("Warning: No PDF or DOCX files found in the Data directory")
        print("Please add some files to process")
    else:
        print(f"Found {len(pdf_files)} PDF files and {len(docx_files)} DOCX/DOC files in the Data directory")

def run_unstructured_pipeline():
    """Run the Unstructured.io pipeline"""
    print_header("RUNNING UNSTRUCTURED.IO PIPELINE")
    
    try:
        from unstructured_io_ingestion_pipeline import main as unstructured_main
        unstructured_main()
    except ImportError:
        print("Error: Could not import the Unstructured.io pipeline")
        print("Make sure you have installed the required packages:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"Error running Unstructured.io pipeline: {str(e)}")

def run_mistral_pipeline():
    """Run the Mistral OCR pipeline"""
    print_header("RUNNING MISTRAL OCR PIPELINE")
    
    try:
        from mistrel_ocr_ingestion_pipeline import main as mistral_main
        mistral_main()
    except ImportError:
        print("Error: Could not import the Mistral OCR pipeline")
        print("Make sure you have installed the required packages:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"Error running Mistral OCR pipeline: {str(e)}")

def main():
    """Main function to run the selected pipeline"""
    parser = argparse.ArgumentParser(description="Run document ingestion pipelines")
    parser.add_argument("--pipeline", choices=["unstructured", "mistral", "both"], 
                        default="both", help="Which pipeline to run")
    
    args = parser.parse_args()
    
    print_header("DOCUMENT INGESTION PIPELINE RUNNER")
    
    # Check environment
    check_environment()
    
    # Run selected pipeline(s)
    if args.pipeline == "unstructured" or args.pipeline == "both":
        run_unstructured_pipeline()
    
    if args.pipeline == "mistral" or args.pipeline == "both":
        run_mistral_pipeline()
    
    print_header("PIPELINE EXECUTION COMPLETED")

if __name__ == "__main__":
    main() 