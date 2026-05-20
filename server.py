import socket
import threading
import requests
import json
import os

DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
    print(f"{DATA_FOLDER} folder created")
else:
    print(f"{DATA_FOLDER} folder already exists")

def load_reference_cache():
    cache = {}

    API_CATEGORIES = "https://www.themealdb.com/api/json/v1/1/list.php?c=list"
    API_AREAS = "https://www.themealdb.com/api/json/v1/1/list.php?a=list"
    API_INGREDIENTS = "https://www.themealdb.com/api/json/v1/1/list.php?i=list"

    # Categories
    r = requests.get(API_CATEGORIES)
    cache['categories'] = [item['strCategory'] for item in r.json()['meals']]

    # Areas
    r = requests.get(API_AREAS)
    cache['areas'] = [item['strArea'] for item in r.json()['meals']]

    # Ingredients
    r = requests.get(API_INGREDIENTS)
    cache['ingredients'] = [item['strIngredient'] for item in r.json()['meals']]

    # حفظ JSON
    with open("data/reference_GroupX.json", "w") as f:
        json.dump({
            "categories": cache['categories'],
            "areas": cache['areas'],
            "ingredients": cache['ingredients'][:50]  
        }, f, indent=4)

    print("Reference cache loaded and saved in data/reference_GroupX.json")
    return cache

reference_cache = load_reference_cache()