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
    