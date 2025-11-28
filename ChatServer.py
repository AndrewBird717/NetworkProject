import socket
import threading

from chatcore.protocol import encode_message, decode_message
from chatcore.handlers import broadcast_message, on_client_join, on_client_leave
from chatcore.tls import create_server_context, wrap_server_connection
from chatcore.state import ChatState
from chatcore.commands import CommandContext, handle_command

HOST = "10.0.0.115"   # adjust if needed
PORT = 5555

clients = []          # list of active client sockets
state = ChatState()   # shared in-memory chat history


def send_full_history(conn):
    """
    Send the entire chat history (with IDs) to a single client.
    Used by the /refresh command.
    """
    for msg in state.all_messages():
        display_text = f"#{msg['id']} {msg['text']}"
        payload = encode_message(msg["sender"], display_text)
        try:
            conn.sendall(payload)
        except Exception:
            break


def handle_client(conn, addr):
    """
    Per-client handler: receive messages, route commands,
    and broadcast chat to others.
    """
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

            # Build command context for this message
            ctx = CommandContext(
                conn=conn,
                sender=sender,
                state=state,
                clients=clients,
                send_full_history=send_full_history,
                broadcast_message=broadcast_message,
            )

            # 1) If the text is a command (starts with "/"), handle it
            if handle_command(ctx, text):
                # Command was processed (or rejected). Do not treat as chat.
                continue

            # 2) Normal chat message: store + broadcast with ID
            stored = state.add_message(sender, text)
            display_text = f"#{stored['id']} {text}"

            print(f"[{sender}] {display_text}")

            payload = encode_message(sender, display_text)
            # Broadcast to all clients (including sender)
            broadcast_message(sender, payload, clients)

    except ConnectionResetError:
        # Client disconnected abruptly
        pass

    finally:
        if conn in clients:
            clients.remove(conn)
        on_client_leave(addr)
        conn.close()


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

            thread = threading.Thread(
                target=handle_client,
                args=(tls_conn, addr),
                daemon=True,
            )
            thread.start()


if __name__ == "__main__":
    start_server()
