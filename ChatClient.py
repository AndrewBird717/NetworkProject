import socket
import threading
import sys
import os
import platform
from chatcore.protocol import encode_message, decode_message
from chatcore.tls import create_client_context, wrap_client_socket

# -------- COLOR DEFINITIONS --------
COLORS = {
    "reset": "\033[0m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

MY_COLOR = COLORS["red"]  # default user message color

# -----------------------------------

if len(sys.argv) < 2:
    print("Usage: python ChatClient.py [SERVER_IP]")
    sys.exit(0)

SERVER = sys.argv[1]
PORT = 5555
username = input("Enter username: ")

def clear_terminal():
    """Clear the terminal screen on Windows or Unix-like OS."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        sys.stdout.write("\033[2J\033[H")  # ANSI clear for all modern terminals
        sys.stdout.flush()

def listen(sock):
    """Background thread to receive and print messages."""
    global MY_COLOR
    while True:
        try:
            raw = sock.recv(1024)
            if not raw:
                print("Server disconnected.")
                break

            sender, text = decode_message(raw)
            if sender:
                # Choose display color: my messages = MY_COLOR, others normal
                color = MY_COLOR if sender == username else COLORS["reset"]

                sys.stdout.write("\r")  # start of line
                sys.stdout.write(f"{color}[{sender}] {text}{COLORS['reset']}\n")
                sys.stdout.write(f"[{username}] ")  # redraw prompt
                sys.stdout.flush()

        except Exception:
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

        thread = threading.Thread(target=listen, args=(tls_sock,), daemon=True)
        thread.start()

        # ---------- SEND LOOP ----------
        while True:
            try:
                msg = input(f"[{username}] ")
                if not msg.strip():
                    continue

                # ----- LOCAL COMMAND: /color <name> -----
                if msg.startswith("/color "):
                    global MY_COLOR
                    color_name = msg.split(maxsplit=1)[1].strip().lower()
                    if color_name not in COLORS or color_name == "reset":
                        print("[SYSTEM] Valid colors: red, green, yellow, blue, magenta, cyan, white")
                        continue
                    MY_COLOR = COLORS[color_name]
                    print(f"[SYSTEM] Color changed to {color_name}")
                    continue  # don't send to server

                # ----- /refresh command -----
                if msg.strip() == "/refresh":
                    clear_terminal()
                    encoded = encode_message(username, "/refresh")
                    tls_sock.sendall(encoded)
                    continue

                # ----- NORMAL CHAT MESSAGE -----
                encoded = encode_message(username, msg)
                tls_sock.sendall(encoded)

            except KeyboardInterrupt:
                print("\nExiting...")
                break


if __name__ == "__main__":
    start_client()
