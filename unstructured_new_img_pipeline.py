import os
import json
from pathlib import Path
from unstructured.partition.pdf import partition_pdf

# Configure paths
INPUT_DIR = Path("New_Data")
JSON_OUTPUT_DIR = Path("new_pipelines_jsons")
IMAGES_OUTPUT_DIR = Path("new_un_images_pipeline")

# Create necessary directories if they don't exist
def setup_directories():
    INPUT_DIR.mkdir(exist_ok=True)
    JSON_OUTPUT_DIR.mkdir(exist_ok=True)
    IMAGES_OUTPUT_DIR.mkdir(exist_ok=True)

# Process each document in the input directory
def process_documents():
    for file_path in INPUT_DIR.glob("*.pdf"):
        try:
            elements = partition_pdf(
                filename=str(file_path),
                strategy="hi_res",
                extract_images_in_pdf=True,
                extract_image_block_output_dir=str(IMAGES_OUTPUT_DIR)
            )
            # Save JSON output
            json_output_path = JSON_OUTPUT_DIR / f"{file_path.stem}.json"
            with open(json_output_path, "w") as json_file:
                json.dump([element.to_dict() for element in elements], json_file)
            print(f"Processed {file_path.name} successfully.")
        except Exception as e:
            print(f"Failed to process {file_path.name}: {e}")

# Main function to run the pipeline
def main():
    setup_directories()
    process_documents()

if __name__ == "__main__":
    main()
