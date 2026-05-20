import socket
import json
import threading

HOST = '127.0.0.1'
PORT = 5050

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
welcome = client_socket.recv(1024).decode()
print(welcome)

def send_request_async(request, callback=None):
    def target():
        try:
            client_socket.send(request.encode())
            response = client_socket.recv(8192).decode()
            if callback:
                callback(response)
        except Exception as e:
            print(f"[Client Error] {e}")
    threading.Thread(target=target, daemon=True).start()

def handle_list_response(data):
    items = json.loads(data)
    for i, item in enumerate(items, start=1):
        print(f"{i}. {item}")

def handle_search_response(data):
    recipes = json.loads(data)
    if not recipes:
        print("No recipes found.")
        return
    for idx, rec in enumerate(recipes, start=1):
        print(f"{idx}. {rec['strMeal']}")
    choice = input("Enter number to see details: ")
    try:
        sel = recipes[int(choice)-1]
        print(f"Name: {sel['strMeal']}")
        print(f"Category: {sel['strCategory']}")
        print(f"Area: {sel['strArea']}")
        print(f"Instructions: {sel['strInstructions']}")
    except:
        print("Invalid choice.")

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
            send_request_async("categories", handle_list_response)
        elif choice == "2":
            send_request_async("areas", handle_list_response)
        elif choice == "3":
            send_request_async("ingredients", handle_list_response)
        elif choice == "4":
            name = input("Enter recipe name: ")
            send_request_async(f"search:{name}", handle_search_response)
        elif choice == "5":
            send_request_async("quit")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    print(welcome)
    main_menu()
    client_socket.close()