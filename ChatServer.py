import socket
import threading
from chatcore.protocol import encode_message, decode_message
from chatcore.handlers import broadcast_message, on_client_join, on_client_leave
from chatcore.tls import create_server_context, wrap_server_connection
from chatcore.commands import CommandContext, handle_command



HOST = "10.0.0.115"
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

            # Build a context object for command handling
            ctx = CommandContext(
                conn=conn,
                sender=sender,
                clients=clients,
                broadcast_message=broadcast_message,
                encode_message=encode_message,
            )

            # If it's a slash-command, let the commands module handle it
            if handle_command(ctx, text):
                # Command handled (or at least recognized)
                # -> don't treat it as a normal chat message
                continue

            # Normal chat message (no leading "/")
            print(f"[{sender}] {text}")

            # Broadcast raw bytes exactly as received to others
            broadcast_message(sender, raw, clients, exclude=conn)

    except ConnectionResetError:
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

            thread = threading.Thread(target=handle_client, args=(tls_conn, addr), daemon=True)
            thread.start()



if __name__ == "__main__":
    start_server()
