import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import time
import Pokemon
import re

BASE_URL = "https://pocket.limitlesstcg.com/cards"
SCRIPT_BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
CARD_DATA_BASE_DIR = os.path.join(SCRIPT_BASE_DIR, "../pokemon_data/card_data")  
IMAGES_BASE_DIR = os.path.join(SCRIPT_BASE_DIR, "../pokemon_data/images")  
os.makedirs(IMAGES_BASE_DIR, exist_ok=True) 
os.makedirs(CARD_DATA_BASE_DIR, exist_ok=True) 
 
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://pocket.limitlesstcg.com" 
    }

def main():

    try: 
        while True:
            response = requests.get(BASE_URL, headers=headers)
            if response.status_code != 200:
                print(f"Failed to access {BASE_URL}. Status code: {response.status_code}")
                exit()

            soup = BeautifulSoup(response.text, "html.parser")
            urls = get_urls(soup)
            scrape_pokemon_data(soup, urls)

    except KeyboardInterrupt:
        # Handle the Ctrl+C interruption
        print("\n\t\t\t\t\U0001F44B\n")

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
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        target_div = soup.find("div", class_="card-search-grid")
        expansion_name = soup.find("div", class_= 'infobox-heading sm').text
        image_dir = os.path.join(IMAGES_BASE_DIR + "/" + expansion_name)  
        os.makedirs(image_dir, exist_ok=True) 

        if target_div:
            # These links are all of the pokemon listed for each expansion
            # but we need to go to each specific associated webpage for each to scrape all of the data

            links_inside = [a["href"] for a in target_div.find_all("a")]  # Get all individual pokemon links
            print(f"\n\n\nFound links for {expansion_name}\n\n\n")
            time.sleep(1)

            for link in links_inside:
                postfix = link.lstrip("/cards")
                individual_pokemon_url = BASE_URL + "/" + postfix
                response = requests.get(individual_pokemon_url, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")
                # We are now on a specific pokemon page such as "https://pocket.limitlesstcg.com/cards/A2/1" - Oddish from Space-Time Smackdown (A2)
                
                if response.status_code == 200:
                    print(f"\033[4m{individual_pokemon_url}\033[0m Status code: \033[32m{response.status_code}\033[0m")
                    _get_pokemon_information(soup, expansion_name, image_dir, postfix)

                    response.close()
                else:
                    print(f" \U0001F635 Failed to scrape {individual_pokemon_url}. Status code: \033[41m{response.status_code} \033[0m")
                    response.close()
                    continue

        response.close()

    return 

def _get_pokemon_information(soup, expansion_name, image_dir, postfix):
    img = soup.find(class_="card shadow resp-w")
    pokemon_name = soup.find(class_= "card-text-name").text

    if "src" in img.attrs:
        img_url = img["src"]

        img_response = requests.get(img_url, headers=headers)
        if img_response.status_code == 200:
            img_data = BytesIO(img_response.content)

            try:
                postfix = postfix.replace("/", "_")
                pokemon_name = pokemon_name.replace(" ", "-")

                webp_path = os.path.join(image_dir, expansion_name, f"{pokemon_name}_{postfix}.webp")
                get_json_info(soup)

                if os.path.exists(webp_path):
                    print(f"Image {pokemon_name}_{postfix}.webp already exists, skipping download.\n")

                    return  

                else:
                    os.makedirs(os.path.dirname(webp_path), exist_ok=True)

                    print(f"Saving image as {webp_path}")
                    img_obj = Image.open(img_data)
                    img_obj.save(webp_path, "WEBP")


            except Exception as e:
                print(f"Failed to process {img_url}: {e}")
        else:
            print(f"Failed to download {img_url}. Status Code: {img_response.status_code}")

    return


def get_json_info(soup):
    time.sleep(.1)
    try:
        name = soup.find(class_="card-text-name").text.strip()
        expansion = soup.find(class_="text-lg").text.strip()
        title = soup.find(class_="card-text-title").text.replace(" ", "").replace("\t", "").replace("\n", "")
        card_type, hp = tokenize_card_title(title)
 
        stage_tok = soup.find(class_="card-text-type").text.strip().split("-")
        stage = stage_tok[1].strip()

        token = soup.find(class_="card-text-wrr").text.strip()
        pattern = r"Weakness:\s*(\S+).*?Retreat:\s*(\d+)"
        match = re.search(pattern, token, re.DOTALL)
        if match:
            weakness = match.group(1)  
            retreat = match.group(2) 
        else:
            print("No match found in:", token)
        
        attack_infos = soup.find_all("p", class_="card-text-attack-info")
        abilities = []
        energy_dict_list = []

        for attack in attack_infos:
            ability_dict = {}
            text = attack.get_text(separator=" ", strip=True) 
            words = text.split()  
            
            energy_dict = get_energy_cost(words[0])
            energy_dict_list.append(energy_dict)

            words = words[1:]

            if len(words) >= 2:
                ability_name = " ".join(words[:-1])
                ability_damage = words[-1]
            else:
                ability_name = "Null"
                ability_damage = 0

            ability_dict[ability_name] = ability_damage 
            abilities.append(ability_dict)

        print(f"\033[31m{name}\033[0m, "
              f"\033[32mExpansion = {expansion}\033[0m, "
              f"\033[34mType = {card_type}\033[0m, "
              f"\033[33mHP = {hp}\033[0m,",
              f"\033[96mStage = {stage}\033[0m,",
              f"\033[96mWeakness = {weakness}\033[0m,",
              f"\033[96mRetreat = {retreat}\033[0m,"
              )

        print(f"\u001b[35mAbilities: \u001b[0m{abilities}", end = " ")  # Output: {'Blot': '10', 'Flame Burst': '30'}
        display_energy_cost(energy_dict_list)

    except Exception as e:
        print(f"Missing information, something went wrong {e}")

    return

def tokenize_card_title(title):
    parts = title.rsplit('-', 2)         # Split from the right, at most 2 times
    return parts[1], int(parts[2][:-2])  # Extract type and remove "HP"

def get_energy_cost(energy_token):

    # EX: GFWL will make energy_dict = {Grass: 1, Fire : 1, Water: 1, Lightning: 1} 

    energy_dict = {
        "Grass": 0,
        "Fire": 0,
        "Water": 0,
        "Lightning": 0,
        "Psychic": 0,
        "Fighting": 0,
        "Darkness": 0,
        "Metal": 0,
        "Dragon": 0,
        "Colorless": 0,
    }

    # Assume words contains energy type symbols (e.g., "G", "F", "W", etc.)
    for i in energy_token:
        match i:
            case "G":
                energy_dict["Grass"] += 1
            case "F": 
                energy_dict["Fire"] += 1
            case "W":  
                energy_dict["Water"] += 1
            case "L":
                energy_dict["Lightning"] += 1
            case "P": 
                energy_dict["Psychic"] += 1
            case "F":  
                energy_dict["Fighting"] += 1
            case "D": 
                energy_dict["Darkness"] += 1
            case "M":
                energy_dict["Metal"] += 1
            # case "Dr":  
            #     energy_dict["Dragon"] += 1   Dragon isnt in the game yet
            case "C":
                energy_dict["Colorless"] += 1
            case _:
                continue  # Ignore unknown energy types or symbols

    try:
        parsed_dict = {}
        for key, value in energy_dict.items():
            if value >= 1:               
                parsed_dict[key] = value  

        #print(f"Parsed dict = {parsed_dict}")
    except Exception as e:
        print("Could not parse energy_list_dict", e)

    return parsed_dict

def display_energy_cost(energy_dict_list):
    # ANSI color mapping for energy types
    energy_colors = {
        "Grass": "\033[32m",     # Green
        "Fire": "\033[31m",      # Red
        "Water": "\033[34m",     # Blue
        "Lightning": "\033[33m", # Yellow
        "Psychic": "\033[35m",   # Magenta
        "Fighting": "\033[36m",  # Cyan
        "Darkness": "\033[90m",  # Dark Gray
        "Metal": "\033[37m",     # White
        "Dragon": "\033[94m",    # Light Blue
        "Colorless": "\033[0m",  # Reset (default color)
    }
    
    # Build a string that looks like a list of dictionaries
    output = "["
    for i, energy_dict in enumerate(energy_dict_list):
        output += "{"
        # Get all items and process them one by one.
        items = []
        for key, value in energy_dict.items():
            # Wrap only the key with its ANSI color code (the value remains unchanged)
            colored_key = f"{energy_colors.get(key, '')}{key}\033[0m"
            items.append(f"'{colored_key}': {value}")
        output += ", ".join(items)
        output += "}"
        if i < len(energy_dict_list) - 1:
            output += ", "
    output += "]"
    
    print(output)

if __name__=="__main__":
    main()