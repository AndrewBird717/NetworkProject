# chatcore/commands.py
# Central command handling for the chat server.

from dataclasses import dataclass
from typing import Callable, List, Any
from chatcore.protocol import encode_message


@dataclass
class CommandContext:
    conn: Any                    # the client's socket
    sender: str                  # username of the client
    state: Any                   # ChatState instance
    clients: List[Any]           # list of all client sockets
    send_full_history: Callable  # function(conn) -> None
    broadcast_message: Callable  # function(sender, payload, clients)
    # encode_message already imported here


def cmd_refresh(ctx: CommandContext, args: str) -> None:
    """
    /refresh
    Clears the client's screen (on client side) and re-sends history.
    Server side: just send full history to this client.
    """
    ctx.send_full_history(ctx.conn)


def cmd_delete(ctx: CommandContext, args: str) -> None:
    """
    /delete <id>
    Marks one of the sender's messages as deleted.
    """
    args = args.strip()
    if not args:
        ctx.conn.sendall(encode_message("SYSTEM", "Usage: /delete <id>"))
        return

    try:
        msg_id = int(args.split()[0])
    except ValueError:
        ctx.conn.sendall(encode_message("SYSTEM", "Usage: /delete <id>"))
        return

    success = ctx.state.delete_message(msg_id, ctx.sender)
    if not success:
        ctx.conn.sendall(
            encode_message("SYSTEM", f"Cannot delete message #{msg_id}")
        )
        return

    # Notify all clients that deletion occurred
    notice = encode_message(
        "SYSTEM", f"Message #{msg_id} deleted by {ctx.sender}"
    )
    ctx.broadcast_message("SYSTEM", notice, ctx.clients)


# Registry of supported commands
COMMANDS = {
    "refresh": cmd_refresh,
    "delete": cmd_delete,
}


def handle_command(ctx: CommandContext, text: str) -> bool:
    """
    Detect and execute a slash command.

    Returns:
        True  -> the text was a command (handled or rejected)
        False -> not a command; treat as a normal chat message
    """
    if not text.startswith("/"):
        return False

    # Strip leading "/" and split into name + args
    body = text[1:].strip()
    if not body:
        ctx.conn.sendall(
            encode_message("SYSTEM", "Empty command. Try /refresh or /delete <id>.")
        )
        return True

    parts = body.split(maxsplit=1)
    name = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    cmd = COMMANDS.get(name)
    if cmd is None:
        ctx.conn.sendall(
            encode_message("SYSTEM", f"Unknown command: /{name}")
        )
        return True

    cmd(ctx, args)
    return True
