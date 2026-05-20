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