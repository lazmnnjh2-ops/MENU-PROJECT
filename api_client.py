import requests
import json

BASE_URL = "http://example.com/api"

def get_data(endpoint):
        response = requests.get(f"{BASE_URL}/{endpoint}")
        return response.json()

def display_data(data):
    
    print(json.dumps(data, indent=4))


def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)



data=get_data("recipes")
display_data(data)
save_data("recipes.json", data)
