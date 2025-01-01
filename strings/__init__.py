import yaml

def strings():
    try:
        with open("./strings/english.yml", encoding="utf8") as file:
            english_strings = yaml.safe_load(file)
            return english_strings
    except Exception as e:
        print("Error loading the language file ", e)
        return {}


strings = strings()  

# Importing helpers and image
from .helpers import *
#from .image import Photos
