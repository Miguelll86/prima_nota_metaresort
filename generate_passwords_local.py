#!/usr/bin/env python3
"""
Script locale per generare password hashate.
NON COMMITTARE QUESTO FILE!
"""

import bcrypt

def hash_password(password):
    """Hasha password con bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

print("🔐 Generatore Password Hashate per Streamlit Secrets")
print("=" * 50)
print("⚠️  ATTENZIONE: Questo script è solo per uso locale!")
print("⚠️  NON committare mai questo file nel repository!")
print()

# Password per gli utenti (modifica secondo necessità)
passwords = {
    "admin": "password123",
    "utente": "demo",
    "SACHIN": "meta2026",
    "MICHELE": "meta2026",
    "SANDRA": "meta2026",
    "SEDE": "meta2026"
}

print("📋 Configurazione per Streamlit Cloud Secrets:")
print("-" * 50)
print("Copia questo nel dashboard di Streamlit Cloud:")
print()
print("[passwords]")

for username, password in passwords.items():
    hashed = hash_password(password)
    print(f'{username} = "{hashed}"')

print()
print("✅ Password generate con successo!")
print("💡 Ricorda di configurare i secrets in Streamlit Cloud")
print("🗑️  Elimina questo file dopo l'uso!") 