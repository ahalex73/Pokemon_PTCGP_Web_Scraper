import json
import os

class Trainer:
    def __init__(self, name: str, expansion: str, trainer_category: str, description: str, rarity: str, illustrator:str):
        self.name = name
        self.expansion = expansion
        self.trainer_category = trainer_category        # Tool, Supporter, Item... 
        self.description = description
        self.illustrator = illustrator


    def to_dict(self):
        """Convert object to dictionary."""
        return self.__dict__
    
    def convert_to_json(self, filename: str):
        """ Convert Trainer class object into JSON and save to a file """
        with open(filename, "w") as file:
            json.dump(self.__dict__, file, indent=4)
        print(f"JSON data saved to {filename}")

    def append_to_json(self, filename: str):
        """Appends a Trainer object to a JSON file dynamically."""
        if os.path.exists(filename):
            with open(filename, "r") as file:
                try:
                    data = json.load(file)
                    if not isinstance(data, list):  
                        data = []
                except json.JSONDecodeError:
                    data = [] 
        else:
            data = []

        data.append(self.to_dict())

        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

        #print(f"Added {self.name} to {filename}")

