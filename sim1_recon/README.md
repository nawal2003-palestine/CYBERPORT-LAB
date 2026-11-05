# Simulation 1 — Network Reconnaissance

**Phase 1 · Mapping the battlefield**

Nmap scan + automated Python CVE mapping against the simulated SCADA target.

## Results

| Metric | Value |
|---|---|
| Hosts found | 3 |
| Open ports | 4 |
| CVEs found | 9 (4 critical) |
| Max CVSS | 10.0 |
| Scan duration | 13.62s |

## Step A — Host Discovery

```bash
sudo nmap -sn 192.168.64.0/24
```

```
Nmap scan report for 192.168.64.1  Host is up (0.00045s latency)  # Gateway
Nmap scan report for 192.168.64.2  Host is up (0.00089s latency)  # TARGET
Nmap scan report for 192.168.64.4  Host is up (0.00012s latency)  # Kali (us)
3 hosts up | Scan completed in 2.11 seconds
```

## Step B — Deep Service & Version Scan

```bash
sudo nmap -sV -sC -O -A 192.168.64.2 -oN scan_scada.txt
```

```
22/tcp    open  ssh    OpenSSH 9.6p1 Ubuntu 4ubuntu0.3
80/tcp    open  http   Apache httpd 2.4.58 (Ubuntu)
3128/tcp  open  http   Squid http proxy 6.13
          |_http-open-proxy: Potentially OPEN proxy  <-- UNEXPECTED FINDING
5020/tcp  open  ?      Python SCADA server (custom port)
          |_ No authentication banner detected  <-- CVSS 10.0

OS: Linux 4.15-5.19 Ubuntu 24 | Confidence: 96% | Duration: 13.62s
```

## Step C — Automated CVE Mapping

Run the included analyzer against the Nmap output:

```bash
python3 recon_analyzer.py scan_scada.txt
```

See [`recon_analyzer.py`](recon_analyzer.py) for the full script.

## CVEs Discovered

| CVE / ID | Service | CVSS | Severity |
|---|---|---|---|
| SCADA-001 | Port 5020 | 10.0 | CRITICAL |
| CVE-2024-6387 | SSH 22 | 9.8 | CRITICAL |
| SCADA-002 | Port 5020 | 9.5 | CRITICAL |
| CVE-2024-38473 | HTTP 80 | 7.5 | HIGH |
| CVE-2023-45802 | HTTP 80 | 7.5 | HIGH |
| CVE-2024-45802 | Squid 3128 | 7.5 | HIGH |
| CVE-2023-51385 | SSH 22 | 6.5 | HIGH |
| CVE-2024-37894 | Squid 3128 | 6.3 | MEDIUM |

## 🔵 Blue Team Lesson

A SCADA port with CVSS 10.0 exposed with zero authentication is the single most dangerous finding. The open proxy on :3128 should be restricted to internal IPs only. 7 of 9 CVEs have patches available.
