# ui/scores.py

import streamlit as st
from core.scores import get_scores
from core.loader import load_game_data

def run():
    st.subheader("📊 Your Scores")
    email = st.session_state.get("player_email", "")
    if not email:
        st.warning("Please enter your email in the sidebar.")
        return

    structured = get_scores(email, "structured")
    unstructured = get_scores(email, "unstructured")

    game_data = load_game_data()
    trouble_tickets = game_data["trouble_tickets"]
    network_issues = game_data["network_issues"]

    # Structured Section
    st.markdown("### 🧩 Structured Trouble Tickets")
    if structured:
        for ticket_id, points in structured.items():
            ticket = next((t for t in trouble_tickets if f"ticket_{t['id']}" == ticket_id), None)
            if ticket:
                max_points = int(ticket["scoring"].split()[0])
                full_credit = int(points) == max_points
                green_check = " ✅" if full_credit else ""
                max_tag = " **(MAX)**" if int(points) == max_points else ""
                st.markdown(f"- **Trouble Ticket #{ticket['id']}**: {points} points{green_check}{max_tag}")
    else:
        st.write("No structured tickets scored yet.")

    # Unstructured Section
    st.markdown("### 🔍 Unstructured Diagnoses")
    if unstructured:
        for issue_id, points in unstructured.items():
            issue = next((i for i in network_issues if f"issue_{i['id']}" == issue_id), None)
            if issue:
                max_points = int(issue["scoring"].split()[0])
                root_cause = issue.get("root_cause", "Unknown Root Cause")
                short_root_cause = (root_cause[:80] + '...') if len(root_cause) > 80 else root_cause
                full_credit = int(points) == max_points
                green_check = " ✅" if full_credit else ""
                max_tag = " **(MAX)**" if full_credit else ""
                st.markdown(f"- **{short_root_cause}**: {points} points{green_check}{max_tag}")
    else:
        st.write("No unstructured entries scored yet.")

