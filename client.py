import socket
import json
from protocol import send_message, recv_message

HOST = '127.0.0.1'
PORT = 5050

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

welcome_message = client_socket.recv(1024).decode()
print(f"Server says: {welcome_message}")

def send_request(request):
    send_message(client_socket, request)

def receive_response():
    return recv_message(client_socket)

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

def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Show Categories")
        print("2. Show Areas")
        print("3. Show Ingredients")
        print("4. Search Recipe")
        print("5. Quit")
        choice = input("Enter choice: ")

        if choice == "1":
            show_categories()
        elif choice == "2":
            show_areas()
        elif choice == "3":
            show_ingredients()
        elif choice == "4":
            search_recipe()
        elif choice == "5":
            send_request("quit")
            print("Exiting client...")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    print(welcome_message)
    main_menu()
    client_socket.close()