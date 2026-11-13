
# === JOMZ PREMIUM PURPLE BLUE THEME ===
import builtins as _jomz_builtins

_jomz_original_print = _jomz_builtins.print
_jomz_original_input = _jomz_builtins.input

def print(*args, **kwargs):
    message = " ".join(str(x) for x in args)
    color = "\033[96m"

    if "JOMZ" in message or "---" in message:
        color = "\033[95m"
    elif any(x in message.lower() for x in
             ["error", "invalid", "warning", "wrong", "denied"]):
        color = "\033[91m"
    elif any(x in message.lower() for x in
             ["saved", "success", "updated", "exported", "goodbye", "granted"]):
        color = "\033[92m"
    elif any(x in message.lower() for x in
             ["dashboard", "total:", "choose"]):
        color = "\033[96m"
    elif message.strip()[:1].isdigit():
        color = "\033[94m"

    _jomz_original_print(color + message + "\033[0m", **kwargs)

def input(prompt=""):
    return _jomz_original_input("\033[96m" + prompt + "\033[0m")

import json
import hashlib
import secrets
import getpass
import csv
import os
import shutil
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(BASE, "jomz_accounts.json")
BACKUP_DIR = os.path.join(BASE, "backups")
MAX = 50

def load():
    if os.path.exists(FILE):
        try:
            with open(FILE, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            print("Warning: Hindi mabasa ang records file.")
    return []

def save(accounts):
    old_accounts = []

    if os.path.exists(FILE):
        try:
            with open(FILE, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    old_accounts = data
        except (json.JSONDecodeError, OSError):
            old_accounts = []

    remaining_old = list(old_accounts)
    events = []

    for new in accounts:
        key = (str(new.get("name", "")), str(new.get("gmail", "")))

        match = None
        for old in remaining_old:
            old_key = (str(old.get("name", "")), str(old.get("gmail", "")))
            if old_key == key:
                match = old
                break

        if match is None:
            events.append(
                ("ADD", new.get("name", "Unknown"),
                 new.get("status", "Unknown"))
            )
        else:
            remaining_old.remove(match)
            old_status = match.get("status", "Unknown")
            new_status = new.get("status", "Unknown")

            if old_status != new_status:
                events.append(
                    ("UPDATE", new.get("name", "Unknown"),
                     f"{old_status} -> {new_status}")
                )

    for old in remaining_old:
        events.append(
            ("DELETE", old.get("name", "Unknown"),
             old.get("status", "Unknown"))
        )

    os.makedirs(BACKUP_DIR, exist_ok=True)

    if os.path.exists(FILE):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = os.path.join(BACKUP_DIR, f"accounts_{stamp}.json")
        shutil.copy2(FILE, backup)

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=4, ensure_ascii=False)

    if events:
        log_file = os.path.join(BASE, "jomz_activity.log")
        with open(log_file, "a", encoding="utf-8") as f:
            for action, name, detail in events:
                stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{stamp} | {action} | {name} | {detail}\n")

def view(accounts):
    print("\n--- SAVED ENTRIES ---")
    if not accounts:
        print("Wala pang entries.")
    for i, a in enumerate(accounts, 1):
        print(f"{i}. {a['name']} | {a['gmail']} | {a['status']}")
    print("Total:", len(accounts))

def choose_entry(accounts):
    view(accounts)
    if not accounts:
        return None
    try:
        n = int(input("Entry number: "))
        if 1 <= n <= len(accounts):
            return n - 1
    except ValueError:
        pass
    print("Invalid number.")
    return None


# JOMZ_PIN_SECURITY
PIN_FILE = os.path.join(BASE, "pin_config.json")

def pin_login():
    if not os.path.exists(PIN_FILE):
        print("\\n=== FIRST TIME PIN SETUP ===")
        while True:
            pin = getpass.getpass("Create 4-8 digit PIN: ")
            if not pin.isdigit() or not 4 <= len(pin) <= 8:
                print("PIN must contain 4-8 digits.")
                continue
            confirm = getpass.getpass("Confirm PIN: ")
            if pin != confirm:
                print("PINs do not match. Try again.")
                continue
            salt = secrets.token_hex(16)
            digest = hashlib.sha256((salt + pin).encode()).hexdigest()
            with open(PIN_FILE, "w", encoding="utf-8") as f:
                json.dump({"salt": salt, "hash": digest}, f)
            print("PIN saved!")
            break

    with open(PIN_FILE, encoding="utf-8") as f:
        saved = json.load(f)

    for attempt in range(3):
        pin = getpass.getpass("Enter JOMZ PIN: ")
        digest = hashlib.sha256((saved["salt"] + pin).encode()).hexdigest()
        if secrets.compare_digest(digest, saved["hash"]):
            print("Access granted!")
            return True
        print("Wrong PIN. Attempts left:", 2 - attempt)

    print("Access denied.")
    return False

if not pin_login():
    raise SystemExit

accounts = load()

while True:
    P = "\033[95m"
    B = "\033[94m"
    C = "\033[96m"
    G = "\033[92m"
    R = "\033[0m"

    _jomz_original_print()
    _jomz_original_print(P + "╔══════════════════════════════════════╗" + R)
    _jomz_original_print(P + "║" + B + "          JOMZ TRACKER PRO            " + P + "║" + R)
    _jomz_original_print(P + "║" + C + "          PREMIUM EDITION             " + P + "║" + R)
    _jomz_original_print(P + "╠══════════════════════════════════════╣" + R)
    _jomz_original_print(B + "║  1. Add Entry                         ║" + R)
    _jomz_original_print(B + "║  2. View Entries                      ║" + R)
    _jomz_original_print(B + "║  3. Search                            ║" + R)
    _jomz_original_print(B + "║  4. Update Status                     ║" + R)
    _jomz_original_print(C + "║  5. Dashboard                         ║" + R)
    _jomz_original_print(B + "║  6. Delete Entry                      ║" + R)
    _jomz_original_print(G + "║  7. Exit                              ║" + R)
    _jomz_original_print(C + "║  8. Export CSV                        ║" + R)
    _jomz_original_print(P + "║  9. Activity History                   ║" + R)
    _jomz_original_print(P + "╚══════════════════════════════════════╝" + R)

    choice = input("Choose: ").strip()

    if choice == "1":
        if len(accounts) >= MAX:
            print("Maximum 50 entries!")
            continue
        name = input("Account label: ").strip()
        gmail = input("Gmail label only (no password): ").strip()
        if not name:
            print("Label cannot be empty.")
            continue
        accounts.append({
            "name": name,
            "gmail": gmail,
            "status": "Pending"
        })
        save(accounts)
        print("Saved!")

    elif choice == "2":
        view(accounts)

    elif choice == "3":
        term = input("Search label: ").strip().casefold()
        found = False
        for i, a in enumerate(accounts, 1):
            if term in a["name"].casefold() or term in a["gmail"].casefold():
                print(f"{i}. {a['name']} | {a['gmail']} | {a['status']}")
                found = True
        if not found:
            print("Walang matching entry.")

    elif choice == "4":
        n = choose_entry(accounts)
        if n is not None:
            print("1. Pending  2. Bound  3. Locked  4. Failed  5. Verified")
            status = {
                "1": "Pending",
                "2": "Bound",
                "3": "Locked",
                "4": "Failed",
                "5": "Verified"
            }
            s = input("New status: ").strip()
            if s in status:
                accounts[n]["status"] = status[s]
                save(accounts)
                print("Status updated!")
            else:
                print("Invalid status.")

    elif choice == "5":
        P = "\033[95m"
        B = "\033[94m"
        C = "\033[96m"
        G = "\033[92m"
        R = "\033[0m"
        RED = "\033[91m"

        statuses = ["Pending", "Bound", "Locked", "Failed", "Verified"]
        counts = {
            status: sum(1 for a in accounts if a.get("status") == status)
            for status in statuses
        }

        total = len(accounts)
        verified = counts["Verified"]
        pending = counts["Pending"]

        _jomz_original_print()
        _jomz_original_print(P + "╔════════════════════════════════════════════╗" + R)
        _jomz_original_print(P + "║" + B + "          JOMZ TRACKER PRO 2.0             " + P + "║" + R)
        _jomz_original_print(P + "║" + C + "          STATISTICS DASHBOARD             " + P + "║" + R)
        _jomz_original_print(P + "╠════════════════════════════════════════════╣" + R)
        _jomz_original_print(B + f"║  TOTAL ENTRIES       : {total:<22}║" + R)
        _jomz_original_print(G + f"║  VERIFIED            : {verified:<22}║" + R)
        _jomz_original_print(C + f"║  PENDING             : {pending:<22}║" + R)
        _jomz_original_print(P + "╠════════════════════════════════════════════╣" + R)

        colors = {
            "Pending": C,
            "Bound": B,
            "Locked": P,
            "Failed": RED,
            "Verified": G
        }

        for status in statuses:
            count = counts[status]
            pct = round(count / total * 100) if total else 0
            filled = min(10, round(pct / 10))
            bar = "█" * filled + "░" * (10 - filled)

            _jomz_original_print(
                colors[status]
                + f"║ {status:<9} {count:>4}  {pct:>3}% [{bar}] ║"
                + R
            )

        _jomz_original_print(P + "╠════════════════════════════════════════════╣" + R)
        _jomz_original_print(C + "║  BACKUP SYSTEM: ACTIVE                     ║" + R)
        _jomz_original_print(P + "╚════════════════════════════════════════════╝" + R)
        _jomz_original_print()

    elif choice == "6":
        n = choose_entry(accounts)
        if n is not None:
            confirm = input("Delete this entry? (y/n): ").strip().lower()
            if confirm == "y":
                removed = accounts.pop(n)
                save(accounts)
                print("Deleted:", removed["name"])
            else:
                print("Cancelled.")

    elif choice == "8":
        export_file = os.path.join(BASE, "jomz_export.csv")
        with open(export_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(
                f, fieldnames=["name", "gmail", "status"]
            )
            writer.writeheader()
            writer.writerows(accounts)
        print("CSV exported:", export_file)

    elif choice == "9":
        log_file = os.path.join(BASE, "jomz_activity.log")
        _jomz_original_print()
        _jomz_original_print(P + "╔══════════════════════════════════════╗" + R)
        _jomz_original_print(P + "║" + B + "        JOMZ ACTIVITY HISTORY        " + P + "║" + R)
        _jomz_original_print(P + "╚══════════════════════════════════════╝" + R)

        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                history = f.readlines()

            if history:
                for entry in history[-50:]:
                    _jomz_original_print(C + entry.rstrip() + R)
                print("Showing latest 50 activities.")
            else:
                print("Wala pang recorded activities.")
        else:
            print("Wala pang activity history.")
        _jomz_original_print()

    elif choice == "7":
        print("Goodbye!")
        break

    else:
        print("Pumili ng 1 hanggang 9.")
