# fastapi_server.py

from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import uvicorn
import os

# Force Ollama to localhost
os.environ["OLLAMA_HOST"] = "http://localhost:11434"

# Import your existing grading functions
from core.grader import get_structured_score, get_unstructured_score
# No need for prefilter (we already decided)

# Config settings
USE_STRUCTURED_MODE = True  # Set to False if you want unstructured
EXPECTED_ROOT_CAUSE = "Incorrect PSK configured"  # Hardcoded for now
UNSTRUCTURED_ROOT_CAUSE = "TALOS is not configured at Site10"  # Unstructured mode root cause

app = FastAPI()

@app.post("/api/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == "player" and password == "letmein":
        return JSONResponse(content={"status": "success"})
    else:
        return JSONResponse(content={"status": "fail"}, status_code=401)

@app.post("/api/submit_diagnosis")
async def submit_diagnosis(diagnosis: str = Form(...)):
    if USE_STRUCTURED_MODE:
        score_result = get_structured_score(diagnosis, EXPECTED_ROOT_CAUSE, max_points=150)
    else:
        score_result = get_unstructured_score(diagnosis, EXPECTED_ROOT_CAUSE, max_points=150)

    return JSONResponse(content={
        "score": score_result.get("awarded_points"),
        "rejection_reason": score_result.get("rejection_reason"),
        "similarity_score": score_result.get("similarity_score"),
    })

@app.post("/api/submit_unstructured_diagnosis")
async def submit_unstructured_diagnosis(diagnosis: str = Form(...)):
    score_result = get_unstructured_score(diagnosis, UNSTRUCTURED_ROOT_CAUSE, max_points=150)

    return JSONResponse(content={
        "score": score_result.get("awarded_points"),
        "rejection_reason": score_result.get("rejection_reason"),
        "similarity_score": score_result.get("similarity_score"),
    })

if __name__ == "__main__":
    uvicorn.run("fastapi_server:app", host="0.0.0.0", port=8502, reload=True)

