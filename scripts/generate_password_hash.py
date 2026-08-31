from getpass import getpass

from pwdlib import PasswordHash

password = getpass("Enter password to hash: ")
if len(password) < 12:
    raise SystemExit("Use a password with at least 12 characters.")

hasher = PasswordHash.recommended()
print(hasher.hash(password))
