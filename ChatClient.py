#!/usr/bin/env python3
import socket
import threading
import sys
from chatcore.protocol import encode_message, decode_message

if len(sys.argv) < 2:
    print("Usage: python ChatClient.py [SERVER_IP]")
    sys.exit(0)

SERVER = sys.argv[1]
PORT = 5555

username = input("Enter username: ")

def listen(sock):
    """Background thread to receive messages."""
    while True:
        try:
            raw = sock.recv(1024)
            if not raw:
                print("Server disconnected.")
                break

            sender, text = decode_message(raw)
            if sender:
                print(f"\n[{sender}] {text}")
        except:
            break

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((SERVER, PORT))
        except:
            print("Could not connect to server.")
            return

        print("Connected! Type messages and press Enter.")
        
        thread = threading.Thread(target=listen, args=(sock,), daemon=True)
        thread.start()

        while True:
            try:
                msg = input()
                encoded = encode_message(username, msg)
                sock.sendall(encoded)
            except KeyboardInterrupt:
                print("\nExiting...")
                break

if __name__ == "__main__":
    start_client()
