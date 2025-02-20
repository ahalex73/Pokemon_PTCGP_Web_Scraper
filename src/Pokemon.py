import json
import os

class Pokemon:
    def __init__(self, name: str, expansion: str, hp: int, pokemon_type: str, rarity: str, stage: str, abilities_dict: dict, ability_description_array: list, energy_dict_list: list, weakness: str, retreat: int, illustrator: str, special_ability_name: str, special_ability_description:str):
        self.name = name
        self.expansion = expansion
        self.hp = hp
        self.pokemon_type = pokemon_type
        self.rarity = rarity
        self.stage = stage
        self.abilities_dict = abilities_dict
        self.special_ability_name = special_ability_name
        self.special_ability_description = special_ability_description
        self.energy_dict_list = energy_dict_list
        self.weakness = weakness
        self.retreat = retreat
        self.illustrator = illustrator


    def to_dict(self):
        """Convert object to dictionary."""
        return self.__dict__
    
    def convert_to_json(self, filename: str):
        """ Convert Pokemon class object into JSON and save to a file """
        with open(filename, "w") as file:
            json.dump(self.__dict__, file, indent=4)
        print(f"JSON data saved to {filename}")

    def append_to_json(self, filename: str):
        """Appends a Pokémon object to a JSON file dynamically."""
        # Check if the file exists and has valid JSON
        if os.path.exists(filename):
            with open(filename, "r") as file:
                try:
                    data = json.load(file)
                    if not isinstance(data, list):  # Ensure it's a list
                        data = []
                except json.JSONDecodeError:
                    data = []  # If JSON is corrupt, reset to empty list
        else:
            data = []

        # Append the new Pokémon
        data.append(self.to_dict())

        # Write back the updated JSON
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

        #print(f"Added {self.name} to {filename}")

