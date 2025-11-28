# chatcore/state.py
# Shared in-memory state for all clients.

import threading


class ChatState:
    def __init__(self):
        # list of dicts: {"id", "sender", "text", "deleted"}
        self._messages = []
        self._next_id = 1
        self._lock = threading.Lock()

    def add_message(self, sender: str, text: str) -> dict:
        """Store a new message and return its record."""
        with self._lock:
            msg_id = self._next_id
            self._next_id += 1
            msg = {
                "id": msg_id,
                "sender": sender,
                "text": text,
                "deleted": False,
            }
            self._messages.append(msg)
            return msg

    def delete_message(self, msg_id: int, requester: str) -> bool:
        """
        Mark a message as deleted if the requester is the sender.
        Returns True if deleted, False if not found or not allowed.
        """
        with self._lock:
            for msg in self._messages:
                if msg["id"] == msg_id:
                    if msg["sender"] != requester:
                        return False
                    msg["deleted"] = True
                    msg["text"] = "[deleted]"
                    return True
        return False

    def all_messages(self) -> list:
        """Return a shallow copy of the current message list."""
        with self._lock:
            return list(self._messages)
