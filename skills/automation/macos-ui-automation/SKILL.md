---
name: macos-ui-automation
type: skill
description: |
  Universal macOS UI Automation Skill v7.0.0.
  Uses launchd for OS-native scheduling (replaces unreliable time.sleep), caffeinate for sleep prevention,
  heartbeat logging, Anti-Modal Focus-Healing, File Lock, and Acknowledgement Feedback Protocol.
version: 7.0.0
platforms: [macos]
metadata:
  hermes:
    tags: [automation, macos, terminal, chrome, launchd, caffeinate, heartbeat, anti-modal, ack-feedback]
    category: automation
---

# Universal macOS Automation Skill v7.0.0

## ⚠️ Breaking Change from v6

**REMOVED**: `--at HH:MM` parameter (used fragile `time.sleep()` internally).
**REPLACED WITH**: `schedule add` subcommand using macOS-native `launchd` plist.

### Why This Matters
`time.sleep()` is structurally unreliable on macOS for scheduling:
- macOS Idle Sleep suspends or kills the Python process.
- App Nap throttles background processes, causing timer drift.
- No heartbeat = no way to verify the process is still alive.

`launchd` is the OS kernel-managed scheduler that:
- Survives sleep/wake cycles (fires immediately on wake if missed).
- Survives terminal closure, SSH disconnection, and reboots.
- Wraps execution with `caffeinate -i` to prevent idle sleep during GUI operations.

---

## Quick Reference Commands

### 1. Terminal IPC Enter (Immediate)
```bash
python mac_auto.py terminal enter --filter "claude"
```

### 2. System Events Key with Anti-Modal Guard (Immediate)
```bash
python mac_auto.py sys-events key --app "Google Chrome" --filter "GitHub" --key enter
```

### 3. Schedule Task via launchd (Replaces --at)
```bash
# Create: Send Enter to claude terminals daily at 23:20
python mac_auto.py schedule add --label claude-enter-daily --time 23:20 --cmd terminal enter --filter claude

# List all scheduled mac_auto tasks
python mac_auto.py schedule list

# Remove a scheduled task
python mac_auto.py schedule remove --label claude-enter-daily
```

### 4. Check Heartbeat Status
```bash
python mac_auto.py heartbeat
```

### 5. Window Inspection
```bash
python mac_auto.py window list --app "Google Chrome" --filter "GitHub"
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  launchd (macOS Kernel Scheduler)                               │
│  • Fires at exact HH:MM, survives sleep/wake/reboot             │
│  • Wraps with caffeinate -i to prevent idle sleep during GUI ops │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Invokes
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  mac_auto.py v7.0.0                                             │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────────┐  │
│  │ Layer 1:     │  │ Layer 2:         │  │ Anti-Modal Engine │  │
│  │ Terminal IPC │  │ System Events    │  │ Focus-Healing     │  │
│  │ (do script)  │  │ (caffeinate+GUI) │  │ Audit & Dismiss   │  │
│  └─────────────┘  └──────────────────┘  └───────────────────┘  │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────────┐  │
│  │ File Lock   │  │ Heartbeat Logger │  │ Network Audit     │  │
│  │ (Atomic)    │  │ (/tmp/heartbeat) │  │ (Ping 8.8.8.8)   │  │
│  └─────────────┘  └──────────────────┘  └───────────────────┘  │
│                                                                 │
│  Output: Structured ACK JSON with modal_audit + environment     │
└─────────────────────────────────────────────────────────────────┘
```
