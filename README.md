# llm-query-retrieval (Updated)

This is an updated version of your project configured to store text chunks and embeddings in Supabase.
- Uses Google Generative AI for embeddings & responses.
- Stores chunks + embeddings in Supabase.
- Computes similarity locally (fetches embeddings and ranks by cosine similarity).
- Designed to work on Render (set env vars in Render dashboard).

## Env vars (set in Render / .env for local)
- GOOGLE_API_KEY
- SUPABASE_URL
- SUPABASE_KEY

## Run locally
1. pip install -r requirements.txt
2. copy `.env.example` to `.env` and fill keys
3. uvicorn main:app --reload

