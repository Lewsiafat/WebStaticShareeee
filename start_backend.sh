#!/bin/bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
echo "FastAPI backend started in background on port 8000."
echo "PID: $!"
