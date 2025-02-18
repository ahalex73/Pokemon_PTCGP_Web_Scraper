import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import time

BASE_URL = "https://pocket.limitlesstcg.com/cards"
script_dir = os.path.dirname(os.path.abspath(__file__))  
card_data = os.path.join(script_dir, "../pokemon_data/card_data")  
images_base_dir = os.path.join(script_dir, "../pokemon_data/images")  
os.makedirs(images_base_dir, exist_ok=True) 

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://pocket.limitlesstcg.com" 
    }

def main():
    response = requests.get(BASE_URL, headers=headers)
    if response.status_code != 200:
        print(f"Failed to access {BASE_URL}. Status code: {response.status_code}")
        exit()

    soup = BeautifulSoup(response.text, "html.parser")
    urls = get_urls(soup)
    scrape_pokemon_data(soup, urls)

def get_urls(soup):
    urls = []

    for code in soup.find_all(class_="code annotation"):
        urls.append(BASE_URL + "/" + code.text)

    return urls

def scrape_pokemon_data(soup, urls):
    """ Postfix url codes: array of codes pointing to different databases for different expansions
        Ex: A2 = Space-Time Smackdown, such that URL = "https://pocket.limitlesstcg.com/cards/A2"
    """

    for url in urls:
        print(f"Main url: {url}")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        target_div = soup.find("div", class_="card-search-grid")
        expansion_name = soup.find("div", class_= 'infobox-heading sm').text
        image_dir = os.path.join(script_dir, "../pokemon_data/images/" + expansion_name)  
        os.makedirs(image_dir, exist_ok=True) 

        if target_div:
            # These links are all of the pokemon listed for each expansion
            # but we need to go to each specific associated webpage for each to scrape all of the data

            links_inside = [a["href"] for a in target_div.find_all("a")]  # Get all individual pokemon links
            print(f"Links found inside webpage {links_inside}")
            time.sleep(1)

            for link in links_inside:
                print(f"Link: {link}")
                postfix = link.lstrip("/cards")
                individual_pokemon_url = BASE_URL + "/" + postfix
                print(f"Individual pokemon link: {individual_pokemon_url}")
                response = requests.get(individual_pokemon_url, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")
                
                # We are now on a specific pokemon page such as "https://pocket.limitlesstcg.com/cards/A2/1" - Oddish from Space-Time Smackdown (A2)
                if response.status_code == 200:
                    print(f"\033[42m \U0001F4AF \033[0m Scraping {individual_pokemon_url}. Status code: {response.status_code}")
                    _gather_pokemon_information(soup, expansion_name, image_dir, postfix)


                    response.close()
                else:
                    print(f"\033[41m \U0001F635 \033[0m Failed to scrape {individual_pokemon_url}. Status code: {response.status_code}")
                    response.close()
                    continue

        response.close()

    return 

def _gather_pokemon_information(soup, expansion_name, image_dir, postfix):
    print("Trying to gather pokemon data... ")
    img = soup.find(class_="card shadow resp-w")
    pokemon_name = soup.find(class_= "card-text-name").text

    if "src" in img.attrs:
        img_url = img["src"]

        img_response = requests.get(img_url, headers=headers)
        if img_response.status_code == 200:
            img_data = BytesIO(img_response.content)  # Store image in memory

            try:
                print(postfix)
                postfix = postfix.replace("/", "_")
                pokemon_name = pokemon_name.replace(" ", "-")

                # Construct the full file path
                webp_path = os.path.join(image_dir, expansion_name, f"{pokemon_name}_{postfix}.webp")

                # Check if the file exists *before* creating the directory
                if os.path.exists(webp_path):
                    print(f"Image {webp_path} already exists, skipping download.")
                    return  # Exit early, no need to create directories or save

                else:
                    # Ensure the directory exists only when saving a new file
                    os.makedirs(os.path.dirname(webp_path), exist_ok=True)

                    print(f"Saving image as {webp_path}")
                    img_obj = Image.open(img_data)
                    img_obj.save(webp_path, "WEBP")

            except Exception as e:
                print(f"Failed to process {img_url}: {e}")
        else:
            print(f"Failed to download {img_url}. Status Code: {img_response.status_code}")

    return 


if __name__=="__main__":
    main()