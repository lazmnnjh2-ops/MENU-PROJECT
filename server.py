import socket
import threading
import requests
import json
import os
import datetime

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

    r = requests.get(API_CATEGORIES)
    cache['categories'] = [item['strCategory'] for item in r.json()['meals']]

    r = requests.get(API_AREAS)
    cache['areas'] = [item['strArea'] for item in r.json()['meals']]

    r = requests.get(API_INGREDIENTS)
    cache['ingredients'] = [item['strIngredient'] for item in r.json()['meals']]

    with open(f"{DATA_FOLDER}/reference_GroupX.json", "w") as f:
        json.dump({
            "categories": cache['categories'],
            "areas": cache['areas'],
            "ingredients": cache['ingredients'][:50]  
        }, f, indent=4)

    print("Reference cache loaded and saved in data/reference_GroupX.json")
    return cache

reference_cache = load_reference_cache()

LOG_FILE = f"{DATA_FOLDER}/server_log.txt"

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}\n"
    print(entry, end="")
    with open(LOG_FILE, "a") as f:
        f.write(entry)

def search_recipe_by_name(name):
    results = []
    for cat in reference_cache['categories']:
        if name.lower() in cat.lower():
            results.append({
                "strMeal": cat,
                "strCategory": cat,
                "strArea": "Unknown",
                "strInstructions": "Check API"
            })
    return results

def save_recipe(recipe):
    file_path = f"{DATA_FOLDER}/saved_recipes.json"
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump([], f)
    with open(file_path, "r+") as f:
        data = json.load(f)
        data.append(recipe)
        f.seek(0)
        json.dump(data, f, indent=4)

HOST = '0.0.0.0'
PORT = 5050

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Server listening on {HOST}:{PORT}")

def handle_client(client_conn, client_addr):
    log_event(f"New connection: {client_addr}")
    client_conn.send(b"Welcome to Recipe Discovery!\n")

    while True:
        try:
            data = client_conn.recv(8192).decode()
            if not data:
                break

            if data.lower() == "quit":
                break

            elif data.lower() == "categories":
                log_event(f"{client_addr} requested categories")
                client_conn.send(json.dumps(reference_cache['categories']).encode())

            elif data.lower() == "areas":
                log_event(f"{client_addr} requested areas")
                client_conn.send(json.dumps(reference_cache['areas']).encode())

            elif data.lower() == "ingredients":
                log_event(f"{client_addr} requested ingredients")
                client_conn.send(json.dumps(reference_cache['ingredients']).encode())

            elif data.startswith("search:"):
                name = data.split("search:")[1]
                recipes = search_recipe_by_name(name)
                log_event(f"{client_addr} searched for: {name}")
                client_conn.send(json.dumps(recipes).encode())

            elif data.startswith("save:"):
                recipe_json = json.loads(data.split("save:")[1])
                save_recipe(recipe_json)
                log_event(f"{client_addr} saved recipe: {recipe_json['strMeal']}")
                client_conn.send(b"Saved")

            else:
                client_conn.send(b"Unknown command")

        except Exception as e:
            log_event(f"Error with {client_addr}: {e}")
            break

    client_conn.close()
    log_event(f"Connection closed: {client_addr}")

while True:
    client_conn, client_addr = server_socket.accept()
    threading.Thread(target=handle_client, args=(client_conn, client_addr)).start()