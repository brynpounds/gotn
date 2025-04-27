# structured_mode.py

import streamlit as st
from core.grader import get_structured_score
from core.scores import update_score
import random

def run(trouble_tickets, snarky_comments):
    st.subheader("📋 Select a Ticket Mode and see if you can diagnose the problem")
    email = st.session_state.get("player_email", "")
    if not email:
        st.warning("Please enter your email in the sidebar to track your score.")
        return

    ticket_options = {str(t["id"]): t["issue"] for t in trouble_tickets}
    ticket_id = st.selectbox("Select a Trouble Ticket:", list(ticket_options.keys()), format_func=lambda x: f"#{x} - {ticket_options[x]}")
    ticket = next(t for t in trouble_tickets if str(t["id"]) == ticket_id)

    st.write(f"**Trouble Ticket {ticket['id']}:** {ticket['issue']}")
    user_answer = st.text_area("Enter your diagnosis:")

    if st.button("Submit Diagnosis"):
        max_points = int(ticket["scoring"].split()[0])
        result = get_structured_score(user_answer, ticket["root_cause"], max_points)

        if result["awarded_points"] == 0 and result["rejection_reason"]:
            st.warning(result["rejection_reason"])
        else:
            if result["awarded_points"] == max_points:
                st.success(f"**Points Awarded:** {result['awarded_points']} points 🎯 Congratulations — you have reached the maximum score for this one!")
            else:
                st.success(f"**Points Awarded:** {result['awarded_points']} points")

        update_score(email, "structured", f"ticket_{ticket['id']}", result["awarded_points"])

        if result["awarded_points"] == 0 and st.session_state["snarky_mode"]:
            st.write(f"💀 **{random.choice(snarky_comments)}**")

        st.caption(f"🔎 Debug Info: Similarity Score = {result['similarity_score']}")

