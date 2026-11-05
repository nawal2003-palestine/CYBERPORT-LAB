# 🚢 Smart Port Cybersecurity Lab — Tanger Med

**Red Team × Blue Team offensive security research lab, built on 2 real virtual machines.**

A fully hands-on cybersecurity research lab inspired by **Tanger Med** — Africa's #1 container port. This project reproduces 4 complete attack scenarios against a simulated smart port infrastructure (IT/OT convergence: SCADA, cranes, sensors) and documents every technical step with real, authentic commands and outputs.

> ⚠️ **Educational / Research project only.** All attacks were executed on fully isolated virtual machines (UTM / Apple Silicon). No real systems, networks, or organizations were accessed or harmed.

---

## 🌐 Live Demo

**[cyberport-naoual.netlify.app](https://cyberport-naoual.netlify.app/)** — full interactive site with all 4 simulations, SIEM live feed, and Blue Team defense summary.

📄 Full PDF report included in `/report`.

---

## 🧭 Lab Architecture

| Machine | Role | IP | OS |
|---|---|---|---|
| Kali Linux | Red Team — Attacker | `192.168.64.4` | Kali 2024.x |
| Ubuntu SCADA | Blue Team — Target | `192.168.64.2` | Ubuntu 24.04 LTS |

Network: NAT `192.168.64.0/24` on UTM hypervisor (Apple Silicon).

**Services on target:**
| Port | Service | Version | Finding |
|---|---|---|---|
| 22/tcp | SSH | OpenSSH 9.6p1 | CVE-2024-6387 (RegreSSHion, CVSS 9.8) |
| 80/tcp | HTTP | Apache 2.4.58 | Multiple CVEs |
| 3128/tcp | Proxy | Squid 6.13 | Open proxy — unauthenticated |
| 5020/tcp | SCADA | Python custom | **CVSS 10.0** — zero auth, zero encryption |

---

## ⚔️ The 4 Simulations

### [Sim 1 — Network Reconnaissance](sim1_recon/)
Nmap scan + automated Python CVE mapping. **9 CVEs found in 13 seconds**, including CVSS 10.0 on the SCADA port.

### [Sim 2 — SSH Brute Force](sim2_ssh_bruteforce/)
Hydra attack with an OSINT-built wordlist. Password cracked in **4 attempts**. Paramiko honeypot captured **47 credentials** across 3 attack waves. Fail2ban progressive banning.

### [Sim 3 — SCADA / ICS MitM Attack](sim3_scada_mitm/)
ARP spoofing + sensor data injection. Crane weight falsified from **15,709 kg → 38,500 kg**. Detected by Wazuh SIEM in under 1 second.

### [Sim 4 — Lateral Movement & Privilege Escalation](sim4_lateral_movement/)
SSH pivot → GTFOBins sudo exploit → **root in 1 command**. 2 backdoors planted (cron reverse shell + SSH key), then fully found and removed via Blue Team forensics.

---

## 🛡️ Defense Stack

- **SSH Honeypot** (Python + Paramiko) — port 2222, 47 credentials captured
- **Fail2ban v1.1.0** — progressive banning (`maxretry=3`, `bantime.multiplier=2`, `maxtime=86400`)
- **Custom Python SIEM** + **Wazuh** — 100% detection rate across all 4 simulations
- **Forensics** — full timeline reconstruction from `auth.log`, `crontab`, `authorized_keys`

See [`defense/`](defense/) for the full recommendations.

---

## 📊 Results Summary

| Metric | Value |
|---|---|
| Simulations completed | 4 / 4 |
| CVEs discovered | 9 (4 critical) |
| Max CVSS score | 10.0 (SCADA-001) |
| Honeypot captures | 47 |
| Time to crack SSH password | 4 attempts |
| Time to root (Sim 4) | < 10 seconds |
| Attacks detected | 100% |
| Backdoors found & removed | 2 / 2 |

---

## 🛠️ Tools Used

Kali Linux · Ubuntu 24 LTS · Nmap 7.95 · Hydra · arpspoof · tcpdump · Python 3.12 · Paramiko · Fail2ban 1.1.0 · Wazuh · Netcat · ReportLab

---

## 📁 Repository Structure

```
smartport-cyberlab/
├── sim1_recon/              → Nmap scan output + CVE analyzer script
├── sim2_ssh_bruteforce/     → Hydra commands, honeypot script, fail2ban config
├── sim3_scada_mitm/         → ARP spoof commands, injection script
├── sim4_lateral_movement/   → Privilege escalation, backdoors, forensics commands
├── defense/                 → SIEM rules, recommendations
├── wordlists/                → OSINT wordlist used for Sim 2
├── report/                      → Full PDF report
└── README.md
```

---

## ⚖️ Ethical Considerations

- All simulations executed on isolated VMs — no real systems accessed or harmed
- All credentials were created specifically for this lab
- Educational purpose: understanding attacks to build better defenses
- All CVEs referenced are publicly documented with available patches

---

## 👤 Author

**Naoual Wafiq** — Cybersecurity Researcher · Red Team / Blue Team / OT Security

- 🌐 Portfolio: [cyberport-naoual.netlify.app](https://cyberport-naoual.netlify.app/)
- 💼 LinkedIn: [linkedin.com/in/naoual-wafiq](https://linkedin.com/in/naoual-wafiq)

---

*All simulations executed live on 2026-03-08 and 2026-03-09. Every command, output, and log entry in this repository is authentic.*
