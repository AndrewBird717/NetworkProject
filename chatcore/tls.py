# chatcore/tls.py
#
# Simple TLS helpers for the chat app.
# Server: uses a cert + key you generate.
# Client: accepts self-signed certificates (good for class demos).

import ssl


def create_server_context(certfile="server.crt", keyfile="server.key"):
    """
    Create a TLS context for the server.

    certfile/keyfile should point to your server certificate and private key.
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    return context


def wrap_server_connection(conn, context):
    """
    Wrap an accepted TCP connection with TLS for the server side.
    """
    tls_conn = context.wrap_socket(conn, server_side=True)
    return tls_conn


def create_client_context(verify=False):
    """
    Create a TLS context for the client.

    If verify is False, we don't verify server certificates
    (OK for local testing / class assignment with self-signed certs).
    """
    if verify:
        # More "realistic" mode (needs proper CA / cert)
        context = ssl.create_default_context()
    else:
        # For self‑signed / local testing
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    return context


def wrap_client_socket(sock, context, server_hostname="localhost"):
    """
    Wrap a connected TCP socket with TLS for the client side.
    """
    tls_sock = context.wrap_socket(sock, server_hostname=server_hostname)
    return tls_sock
