---
name: launchd-scheduling
type: skill
description: Schedule recurring tasks on macOS using launchd plist files for transparency and easy editing by AI CLI tools.
version: 1.0.0
author: Hermes Agent
category: devops
platforms: [macos]
---
# Launchd Scheduling Skill

This skill covers how to schedule recurring tasks on macOS using `launchd` (plist files) instead of relying solely on Hermes' built-in cron. Using `launchd` gives you direct control over the plist files, making it easy for other AI CLI tools to read and modify schedules.

## When to Use

- You need other AI/CLI tools (e.g., Claude Code, Codex, Hermes itself) to be able to read or edit the schedule directly.
- You prefer the native macOS launchd system for its integration with system events, logging, and ease of management via `launchctl`.
- You want to avoid extra abstraction layers and keep scheduling configuration as plain XML files.

## Overview

`launchd` uses property list (.plist) files located in `~/Library/LaunchAgents/` for per-user agents. Each plist defines a label, the program to run, and when to run it (via `StartCalendarInterval` or `StartInterval`).

## Steps

1. **Create a script** (if needed) that contains the actual commands you want to run.  
   Example: `~/scripts/update_ai_tools.sh`  
   Make it executable: `chmod +x ~/scripts/update_ai_tools.sh`

2. **Write a plist file** in `~/Library/LaunchAgents/` with a unique reverse-DNS label.  
   Key plist keys:
   - `Label`: unique identifier (e.g., `com.drew.ai-tools-update`)
   - `ProgramArguments`: array where the first string is the interpreter (e.g., `/bin/bash`) and subsequent strings are script path and args.
   - `StartCalendarInterval` (for calendar-based schedules) or `StartInterval` (for fixed interval in seconds).
   - `StandardOutPath` and `StandardErrorPath`: optional log file paths.

3. **Load the plist**:  
   ```bash
   launchctl load ~/Library/LaunchAgents/com.drew.ai-tools-update.plist
   ```

4. **Verify**:  
   ```bash
   launchctl list | grep com.drew.ai-tools-update
   ```

5. **Unload / Reload** when you modify the plist:  
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.drew.ai-tools-update.plist
   # edit plist
   launchctl load ~/Library/LaunchAgents/com.drew.ai-tools-update.plist
   ```

6. **Test immediately** (optional):  
   ```bash
   launchctl start com.drew.ai-tools-update
   ```

## Example: Daily AI Tools Update at 04:00

**Script** (`~/scripts/update_ai_tools.sh`):
```bash
#!/bin/bash
echo "[$(date)] Starting AI tools update" >> ~/logs/ai-update.log
/usr/local/bin/hermes update >> ~/logs/ai-update.log 2>&1
npm update -g @github/copilot-cli >> ~/logs/ai-update.log 2>&1
echo "[$(date)] Update finished" >> ~/logs/ai-update.log
```

**Plist** (`~/Library/LaunchAgents/com.drew.ai-tools-update.plist`):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.drew.ai-tools-update</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>~/scripts/update_ai_tools.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>4</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>~/logs/ai-update.log</string>
    <key>StandardErrorPath</key>
    <string>~/logs/ai-update-error.log</string>
</dict>
</plist>
```

## Example: Hourly Local LLM Health Check

**Script** (`~/scripts/monitor_local_llm.sh`):
```bash
#!/bin/bash
LLM_URL="http://localhost:11434/api/tags"
response=$(curl -s -o /dev/null -w "%{http_code}" $LLM_URL)
if [ "$response" != "200" ]; then
    echo "[$(date)] ALERT: Local LLM service is DOWN (HTTP $response)" >> ~/logs/llm-monitor.log
else
    echo "[$(date)] Local LLM service is healthy" >> ~/logs/llm-monitor.log
fi
```

**Plist** (`~/Library**(`Library/LaunchAgents/com.drew.llm-monitor.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.drew.llm-monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>~/scripts/monitor_local_llm.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>StandardOutPath</key>
    <string>~/logs/llm-monitor.log</string>
    <key>StandardErrorPath</key>
    <string>~/logs/llm-monitor-error.log</string>
</dict>
</plist>
```

## Best Practices & Pitfalls

- **Use absolute paths** in `ProgramArguments`. launchd runs with a minimal environment; `$PATH` may not include `/usr/local/bin` or your user's bin.
- **Keep scripts idempotent** where possible, to avoid issues if a run overlaps with the next interval.
- **Log to files** under `~/logs/` (or another persistent location) and rotate them periodically; console output is captured only via these paths.
- **Avoid indefinite loops** inside scripts; let `launchd` handle the scheduling via `StartInterval` or `StartCalendarInterval`.
- **Testing**: Use `launchctl start <label>` to run the job immediately for verification.
- **Unloading**: Always unload before editing a plist; otherwise changes may not take effect until the next load.
- **Permissions**: Ensure the script and plist are readable by your user; no special privileges are needed for LaunchAgents.

## Troubleshooting

- Job not running? Check the status: `launchctl list | grep <label>`. Look at the last exit code.
- No output? Verify `StandardOutPath` and `StandardErrorPath` directories exist and are writable.
- Bad plist? Use `plutil -lint ~/Library/LaunchAgents/your.plist` to validate XML syntax.
- Environment variables? Set them inside the script or use `<key>EnvironmentVariables</key>` in the plist (advanced).

## References

- See `references/example-plist.md` for a copy‑paste ready plist template.
- See `scripts/update_ai_tools.sh` and `scripts/monitor_local_llm.sh` for example scripts (copy and adapt as needed).

---
*This skill enables you to manage macOS native scheduling in a way that is transparent and editable by other AI CLI tools, satisfying the user’s preference for launchd‑based automation.*