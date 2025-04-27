import streamlit as st

def list_tickets(trouble_tickets):
    st.subheader("📃 All Trouble Tickets")
    for ticket in trouble_tickets:
        st.write(f"**#{ticket['id']}:** {ticket['issue']}")

def random_joke(jokes, snarky_comments):
    import random
    st.subheader("😂 Random Joke")
    st.write(random.choice(jokes))
    if st.session_state["snarky_mode"]:
        st.write(f"💀 **{random.choice(snarky_comments)}**")

def random_trivia(trivia, snarky_comments):
    import random
    st.subheader("📚 Random Networking Trivia")
    st.write(random.choice(trivia))
    if st.session_state["snarky_mode"]:
        st.write(f"💀 **{random.choice(snarky_comments)}**")