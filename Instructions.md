To use application you need one server per chatroom

Server can be set up by setting the IP address in the ChatServer.py to your devices IP, as well as setting the port number to the desired port.
To Actually use server simply run the program and it will begin listening

Client can be used by manually setting port number in ChatClient.py and setting IP as first argument in terminal
Simply run ChatClient.py in terminal in the format "ChatClient.py YOUR_IP"

You may need to call the file using python3 beforehand to specify interpreter, ex. "python3 ChatClient.py 10.0.0.15"

The application supports numerous commands:
/refresh - refreshes/ retransmits chat history back to client who sent command, useful for when a client first joins the chat and wants to see history

/delete "message_id" - allows a client to delete one of their own messages, message specified by message id

/search "string to be searched for" - allows a client to search through all messages for a specified string

/color "color_name" - allows a client to change their own text color (clientside only), colors include (red, green, yellow, blue, magenta, cyan, white)

/exit - same as .exit, allows client to disconnect from chat and ends program

implemented features
1. TLS
2. Delete
3. Search
4. Multiple Users
5. Message Colors
6. Refreshing Chat History (allows for long term message history like other messaging apps (discord, iMessage))

