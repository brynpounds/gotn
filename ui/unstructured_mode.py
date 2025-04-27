# ui/unstructured_mode.py

import streamlit as st
from core.grader import get_unstructured_score
from core.scores import update_score
import random

def run(network_issues, snarky_comments):
    st.subheader("🛠️ Unstructured Troubleshooting Mode")
    email = st.session_state.get("player_email", "")
    if not email:
        st.warning("Please enter your email in the sidebar to track your score.")
        return

    st.markdown("""
    ### 🕵️ This is where you submit any unknown problems you find in the network.

    - No hints are provided.
    - You must discover real problems on your own.
    - Enter your best technical diagnosis below.
    """)

    user_answer = st.text_area("Enter the problem you found and diagnosed:")

    if st.button("Submit Diagnosis"):
        # Match player's answer against *all* known root causes
        best_match = None

        for issue in network_issues:
            points = int(issue["scoring"].split()[0])
            result = get_unstructured_score(user_answer, issue["root_cause"], points)
            if not best_match or result["awarded_points"] > best_match[1]["awarded_points"]:
                best_match = (issue, result)

        if best_match:
            issue, result = best_match
            issue_max_points = int(issue["scoring"].split()[0])

            if result["awarded_points"] == 0 and result["rejection_reason"]:
                st.warning(result["rejection_reason"])
            else:
                if result["awarded_points"] == issue_max_points:
                    st.success(f"**Points Awarded:** {result['awarded_points']} points 🎯 Congratulations — you nailed the maximum score!")
                else:
                    st.success(f"**Points Awarded:** {result['awarded_points']} points")

            update_score(email, "unstructured", f"issue_{issue['id']}", result["awarded_points"])

            if result["awarded_points"] == 0 and st.session_state["snarky_mode"]:
                st.write(f"💀 **{random.choice(snarky_comments)}**")

            st.caption(f"🔎 Debug Info: Best Similarity Score = {result['similarity_score']}")
        else:
            st.error("No matching issue found. Make sure you are diagnosing an actual known problem.")

