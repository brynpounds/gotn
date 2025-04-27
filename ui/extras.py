import streamlit as st
import logging  # 🛑 Add logging import

def list_tickets(trouble_tickets):
    st.subheader("📃 All Trouble Tickets")

    email = st.session_state.get("player_email", "")
    if email:
        logging.info(f"Player {email} navigated to the 'All Trouble Tickets' page.")

    for ticket in trouble_tickets:
        st.write(f"**#{ticket['id']}:** {ticket['issue']}")

def random_joke(jokes, snarky_comments):
    import random
    st.subheader("😂 Random Joke")

    email = st.session_state.get("player_email", "")
    if email:
        logging.info(f"Player {email} navigated to the 'Random Joke' page.")

    st.write(random.choice(jokes))
    if st.session_state["snarky_mode"]:
        st.write(f"💀 **{random.choice(snarky_comments)}**")

def random_trivia(trivia, snarky_comments):
    import random
    st.subheader("📚 Random Networking Trivia")

    email = st.session_state.get("player_email", "")
    if email:
        logging.info(f"Player {email} navigated to the 'Random Networking Trivia' page.")

    st.write(random.choice(trivia))
    if st.session_state["snarky_mode"]:
        st.write(f"💀 **{random.choice(snarky_comments)}**")

