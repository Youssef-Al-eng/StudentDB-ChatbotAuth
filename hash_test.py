# hash_password.py
import hashlib
import json
from getpass import getpass
from pathlib import Path

def sha256_hash(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def main():
    username = input("Username (leave empty for 'admin'): ").strip() or "admin"
    pwd = getpass("Enter password: ")
    confirm = getpass("Confirm password: ")
    if pwd != confirm:
        print("Error: passwords do not match.")
        return

    hashed = sha256_hash(pwd)
    print("SHA256 hash:", hashed)

    save = input("Save to credentials.json? (y/N): ").strip().lower()
    if save == "y":
        creds_path = Path("credentials.json")
        data = {}
        if creds_path.exists():
            try:
                data = json.loads(creds_path.read_text(encoding="utf-8"))
            except Exception:
                data = {}

        data[username] = {"username": username, "password": hashed}
        creds_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Saved under username '{username}' in {creds_path.resolve()}")

if __name__ == "__main__":
    main()
