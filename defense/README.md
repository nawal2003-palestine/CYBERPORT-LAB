# Defense in Depth — Blue Team Response

3 layers, 100% detection rate across all 4 simulations.

## Defensive Mechanisms Deployed

| Mechanism | Description |
|---|---|
| 🍯 **SSH Honeypot** | Python + Paramiko fake SSH server, port 2222. 47 credentials harvested with full IP/timestamp logging. |
| 🚫 **Fail2ban Progressive** | `maxretry=3`, `bantime.multiplier=2`, `maxtime=86400`. Exponential backoff: 1min → 2min → 4min → ... → 24h cap. |
| 📊 **Python SIEM + Wazuh** | Real-time monitoring of `/var/log/auth.log` and `/var/log/scada_server.log`. 8 detection rules. All 4 sims detected in < 1 second. |
| 🗺️ **CVE Auto-Mapping** | Correlates Nmap results with CVE DB for instant vulnerability assessment ([`recon_analyzer.py`](../sim1_recon/recon_analyzer.py)). |
| 🔍 **Forensic Analysis** | Post-incident investigation via `last`, `auth.log`, `crontab`, `authorized_keys` ([`forensics.sh`](../sim4_lateral_movement/forensics.sh)). |

## Wazuh SIEM Detection Rules

See [`siem_rules.py`](siem_rules.py) for the custom detection engine used alongside Wazuh.

## 8 Prioritized Recommendations

| Priority | Recommendation | Addresses |
|---|---|---|
| 🔴 CRITICAL | Authenticate SCADA (Modbus/TLS or OPC-UA) | SCADA-001 (CVSS 10.0) |
| 🔴 CRITICAL | Patch CVE-2024-6387 within 72h | RegreSSHion (CVSS 9.8) |
| 🔴 CRITICAL | Remove sudo NOPASSWD on interpreters | Sim 4 — root in 1 cmd |
| 🟠 HIGH | SSH Keys + MFA, disable PasswordAuthentication | Sim 2 — brute force |
| 🟠 HIGH | Network segmentation — dedicated OT VLAN | Sim 1 — flat network |
| 🟠 HIGH | Close open Squid proxy (:3128) | Sim 1 — anonymization risk |
| 🟡 MEDIUM | Permanent honeypots (Conpot, T-Pot, OpenCanary) | Ongoing intel gathering |
| 🟡 MEDIUM | 24/7 OT SOC with Wazuh/Splunk + OT rule packs | Continuous monitoring |

## Key Findings & Proofs

- **tangermed2024 cracked in 4 attempts** — OSINT wordlists beat generic lists exponentially
- **47 attacker credentials captured** — honeypots convert attackers into intelligence sources
- **CVSS 10.0 found in a 13-second scan** — misconfiguration is more dangerous than missing patches
- **Root access in 1 command** — principle of least privilege is non-negotiable in critical infrastructure
