# api/main.py

from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv # <-- New addition

# Ensure your PYTHONPATH is set correctly in Codespaces for this import to work.
# Often, adding 'export PYTHONPATH=$PYTHONPATH:.' to your .bashrc or .zshrc in Codespaces helps.
from src.core_logic import process_user_query_with_guardrails

load_dotenv() # <-- Load environment variables from .env

class QueryRequest(BaseModel):
    query: str

app = FastAPI()

@app.post("/query")
async def process_query(request: QueryRequest):
    user_query = request.query
    response = process_user_query_with_guardrails(user_query) # Use the imported function
    return {"response": response}

@app.get("/")
async def read_root():
    return {"message": "Airline Customer Support API is running!"}