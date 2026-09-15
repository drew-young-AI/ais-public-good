---
name: macos-network-troubleshooting
type: skill
description: Troubleshoot LAN connectivity on macOS
---

# macOS Network Troubleshooting (LAN)

## Trigger
- User reports inability to ping or connect to a device on the same LAN while the Mac shows an active interface.
- Common symptoms: “ping timeout”, “no response”, but link lights are on.

## Goal
Verify Layer 2 (ARP) and Layer 3 (IP) connectivity, identify if the target is blocking ICMP, and provide alternative checks.

## Steps
1. **Check interface status**
   ```sh
   ifconfig <interface>   # e.g., en0, en7
   ```
   Look for `status: active` and a valid IPv4 address in the expected subnet.

2. **Confirm IP configuration**
   ```sh
   ipconfig getpacket <interface>   # macOS specific
   ```
   or
   ```sh
   ifconfig <interface> | grep inet
   ```

3. **Test Layer 2 reachability (ARP)**
   ```sh
   arp -n <target-IP>
   ```
   If you see a MAC address, the device is on the same broadcast domain.

4. **Test IP reachability with non-ICMP probes**
   - TCP port (if a service is expected):
     ```sh
     nc -z -v -w2 <target-IP> <port>
     ```
   - UDP port (e.g., DNS 53):
     ```sh
     nc -u -z -v -w2 <target-IP> 53
     ```
   - If any succeeds, the IP layer works; the target may be blocking ICMP.

5. **Check routing**
   ```sh
   netstat -rn | grep <target-subnet>
   ```
   Ensure traffic is routed via the correct interface.

6. **If still no success, verify physical layer**
   - Try a different cable or port.
   - Ensure the switch port is not in error-disabled state.
   - On the Mac, toggle the interface:
     ```sh
     sudo ifconfig <interface> down && sudo ifconfig <interface> up
     ```

7. **Alternative: Use DHCP to obtain address (if static not required)**
   ```sh
   sudo ipconfig set <interface> DHCP
   ```

## Pitfalls
- Assuming `ping` failure means no network; many devices block ICMP by default.
- Forgetting that macOS may have multiple network services (Wi‑Fi, Ethernet, Thunderbolt Bridge) – verify you are configuring/checking the correct interface.
- Not clearing old ARP entries; run `sudo arp -d <target-IP>` if you suspect a stale entry.
- Overlooking that the target might be on a different VLAN/subnet; confirm subnet masks match.

## Verification
After steps, you should be able to:
- See an ARP entry for the target.
- Successfully connect to at least one service port on the target (TCP or UDP).
- If needed, access the target’s management interface via a browser (http:// or https://).

## References
- macOS `ifconfig` and `ipconfig` manuals.
- Basic networking: ARP, ICMP, TCP/UDP connectivity testing.

> **Note**: This skill is intended for LAN troubleshooting on macOS. Adjust interface names and tools as needed for other Unix‑like systems.