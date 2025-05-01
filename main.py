import streamlit as st
import hashlib
from cryptography.fernet import Fernet

# Use session state for attempts
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

# Cache the key so it stays the same across reruns
@st.cache_resource
def get_cipher():
    key = Fernet.generate_key()
    return Fernet(key)

cipher = get_cipher()

# In-memory storage
stored_data = {}

# Hash function
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

# Encrypt function
def encrypt_data(text):
    return cipher.encrypt(text.encode()).decode()

# Decrypt function
def decrypt_data(encrypted_text, passkey):
    hashed = hash_passkey(passkey)
    if encrypted_text in stored_data and stored_data[encrypted_text]["passkey"] == hashed:
        st.session_state.failed_attempts = 0
        return cipher.decrypt(encrypted_text.encode()).decode()
    else:
        st.session_state.failed_attempts += 1
        return None

# UI
st.title("🔒 Secure Data Encryption System")

menu = ["Home", "Store Data", "Retrieve Data", "Login"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Home":
    st.subheader("🏠 Welcome")
    st.write("Use this app to securely **store and retrieve** data with passkeys.")

elif choice == "Store Data":
    st.subheader("📂 Store Data")
    data = st.text_area("Enter Data:")
    passkey = st.text_input("Enter Passkey:", type="password")

    if st.button("Encrypt & Save"):
        if data and passkey:
            encrypted = encrypt_data(data)
            stored_data[encrypted] = {
                "passkey": hash_passkey(passkey)
            }
            st.success("✅ Data stored securely!")
            st.write("🔐 Encrypted Text:")
            st.code(encrypted)
        else:
            st.error("⚠️ Please fill in both fields.")

elif choice == "Retrieve Data":
    st.subheader("🔍 Retrieve Data")
    encrypted_input = st.text_area("Enter Encrypted Text:")
    passkey_input = st.text_input("Enter Passkey:", type="password")

    if st.button("Decrypt"):
        if encrypted_input and passkey_input:
            result = decrypt_data(encrypted_input, passkey_input)
            if result:
                st.success(f"✅ Decrypted Text: {result}")
            else:
                remaining = 3 - st.session_state.failed_attempts
                st.error(f"❌ Incorrect passkey! Attempts remaining: {remaining}")
                if remaining <= 0:
                    st.warning("🔒 Too many failed attempts! Please reauthorize.")
                    st.experimental_rerun()
        else:
            st.error("⚠️ Both fields are required.")

elif choice == "Login":
    st.subheader("🔑 Reauthorization")
    master_password = st.text_input("Enter Master Password:", type="password")

    if st.button("Login"):
        if master_password == "admin123":
            st.session_state.failed_attempts = 0
            st.success("✅ Access granted. You can try retrieving data again.")
            st.experimental_rerun()
        else:
            st.error("❌ Incorrect master password.")
