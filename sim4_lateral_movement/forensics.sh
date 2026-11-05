#!/usr/bin/env bash
#
# forensics.sh — Blue Team incident response script
# Smart Port Cybersecurity Lab — Tanger Med
# Author: Naoual Wafiq
#
# Reconstructs the attack timeline and removes both backdoors
# planted during Simulation 4 (cron reverse shell + SSH key).
#
# Usage: sudo bash forensics.sh

set -euo pipefail

echo "=========================================="
echo " BLUE TEAM FORENSIC RESPONSE — SmartPort Lab"
echo "=========================================="

echo -e "\n[1] Who logged in and when?"
last | head -10

echo -e "\n[2] Searching for privilege escalation events..."
grep "sudo.*python3" /var/log/auth.log | tail -5 || echo "  (none found)"

echo -e "\n[3] Checking for cron backdoor..."
if sudo crontab -l -u root 2>/dev/null | grep -q "/dev/tcp"; then
    echo "  [FOUND] Reverse shell cron job:"
    sudo crontab -l -u root | grep "/dev/tcp"
    echo "  Removing..."
    sudo crontab -r -u root
    echo "  [CLEANED] Cron backdoor removed."
else
    echo "  No cron backdoor found."
fi

echo -e "\n[4] Checking for SSH key backdoor..."
if sudo grep -q "attacker@kali" /root/.ssh/authorized_keys 2>/dev/null; then
    echo "  [FOUND] Unauthorized SSH key:"
    sudo grep "attacker@kali" /root/.ssh/authorized_keys
    echo "  Removing..."
    sudo sed -i '/attacker@kali/d' /root/.ssh/authorized_keys
    echo "  [CLEANED] SSH backdoor key removed."
else
    echo "  No SSH backdoor key found."
fi

echo -e "\n[5] Checking sudoers for dangerous NOPASSWD rules..."
sudo grep -n "NOPASSWD" /etc/sudoers /etc/sudoers.d/* 2>/dev/null || echo "  None found in scanned files."
echo "  --> Review manually and remove any NOPASSWD rule on interpreters"
echo "      (python3, perl, ruby, node, etc.)"

echo -e "\n=========================================="
echo " FORENSIC ANALYSIS COMPLETE"
echo " Both backdoors checked and remediated."
echo "=========================================="
