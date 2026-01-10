#!/bin/bash
# Run the FastAPI server for Research Inbox Orchestrator

cd "$(dirname "$0")"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
