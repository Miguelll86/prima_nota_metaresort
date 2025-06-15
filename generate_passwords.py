#!/usr/bin/env python3
"""
Script per generare password hashate per Streamlit Secrets
"""

import bcrypt

def hash_password(password):
    """Hasha una password con bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def main():
    print("🔐 Generatore Password Hashate per Streamlit Secrets")
    print("=" * 50)
    
    # Password da hashare
    passwords = {
        "admin": "password123",
        "utente": "demo", 
        "SACHIN": "meta2026",
        "MICHELE": "meta2026",
        "SANDRA": "meta2026",
        "SEDE": "meta2026"
    }
    
    print("\n📋 Configurazione per .streamlit/secrets.toml:")
    print("-" * 50)
    print("[passwords]")
    
    for username, password in passwords.items():
        hashed = hash_password(password)
        print(f'{username} = "{hashed}"  # {password}')
    
    print("\n📋 Configurazione per Streamlit Cloud Secrets:")
    print("-" * 50)
    print("Copia questo nel dashboard di Streamlit Cloud:")
    print()
    print("[passwords]")
    
    for username, password in passwords.items():
        hashed = hash_password(password)
        print(f'{username} = "{hashed}"')
    
    print("\n✅ Password generate con successo!")
    print("💡 Ricorda di aggiornare sia il file .streamlit/secrets.toml che Streamlit Cloud")

if __name__ == "__main__":
    main() 