# GTFOBins — Why `sudo python3` = root

[GTFOBins](https://gtfobins.github.io/) documents Unix binaries that can be
abused to bypass local security restrictions. **Python is on that list**
because `os.system()` executes arbitrary shell commands.

When `python3` runs via `sudo` (as root), any shell it spawns **inherits
root privileges**:

```bash
sudo python3 -c "import os; os.system('/bin/bash')"
```

1. `sudo` elevates `python3` to run as root
2. `os.system('/bin/bash')` spawns a new shell process
3. The child process inherits the parent's (root) UID
4. Result: a root shell, no password prompt, one command

## Why this misconfiguration happens in the real world

```
portuser ALL=(ALL) NOPASSWD: /usr/bin/python3
```

Admins often add this kind of rule so a service account can run automation
scripts (e.g. SCADA monitoring scripts) without needing a password each
time. The problem: **any** interpreter with shell-execution capabilities
(python, perl, ruby, node, etc.) becomes a universal privilege-escalation
path once granted NOPASSWD sudo.

## Classification

Flagged as **CRITICAL** in:
- CIS Benchmarks
- NIST 800-53
- ISO 27001 Annex A.9

## The fix

```bash
# Remove the dangerous rule
sudo visudo
# delete: portuser ALL=(ALL) NOPASSWD: /usr/bin/python3
```

If automation needs elevated privileges, use a **narrowly scoped wrapper
script** with a fixed set of allowed arguments — never grant NOPASSWD on
a general-purpose interpreter.
