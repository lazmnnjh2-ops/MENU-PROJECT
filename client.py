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