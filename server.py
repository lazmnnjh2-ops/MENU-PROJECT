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

    r = requests.get(API_CATEGORIES)
    cache['categories'] = [item['strCategory'] for item in r.json()['meals']]

    r = requests.get(API_AREAS)
    cache['areas'] = [item['strArea'] for item in r.json()['meals']]

    r = requests.get(API_INGREDIENTS)
    cache['ingredients'] = [item['strIngredient'] for item in r.json()['meals']]

    with open("data/reference_GroupX.json", "w") as f:
        json.dump({
            "categories": cache['categories'],
            "areas": cache['areas'],
            "ingredients": cache['ingredients'][:50]  
        }, f, indent=4)

    print("Reference cache loaded and saved in data/reference_GroupX.json")
    return cache

reference_cache = load_reference_cache()
HOST = '0.0.0.0'
PORT = 5050

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Server listening on {HOST}:{PORT}")

def handle_client(client_conn, client_addr):
    print(f"New connection: {client_addr}")
    client_conn.send(b"Welcome to Recipe Discovery!\n")

    while True:
        try:
            data = client_conn.recv(8192).decode()
            if not data:
                break

            if data == "categories":
                client_conn.send(json.dumps(reference_cache['categories']).encode())
            elif data == "areas":
                client_conn.send(json.dumps(reference_cache['areas']).encode())
            elif data == "ingredients":
                client_conn.send(json.dumps(reference_cache['ingredients']).encode())
            elif data.startswith("search:"):
                name = data.split("search:")[1]
                client_conn.send(b"[]")  
            elif data.startswith("save:"):
                recipe_json = data.split("save:")[1]
                with open("data/saved_recipes.json", "a") as f:
                    f.write(recipe_json + "\n")
                client_conn.send(b"Saved")
            elif data == "quit":
                break

        except Exception as e:
            print(f"Client error: {e}")
            break

    client_conn.close()
    print(f"Connection closed: {client_addr}")


while True:
    client_conn, client_addr = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(client_conn, client_addr))
    client_thread.start()