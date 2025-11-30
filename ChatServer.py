import socket
import threading

from chatcore.protocol import encode_message, decode_message
from chatcore.handlers import broadcast_message, on_client_join, on_client_leave
from chatcore.tls import create_server_context, wrap_server_connection
from chatcore.state import ChatState
from chatcore.commands import CommandContext, handle_command

HOST = "10.0.0.115"     # change if needed
PORT = 5555

clients = []            # active TLS sockets
state = ChatState()     # shared message history

# ----- CLIENT ID MANAGEMENT -----
next_client_id = 0                  # will increment per client
client_ids = {}                     # conn -> numeric ID
MAX_CLIENTS = 10000                 # hard user cap

client_usernames = {}


def send_full_history(conn):
    """
    Sends the entire chat history to a single client.
    Each message is shown with its message ID (#n).
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
    Handle a single client connection.
    Parses commands and broadcasts messages with unique sender IDs.
    """
    global next_client_id

    on_client_join(addr)
    clients.append(conn)

    # ---- ASSIGN CLIENT ID ----
    client_id = next_client_id
    next_client_id += 1
    client_ids[conn] = client_id

    # Tell the client their unique ID
    if client_usernames == {}:
        conn.sendall(encode_message("SYSTEM", f"No Connected Users"))
    else:
        temp = []
        for _, username in client_usernames.items():
            temp.append(username)
        conn.sendall(encode_message("SYSTEM", f"Connected Users: {temp}"))



    conn.sendall(encode_message("SYSTEM", f"/id {client_id}"))
    

    try:
        while True:
            raw = conn.recv(1024)
            if not raw:
                break

            sender, text = decode_message(raw)
            if text is None:
                continue
            # Store username if first message from this client
            if conn not in client_usernames:
                client_usernames[conn] = sender


            # Build command context
            ctx = CommandContext(
                conn=conn,
                sender=sender,
                state=state,
                clients=clients,
                send_full_history=send_full_history,
                broadcast_message=broadcast_message,
            )

            # 1) Run commands like /refresh, /delete
            if handle_command(ctx, text):
                continue  # command handled, skip normal broadcast

            # 2) NORMAL MESSAGE → store and broadcast
            uname = client_usernames.get(conn, sender)
            stored = state.add_message(uname, text)
            display_text = f"#{stored['id']} {text}"

            # sender label WITH ID
            sender_id = client_ids[conn]
            sender_label = f"{uname}#{sender_id:04d}"   # zero-padded 5 digits

            print(f"[{sender_label}] {display_text}")

            payload = encode_message(sender_label, display_text)
            broadcast_message(sender_label, payload, clients)

    except ConnectionResetError:
        # client killed connection
        pass

    finally:
        # cleanup
        if conn in clients:
            clients.remove(conn)

        if conn in client_ids:
            del client_ids[conn]

        on_client_leave(addr)
        conn.close()


def start_server():
    print(f"Server running on {HOST}:{PORT} ...")

    # TLS configuration
    tls_context = create_server_context(
        certfile="server.crt",
        keyfile="server.key",
    )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()

        while True:
            conn, addr = server.accept()

            # PREVENT OVER-CAPACITY
            if len(clients) >= MAX_CLIENTS:
                conn.sendall(encode_message("SYSTEM", "Server full (10,000 users max)."))
                conn.close()
                continue

            # TLS handshake
            try:
                tls_conn = wrap_server_connection(conn, tls_context)
            except Exception as e:
                print(f"TLS handshake failed with {addr}: {e}")
                conn.close()
                continue

            thread = threading.Thread(
                target=handle_client,
                args=(tls_conn, addr),
                daemon=True
            )
            thread.start()


if __name__ == "__main__":
    start_server()
