#!/usr/bin/env python3
# Document Viewer for Mistral OCR and Unstructured.io Pipelines
# This script helps view processed document data in a user-friendly way

import os
import json
import argparse
import textwrap
from pathlib import Path
from typing import List, Dict, Any, Optional
import colorama
from colorama import Fore, Back, Style
from tabulate import tabulate

# Initialize colorama
colorama.init()

# Path configuration
UNSTRUCTURED_DIR = Path("unstructured_json")
MISTRAL_JSON_DIR = Path("mistral_output/json")
MISTRAL_MARKDOWN_DIR = Path("mistral_output/markdown")
MISTRAL_IMAGES_DIR = Path("mistral_output/images")

def print_header(title, color=Fore.CYAN):
    """Print a formatted header"""
    width = os.get_terminal_size().columns
    print(f"\n{color}" + "=" * width)
    print(f"{title}".center(width))
    print("=" * width + f"{Style.RESET_ALL}")

def print_section(title, color=Fore.YELLOW):
    """Print a section header"""
    width = os.get_terminal_size().columns
    print(f"\n{color}" + "-" * width)
    print(f" {title} ".center(width, "-"))
    print("-" * width + f"{Style.RESET_ALL}")

def wrap_text(text, width=100):
    """Wrap text to a specified width"""
    return "\n".join(textwrap.wrap(text, width=width))

def get_available_documents():
    """Get a list of all available processed documents"""
    unstructured_docs = []
    mistral_docs = []
    
    # Check for Unstructured.io documents
    if UNSTRUCTURED_DIR.exists():
        for file_path in UNSTRUCTURED_DIR.glob("*.json"):
            unstructured_docs.append(file_path.stem)
    
    # Check for Mistral documents
    if MISTRAL_JSON_DIR.exists():
        # Look for JSON files directly in the directory or its subdirectories
        for file_path in MISTRAL_JSON_DIR.glob("**/*.json"):
            # Get the parent directory name if it's in a subdirectory
            if file_path.parent.name != MISTRAL_JSON_DIR.name:
                mistral_docs.append(file_path.parent.name)
            else:
                # If JSON is directly in the main directory, use the filename without extension
                mistral_docs.append(file_path.stem)
    
    # Remove duplicates
    mistral_docs = list(set(mistral_docs))
    
    return {
        "unstructured": unstructured_docs,
        "mistral": mistral_docs,
        "both": list(set(unstructured_docs) & set(mistral_docs))
    }

def display_document_list(documents):
    """Display a list of available documents"""
    print_header("AVAILABLE DOCUMENTS")
    
    # Create a single combined table
    combined_table = []
    
    # Add documents from both pipelines
    for doc in sorted(set(documents["unstructured"] + documents["mistral"])):
        in_unstructured = "✓" if doc in documents["unstructured"] else ""
        in_mistral = "✓" if doc in documents["mistral"] else ""
        combined_table.append([len(combined_table) + 1, doc, in_unstructured, in_mistral])
    
    # Display the combined table
    print(tabulate(combined_table, headers=["#", "Document Name", "Unstructured", "Mistral"], tablefmt="pretty"))
    
    # Return just the document names
    return [doc[1] for doc in combined_table]

def read_unstructured_json(doc_name):
    """Read and parse Unstructured.io JSON data"""
    json_files = list(UNSTRUCTURED_DIR.glob(f"{doc_name}*.json"))
    
    if not json_files:
        return None
    
    try:
        with open(json_files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"{Fore.RED}Error reading Unstructured.io JSON: {str(e)}{Style.RESET_ALL}")
        return None

def read_mistral_json(doc_name):
    """Read and parse Mistral OCR JSON data"""
    json_dir = MISTRAL_JSON_DIR / doc_name
    
    # First try looking in a subdirectory with the document name
    if json_dir.exists():
        try:
            # Read OCR response
            ocr_json_path = json_dir / "ocr_response.json"
            if ocr_json_path.exists():
                with open(ocr_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Read summary
                summary_path = json_dir / "summary.json"
                if summary_path.exists():
                    with open(summary_path, 'r', encoding='utf-8') as f:
                        summary = json.load(f)
                else:
                    summary = {}
                
                return {"ocr_data": data, "summary": summary}
        except Exception as e:
            print(f"{Fore.RED}Error reading Mistral JSON from directory: {str(e)}{Style.RESET_ALL}")
    
    # If not found in subdirectory, try looking for files directly in the main directory
    try:
        # Look for files with the document name in the filename
        ocr_files = list(MISTRAL_JSON_DIR.glob(f"{doc_name}*.json"))
        if ocr_files:
            with open(ocr_files[0], 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {"ocr_data": data, "summary": {}}
    except Exception as e:
        print(f"{Fore.RED}Error reading Mistral JSON from main directory: {str(e)}{Style.RESET_ALL}")
    
    return None

def read_mistral_markdown(doc_name):
    """Read Mistral OCR markdown data"""
    markdown_dir = MISTRAL_MARKDOWN_DIR / doc_name
    
    if not markdown_dir.exists():
        return None
    
    try:
        markdown_files = list(markdown_dir.glob("*.md"))
        if not markdown_files:
            return None
        
        with open(markdown_files[0], 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        return markdown_content
    except Exception as e:
        print(f"{Fore.RED}Error reading Mistral markdown: {str(e)}{Style.RESET_ALL}")
        return None

def get_mistral_images(doc_name):
    """Get list of images extracted by Mistral OCR"""
    images_dir = MISTRAL_IMAGES_DIR / doc_name
    
    if not images_dir.exists():
        return []
    
    return list(images_dir.glob("*.*"))

def display_unstructured_data(data):
    """Display Unstructured.io data in a readable format"""
    if not data:
        print(f"{Fore.RED}No Unstructured.io data available for this document.{Style.RESET_ALL}")
        return
    
    print_section("UNSTRUCTURED.IO EXTRACTED CONTENT", Fore.GREEN)
    
    # Extract and display just the text content
    full_text = ""
    for element in data:
        if "text" in element and element["text"]:
            full_text += element["text"].strip() + "\n\n"
    
    print(f"{Fore.WHITE}{full_text}{Style.RESET_ALL}")

def display_mistral_data(json_data, markdown_content, images):
    """Display Mistral OCR data in a readable format"""
    if not json_data and not markdown_content and not images:
        print(f"{Fore.RED}No Mistral OCR data available for this document.{Style.RESET_ALL}")
        return
    
    print_section("MISTRAL OCR EXTRACTED CONTENT", Fore.MAGENTA)
    
    # Display summary
    if json_data and "summary" in json_data:
        print_section("Document Summary", Fore.CYAN)
        summary = json_data["summary"]
        summary_table = []
        
        for key, value in summary.items():
            if key not in ["json_path", "markdown_path", "images_dir"]:
                summary_table.append([key.replace("_", " ").title(), value])
        
        print(tabulate(summary_table, tablefmt="pretty"))
    
    # Display OCR JSON data
    if json_data and "ocr_data" in json_data:
        print_section("OCR JSON Content", Fore.CYAN)
        ocr_data = json_data["ocr_data"]
        
        # Try to extract and display text content based on common JSON structures
        text_found = False
        
        # Check for direct text field
        if isinstance(ocr_data, dict) and "text" in ocr_data:
            print(f"{Fore.WHITE}{ocr_data['text']}{Style.RESET_ALL}")
            text_found = True
        
        # Check for pages array with text
        elif isinstance(ocr_data, dict) and "pages" in ocr_data and isinstance(ocr_data["pages"], list):
            for i, page in enumerate(ocr_data["pages"], 1):
                if isinstance(page, dict) and "text" in page:
                    print(f"{Fore.YELLOW}[Page {i}]{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}{page['text']}{Style.RESET_ALL}")
                    print(f"{Fore.BLUE}{'-' * 50}{Style.RESET_ALL}")
                    text_found = True
        
        # Check for document with blocks/paragraphs
        elif isinstance(ocr_data, dict) and "document" in ocr_data:
            doc = ocr_data["document"]
            if isinstance(doc, dict) and "blocks" in doc:
                for i, block in enumerate(doc["blocks"], 1):
                    if isinstance(block, dict) and "text" in block:
                        print(f"{Fore.YELLOW}[Block {i}]{Style.RESET_ALL}")
                        print(f"{Fore.WHITE}{block['text']}{Style.RESET_ALL}")
                        print(f"{Fore.BLUE}{'-' * 50}{Style.RESET_ALL}")
                        text_found = True
        
        # If no structured text was found, print the raw JSON
        if not text_found:
            print(f"{Fore.YELLOW}Full JSON Content:{Style.RESET_ALL}")
            try:
                formatted_json = json.dumps(ocr_data, indent=2)
                print(f"{Fore.WHITE}{formatted_json}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error formatting JSON: {str(e)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}{str(ocr_data)}{Style.RESET_ALL}")
    
    # Display extracted text from markdown
    if markdown_content:
        print_section("Markdown Content", Fore.CYAN)
        print(f"{Fore.WHITE}{markdown_content}{Style.RESET_ALL}")
    
    # Display image information
    if images:
        print_section("Extracted Images", Fore.CYAN)
        image_table = []
        
        for i, img_path in enumerate(images, 1):
            image_table.append([i, img_path.name, f"{img_path.stat().st_size / 1024:.2f} KB"])
        
        print(tabulate(image_table, headers=["#", "Image Name", "Size"], tablefmt="pretty"))
        print(f"\n{Fore.YELLOW}Total Images: {len(images)}{Style.RESET_ALL}")

def view_document(doc_name):
    """View a specific document's processed data"""
    print_header(f"VIEWING DOCUMENT: {doc_name}", Fore.MAGENTA)
    
    # Get data from both pipelines
    unstructured_data = read_unstructured_json(doc_name)
    mistral_json = read_mistral_json(doc_name)
    mistral_markdown = read_mistral_markdown(doc_name)
    mistral_images = get_mistral_images(doc_name)
    
    # Display data from both pipelines
    print_header("DOCUMENT CONTENT COMPARISON", Fore.YELLOW)
    print(f"{Fore.CYAN}Showing content from both Unstructured.io and Mistral OCR pipelines for comparison.{Style.RESET_ALL}")
    
    # Always display both, even if one is empty
    display_unstructured_data(unstructured_data)
    display_mistral_data(mistral_json, mistral_markdown, mistral_images)
    
    if not unstructured_data and not mistral_json and not mistral_markdown and not mistral_images:
        print(f"{Fore.RED}No data available for this document from either pipeline.{Style.RESET_ALL}")

def interactive_mode():
    """Run the viewer in interactive mode"""
    print_header("DOCUMENT VIEWER", Fore.MAGENTA)
    print(f"{Fore.CYAN}This tool helps you view processed document data from both pipelines.{Style.RESET_ALL}")
    
    # Get available documents
    documents = get_available_documents()
    
    if not documents["unstructured"] and not documents["mistral"]:
        print(f"{Fore.RED}No processed documents found. Please run the pipelines first.{Style.RESET_ALL}")
        return
    
    # Display document list
    all_docs = display_document_list(documents)
    
    while True:
        try:
            print(f"\n{Fore.CYAN}Enter the number or name of the document to view (or 'q' to quit):{Style.RESET_ALL}")
            choice = input("> ").strip()
            
            if choice.lower() in ['q', 'quit', 'exit']:
                break
            
            # Handle numeric choice
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(all_docs):
                    view_document(all_docs[idx])
                else:
                    print(f"{Fore.RED}Invalid document number. Please try again.{Style.RESET_ALL}")
            # Handle document name
            elif choice in all_docs:
                view_document(choice)
            else:
                print(f"{Fore.RED}Document not found. Please try again.{Style.RESET_ALL}")
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Document Viewer for Mistral OCR and Unstructured.io Pipelines")
    parser.add_argument("--doc", help="View a specific document")
    parser.add_argument("--list", action="store_true", help="List available documents")
    
    args = parser.parse_args()
    
    if args.list:
        documents = get_available_documents()
        display_document_list(documents)
    elif args.doc:
        view_document(args.doc)
    else:
        interactive_mode()

if __name__ == "__main__":
    main() 