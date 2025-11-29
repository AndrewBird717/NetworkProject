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

MY_COLOR = COLORS["red"]  # default self-message color
# -----------------------------------

if len(sys.argv) < 2:
    print("Usage: python ChatClient.py [SERVER_IP]")
    sys.exit(0)

SERVER = sys.argv[1]
PORT = 5555
username = input("Enter username: ")

CHAT_HISTORY = []


def clear_terminal():
    """Clear the terminal window."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        sys.stdout.write("\033[2J\033[H")  # ANSI wipe
        sys.stdout.flush()

def listen(sock):
    """Background thread to receive chat messages."""
    global MY_COLOR
    while True:
        try:
            raw = sock.recv(1024)
            if not raw:
                print("Server disconnected.")
                break

            sender, text = decode_message(raw)
            if sender:
                # Color my own messages only
                color = MY_COLOR if sender == username else COLORS["reset"]

                # store message
                CHAT_HISTORY.append((sender, text))

                clear_terminal()

                for s, t in CHAT_HISTORY:
                    if s.startswith(username):  # your own messages
                        print(f"{MY_COLOR}[{s}] {t}{COLORS['reset']}")
                    else:
                        print(f"[{s}] {t}")

                #sys.stdout.write("\r")  # move cursor to start of line
                #sys.stdout.write(f"{color}[{sender}] {text}{COLORS['reset']}\n")
                sys.stdout.write(f"[{username}] ")
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
                sock, tls_context, server_hostname=SERVER or "localhost"
            )
        except Exception as e:
            print(f"TLS handshake failed: {e}")
            return

        print("Connected over TLS! Type messages and press Enter.")

        thread = threading.Thread(target=listen, args=(tls_sock,), daemon=True)
        thread.start()

        # ----- SEND LOOP -----
        while True:
            try:
                msg = input(f"[{username}] ").strip()
                if not msg:
                    continue

                # ===== LOCAL COMMAND: /exit =====
                if msg == "/exit":
                    print("[SYSTEM] Exiting chat...")
                    tls_sock.close()
                    sys.exit(0)

                # ===== LOCAL COMMAND: /color <color> =====
                if msg.startswith("/color "):
                    global MY_COLOR
                    color_name = msg.split(maxsplit=1)[1].lower()
                    if color_name not in COLORS or color_name == "reset":
                        print("[SYSTEM] Valid colors: red, green, yellow, blue, magenta, cyan, white")
                        continue
                    MY_COLOR = COLORS[color_name]
                    print(f"[SYSTEM] Color changed to {color_name}")
                    continue

                # ===== REMOTE COMMAND: /refresh =====
                if msg == "/refresh":
                    clear_terminal()
                    tls_sock.sendall(encode_message(username, "/refresh"))
                    continue

                # ===== NORMAL MESSAGE =====
                tls_sock.sendall(encode_message(username, msg))

            except KeyboardInterrupt:
                print("\n[SYSTEM] Interrupted. Closing client...")
                tls_sock.close()
                sys.exit(0)

if __name__ == "__main__":
    start_client()
