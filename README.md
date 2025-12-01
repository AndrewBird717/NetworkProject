# Modular Client–Server Chat Application (with TLS)

This project is a modular, terminal-based client–server chat application built using Python sockets. 
It supports multiple clients, TLS-encrypted communication, message history, message searching and deletion, 
username/color customization, and a flexible command system.

This work was completed by **Ismael Cabrera-Hernandez** and **Andrew T. Bird** for a computer networking course.

---

## 1. Introduction

This project implements a fully modular chat system using a Python client–server architecture. The application
supports multiple clients simultaneously, using a custom chat protocol. The server handles message distribution,
message history, client tracking, and command processing.

The system was designed to allow incremental upgrades and modular feature additions such as TLS encryption,
searching, deletion, and color customization.

---

## 2. Full List of Prompts Used (Development Log)

These are all ChatGPT prompts used during the design and development process:

- “I need to make a simple chat app that utilizes a client server model…”
- “Make it terminal based where a client can connect using: ChatClient.py [IP_ADDRESS_OF_SERVER].”
- “Make the framework modular so I can add features later.”
- “So what exactly does chatcore do?”
- “What do I put in __init__.py?”
- “Can you make the class diagram/improvement plan?”
- “We implemented TLS into the server allowing encryption of chats.”
- “Tested.”
- “Help me clean up the UI.”
- “Allow usernames to appear when sending messages.”
- “Allow color selection when joining the server.”
- “Add message IDs.”
- “Add a search command.”
- “Add a delete command.”
- “Add a refresh system.”
- “Fix client echo-loop.”
- “Fix TLS disconnection errors.”
- “Allow unique username+#id system.”
- “Add server-side message history.”
- “Add dynamic commands and state management.”

---

## 3. Development Process

The project began with a baseline modular structure, separating core functionality into dedicated modules. 
The initial system included:
- ChatServer.py
- ChatClient.py
- chatcore/
- protocol.py
- handlers.py
- state.py
- commands.py
- tls.py
- init.py


A GitHub repository was used to collaborate and track changes.

### Features added over time:
- Username registration
- Color customization
- Server-side message history
- Message IDs
- `/search` command
- `/delete` command
- `/refresh` command
- `/color` command
- TLS encryption for secure communication
- Client join/leave announcements
- Improved UI formatting
- Stability and bug fixes

---

## 4. Architecture & Class Diagram

The system uses a classic client–server model. Clients connect to the server, which maintains the global message
state and broadcasts received messages to all clients.

### Text-Based Class Diagram

+-----------------------+ +------------------------+
| ChatClient | | ChatServer |
|-----------------------| |------------------------|
| username | | clients[] |
| color | | client_usernames{} |
| start_client() | | client_ids{} |
| listen() | | handle_client() |
| send_message() | | broadcast() |
+-----------------------+ +------------------------+
| |
| uses | uses
v v
+-----------------------+ +------------------------+
| protocol | | state |
| encode_message() | | add_message() |
| decode_message() | | delete_message() |
| format_message() | | search() |
+-----------------------+ +------------------------+
|
| uses
v
+-----------------------+
| commands |
| cmd_delete() |
| cmd_search() |
| cmd_refresh() |
| cmd_color() |
+-----------------------+

---

## 5. TLS Encryption Implementation

TLS was added using server-generated certificates (`server.crt` and `server.key`). Both the client and server 
wrap their sockets in SSL contexts to ensure encrypted communication.

### Server TLS Example

```python
tls_context = create_server_context(certfile="server.crt", keyfile="server.key")
tls_conn = wrap_server_connection(conn, tls_context)

tls_context = create_client_context(verify=False)
tls_sock = wrap_client_socket(sock, tls_context)
```


## 6. Feature Set Implemented
Core Requirements:

Supports multiple clients

Unique identifiers for each client

Proper message forwarding

Clean handling of client disconnections

Modular and extendable architecture

Augmentations Implemented (6 total, only 4 required)

Message searching (/search)

Message deletion (/delete)

Color customization (/color)

TLS encryption

Persistent message history

Client join/leave announcements
