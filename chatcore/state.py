# chatcore/state.py
# Shared in-memory state for all clients.

import threading

class ChatState:
    def __init__(self):
        self._messages = []   # list of dicts: {"id", "sender", "text", "deleted"}
        self._next_id = 1
        self._lock = threading.Lock()

    def add_message(self, sender, text):
        """Store a new message and return its record."""
        with self._lock:
            mid = self._next_id
            self._next_id += 1
            msg = {
                "id": mid,
                "sender": sender,
                "text": text,
                "deleted": False,
            }
            self._messages.append(msg)
        return msg

    def delete_message(self, msg_id, requester):
        """Mark a message as deleted if requester is the sender."""
        with self._lock:
            for msg in self._messages:
                if msg["id"] == msg_id:
                    if msg["sender"] != requester:
                        return False   # not your message
                    msg["deleted"] = True
                    msg["text"] = "[deleted]"
                    return True
        return False  # not found

    def all_messages(self):
        """Return a shallow copy of the current message list."""
        with self._lock:
            return list(self._messages)
