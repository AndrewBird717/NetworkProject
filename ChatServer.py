import socket
import threading
from chatcore.protocol import encode_message, decode_message
from chatcore.handlers import broadcast_message, on_client_join, on_client_leave
from chatcore.tls import create_server_context, wrap_server_connection
from chatcore.commands import CommandContext, handle_command
from chatcore.state import ChatState



HOST = "10.0.0.115"
PORT = 5555

clients = []  # holds sockets
state = ChatState()

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

            # --- /refresh command: just send this client full history ---
            if text.strip() == "/refresh":
                send_full_history(conn)
                continue

            # --- normal chat message: store + broadcast ---
            # normal chat message: store + broadcast with ID
            stored = state.add_message(sender, text)           # <-- get the assigned ID
            display_text = f"#{stored['id']} {text}"           # <-- prefix ID
            print(f"[{sender}] {display_text}")                # server console shows ID
            payload = encode_message(sender, display_text)     # broadcast with ID
            broadcast_message(sender, payload, clients)        # send to all


    except ConnectionResetError:
        pass
    finally:
        if conn in clients:
            clients.remove(conn)
        on_client_leave(addr)
        conn.close()


def send_full_history(conn):
    """Send the entire chat history to a single client."""
    for msg in state.all_messages():
        display_text = f"#{msg['id']} {msg['text']}"   # <-- ADD ID HERE
        payload = encode_message(msg["sender"], display_text)       
        try:
            conn.sendall(payload)
        except:
            break



def start_server():
    print(f"Server running on {HOST}:{PORT} ...")

    tls_context = create_server_context(
        certfile="server.crt",
        keyfile="server.key",
    )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()

        while True:
            conn, addr = server.accept()

            try:
                tls_conn = wrap_server_connection(conn, tls_context)
            except Exception as e:
                print(f"TLS handshake failed with {addr}: {e}")
                conn.close()
                continue

            thread = threading.Thread(target=handle_client, args=(tls_conn, addr), daemon=True)
            thread.start()



if __name__ == "__main__":
    start_server()
