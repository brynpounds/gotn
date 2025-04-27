# grader.py

import ollama
import json
import time
from sentence_transformers import SentenceTransformer, util
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config.settings import OLLAMA_URL, INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET
from config.settings import SIMILARITY_THRESHOLD, UNSTRUCTURED_SIMILARITY_THRESHOLD
import os
from core.telemetry_buffer import log_duration
from config.settings import OLLAMA_MODEL

os.environ["OLLAMA_HOST"] = OLLAMA_URL

# Load embedding model once
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# InfluxDB setup
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

#def log_duration(metric_name, duration, tags=None):
#    try:
#        point = Point(metric_name).field("duration", duration)
#        if tags:
#            for key, value in tags.items():
#                point = point.tag(key, value)
#        write_api.write(bucket=INFLUX_BUCKET, record=point)
#    except Exception as e:
#        print(f"⚠️ ERROR writing to InfluxDB for metric {metric_name}: {e}")

def is_semantically_relevant(user_input, expected_root_cause):
    start = time.time()

    user_embedding = embedding_model.encode(user_input, convert_to_tensor=True)
    root_embedding = embedding_model.encode(expected_root_cause, convert_to_tensor=True)
    similarity = util.cos_sim(user_embedding, root_embedding).item()

    duration = round(time.time() - start, 3)
    log_duration("embedding_similarity_check", duration)

    return similarity >= SIMILARITY_THRESHOLD, round(similarity, 3)

# ------------------------------
# Structured Prompt Builder
# ------------------------------
def build_structured_llm_prompt(expected_root_cause, user_input, max_points):
    return f'''
You are a network troubleshooting expert and game evaluator.

Compare the following player response against the expected root cause.
Assign a score between 0 and {max_points}.

Root Cause: {expected_root_cause}
Player Response: {user_input}

Instructions:
- Full points if the player identifies the key concepts in the root cause.
- Partial points if they get part of the answer right.
- Zero if the response is irrelevant, vague, or not a technical diagnosis.
- Accept reworded answers or synonyms (e.g., "10 meg" = "10 Mbps").
- Do not reward effort-based or emotional responses.

Now return only a numeric score between 0 and {max_points}.
'''

# ------------------------------
# Unstructured Prompt Builder
# ------------------------------
def build_unstructured_llm_prompt(expected_root_cause, user_input, max_points):
    return f'''
You are a network troubleshooting expert and game evaluator.

A player has submitted a diagnosis for a network issue.
Evaluate how well the player's diagnosis matches the known root cause.

Scoring Instructions:
- Award {max_points} points only if the player's response clearly identifies:
    1. The correct technology, service, or feature involved (e.g., Talos, DHCP, WAN, VLAN 20).
    2. The correct site or location if one is mentioned in the known root cause (e.g., Site9, Building A).
    3. The nature of the problem (e.g., disabled, missing, not configured, down, broken).
- All three elements must be clearly present for full points.
- If the technology or site is missing, or if the player fails to describe what is wrong (the nature of the problem), award zero points.
- Accept minor variations in wording for the problem type (e.g., "Talos not working" = "Talos disabled") but the problem must still be clearly described.
- Simply stating the site and technology isn't enough.  (e.g., "Site10 Talos" should not receive credit.  "Site10 undofigured TALOS" would receive full credit.  "talos is unconfigured at site10" would receive full credit.
- Do not award partial points. It is either full points if all requirements are met, or zero points if any requirement is missing.

Known Root Cause: {expected_root_cause}
Player Response: {user_input}

Return only a numeric score: either {max_points} or 0. Do not return anything else.
'''

# ------------------------------
# Structured Grading
# ------------------------------
def grade_with_llm(prompt):
    start = time.time()
    try:
        print("DEBUG - OLLAMA_URL is:", os.getenv("OLLAMA_HOST"))
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.2}
        )
        print("DEBUG - Raw LLM response:", response)  # Only print if success
    except Exception as e:
        print(f"ERROR - Failed to get LLM response: {e}")
        return 0  # Fail safe: give zero points if LLM call fails

    duration = round(time.time() - start, 3)
    log_duration("llm_structured_response", duration)

    try:
        return int(response["message"]["content"].strip())
    except (ValueError, KeyError, TypeError) as e:
        print(f"ERROR - Failed to parse LLM grading response: {e}")
        return 0  # Fail safe: if parsing fails, score = 0

def get_structured_score(user_input, expected_root_cause, max_points):
    relevant, similarity_score = is_semantically_relevant(user_input, expected_root_cause)
    if not relevant:
        return {
            "awarded_points": 0,
            "rejection_reason": "Hmm… your diagnosis didn’t match the problem well enough to evaluate. Give it another shot!",
            "similarity_score": similarity_score
        }

    prompt = build_structured_llm_prompt(expected_root_cause, user_input, max_points)
    points = grade_with_llm(prompt)

    return {
        "awarded_points": min(points, max_points),
        "rejection_reason": None,
        "similarity_score": similarity_score
    }

# ------------------------------
# Unstructured Grading
# ------------------------------
def get_unstructured_score(user_input, expected_issue, max_points):
    start = time.time()
    user_embedding = embedding_model.encode(user_input, convert_to_tensor=True)
    issue_embedding = embedding_model.encode(expected_issue, convert_to_tensor=True)
    similarity = util.cos_sim(user_embedding, issue_embedding).item()
    duration = round(time.time() - start, 3)
    log_duration("embedding_similarity_check", duration)

    if similarity < UNSTRUCTURED_SIMILARITY_THRESHOLD:
        return {
            "awarded_points": 0,
            "rejection_reason": "Hmm… your diagnosis didn’t match the problem well enough to evaluate. Give it another shot!",
            "similarity_score": round(similarity, 3)
        }

    prompt = build_unstructured_llm_prompt(expected_issue, user_input, max_points)
    start = time.time()
    response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}], options={"temperature": 0.2})
    duration = round(time.time() - start, 3)
    log_duration("llm_unstructured_response", duration)

    try:
        return {
            "awarded_points": min(int(response["message"]["content"].strip()), max_points),
            "rejection_reason": None,
            "similarity_score": round(similarity, 3)
        }
    except ValueError:
        return {
            "awarded_points": 0,
            "rejection_reason": "There was an error evaluating your response. Please try again.",
            "similarity_score": round(similarity, 3)
        }

