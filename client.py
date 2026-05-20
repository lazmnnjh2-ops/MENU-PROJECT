import socket
import json

HOST = '127.0.0.1'  # localhost
PORT = 5050

# إنشاء الـ socket والاتصال بالسيرفر
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# استقبال رسالة الترحيب
welcome = client_socket.recv(1024).decode()
print(welcome)