from bs4 import BeautifulSoup
import requests
import os
import argparse
from urllib.parse import urljoin

def folder_create(base_path):
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    return base_path

def download_images(images, base_folder, base_url, valid_extensions, images_per_folder=10):
    count = 0
    folder_index = 1
    current_folder = os.path.join(base_folder, f"batch_{folder_index}")
    folder_create(current_folder)
    stop_flag = False

    print(f"Total {len(images)} Images Found!")

    for i, image in enumerate(images):
        image_link = None

        try:
            image_link = image["data-srcset"]
        except KeyError:
            try:
                image_link = image["data-src"]
            except KeyError:
                try:
                    image_link = image["data-fallback-src"]
                except KeyError:
                    try:
                        image_link = image["src"]
                    except KeyError:
                        continue

        if image_link:
            image_link = urljoin(base_url, image_link)

            if any(image_link.lower().endswith(ext) for ext in valid_extensions):
                try:
                    r = requests.get(image_link, timeout=10).content
                    if count >= images_per_folder:
                        count = 0
                        folder_index += 1
                        current_folder = os.path.join(base_folder, f"batch_{folder_index}")
                        folder_create(current_folder)
                    
                    image_path = os.path.join(current_folder, f"image_{count+1}.jpg")
                    with open(image_path, "wb") as f:
                        f.write(r)
                    count += 1

                    if count % images_per_folder == 0:
                        # Ask user if they want to continue after every images_per_folder images
                        user_input = input(f"{count} images downloaded. Continue? (y/n): ")
                        if user_input.lower() == 'n':
                            print("Stopping download.")
                            stop_flag = True
                            break

                except Exception as e:
                    print(f"Failed to download image {i+1}: {e}")

    print(f"Total {count} Images Downloaded Out Of {len(images)}")
    return 1 if stop_flag else 0

def recursive_scrape(url, base_folder, depth, current_depth, valid_extensions):
    if current_depth > depth:
        return 0
    
    print(f"Scraping {url} at depth {current_depth}")

    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Failed to retrieve URL {url}: {e}")
        return 0

    images = soup.findAll('img')
    stop_flag = download_images(images, base_folder, url, valid_extensions)
    
    if stop_flag:
        return 1

    links = soup.findAll('a', href=True)
    for link in links:
        if stop_flag:
            return 1
        next_url = urljoin(url, link['href'])
        if next_url.startswith('http'):
            stop_flag = recursive_scrape(next_url, base_folder, depth, current_depth + 1, valid_extensions)
            if stop_flag:
                return 1

    return 0

def main():
    parser = argparse.ArgumentParser(description="Spider program to download images recursively.")
    parser.add_argument("url", help="The URL to scrape images from.")
    parser.add_argument("-r", action="store_true", help="Recursively download images.")
    parser.add_argument("-l", type=int, default=5, help="Maximum depth for recursive downloading. Default is 5.")
    parser.add_argument("-p", type=str, default="./data/", help="Path where the images will be saved. Default is ./data/.")
    
    args = parser.parse_args()

    valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

    folder_name = folder_create(args.p)

    if args.r:
        print("RECURSIVE\n")
        recursive_scrape(args.url, folder_name, args.l, 0, valid_extensions)
    else:
        r = requests.get(args.url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        images = soup.findAll('img')
        download_images(images, folder_name, args.url, valid_extensions)
        print("STOP2")

if __name__ == "__main__":
    main()
