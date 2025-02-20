import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import time
import re
from Pokemon import Pokemon
from Trainer import Trainer

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

colors = {

    # Energy colors
    "Green": "\033[38;5;077m",      # Grass
    "Red": "\033[38;5;167m",        # Fire
    "Blue": "\033[38;5;080m",       # Water
    "Yellow": "\033[38;5;185m",     # Lightning
    "Magenta": "\033[38;5;098m",    # Psychic
    "Orange": "\033[38;5;173m",     # Fighting
    "Dark Gray": "\033[38;5;060m",  # Darkness
    "White": "\033[38;5;231m",      # Metal
    "Light Blue": "\033[38;5;168m", # Dragon
    "Reset": "\033[0m",             # Colorless

    # Additional colors
    "Light Gray": "\033[38;5;102m",      # Light Gray  (102)
    "Olive Green": "\033[38;5;138m",     # Olive Green (138)
    "Light Aqua": "\033[38;5;144m",      # Light Aqua  (144)
    "Dark Yellow": "\033[38;5;108m",     # Dark Yellow (108)
    "Brown": "\033[38;5;109m",           # Brown       (109)
    "Olive": "\033[38;5;103m",           # Olive       (103)
    "Sea Green": "\033[38;5;139m",       # Sea Green   (139)
    "Soft Pink": "\033[38;5;145m",       # Soft Pink   (145)

    # Underlined Additional colors
    "Underlined Light Gray": "\033[4m\033[38;5;102m",  # Underlined Light Gray (102)
    "Underlined Olive Green": "\033[4m\033[38;5;138m", # Underlined Olive Green (138)
    "Underlined Light Aqua": "\033[4m\033[38;5;144m",  # Underlined Light Aqua (144)
    "Underlined Dark Yellow": "\033[4m\033[38;5;108m", # Underlined Dark Yellow (108)
    "Underlined Brown": "\033[4m\033[38;5;109m",       # Underlined Brown (109)
    "Underlined Olive": "\033[4m\033[38;5;103m",       # Underlined Olive (103)
    "Underlined Sea Green": "\033[4m\033[38;5;139m",   # Underlined Sea Green (139)
    "Underlined Soft Pink": "\033[4m\033[38;5;145m",   # Underlined Soft Pink (145)

    # Blue Gradient
    "GB1": "\033[38;5;195m",
    "GB2": "\033[38;5;159m",
    "GB3": "\033[38;5;123m",
    "GB4": "\033[38;5;087m",
    "GB5": "\033[38;5;051m",
    "GB6": "\033[38;5;044m",
    "GB7": "\033[38;5;037m",
    "GB8": "\033[38;5;030m",
    "GB9": "\033[38;5;023m",

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

            print("\n\t\t\t\t Scraping Complete! \U0001F44B\n")
            return False

    except KeyboardInterrupt:
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

        expansion_image_dir = os.path.join(IMAGES_BASE_DIR + "/" + expansion_name)
        expansion_card_info_dir = os.path.join(CARD_DATA_BASE_DIR + "/" + expansion_name) 
        os.makedirs(expansion_image_dir, exist_ok=True) 
        os.makedirs(expansion_card_info_dir, exist_ok=True) 

        if target_div:
            # These links are all of the pokemon listed for each specific expansion
            # but we need to go to each specific associated webpage for each to scrape all of the data

            links_inside = [a["href"] for a in target_div.find_all("a")]  # Get all individual pokemon links
            print(f"\n\nFound links for {expansion_name}\n\n")
            time.sleep(1)

            for link in links_inside:
                postfix = link.lstrip("/cards")
                individual_pokemon_url = BASE_URL + "/" + postfix
                response = requests.get(individual_pokemon_url, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")
                # We are now on a specific pokemon page such as "https://pocket.limitlesstcg.com/cards/A2/1" - Oddish from Space-Time Smackdown (A2)
                
                if response.status_code == 200:
                    scrape_and_store(soup, expansion_name, expansion_image_dir, postfix)

                    response.close()
                else:
                    print(f" \U0001F635 Failed to scrape {individual_pokemon_url}. Status code: \033[41m{response.status_code} \033[0m")
                    response.close()
                    continue

        response.close()

    return False

def scrape_and_store(soup, expansion_name, expansion_image_dir, postfix):
    img = soup.find(class_="card shadow resp-w")
    pokemon_name = soup.find(class_= "card-text-name").text

    if "src" in img.attrs:
        img_url = img["src"]

        img_response = requests.get(img_url, headers=headers)
        if img_response.status_code == 200:
            img_data = BytesIO(img_response.content)

            # try:
            postfix = postfix.replace("/", "_")
            pokemon_name = pokemon_name.replace(" ", "-")

            webp_path = os.path.join(expansion_image_dir, f"{pokemon_name}_{postfix}.webp")
            json_path = os.path.join(CARD_DATA_BASE_DIR, expansion_name, ".json")

            get_json_info(soup, json_path)

            if os.path.exists(webp_path):
                #print(f"{colors['Light Gray']}Image {pokemon_name}_{postfix}.webp already exists, skipping download.{colors['Reset']}\n")
                return  

            else:
                os.makedirs(os.path.dirname(webp_path), exist_ok=True)
                img_obj = Image.open(img_data)
                img_obj.save(webp_path, "WEBP")

            # except Exception as e:
            #     print(f"Failed to process {img_url}: {e}")
        else:
            print(f"Failed to download {img_url}. Status Code: {img_response.status_code}")
    return

def get_json_info(soup, json_path):
    is_trainer = is_trainer_card(soup)
    if is_trainer:
        # We have a Trainer!
        name, expansion, trainer_category, description, rarity, illustrator = get_trainer_info(soup) #Already have category: Tool, Item, Supporter
        t = Trainer(name, expansion, trainer_category, description, rarity, illustrator)
        t.append_to_json(json_path)

        print(f"{colors['GB1']}Trainer: {name}{colors['Reset']}, "
              f"{colors['GB2']}Expansion: {expansion}{colors['Reset']}, "
              f"\n{colors['GB3']}Description: {description}{colors['Reset']}\n "
              f"{colors['GB4']}Category {trainer_category}{colors['Reset']}, "
              f"{colors['GB5']}Rarity = {rarity}{colors['Reset']}, "
              f"{colors['GB6']}Illustrator = {illustrator}{colors['Reset']}, \n"
            ) 
        return
    
    else:
        # We have a Pokemon!
        name, expansion, hp, card_type, rarity, stage, ability_dict, weakness, retreat, illustrator, energy_dict_list, abilities, special_ability_name, special_ability_description = get_pokemon_info(soup)
        p = Pokemon(name, expansion, hp, card_type, rarity, stage, ability_dict, None, energy_dict_list, weakness, retreat, illustrator, special_ability_name, special_ability_description)
        p.append_to_json(json_path)

        print(f"{colors['GB1']}{name}{colors['Reset']}, "
            f"{colors['GB2']}Expansion = {expansion}{colors['Reset']}, "
            f"{colors['GB3']}Type = {card_type}{colors['Reset']}, "
            f"{colors['GB4']}HP = {hp}{colors['Reset']}, "
            f"{colors['GB5']}Rarity = {rarity}{colors['Reset']}, "
            f"{colors['GB6']}Stage = {stage}{colors['Reset']}, "
            f"{colors['GB7']}Weakness = {weakness}{colors['Reset']}, "
            f"{colors['GB8']}Retreat = {retreat}{colors['Reset']},"
            f"{colors['GB8']} {illustrator}{colors['Reset']}"
            ) 

        # print(f"\t\U00002728 {colors['GB1']}Abilities = {abilities}{colors['Reset']}", end = " ")  # Output: {'Blot': '10', 'Flame Burst': '30'}
        # display_energy_cost(energy_dict_list)
        # print("\n")

    return

def get_pokemon_info(soup):
    special_ability_name = ""
    special_ability_description = ""

    if has_special_ability(soup):
        special_ability_name, special_ability_description = get_special_ability(soup)

    name = soup.find(class_="card-text-name").text.strip()
    expansion = soup.find(class_="text-lg").text.strip()
    rarity = get_card_rarity(soup)

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
    
    illustrator_token_div = soup.find(class_="card-text-section card-text-artist")
    illustrator = illustrator_token_div.find("a").text.strip().title()
    attack_infos = soup.find_all("p", class_="card-text-attack-info")
    abilities = []
    energy_dict_list = []
    ability_dict = {}
    for attack in attack_infos:
        text = attack.get_text(separator=" ", strip=True) 
        words = text.split()

        energy_dict = get_energy_cost(words[0])
        energy_dict_list.append(energy_dict)

        words = words[1:]

        if len(words) >= 2:
            ability_name = " ".join(words[:-1])
            ability_damage = words[-1]
        else:
            ability_name = words[0]
            ability_damage = 0

        ability_dict[ability_name] = ability_damage
        abilities.append(ability_dict)
    
    return name, expansion, hp, card_type, rarity, stage, ability_dict, weakness, retreat, illustrator, energy_dict_list, abilities, special_ability_name, special_ability_description

def has_special_ability(soup):
        ability = soup.find(class_="card-text-ability-info")
        if ability == None:
            return False
        return True

def get_special_ability(soup):
    special_ability_name = soup.find(class_="card-text-ability-info").text.split("Ability:")[1].strip()
    special_ability_description = soup.find(class_="card-text-ability-effect").text.replace("\t", "").replace("\n", "").replace("\r", "").strip()
    return special_ability_name, special_ability_description

def is_trainer_card(soup):
    token = soup.find(class_="card-text-type").text.strip().split("-")

    if len(token) < 2:
        return False
    
    match_str = " - ".join(token)

    pattern = r"(\w+)\s*-\s*(\w+)"
    match = re.match(pattern, match_str)

    if match:
        category, subcategory = match.groups()
        
        if category == "Trainer":
            return True
        else:
            return False

    return False

def get_trainer_info(soup):
    rarity = get_card_rarity(soup)
    expansion = soup.find(class_="text-lg").text.strip()
    card_desc_section_token = soup.find_all("div", class_="card-text-section")
    
    if len(card_desc_section_token) > 1:
        name = card_desc_section_token[0].get_text(separator=" ", strip=True).split(" ")[0]
        trainer_category = card_desc_section_token[0].get_text(separator="- ", strip=True).split(" ")[-1]
        description = card_desc_section_token[1].get_text(separator=" ", strip=True).strip()
    else:
        name = card_desc_section_token[0].get_text(separator=" ", strip=True).split(" ")[0]

    illustrator_token_div = soup.find(class_="card-text-section card-text-artist")
    illustrator = illustrator_token_div.find("a").text.strip().title()

    return name, expansion, trainer_category, description, rarity, illustrator

def get_card_rarity(soup):
    second_span = soup.select_one(".prints-current-details span:nth-of-type(2)")

    rarity_dict = {
        "◊": "one-diamond",
        "◊◊": "two-diamond",
        "◊◊◊": "three-diamond",
        "◊◊◊◊": "four-diamond",
        "☆": "one-star",
        "☆☆": "two-star",
        "☆☆☆": "three-star",
        "Crown Rare": "crown" 
    }

    if second_span:
        rarity_token = second_span.get_text(strip=True)  
        pattern = r"(◊{1,4})|(☆{1,3})|(Crown Rare)"       
        match = re.search(pattern, rarity_token)

        if match:
            found_rarity = match.group(0)                            
            rarity_value = rarity_dict.get(found_rarity, "unknown")
            return rarity_value

    return "unknown"

def tokenize_card_title(title):
    parts = title.rsplit('-', 2)         # Split from the right, at most 2 times
    return parts[1], int(parts[2][:-2])  # Extract type and remove "HP"

def get_energy_cost(energy_token):
    # EX: 'GFWL' from database will make energy_dict = {Grass: 1, Fire : 1, Water: 1, Lightning: 1} 

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

    # Assume word contains energy type symbols (e.g., "G", "F", "W", etc.)
    for i in energy_token:
        match i:
            case "G":
                energy_dict["Grass"] += 1
            case "R": 
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
            case "Dr":  
                energy_dict["Dragon"] += 1   # Dragon isnt in the game yet
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
        "Grass":     colors["Green"],      
        "Fire":      colors["Red"],         
        "Water":     colors["Blue"],       
        "Lightning": colors["Yellow"], 
        "Psychic":   colors["Magenta"],  
        "Fighting":  colors["Orange"],  
        "Darkness":  colors["Dark Gray"],
        "Metal":     colors["White"],      
        "Dragon":    colors["Light Blue"], 
        "Colorless": colors["Reset"]  
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
            colored_value = f"{energy_colors.get(key, '')}{value}\033[0m"
            items.append(f"'{colored_key}': {colored_value}")
        output += ", ".join(items)
        output += "}"
        if i < len(energy_dict_list) - 1:
            output += ", "
    output += "]"
    
    print(output, end = ' ')

if __name__=="__main__":
    main()