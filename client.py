import socket
import json


HOST = '127.0.0.1'
PORT = 5050

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

welcome_message = client_socket.recv(1024).decode()
print(f"Server says: {welcome_message}")

def send_request(request):

    client_socket.send(request.encode())

def receive_response():

    data = client_socket.recv(8192).decode()
    return json.loads(data)

if __name__ == "__main__":
    send_request("Hello Server")
    response = receive_response()
    print("Server Response:", response)

def show_categories():
    send_request("categories")
    categories = receive_response()
    print("\nCategories:")
    for c in categories:
        print(f"- {c}")

def show_areas():
    send_request("areas")
    areas = receive_response()
    print("\nAreas:")
    for a in areas:
        print(f"- {a}")

def show_ingredients():
    send_request("ingredients")
    ingredients = receive_response()
    print("\nIngredients:")
    for i in ingredients:
        print(f"- {i}")

if __name__ == "__main__":
    print(welcome_message)

    show_categories()
    show_areas()
    show_ingredients()    

def search_recipe():
    name = input("\nEnter recipe name to search: ")
    if not name:
        print("No name entered.")
        return
    send_request(f"search:{name}")
    recipes = receive_response()
    if not recipes:
        print("No recipes found.")
        return

    print("\nSearch Results:")
    for idx, r in enumerate(recipes, start=1):
        print(f"{idx}. {r['strMeal']} (Category: {r['strCategory']}, Area: {r['strArea']})")

    choice = input("\nEnter recipe number to save (or press Enter to skip): ")
    if choice.isdigit():
        choice = int(choice)
        if 1 <= choice <= len(recipes):
            selected = recipes[choice - 1]
            send_request(f"save:{json.dumps(selected)}")
            confirmation = client_socket.recv(1024).decode()
            print(f"Server Response: {confirmation}")
        else:
            print("Invalid choice.")
    else:
        print("Skipped saving.")