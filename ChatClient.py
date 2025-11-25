import socket
import threading
import sys
from chatcore.protocol import encode_message, decode_message
from chatcore.tls import create_client_context, wrap_client_socket


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
        tls_context = create_client_context(verify=False)

        try:
            tls_sock = wrap_client_socket(
                sock,
                tls_context,
                server_hostname=SERVER or "localhost",
            )
        except Exception as e:
            print(f"TLS handshake failed: {e}")
            return

        print("Connected over TLS! Type messages and press Enter.")
        
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
