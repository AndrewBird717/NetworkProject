# chatcore/handlers.py
# Future features (rooms, file transfers, commands) go here.

def broadcast_message(sender, text, clients, exclude=None):
    """Send a message to all connected clients."""
    for sock in clients:
        if sock != exclude:
            try:
                sock.sendall(text)
            except:
                pass  # Dead socket, ignore for now

def on_client_join(addr):
    print(f"[+] Client connected: {addr}")

def on_client_leave(addr):
    print(f"[-] Client disconnected: {addr}")
