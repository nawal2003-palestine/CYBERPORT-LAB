#!/usr/bin/env python3
"""
recon_analyzer.py — Automated CVE mapping from Nmap scan output
Smart Port Cybersecurity Lab — Tanger Med
Author: Naoual Wafiq

Parses an Nmap -sV output file, extracts service/version pairs,
and cross-references them against a local CVE database (mirrors NVD).
"""

import re
import sys
import json
from datetime import datetime

# Local CVE database — mirrors NVD lookups for known service versions
CVE_DATABASE = {
    ("ssh", "openssh 9.6p1"): [
        {"id": "CVE-2024-6387", "cvss": 9.8, "severity": "CRITICAL",
         "desc": "RegreSSHion — Race condition in SIGALRM handler allows unauthenticated RCE"},
        {"id": "CVE-2023-51385", "cvss": 6.5, "severity": "HIGH",
         "desc": "Command injection via special-character usernames in ssh_config expansion"},
    ],
    ("http", "apache 2.4.58"): [
        {"id": "CVE-2024-38473", "cvss": 7.5, "severity": "HIGH",
         "desc": "mod_proxy incorrect encoding — authentication and ACL bypass"},
        {"id": "CVE-2023-45802", "cvss": 7.5, "severity": "HIGH",
         "desc": "HTTP/2 stream reset causes memory corruption — remote DoS"},
    ],
    ("http", "squid 6.13"): [
        {"id": "CVE-2024-45802", "cvss": 7.5, "severity": "HIGH",
         "desc": "DoS via ESI response processing crash"},
        {"id": "CVE-2024-37894", "cvss": 6.3, "severity": "MEDIUM",
         "desc": "Internal resource access via unauthenticated open proxy"},
    ],
}

# Custom SCADA findings — not in NVD, discovered via manual protocol analysis
SCADA_FINDINGS = [
    {"id": "SCADA-001", "cvss": 10.0, "severity": "CRITICAL",
     "desc": "Zero authentication on SCADA interface — any machine on the network "
             "can read/write all sensor data."},
    {"id": "SCADA-002", "cvss": 9.5, "severity": "CRITICAL",
     "desc": "Zero encryption on all SCADA communications — sensor data transmitted "
             "in plaintext, readable via ARP MitM."},
]


def parse_nmap_output(filepath):
    """Extract (port, service, version) tuples from an Nmap -sV scan file."""
    services = []
    port_line = re.compile(r"^(\d+)/tcp\s+open\s+(\S+)\s+(.*)$")
    with open(filepath, "r") as f:
        for line in f:
            m = port_line.match(line.strip())
            if m:
                port, svc, version = m.groups()
                services.append({"port": int(port), "service": svc, "version": version.strip()})
    return services


def match_cves(services):
    """Cross-reference discovered services against the CVE database."""
    findings = []
    for svc in services:
        key_candidates = [
            (svc["service"].lower(), svc["version"].lower()),
        ]
        for key in CVE_DATABASE:
            svc_name, svc_version = key
            if svc_name in svc["service"].lower() and svc_version.split()[0] in svc["version"].lower():
                for cve in CVE_DATABASE[key]:
                    findings.append({**cve, "port": svc["port"], "service": svc["version"]})

        # Special case: unauthenticated custom SCADA server on 5020
        if svc["port"] == 5020:
            for finding in SCADA_FINDINGS:
                findings.append({**finding, "port": 5020, "service": "Python SCADA server (custom)"})

    return sorted(findings, key=lambda x: -x["cvss"])


def print_report(findings):
    print("=" * 60)
    print("  SMARTPORT CVE ANALYSIS — recon_analyzer.py")
    print("=" * 60)
    for f in findings:
        marker = "CRITICAL" if f["cvss"] >= 9.0 else f["severity"]
        print(f"► {f['id']:<16} Port {f['port']:<6} CVSS {f['cvss']:<5} "
              f"{marker:<10} {f['desc'][:60]}")
    critical = sum(1 for f in findings if f["cvss"] >= 9.0)
    print("=" * 60)
    print(f"SUMMARY: {len(findings)} vulnerabilities | {critical} CRITICAL | "
          f"Overall Risk: {'CRITICAL' if critical else 'MODERATE'}")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 recon_analyzer.py <nmap_output.txt>")
        sys.exit(1)

    services = parse_nmap_output(sys.argv[1])
    findings = match_cves(services)
    print_report(findings)

    # Save JSON report for PDF generation
    report = {
        "scan_date": datetime.now().isoformat(),
        "services_found": services,
        "cve_findings": findings,
        "summary": {
            "total_cves": len(findings),
            "critical_count": sum(1 for f in findings if f["cvss"] >= 9.0),
            "max_cvss": max((f["cvss"] for f in findings), default=0),
        }
    }
    with open("cve_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\nFull report saved: cve_report.json")
