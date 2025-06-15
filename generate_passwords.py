#!/usr/bin/env python3
"""
Script per generare password hashate per Streamlit Secrets
"""

import bcrypt

def hash_password(password):
    """Hasha password con bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Password per gli utenti
passwords = {
    "admin": "password123",
    "utente": "demo",
    "SACHIN": "meta2026",
    "MICHELE": "meta2026",
    "SANDRA": "meta2026",
    "SEDE": "meta2026"
}

print("Password hashate per Streamlit Secrets:")
print("[passwords]")
for username, password in passwords.items():
    hashed = hash_password(password)
    print(f"{username} = \"{hashed}\"")

print("\nCopia questo contenuto nei Secrets di Streamlit Cloud!") 