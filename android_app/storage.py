import os
import json
import csv
import hashlib
import secrets
import shutil
from datetime import datetime


class TrackerStorage:

    def __init__(self, folder):
        self.folder = folder
        self.data_file = os.path.join(folder, "jomz_accounts.json")
        self.pin_file = os.path.join(folder, "pin_config.json")
        self.log_file = os.path.join(folder, "jomz_activity.log")
        self.backup_dir = os.path.join(folder, "backups")

        os.makedirs(self.folder, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)

        if not os.path.exists(self.data_file):
            self.save_json(self.data_file, [])

    def save_json(self, path, data):
        temp = path + ".tmp"
        with open(temp, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        os.replace(temp, path)

    def load_accounts(self):
        try:
            with open(self.data_file, encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, list) else []
        except (OSError, ValueError):
            return []

    def save_accounts(self, accounts):
        self.save_json(self.data_file, accounts)
        backup = os.path.join(
            self.backup_dir, "latest_backup.json"
        )
        shutil.copy2(self.data_file, backup)

    def has_pin(self):
        return os.path.isfile(self.pin_file)

    def create_pin(self, pin):
        if not pin.isdigit() or not 4 <= len(pin) <= 8:
            return False

        salt = secrets.token_hex(16)
        digest = hashlib.sha256(
            (salt + pin).encode("utf-8")
        ).hexdigest()

        self.save_json(self.pin_file, {
            "salt": salt,
            "hash": digest
        })
        return True

    def verify_pin(self, pin):
        try:
            with open(self.pin_file, encoding="utf-8") as file:
                config = json.load(file)

            digest = hashlib.sha256(
                (config["salt"] + pin).encode("utf-8")
            ).hexdigest()

            return secrets.compare_digest(
                digest, config["hash"]
            )
        except (OSError, ValueError, KeyError, TypeError):
            return False

    def log_activity(self, action, name, detail):
        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        line = f"{timestamp} | {action} | {name} | {detail}\n"

        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(line)

    def get_activity(self, limit=50):
        try:
            with open(self.log_file, encoding="utf-8") as file:
                return file.readlines()[-limit:]
        except OSError:
            return []

    def export_csv(self):
        path = os.path.join(self.folder, "jomz_export.csv")
        accounts = self.load_accounts()

        with open(path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["name", "gmail", "status"]
            )
            writer.writeheader()

            for account in accounts:
                writer.writerow({
                    "name": account.get("name", ""),
                    "gmail": account.get("gmail", ""),
                    "status": account.get("status", "Pending")
                })

        return path
