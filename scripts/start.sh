#!/bin/sh

echo "Starting the application..."

uvicorn api.main:app --host 0.0.0.0 --port 8000 &
exec streamlit run ui/streamlit_app.py \
    --server.address 0.0.0.0 \
    --server.port 8501
