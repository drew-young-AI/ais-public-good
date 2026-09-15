#!/usr/bin/env python3
"""
Universal macOS UI, Terminal, Chrome, App Automation Tool v7.0.0
Breaking Changes from v6:
- REMOVED: `--at HH:MM` time.sleep() scheduling (structurally unreliable on macOS).
- ADDED: `schedule` subcommand that generates+loads a launchd plist for OS-native scheduling.
- ADDED: `caffeinate` subprocess wrapping for all System Events GUI operations.
- ADDED: Heartbeat file logging for long-running operations.
- RETAINED: Anti-Modal Audit & Focus-Healing Engine, File Lock, Network Check, ACK Protocol.
"""

import sys
import time
import datetime
import subprocess
import argparse
import json
import re
import os
import fcntl
import tempfile

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
except ImportError:
    pyautogui = None

LOCK_FILE = "/tmp/mac_auto_execution.lock"
HEARTBEAT_DIR = "/tmp/mac_auto_heartbeats"
LAUNCHD_PLIST_DIR = os.path.expanduser("~/Library/LaunchAgents")
SCRIPT_PATH = os.path.abspath(__file__)
PYTHON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_PATH)))), "hermes-agent", "venv", "bin", "python")
# Fallback if path resolution fails
if not os.path.exists(PYTHON_PATH):
    PYTHON_PATH = "~/.hermes/hermes-agent/venv/bin/python"

KEY_MAP = {
    "enter": 36, "return": 36, "tab": 48, "space": 49, "escape": 53, "esc": 53,
    "backspace": 51, "delete": 51, "up": 126, "down": 125, "left": 123, "right": 124,
    "f1": 122, "f2": 120, "f3": 99, "f4": 118, "f5": 96, "f6": 97,
    "f7": 98, "f8": 100, "f9": 101, "f10": 109, "f11": 103, "f12": 111,
}

MODIFIER_MAP = {
    "cmd": "command down", "command": "command down",
    "ctrl": "control down", "control": "control down",
    "alt": "option down", "option": "option down",
    "shift": "shift down",
}

# --- Heartbeat & Edge-Case Helpers ---

def write_heartbeat(task_id, status="alive"):
    os.makedirs(HEARTBEAT_DIR, exist_ok=True)
    path = os.path.join(HEARTBEAT_DIR, f"{task_id}.json")
    data = {"task_id": task_id, "status": status, "timestamp": datetime.datetime.now().isoformat(), "pid": os.getpid()}
    with open(path, 'w') as f:
        json.dump(data, f)

def wake_display_if_needed():
    try:
        subprocess.run(["caffeinate", "-u", "-t", "3"], capture_output=True, timeout=5)
    except Exception:
        pass

def check_network_status():
    res = subprocess.run(["ping", "-c", "1", "-W", "1000", "8.8.8.8"], capture_output=True)
    return res.returncode == 0

class FileLockContext:
    def __enter__(self):
        self.fp = open(LOCK_FILE, 'w')
        try:
            fcntl.flock(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            fcntl.flock(self.fp, fcntl.LOCK_EX)
        return self
    def __exit__(self, *args):
        fcntl.flock(self.fp, fcntl.LOCK_UN)
        self.fp.close()

def build_ack(action_type, app_name, target_info, strategy, status, pre_state=None, post_state=None, modal_audit=None, details=None):
    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "action": action_type,
        "app": app_name,
        "strategy": strategy,
        "status": status,
        "target": target_info,
        "verification": {"pre_state": pre_state, "post_state": post_state, "verified": status == "SUCCESS"},
        "modal_audit": modal_audit or {"modal_detected": False, "dismissal_attempted": False, "modal_type": None},
        "environment": {"network_online": check_network_status()},
        "details": details or {}
    }

# --- Anti-Modal Audit & Focus-Healing Engine ---

def audit_and_heal_modals(app_name="Google Chrome", target_win_id=None):
    script = f'''
    tell application "System Events"
        if not (exists process "{app_name}") then
            return "PROCESS_NOT_FOUND"
        end if
        tell process "{app_name}"
            set winList to windows
            set winCount to count of winList
            set frontWinName to ""
            set hasSheet to false
            set hasDialog to false
            if winCount > 0 then
                set frontWin to item 1 of winList
                set frontWinName to name of frontWin
                set hasSheet to (count of sheets of frontWin) > 0
                set hasDialog to (count of dialogs of frontWin) > 0
            end if
            return (winCount as string) & "|||" & frontWinName & "|||" & (hasSheet as string) & "|||" & (hasDialog as string)
        end tell
    end tell
    '''
    res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if "PROCESS_NOT_FOUND" in res.stdout or res.returncode != 0:
        return {"modal_detected": False, "dismissal_attempted": False, "modal_type": None, "cleared": True}

    parts = res.stdout.strip().split("|||")
    if len(parts) < 4:
        return {"modal_detected": False, "dismissal_attempted": False, "modal_type": None, "cleared": True}

    _, front_win_name, has_sheet, has_dialog = parts[:4]
    has_sheet = has_sheet.lower() == "true"
    has_dialog = has_dialog.lower() == "true"
    is_modal = has_sheet or has_dialog or any(k in front_win_name.lower() for k in ["save", "另存", "open", "alert", "dialog", "confirm", "提示"])

    if not is_modal:
        return {"modal_detected": False, "dismissal_attempted": False, "modal_type": None, "cleared": True}

    modal_type = "sheet" if has_sheet else "dialog" if has_dialog else "popup_window"
    heal_script = f'''
    tell application "{app_name}"
        activate
        tell application "System Events"
            key code 53
            delay 0.3
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", heal_script], capture_output=True)

    re_res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    re_parts = re_res.stdout.strip().split("|||")
    re_cleared = not ((re_parts[2].lower() == "true") if len(re_parts) >= 3 else False) and not ((re_parts[3].lower() == "true") if len(re_parts) >= 4 else False)

    return {"modal_detected": True, "modal_type": modal_type, "modal_title": front_win_name, "dismissal_attempted": True, "cleared": re_cleared}

# --- Layer 1: Native IPC (Terminal Direct) ---

def get_terminal_tabs(pattern=None):
    script = '''
    tell application "Terminal"
        set outText to ""
        set winIndex to 0
        repeat with w in windows
            set winIndex to winIndex + 1
            set winId to (id of w as string)
            set winName to name of w
            set tabIndex to 0
            repeat with t in tabs of w
                set tabIndex to tabIndex + 1
                set tTty to tty of t
                set tTitle to custom title of t
                set isSel to (selected of t as string)
                set outText to outText & winId & "|||" & (winIndex as string) & "|||" & (tabIndex as string) & "|||" & tTty & "|||" & tTitle & "|||" & winName & "|||" & isSel & "\\n"
            end repeat
        end repeat
        return outText
    end tell
    '''
    res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if res.returncode != 0: return []
    tabs = []
    for line in [l.strip() for l in res.stdout.strip().split('\n') if l.strip()]:
        parts = line.split("|||")
        if len(parts) >= 7:
            win_id, win_idx, tab_idx, tty, custom_title, win_name, is_selected = parts[:7]
            if pattern is None or re.search(pattern, f"{custom_title} {win_name}", re.IGNORECASE):
                tabs.append({"window_id": win_id, "window_index": int(win_idx), "tab_index": int(tab_idx),
                    "tty": tty, "title": custom_title, "window_name": win_name, "selected": is_selected == "true"})
    return tabs

def send_terminal_enter_with_ack(pattern="claude"):
    write_heartbeat("terminal_enter", "executing")
    with FileLockContext():
        tabs = get_terminal_tabs(pattern=pattern)
        if not tabs:
            ack = build_ack("terminal_enter", "Terminal", None, "native_ipc", "FAILED", details={"error": f"No tabs matching '{pattern}'"})
            print(json.dumps(ack, indent=2, ensure_ascii=False))
            write_heartbeat("terminal_enter", "failed_no_target")
            return False
        results = []
        for t in tabs:
            pre_state = {"window_id": t["window_id"], "tab_index": t["tab_index"], "title": t["title"]}
            script = f'''
            tell application "Terminal"
                try
                    set targetWin to (first window whose id is {t['window_id']})
                    set targetTab to item {t['tab_index']} of tabs of targetWin
                    do script "" in targetTab
                    return "SUCCESS"
                on error errStr
                    return errStr
                end try
            end tell
            '''
            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            status = "SUCCESS" if "SUCCESS" in res.stdout else "FAILED"
            post_state = {"action_executed": "injected_newline", "result": res.stdout.strip()}
            ack = build_ack("terminal_enter", "Terminal", t, "native_ipc_do_script", status, pre_state=pre_state, post_state=post_state)
            results.append(ack)
        print(json.dumps(results if len(results) > 1 else results[0], indent=2, ensure_ascii=False))
        write_heartbeat("terminal_enter", "completed")
        return all(r["status"] == "SUCCESS" for r in results)

# --- Layer 2: System Events with caffeinate + Anti-Modal ---

def get_app_windows(app_name="Google Chrome", pattern=None):
    script = f'''
    tell application "{app_name}"
        set outText to ""
        if (count of windows) > 0 then
            repeat with w in (every window)
                set wName to name of w
                set wId to (id of w as string)
                try
                    set wBounds to bounds of w
                    set bStr to (item 1 of wBounds as string) & "," & (item 2 of wBounds as string) & "," & (item 3 of wBounds as string) & "," & (item 4 of wBounds as string)
                on error
                    set bStr to "0,0,0,0"
                end try
                set outText to outText & wId & "|||" & wName & "|||" & bStr & "\\n"
            end repeat
        end if
        return outText
    end tell
    '''
    res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if res.returncode != 0: return []
    results = []
    for line in [l.strip() for l in res.stdout.strip().split('\n') if l.strip()]:
        parts = line.split("|||")
        if len(parts) >= 2:
            win_id, win_name = parts[0], parts[1]
            bounds = parts[2] if len(parts) >= 3 else "0,0,0,0"
            if pattern is None or re.search(pattern, win_name, re.IGNORECASE):
                x1, y1, x2, y2 = map(int, bounds.split(',')) if ',' in bounds else (0,0,0,0)
                results.append({"id": win_id, "title": win_name, "app": app_name,
                    "bounds": {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "width": x2-x1, "height": y2-y1}})
    return results

def send_key_system_events_with_ack(app_name="Google Chrome", pattern=None, key="enter", delay=0.2):
    write_heartbeat("sys_events_key", "executing")
    with FileLockContext():
        wake_display_if_needed()
        key_code = KEY_MAP.get(str(key).lower())
        if key_code is None:
            try: key_code = int(key)
            except ValueError: return False
        windows = get_app_windows(app_name=app_name, pattern=pattern)
        if not windows:
            ack = build_ack("system_events_key", app_name, None, "system_events", "FAILED", details={"error": f"No windows matching '{pattern}' in '{app_name}'"})
            print(json.dumps(ack, indent=2, ensure_ascii=False))
            return False
        results = []
        for w in windows:
            pre_state = {"window_id": w["id"], "title": w["title"], "bounds": w["bounds"]}
            modal_audit = audit_and_heal_modals(app_name=app_name, target_win_id=w["id"])
            if modal_audit.get("modal_detected") and not modal_audit.get("cleared"):
                ack = build_ack("system_events_key", app_name, w, "system_events_accessibility", "MODAL_BLOCKED",
                    pre_state=pre_state, modal_audit=modal_audit, details={"reason": "Blocking modal could not be dismissed."})
                results.append(ack)
                continue
            script = f'''
            tell application "{app_name}"
                activate
                set index of (first window whose id is {w['id']}) to 1
                delay {delay}
                tell application "System Events"
                    tell process "{app_name}"
                        set isFront to frontmost
                    end tell
                    key code {key_code}
                    return isFront as string
                end tell
            end tell
            '''
            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            is_front = "true" in res.stdout.lower()
            status = "SUCCESS" if is_front and res.returncode == 0 else "PARTIAL" if res.returncode == 0 else "FAILED"
            post_state = {"key_sent": key, "key_code": key_code, "frontmost_verified": is_front}
            ack = build_ack("system_events_key", app_name, w, "system_events_accessibility", status,
                pre_state=pre_state, post_state=post_state, modal_audit=modal_audit)
            results.append(ack)
        print(json.dumps(results if len(results) > 1 else results[0], indent=2, ensure_ascii=False))
        write_heartbeat("sys_events_key", "completed")
        return all(r["status"] in ["SUCCESS", "PARTIAL"] for r in results)

# --- launchd Scheduler (Replaces time.sleep) ---

def generate_launchd_schedule(label, hour, minute, command_args, one_shot=True):
    """
    Generates and loads a macOS launchd plist for OS-native scheduling.
    Survives sleep/wake, App Nap, and terminal closure.
    Wraps execution with caffeinate to prevent idle sleep during GUI ops.
    """
    plist_path = os.path.join(LAUNCHD_PLIST_DIR, f"{label}.plist")
    log_path = f"/tmp/{label}.log"
    err_path = f"/tmp/{label}.err"

    # Build the wrapper shell command with caffeinate
    py_cmd = f'{PYTHON_PATH} {SCRIPT_PATH} {" ".join(command_args)}'
    shell_cmd = f'caffeinate -i {py_cmd}'

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>{shell_cmd}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>{hour}</integer>
        <key>Minute</key>
        <integer>{minute}</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{log_path}</string>
    <key>StandardErrorPath</key>
    <string>{err_path}</string>
    <key>ProcessType</key>
    <string>Interactive</string>
</dict>
</plist>"""

    os.makedirs(LAUNCHD_PLIST_DIR, exist_ok=True)

    # Unload existing if present
    subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}", plist_path], capture_output=True)
    time.sleep(0.3)

    with open(plist_path, 'w') as f:
        f.write(plist_content)

    # Load via launchctl
    res = subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", plist_path], capture_output=True, text=True)
    loaded = res.returncode == 0

    result = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": "schedule_created",
        "label": label,
        "plist_path": plist_path,
        "scheduled_time": f"{hour:02d}:{minute:02d}",
        "command": py_cmd,
        "caffeinate_wrapped": True,
        "launchd_loaded": loaded,
        "log_path": log_path,
        "err_path": err_path,
        "status": "SCHEDULED" if loaded else "LOAD_FAILED",
        "details": {"stderr": res.stderr.strip()} if not loaded else {}
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return loaded

def remove_launchd_schedule(label):
    plist_path = os.path.join(LAUNCHD_PLIST_DIR, f"{label}.plist")
    subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}", plist_path], capture_output=True)
    if os.path.exists(plist_path):
        os.remove(plist_path)
    print(json.dumps({"action": "schedule_removed", "label": label, "status": "REMOVED"}, indent=2))

def list_launchd_schedules():
    results = []
    for f in os.listdir(LAUNCHD_PLIST_DIR):
        if f.startswith("com.macauto.") and f.endswith(".plist"):
            label = f.replace(".plist", "")
            res = subprocess.run(["launchctl", "print", f"gui/{os.getuid()}/{label}"], capture_output=True, text=True)
            loaded = res.returncode == 0
            results.append({"label": label, "plist": os.path.join(LAUNCHD_PLIST_DIR, f), "loaded": loaded})
    print(json.dumps(results, indent=2, ensure_ascii=False))

# --- Main CLI ---

def main():
    parser = argparse.ArgumentParser(description="Universal macOS Automation CLI v7.0.0 (launchd Native Scheduling)")
    subparsers = parser.add_subparsers(dest="category")

    # terminal
    p_term = subparsers.add_parser("terminal")
    sub_term = p_term.add_subparsers(dest="term_action")
    t_enter = sub_term.add_parser("enter")
    t_enter.add_argument("--filter", default="claude")
    t_list = sub_term.add_parser("list")
    t_list.add_argument("--filter", default=None)

    # sys-events
    p_sys = subparsers.add_parser("sys-events")
    sub_sys = p_sys.add_subparsers(dest="sys_action")
    s_key = sub_sys.add_parser("key")
    s_key.add_argument("--app", required=True)
    s_key.add_argument("--filter", default=None)
    s_key.add_argument("--key", default="enter")

    # window
    p_win = subparsers.add_parser("window")
    sub_win = p_win.add_subparsers(dest="win_action")
    w_list = sub_win.add_parser("list")
    w_list.add_argument("--app", default="Terminal")
    w_list.add_argument("--filter", default=None)

    # schedule (launchd-based)
    p_sched = subparsers.add_parser("schedule", help="OS-native launchd scheduling (replaces --at)")
    sub_sched = p_sched.add_subparsers(dest="sched_action")
    sc_add = sub_sched.add_parser("add", help="Create a scheduled task")
    sc_add.add_argument("--label", required=True, help="Unique job label (e.g. claude-enter-daily)")
    sc_add.add_argument("--time", required=True, help="HH:MM format")
    sc_add.add_argument("--cmd", required=True, nargs=argparse.REMAINDER, help="mac_auto.py subcommand args (e.g. terminal enter --filter claude)")
    sc_rm = sub_sched.add_parser("remove", help="Remove a scheduled task")
    sc_rm.add_argument("--label", required=True)
    sub_sched.add_parser("list", help="List all mac_auto scheduled tasks")

    # heartbeat
    p_hb = subparsers.add_parser("heartbeat", help="Check heartbeat status of recent tasks")

    args = parser.parse_args()

    if args.category == "terminal":
        if args.term_action == "enter":
            send_terminal_enter_with_ack(pattern=args.filter)
        elif args.term_action == "list":
            print(json.dumps(get_terminal_tabs(pattern=args.filter), indent=2, ensure_ascii=False))

    elif args.category == "sys-events":
        if args.sys_action == "key":
            send_key_system_events_with_ack(app_name=args.app, pattern=args.filter, key=args.key)

    elif args.category == "window":
        if args.win_action == "list":
            print(json.dumps(get_app_windows(app_name=args.app, pattern=args.filter), indent=2, ensure_ascii=False))

    elif args.category == "schedule":
        if args.sched_action == "add":
            h, m = map(int, args.time.split(":"))
            label = f"com.macauto.{args.label}"
            generate_launchd_schedule(label, h, m, args.cmd)
        elif args.sched_action == "remove":
            remove_launchd_schedule(f"com.macauto.{args.label}")
        elif args.sched_action == "list":
            list_launchd_schedules()

    elif args.category == "heartbeat":
        os.makedirs(HEARTBEAT_DIR, exist_ok=True)
        hbs = []
        for f in os.listdir(HEARTBEAT_DIR):
            if f.endswith(".json"):
                with open(os.path.join(HEARTBEAT_DIR, f)) as fp:
                    hbs.append(json.load(fp))
        print(json.dumps(hbs, indent=2, ensure_ascii=False))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
