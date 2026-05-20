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

GCC_AREAS = [
    "Saudi Arabia", "United Arab Emirates", "Bahrain",
    "Kuwait", "Oman", "Qatar"
]

FAMOUS_CATEGORIES = [
    "Beef", "Chicken", "Seafood", "Pasta", "Vegetarian",
    "Dessert", "Breakfast", "Side", "Starter", "Lamb",
    "Pork", "Vegan", "Goat", "Miscellaneous"
]


def load_reference_cache():
    cache = {}
    API_CATEGORIES = "https://www.themealdb.com/api/json/v1/1/list.php?c=list"
    r = requests.get(API_CATEGORIES, timeout=10)
    all_cats = [item['strCategory'] for item in r.json()['meals']]
    cache['categories'] = [c for c in all_cats if c in FAMOUS_CATEGORIES]
    cache['categories'] = [c for c in FAMOUS_CATEGORIES if c in cache['categories']]

    cache['areas'] = GCC_AREAS

    API_INGREDIENTS = "https://www.themealdb.com/api/json/v1/1/list.php?i=list"
    r = requests.get(API_INGREDIENTS, timeout=10)
    cache['ingredients'] = [item['strIngredient'] for item in r.json()['meals']]

    with open(f"{DATA_FOLDER}/reference_Group3.json", "w") as f:
        json.dump({
            "categories": cache['categories'],
            "areas": cache['areas'],
            "ingredients": cache['ingredients'][:50]
        }, f, indent=4)

    print("Reference cache loaded and saved in data/reference_Group3.json")
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

def recv_full(conn):
    """Receive until we get a complete JSON (handles large payloads)."""
    data = b""
    while True:
        chunk = conn.recv(8192)
        if not chunk:
            break
        data += chunk
        try:
            data.decode('utf-8')
            break
        except UnicodeDecodeError:
            continue
    return data.decode('utf-8', errors='replace')

def send_large(conn, payload_bytes):
    """Send large data in chunks to avoid truncation."""
    total = len(payload_bytes)
    sent = 0
    while sent < total:
        chunk = payload_bytes[sent:sent+8192]
        conn.sendall(chunk)
        sent += len(chunk)

HOST = '0.0.0.0'
PORT = 5050

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

            data = data.strip()

            if data.lower() == "quit":
                break

            elif data.lower() == "categories":
                log_event(f"{client_addr} requested categories")
                payload = json.dumps(reference_cache['categories']).encode()
                send_large(client_conn, payload)

            elif data.lower() == "areas":
                log_event(f"{client_addr} requested areas")
                payload = json.dumps(reference_cache['areas']).encode()
                send_large(client_conn, payload)

            elif data.lower() == "ingredients":
                log_event(f"{client_addr} requested ingredients")
                payload = json.dumps(reference_cache['ingredients']).encode()
                length_header = f"{len(payload):<8}".encode()
                client_conn.sendall(length_header + payload)
                log_event(f"{client_addr} received {len(reference_cache['ingredients'])} ingredients ({len(payload)} bytes)")

            elif data.startswith("search:"):
                name = data.split("search:")[1]
                recipes = search_recipe_by_name(name)
                log_event(f"{client_addr} searched for: {name}")
                payload = json.dumps(recipes).encode()
                send_large(client_conn, payload)

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