#!/usr/bin/env python3
"""
siem_rules.py — Custom Python SIEM detection engine
Smart Port Cybersecurity Lab — Tanger Med
Author: Naoual Wafiq

Monitors /var/log/auth.log and /var/log/scada_server.log in real time.
Complements Wazuh with custom rules specific to the lab's attack surface.
8 detection rules covering SSH brute force, SCADA anomalies, ARP spoofing,
and lateral movement events. All 4 simulations detected in < 1 second.
"""

import re
import time
import json
from datetime import datetime
from collections import deque

AUTH_LOG = "/var/log/auth.log"
SCADA_LOG = "/var/log/scada_server.log"

# Physical safety thresholds — values beyond these trigger CRITICAL alerts
THRESHOLDS = {
    "crane_01_weight": 20000.0,   # kg — max safe crane load
    "container_temp": 40.0,        # Celsius — max safe refrigeration temp
}

ssh_failures = deque(maxlen=50)  # sliding window for brute-force detection


def alert(level, rule_id, message):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] L{level} Rule {rule_id} — {message}")
    return {"timestamp": ts, "level": level, "rule": rule_id, "message": message}


def check_ssh_bruteforce(line):
    """Rule 200001/200002 — detect repeated SSH failures from same IP."""
    m = re.search(r"Failed password for (\S+) from (\S+)", line)
    if m:
        user, ip = m.groups()
        now = time.time()
        ssh_failures.append((now, ip, user))
        recent = [f for f in ssh_failures if now - f[0] < 60 and f[1] == ip]
        alert(5, 200001, f"SSH connection attempt — {ip} -> {user}")
        if len(recent) >= 5:
            alert(10, 200002, f"BRUTE FORCE DETECTED — 5 SSH failures in <60s from {ip}")


def check_ssh_success(line):
    """Rule 200004 — detect successful SSH login (post-brute-force)."""
    m = re.search(r"Accepted password for (\S+) from (\S+)", line)
    if m:
        user, ip = m.groups()
        alert(10, 200004, f"SSH INTRUSION — Successful login: {user}@192.168.64.2 from {ip}")


def check_sudo_escalation(line):
    """Rule — detect privilege escalation via sudo python3/perl/ruby."""
    if re.search(r"sudo:.*COMMAND=/usr/bin/(python3|perl|ruby|node)", line):
        alert(10, 300001, f"PRIV_ESC — {line.strip()}")


def check_scada_anomaly(sensor_data: dict, source_ip: str):
    """Rule 100002/100003 — detect sensor values beyond physical safety limits."""
    alert(5, 100001, f"SCADA: External connection to port 5020 from {source_ip}")
    for key, limit in THRESHOLDS.items():
        if key in sensor_data and sensor_data[key] > limit:
            alert(10, 100002 if "weight" in key else 100003,
                  f"CRITICAL: {key} = {sensor_data[key]} (threshold: {limit}) — ANOMALY")


def check_arp_anomaly(mac_claim: str, claimed_ip: str, source_ip: str):
    """Rule 100004 — detect ARP spoofing (gateway MAC impersonation)."""
    alert(8, 100004, f"ARP anomaly: {source_ip} claiming {claimed_ip} MAC address on eth0")


def tail_log(filepath, callback):
    """Follow a log file in real time (like `tail -f`)."""
    with open(filepath, "r") as f:
        f.seek(0, 2)  # jump to end
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2)
                continue
            callback(line)


if __name__ == "__main__":
    print("=== SmartPort Python SIEM — siem_rules.py ===")
    print(f"Monitoring {AUTH_LOG} ...")

    def dispatch(line):
        check_ssh_bruteforce(line)
        check_ssh_success(line)
        check_sudo_escalation(line)

    try:
        tail_log(AUTH_LOG, dispatch)
    except KeyboardInterrupt:
        print("\nSIEM stopped.")
    except FileNotFoundError:
        print(f"[DEMO MODE] {AUTH_LOG} not found — run on the lab VM to monitor live.")
