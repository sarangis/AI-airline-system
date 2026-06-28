# ui/streamlit_app.py

import streamlit as st
import requests
import os

# Assuming your FastAPI is running on http://localhost:8000 in the same Codespace
# If running externally or on a different port, adjust this URL.
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000/query")

st.set_page_config(page_title="Airline Customer Support AI", layout="centered")
st.title("✈️ AI-Powered Airline Customer Support")
st.markdown("Ask me anything about flights, policies, or general airline information!")

# User input
user_query = st.text_input("Your Query:", "What is the status of flight 6E477?")

if st.button("Get Response"):
    if user_query:
        try:
            with st.spinner("Fetching response..."):
                response = requests.post(FASTAPI_URL, json={"query": user_query})
                response.raise_for_status() # Raise an exception for HTTP errors
                api_response = response.json()
                st.subheader("AI Response:")
                st.info(api_response.get("response", "No response from API."))
        except requests.exceptions.ConnectionError:
            st.error(f"Could not connect to the FastAPI backend at {FASTAPI_URL}. Is it running?")
            st.info("Please ensure your FastAPI application (`api/main.py`) is running in a separate terminal.")
            st.info("You can run it with: `uvicorn api/main:app --host 0.0.0.0 --port 8000`")
        except requests.exceptions.HTTPError as e:
            st.error(f"HTTP error occurred: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
    else:
        st.warning("Please enter a query.")

st.markdown("--- Say Hi to your AI Assistant! ---")