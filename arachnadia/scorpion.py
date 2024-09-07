from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import argparse

def extract_exif(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data is not None:
            print(f"EXIF data for {image_path}:")
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                print(f"  {tag}: {value}")
        else:
            print(f"No EXIF data found for {image_path}.")
    except Exception as e:
        print(f"Error extracting EXIF from {image_path}: {e}")

def display_metadata(file_paths):
    for file_path in file_paths:
        if os.path.isfile(file_path):
            print(f"\nProcessing file: {file_path}")
            extract_exif(file_path)
        else:
            print(f"{file_path} is not a valid file.")

def main():
    parser = argparse.ArgumentParser(description="Extract and display EXIF and other metadata from image files.")
    parser.add_argument("files", help="List of image files to process.", nargs='+')
    
    args = parser.parse_args()
    display_metadata(args.files)

if __name__ == "__main__":
    main()
