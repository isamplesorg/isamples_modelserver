#!/bin/bash
export PYTHONPATH=/app
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4