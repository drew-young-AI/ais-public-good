---
name: network-troubleshooting-lan-ics
type: skill
category: devops
description: Troubleshoot LAN Internet Sharing from Windows to macOS.
version: 1.0.0
---

## When to Use
This skill applies when a macOS machine is connected to a Windows host via a LAN (e.g., Ethernet, USB‑to‑LAN adapter) and the Windows host is providing Internet Connection Sharing (ICS). The macOS device can ping the Windows host but cannot reach external destinations (e.g., 8.8.8.8) or resolve DNS.

## Prerequisites
- Physical link is up (link LEDs lit, `ifconfig <interface>` shows `status: active`).
- macOS interface has an IP in the same subnet as the Windows host (typically `192.168.137.0/24`).
- Windows ICS is enabled on the adapter that connects to the macOS device.

## Verification Steps
1. **Confirm LAN connectivity**
   ```bash
   # Replace en7 with your LAN interface (e.g., en0, en2, etc.)
   ifconfig en7
   # Look for: inet 192.168.137.2 netmask 0xffffff00 status: active
   # Ping the Windows host (gateway)
   ping -c 3 192.168.137.1
   ```

2. **Check current default route**
   ```bash
   netstat -rn | grep default
   # Expected to show a gateway via Wi‑Fi or another interface if mis‑configured.
   ```

3. **Set the default gateway to the Windows host (temporary)**
   ```bash
   sudo route -n change default 192.168.137.1
   ```

4. **(Optional) Remove conflicting default route from other interfaces**
   ```bash
   # Example: delete the Wi‑Fi default if it persists
   sudo route -n delete default 172.20.10.1   # replace with actual Wi‑Fi gateway
   ```

5. **Configure DNS to use the Windows host or a public resolver**
   ```bash
   # Use the Windows host as DNS (common with ICS)
   networksetup -setdnsservers "USB 10/100/1000 LAN" 192.168.137.1
   # Or use public DNS (e.g., Google)
   networksetup -setdnsservers "USB 10/100/1000 LAN" 8.8.8.8 1.1.1.1
   ```

6. **Prioritize the LAN service over Wi‑Fi (if both are active)**
   ```bash
   networksetup -ordernetworkservices "USB 10/100/1000 LAN" "Wi-Fi"
   ```

7. **(If you only want LAN) Turn off Wi‑Fi to avoid ambiguity**
   ```bash
   networksetup -setairportpower en0 off
   ```

8. **Test external connectivity**
   ```bash
   ping -c 3 8.8.8.8
   nslookup apple.com
   curl -I https://apple.com
   ```

## Persistent Configuration (macOS System Settings)
1. Open **System Settings → Network**.
2. Select the LAN service (e.g., “USB 10/100/1000 LAN”).
3. Configure IPv4 to **Using DHCP** (Windows ICS will hand out address, gateway, and DNS).
4. In the **TCP/IP** pane, ensure the **Router** field is either blank (DHCP) or explicitly set to the Windows host IP (`192.168.137.1`).
5. In the **DNS** pane, either leave blank (to accept DHCP‑provided DNS) or add preferred servers.
6. Drag the LAN service above Wi‑Fi in the service order list (gear icon → Set Service Order…) to give it higher priority.
7. Click **Apply**.

## Windows Host Checks
- Ensure **Internet Connection Sharing** is enabled on the adapter that connects to the macOS device:
  - Control Panel → Network and Internet → Network Connections → Right‑click the Internet‑connected adapter → Properties → Sharing tab → Check “Allow other network users to connect through this computer’s Internet connection”.
  - In the dropdown, select the LAN adapter that links to the macOS machine.
- Verify the LAN adapter on Windows has a static IP (commonly `192.168.137.1`) and is not set to obtain an address via DHCP from another source.
- Temporarily disable third‑party firewalls or create an inbound rule to allow ICMP Echo Request if needed for ping testing.

## Common Pitfalls
- **Default gateway still points to Wi‑Fi**: Even after changing the route, some applications may cache the old route; restarting the network interface (`sudo ifconfig en7 down && sudo ifconfig en7 up`) or rebooting helps.
- **DNS not forwarded by ICS**: Some Windows configurations only share the connection but not DNS; manually set DNS to a public resolver (8.8.8.8, 1.1.1.1) as shown above.
- **Multiple default routes**: Having two default gateways (one via en0, one via en7) can cause unpredictable routing; delete the unwanted one.
- **Interface naming confusion**: On macOS, the USB‑to‑LAN adapter may appear as `en7`, `en2`, etc.; always verify with `ifconfig` before applying commands.
- **Link‑local address (169.254.x.x)**: If the macOS interface self‑assigns a link‑local address, DHCP from Windows is not reaching it; check the cable, try a different port, or reboot the Windows ICS service.

## References
- macOS `route` and `networksetup` command manuals (`man route`, `man networksetup`).
- Windows Internet Connection Sharing documentation: <https://learn.microsoft.com/windows-server/networking/technologies/internet-connection-sharing>.
- Example troubleshooting log from this session (see `references/lan-ics-troubleshoot-log.md`).

## Linked Files
- `references/lan-ics-troubleshoot-log.md` – captured console output and command sequence from the debugging session.