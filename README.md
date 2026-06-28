# AirlineSupportSystem


# Run fast API
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Streamlit frontend
streamlit run ui/streamlit_app.py --server.port 8501 --server.enableCORS false


# If port in use for uvicorn
ps -ef | grep uvicorn
kill -9 <pid>

# If port in use for streamlit
ps -ef | grep streamlit
kill -9 <pid>


# Connect to DB
Connect to Database  https://supabase.com
Select the Connect button showing above your database table.
Tab: Connection String
Type: PSQL
Source: Primary Database
Method: Session Pooler

# Connect to Vector DB with API 
https://app.pinecone.io/
Pinecone Starter (free)
Pinecone Starter does not automatically generate embeddings for your documents. It stores vectors and performs similarity search, but you still need an embedding model to convert text into vectors before uploading them.

# Docker
docker build -t airline-supportsystem .
docker images
docker run \
  --env-file .env \
  -p 8000:8000 \
  -p 8501:8501 \
  airline-supportsystem
docker ps

# Docker registry
docker login -u dileepdominic
docker tag airline-supportsystem:latest dileepdominic/airline-supportsystem:latest
docker push dileepdominic/airline-supportsystem:latest

# Space Cleanup
pip cache purge
docker system prune -a -f
docker builder prune -a -f

# Important notes
In .env file then should not be any double quotes to value

# Hugging face
https://huggingface.co/spaces/dileepdominic/airlinesupportsystem