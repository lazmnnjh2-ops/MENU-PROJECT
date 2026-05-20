import json
class Message:
    BUFFER_SIZE = 4096
    DELIMITER = '\n'

def send_message(sock, data):
    try:
        message = json.dumps(data) +  Message.DELIMITER
        sock.sendall(message.encode('utf-8'))
        return True
    except Exception as e:
      print(f"[protocol Error]Failed to send message: {e}")
def recv_message(sock):
    try:
        buffer=''
        while Message.DELIMITER not in buffer:
            chunk = sock.recv(Message.BUFFER_SIZE).decode('utf-8')
            if not chunk:
                raise None
            buffer += chunk
        message_str,_,_= buffer.partition(Message.DELIMITER)
        return json.loads(message_str)
    except json.JSONDecodeError as e:
        print(f"[protocol Error]Failed to decode message: {e}")
        return None
    except Exception as e:
        print(f"[protocol Error]Failed to receive message: {e}")
        return None
    
if __name__ == "__main__":
    print("protocol.py - Module Test")
    print("Class: Message")
    print("Methods:")
    print("  - send(sock, data)")
    print("  - receive(sock)")

