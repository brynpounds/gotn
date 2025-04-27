import sys, os
sys.path.append(os.path.dirname(__file__))

import streamlit as st
from core.loader import load_game_data
from core.database import setup_database, get_all_tickets
from ui import structured_mode, unstructured_mode, extras, scores, leaderboard
from utils.session import init_session, register_or_validate_user
from core.scores import get_scores
from config.settings import REDIS_HOST, REDIS_PORT

import redis

import logging

# Configure logging
LOG_FILE_PATH = '/var/log/gotn.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()  # also prints to console for now
    ]
)

# Optional: import threshold to display in sidebar
from core.grader import SIMILARITY_THRESHOLD

# 👉 Set structured/unstructured mode globally for the API
USE_STRUCTURED_MODE = True

# 👉 Temporary root cause for scoring (later make dynamic per user)
EXPECTED_ROOT_CAUSE = "Incorrect PSK configured"

# 👉 Bring in scoring + prefilter functions
from core.grader import get_structured_score, get_unstructured_score

# ---- Your Original Streamlit App Flow (unchanged below this line) ----

init_session()
register_or_validate_user()

if not st.session_state.get("auth_passed"):
    st.stop()

def get_total_score(email):
    structured = get_scores(email, "structured").values()
    unstructured = get_scores(email, "unstructured").values()
    return sum(map(int, structured)) + sum(map(int, unstructured))

def get_leaderboard_position(email):
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    keys = r.keys("player:*:structured")
    players = list({key.split(":")[1] for key in keys})

    leaderboard = []
    for player in players:
        total = get_total_score(player)
        leaderboard.append((player, total))

    leaderboard.sort(key=lambda x: x[1], reverse=True)

    for rank, (player_email, _) in enumerate(leaderboard, start=1):
        if player_email == email:
            return rank, len(leaderboard)

    return None, len(leaderboard)

if st.session_state.get("auth_passed"):
    email = st.session_state["player_email"]
    total_score = get_total_score(email)
    rank, total_players = get_leaderboard_position(email)
    st.sidebar.markdown(f"### 🧠 Your Score: **{total_score}** points")
    st.sidebar.markdown(f"### 🏆 Rank: **#{rank}** of {total_players} players")

game_data = load_game_data()
setup_database(game_data["trouble_tickets"])
trouble_tickets = get_all_tickets()
network_issues = game_data["network_issues"]
jokes = game_data["jokes"]
trivia = game_data["trivia"]
snarky_comments = game_data["snarky_comments"]

st.sidebar.header("Settings")
snarky_mode_toggle = st.sidebar.checkbox("Enable Snarky Mode", value=st.session_state["snarky_mode"])

# Check if the user changed snarky mode
previous_snarky = st.session_state.get("previous_snarky_mode", None)

st.session_state["snarky_mode"] = snarky_mode_toggle
st.session_state["previous_snarky_mode"] = snarky_mode_toggle

email = st.session_state.get("player_email", "")

if previous_snarky is not None and previous_snarky != snarky_mode_toggle:
    status = "ENABLED" if snarky_mode_toggle else "DISABLED"
    logging.info(f"Player {email} {status} Snarky Mode.")

# Optional: Show threshold (for debug/tuning visibility)
st.sidebar.markdown(f"### Filter Threshold: `{SIMILARITY_THRESHOLD}`")

st.title("🛡️ Guardians of the Network - Bryn version for scale testing.  Not TechM Version")
menu_choice = st.radio("Select an option:", [
    "Structured Trouble Ticket Mode",
    "Unstructured Troubleshooting",
    "List All Trouble Tickets",
    "Random Joke",
    "Random Networking Trivia",
    "Your Scores",
    "Leaderboard"
])

if menu_choice == "Structured Trouble Ticket Mode":
    structured_mode.run(trouble_tickets, snarky_comments)
elif menu_choice == "Unstructured Troubleshooting":
    unstructured_mode.run(network_issues, snarky_comments)
elif menu_choice == "List All Trouble Tickets":
    extras.list_tickets(trouble_tickets)
elif menu_choice == "Random Joke":
    extras.random_joke(jokes, snarky_comments)
elif menu_choice == "Random Networking Trivia":
    extras.random_trivia(trivia, snarky_comments)
elif menu_choice == "Your Scores":
    scores.run()
elif menu_choice == "Leaderboard":
    leaderboard.run()

