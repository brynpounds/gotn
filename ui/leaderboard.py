import streamlit as st
import logging
import redis
from config.settings import REDIS_HOST, REDIS_PORT
from core.scores import get_scores

def run():
    st.subheader("🏆 Leaderboard")

    email = st.session_state.get("player_email", "")
    if email:
        logging.info(f"Player {email} navigated to the 'Leaderboard' page.")

    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    keys = r.keys("player:*:structured")
    players = list({key.split(":")[1] for key in keys})

    leaderboard = []
    for player in players:
        structured = get_scores(player, "structured").values()
        unstructured = get_scores(player, "unstructured").values()
        total = sum(map(int, structured)) + sum(map(int, unstructured))
        leaderboard.append((player, total))

    leaderboard.sort(key=lambda x: x[1], reverse=True)

    for i, (player, score) in enumerate(leaderboard, start=1):
        st.write(f"**#{i}** - {player}: {score} points")
