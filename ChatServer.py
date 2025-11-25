#!/usr/bin/env python3
import socket
import threading
from chatcore.protocol import encode_message, decode_message
from chatcore.handlers import broadcast_message, on_client_join, on_client_leave

HOST = "0.0.0.0"
PORT = 5555

clients = []  # holds sockets

def handle_client(conn, addr):
    on_client_join(addr)
    clients.append(conn)

    try:
        while True:
            raw = conn.recv(1024)
            if not raw:
                break

            sender, text = decode_message(raw)
            if text is None:
                continue

            print(f"[{sender}] {text}")

            # Broadcast raw bytes exactly as received
            broadcast_message(sender, raw, clients, exclude=conn)

    except ConnectionResetError:
        pass  
    finally:
        clients.remove(conn)
        on_client_leave(addr)
        conn.close()

def start_server():
    print(f"Server running on {HOST}:{PORT} ...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()

        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()

if __name__ == "__main__":
    start_server()
