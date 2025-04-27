# admin_app.py

import streamlit as st
import redis
import os
from dotenv import load_dotenv
import json

# Load .env file
load_dotenv()
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# Load game data
GAME_DATA_FILE = './data/game_data.json'

try:
    with open(GAME_DATA_FILE, 'r') as f:
        game_data = json.load(f)

    trouble_tickets = [
        {
            "id": f"ticket_{t['id']}",
            "root_cause": t.get("root_cause", "No root cause provided")
        }
        for t in game_data.get("trouble_tickets", [])
    ]

    network_issues = [
        {
            "id": f"issue_{i['id']}",
            "root_cause": i.get("root_cause", "No root cause provided")
        }
        for i in game_data.get("network_issues", [])
    ]

except Exception as e:
    st.error(f"Failed to load game data: {e}")
    trouble_tickets = []
    network_issues = []

# Connect to Redis
r = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# Streamlit UI
st.set_page_config(page_title="Admin Interface", page_icon="🔧", layout="centered")
st.title("🔧 Admin Interface")

# --- Redis Connection Info ---
with st.expander("📡 Redis Connection Details", expanded=True):
    st.write(f"**Host:** {REDIS_HOST}")
    st.write(f"**Port:** {REDIS_PORT}")
    st.write(f"**DB:** {REDIS_DB}")
    if REDIS_PASSWORD:
        st.write(f"**Password:** (set)")
    else:
        st.write(f"**Password:** (not set)")

st.divider()

# Helper functions
def player_prefix(email):
    return f"player:{email}"

def player_password_key(email):
    return f"{player_prefix(email)}:password"

def player_structured_key(email):
    return f"{player_prefix(email)}:structured"

def player_unstructured_key(email):
    return f"{player_prefix(email)}:unstructured"

# Sidebar
menu = st.sidebar.selectbox("Menu", ["View Players", "Create Player", "Update Player", "Delete Player"])

# --- View Players ---
if menu == "View Players":
    st.subheader("👥 All Players")
    player_password_keys = r.keys("player:*:password")
    if not player_password_keys:
        st.info("No players found.")
    else:
        for key in player_password_keys:
            email = key.split("player:")[1].replace(":password", "")
            password = r.get(player_password_key(email))

            # Structured scores
            structured_score = {}
            if r.exists(player_structured_key(email)) and r.type(player_structured_key(email)) == "hash":
                structured_score = r.hgetall(player_structured_key(email))

            # Unstructured scores
            unstructured_score = {}
            if r.exists(player_unstructured_key(email)) and r.type(player_unstructured_key(email)) == "hash":
                unstructured_score = r.hgetall(player_unstructured_key(email))

            st.write(f"### 📧 {email}")
            with st.expander("Details", expanded=False):
                st.write(f"**Password:** {password}")
                st.write(f"**Structured Scores:**")
                st.json(structured_score if structured_score else "None")
                st.write(f"**Unstructured Scores:**")
                st.json(unstructured_score if unstructured_score else "None")

# --- Create Player ---
elif menu == "Create Player":
    st.subheader("🆕 Create New Player")
    email = st.text_input("Player Email")
    password = st.text_input("Password", type="password")

    if st.button("Create Player"):
        if r.exists(player_password_key(email)):
            st.error("Player already exists!")
        else:
            r.set(player_password_key(email), password)
            st.success(f"Player {email} created.")
            st.info("You can add scores using Update Player after creating.")

# --- Update Player ---
elif menu == "Update Player":
    st.subheader("✏️ Update Existing Player")

    # Fetch all players
    player_password_keys = r.keys("player:*:password")
    player_emails = [key.split("player:")[1].replace(":password", "") for key in player_password_keys]

    if not player_emails:
        st.info("No players found.")
    else:
        # Dropdown to select player
        email = st.selectbox("Select a Player to Update", options=player_emails)

        if email:
            # Password editing
            st.subheader("🔑 Update Password")
            new_password = st.text_input("New Password (leave blank to keep current)", type="password")
            
            if st.button("Update Password"):
                if new_password:
                    r.set(player_password_key(email), new_password)
                    st.success(f"Password updated for {email}.")

            st.divider()

            # --- Structured Challenges ---
            st.subheader("🛠 Structured Challenges (Trouble Tickets)")

            structured_scores = {}
            if r.exists(player_structured_key(email)) and r.type(player_structured_key(email)) == "hash":
                structured_scores = r.hgetall(player_structured_key(email))

            structured_options = {
                f"{ticket['id']} — {ticket['root_cause']}": ticket['id']
                for ticket in trouble_tickets
            }

            selected_structured_label = st.selectbox(
                "Select Structured Trouble Ticket",
                options=list(structured_options.keys())
            )

            selected_ticket_id = structured_options[selected_structured_label]

            current_structured_score = int(structured_scores.get(selected_ticket_id, 0))
            new_structured_score = st.number_input(
                "Structured Score",
                value=current_structured_score,
                min_value=0,
                step=1,
                key="structured_score_input"
            )

            if st.button("Update Structured Score"):
                if selected_ticket_id:
                    r.hset(player_structured_key(email), selected_ticket_id, new_structured_score)
                    st.success(f"Structured score for {selected_ticket_id} updated to {new_structured_score}.")

            st.divider()

            # --- Unstructured Challenges ---
            st.subheader("🛠 Unstructured Challenges (Network Issues)")

            unstructured_scores = {}
            if r.exists(player_unstructured_key(email)) and r.type(player_unstructured_key(email)) == "hash":
                unstructured_scores = r.hgetall(player_unstructured_key(email))

            unstructured_options = {
                f"{issue['id']} — {issue['root_cause']}": issue['id']
                for issue in network_issues
            }

            selected_unstructured_label = st.selectbox(
                "Select Unstructured Issue",
                options=list(unstructured_options.keys())
            )

            selected_issue_id = unstructured_options[selected_unstructured_label]

            current_unstructured_score = int(unstructured_scores.get(selected_issue_id, 0))
            new_unstructured_score = st.number_input(
                "Unstructured Score",
                value=current_unstructured_score,
                min_value=0,
                step=1,
                key="unstructured_score_input"
            )

            if st.button("Update Unstructured Score"):
                if selected_issue_id:
                    r.hset(player_unstructured_key(email), selected_issue_id, new_unstructured_score)
                    st.success(f"Unstructured score for {selected_issue_id} updated to {new_unstructured_score}.")

# --- Delete Player ---
elif menu == "Delete Player":
    st.subheader("❌ Delete a Player")
    email = st.text_input("Player Email to Delete")

    if st.button("Delete Player"):
        deleted = False
        if r.exists(player_password_key(email)):
            r.delete(player_password_key(email))
            deleted = True
        if r.exists(player_structured_key(email)):
            r.delete(player_structured_key(email))
            deleted = True
        if r.exists(player_unstructured_key(email)):
            r.delete(player_unstructured_key(email))
            deleted = True

        if deleted:
            st.success(f"Player {email} deleted from Redis.")
        else:
            st.warning("Player not found.")

