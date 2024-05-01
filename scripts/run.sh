#!/bin/bash
cd /workspace/app && uvicorn app:app --reload --port=8000 --host=0.0.0.0
