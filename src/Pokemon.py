import json

class Pokemon:
    def __init__(self, name: str, expansion: str, hp: int, type: str, stage: str, abilities_dict: dict, ability_description_array: list, weakness: str, retreat: int, illustrator: str, CARD_DATA_BASE_DIR):
        self.name = name
        self.expansion = expansion
        self.hp = hp
        self.type = type
        self.stage = stage
        self.abilities_dict = abilities_dict
        self.abilities_description_array = []
        self.weakness = weakness
        self.retreat = retreat
        self.illustrator = illustrator
    
    def convert_to_json(self, filename: str):
        """ Convert Pokemon class object into JSON and save to a file """
        with open(filename, "w") as file:
            json.dump(self.__dict__, file, indent=4)
        print(f"JSON data saved to {filename}")