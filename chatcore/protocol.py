# chatcore/protocol.py
# Defines how messages are encoded, decoded, and routed.

HEADER = "[CHAT]"  # Helps future-proof other command types

def encode_message(sender, text):
    """Convert a message to a simple protocol format."""
    return f"{HEADER}{sender}:{text}".encode()

def decode_message(raw):
    """Parse raw incoming bytes into structured data."""
    try:
        data = raw.decode()
        if not data.startswith(HEADER):
            return None, None
        body = data[len(HEADER):]
        sender, text = body.split(":", 1)
        return sender, text
    except:
        return None, None
