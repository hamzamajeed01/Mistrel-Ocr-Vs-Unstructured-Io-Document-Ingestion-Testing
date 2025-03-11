import os
import sys
from pathlib import Path
from docx2pdf import convert
from tqdm import tqdm

def convert_docx_to_pdf(input_path, output_path=None):
    """
    Convert a single DOCX file to PDF
    
    Args:
        input_path: Path to the DOCX file
        output_path: Path where the PDF will be saved (optional)
    
    Returns:
        Path to the created PDF file
    """
    try:
        if output_path is None:
            output_path = str(input_path).replace('.docx', '.pdf')
        
        convert(input_path, output_path)
        return output_path
    except Exception as e:
        print(f"Error converting {input_path}: {str(e)}")
        return None

def process_directory(directory_path):
    """
    Process all DOCX files in a directory and its subdirectories
    
    Args:
        directory_path: Path to the directory containing DOCX files
    """
    directory = Path(directory_path)
    if not directory.exists():
        print(f"Directory not found: {directory_path}")
        return
    
    # Find all DOCX files
    docx_files = list(directory.glob('**/*.docx'))
    
    if not docx_files:
        print(f"No DOCX files found in {directory_path}")
        return
    
    print(f"Found {len(docx_files)} DOCX files to convert")
    
    # Convert each file with a progress bar
    successful = 0
    failed = 0
    
    for docx_file in tqdm(docx_files, desc="Converting"):
        pdf_path = str(docx_file).replace('.docx', '.pdf')
        try:
            convert_docx_to_pdf(str(docx_file), pdf_path)
            successful += 1
        except Exception as e:
            print(f"\nFailed to convert {docx_file}: {str(e)}")
            failed += 1
    
    print(f"\nConversion complete: {successful} successful, {failed} failed")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        # Default to 'Data' folder in the current directory
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data')
    
    print(f"Processing DOCX files in: {data_dir}")
    process_directory(data_dir)