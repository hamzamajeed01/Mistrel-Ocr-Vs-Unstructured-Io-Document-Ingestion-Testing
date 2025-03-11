#!/usr/bin/env python3
# Utility functions for document processing

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

def ensure_directory(directory_path: str) -> Path:
    """
    Ensure a directory exists, create it if it doesn't.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        Path object for the directory
    """
    path = Path(directory_path)
    path.mkdir(exist_ok=True, parents=True)
    return path

def get_file_metadata(file_path: str) -> Dict[str, Any]:
    """
    Get metadata for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file metadata
    """
    file_path = Path(file_path)
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
    """
    Format file size in human-readable format.
    
    Args:
        size_in_bytes: File size in bytes
        
    Returns:
        Human-readable file size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0 or unit == 'GB':
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0

def extract_text_from_json(json_file_path: str) -> str:
    """
    Extract text content from a JSON file produced by Unstructured.io.
    
    Args:
        json_file_path: Path to the JSON file
        
    Returns:
        Extracted text content
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
            # Extract text from elements
            text_content = '\n'.join(
                element["metadata"].get("text_as_html", "")
                if "metadata" in element and "text_as_html" in element["metadata"]
                else element.get("text", "")
                for element in data
            )
            
            return text_content
    except Exception as e:
        logger.error(f"Error extracting text from {json_file_path}: {str(e)}")
        return ""

def summarize_document_collection(output_dir: str) -> Dict[str, Any]:
    """
    Generate a summary of the document collection.
    
    Args:
        output_dir: Directory containing processed JSON files
        
    Returns:
        Dictionary with collection summary
    """
    total_files = 0
    pdf_count = 0
    docx_count = 0
    total_size_bytes = 0
    file_list = []
    
    for file_name in os.listdir(output_dir):
        if file_name.endswith('.json'):
            file_path = os.path.join(output_dir, file_name)
            total_files += 1
            
            # Get file metadata
            metadata = get_file_metadata(file_path)
            total_size_bytes += metadata["size_bytes"]
            
            # Count file types
            if "pdf" in file_name.lower():
                pdf_count += 1
            elif any(ext in file_name.lower() for ext in ["docx", "doc"]):
                docx_count += 1
                
            # Add to file list
            file_list.append({
                "filename": file_name,
                "size": metadata["size_human"]
            })
    
    return {
        "total_files": total_files,
        "pdf_count": pdf_count,
        "docx_count": docx_count,
        "total_size": format_file_size(total_size_bytes),
        "file_list": file_list
    }

def save_document_texts(documents_texts: List[str], output_file: str) -> bool:
    """
    Save document texts to a file.
    
    Args:
        documents_texts: List of document texts
        output_file: Path to the output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(repr(documents_texts))
        return True
    except Exception as e:
        logger.error(f"Error saving document texts to {output_file}: {str(e)}")
        return False
