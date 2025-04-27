# utils/session.py

import streamlit as st
import redis
import hashlib
from config.settings import REDIS_HOST, REDIS_PORT

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(email, password):
    hashed_pw = r.get(f"player:{email}:password")
    return hashed_pw == hash_password(password)

def register_or_validate_user():
    if not st.session_state.get("auth_passed", False):
        st.sidebar.header("Login")
        st.sidebar.info("👋 First time users: Just enter your CCO ID and create your own password for tonight's event!")

        email_input = st.sidebar.text_input("Your Email (for scoring):", key="email_input")
        password_input = st.sidebar.text_input("Your Password:", type="password", key="password_input")

        if email_input and password_input:
            email = email_input.strip().lower()
            password = password_input
            st.session_state["player_email"] = email

            user_key = f"player:{email}:password"
            stored = r.get(user_key)
            hashed = hash_password(password)

            if stored is None:
                r.set(user_key, hashed)
                st.session_state["auth_passed"] = True
                st.sidebar.success("✅ New player registered.")
            elif stored == hashed:
                st.session_state["auth_passed"] = True
                st.sidebar.success("✅ Logged in.")
            else:
                st.session_state["auth_passed"] = False
                st.sidebar.error("❌ Incorrect password.")
    else:
        st.sidebar.success("✅ Logged in.")

def init_session():
    if "snarky_mode" not in st.session_state:
        st.session_state["snarky_mode"] = False

