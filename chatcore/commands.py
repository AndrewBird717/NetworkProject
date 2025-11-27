# chatcore/commands.py
#
# Central place to define chat commands like:
#   /help
#   /me <action>
# and later:
#   /delete <id>, /history, /nick, etc.

from dataclasses import dataclass

@dataclass
class CommandContext:
    conn: object              # client's socket
    sender: str               # username (from protocol)
    clients: list             # list of all client sockets
    broadcast_message: object # function(sender, payload, clients)
    encode_message: object    # function(sender, text) -> bytes
    state: object


def cmd_help(ctx: CommandContext, args: str):
    """Show available commands."""
    names = sorted(COMMANDS.keys())
    text = "Available commands: " + ", ".join(f"/{n}" for n in names)
    ctx.conn.sendall(ctx.encode_message("SYSTEM", text))


def cmd_me(ctx: CommandContext, args: str):
    """Emote-style message: /me waves -> *alice waves*"""
    if not args.strip():
        ctx.conn.sendall(ctx.encode_message("SYSTEM", "Usage: /me <action>"))
        return

    # Broadcast a system-style message to everyone
    msg_text = f"*{ctx.sender} {args.strip()}*"
    payload = ctx.encode_message("SYSTEM", msg_text)
    ctx.broadcast_message("SYSTEM", payload, ctx.clients)

def cmd_delete(ctx: CommandContext, args: str):
    """Delete one of your messages: /delete <id>"""
    if not args.strip():
        ctx.conn.sendall(ctx.encode_message("SYSTEM", "Usage: /delete <id>"))
        return

    try:
        msg_id = int(args.strip().split()[0])
    except ValueError:
        ctx.conn.sendall(ctx.encode_message("SYSTEM", "Usage: /delete <id>"))
        return

    success = ctx.state.delete_message(msg_id, ctx.sender)
    if not success:
        ctx.conn.sendall(
            ctx.encode_message("SYSTEM", f"Cannot delete message #{msg_id}")
        )
        return

    ctx.broadcast_message(
        "SYSTEM",
        ctx.encode_message("SYSTEM", f"Message #{msg_id} deleted by {ctx.sender}"),
        ctx.clients,
    )



# Registry of commands
COMMANDS = {
    "help": cmd_help,
    "me": cmd_me,
    "delete": cmd_delete,
    # "history": cmd_history,
}


def handle_command(ctx: CommandContext, text: str) -> bool:
    """
    Parse and execute a slash command like '/help' or '/me waves'.

    Returns:
        True  -> it WAS a command (handled or at least recognized)
        False -> not a command; treat as normal chat
    """
    if not text.startswith("/"):
        return False

    body = text[1:]
    if not body:
        ctx.conn.sendall(ctx.encode_message("SYSTEM", "Empty command."))
        return True

    parts = body.split(maxsplit=1)
    name = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    cmd = COMMANDS.get(name)
    if cmd is None:
        ctx.conn.sendall(
            ctx.encode_message("SYSTEM", f"Unknown command: /{name}")
        )
        return True

    cmd(ctx, args)
    return True
