#!/usr/bin/env python3
"""
ssh_honeypot.py — Fake SSH server that captures credentials
Smart Port Cybersecurity Lab — Tanger Med
Author: Naoual Wafiq

Built with Paramiko — mimics a real SSH server's handshake but never
grants access. Every credential attempted is logged with full timestamp
and source IP. 47 credentials captured in Simulation 2.
"""

import socket
import threading
import logging
import paramiko
from datetime import datetime

HOST = "0.0.0.0"
PORT = 2222
LOG_FILE = "honeypot.log"
HOST_KEY_FILE = "server.key"  # generate with: ssh-keygen -t rsa -f server.key

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

capture_count = 0


class HoneypotServer(paramiko.ServerInterface):
    def __init__(self, client_addr):
        self.client_addr = client_addr
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        global capture_count
        capture_count += 1
        entry = f"TRAP | {self.client_addr[0]} | user: {username} | pass: {password}"
        logging.info(entry)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {entry}  (#{capture_count})")
        # Always reject — this is a trap, never a real login
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED

    def get_allowed_auths(self, username):
        return "password"


def handle_connection(client_socket, client_addr, host_key):
    transport = paramiko.Transport(client_socket)
    transport.add_server_key(host_key)
    server = HoneypotServer(client_addr)
    try:
        transport.start_server(server=server)
    except Exception:
        pass
    finally:
        transport.close()


def main():
    print("=" * 52)
    print("  HONEYPOT SSH — Tanger Med Port Simulator")
    print(f"  Listening on {HOST}:{PORT}")
    print(f"  Logging to: {LOG_FILE}")
    print("=" * 52)

    host_key = paramiko.RSAKey.generate(2048)  # or load from HOST_KEY_FILE

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(100)

    try:
        while True:
            client_socket, client_addr = sock.accept()
            thread = threading.Thread(
                target=handle_connection,
                args=(client_socket, client_addr, host_key),
                daemon=True,
            )
            thread.start()
    except KeyboardInterrupt:
        print(f"\nTotal captures: {capture_count}")
        sock.close()


if __name__ == "__main__":
    main()
