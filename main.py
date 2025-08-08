from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import google.generativeai as genai
from app import routes

# Load .env for local dev; in production (Render) environment variables are set in dashboard.
load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY environment variable is missing. Set it in Render env or .env for local dev.")

genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="LLM Query Retrieval")

app.include_router(routes.router)

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def health_check():
    return {"message": "LLM Query System is running!"}

@app.post("/webhook")
def webhook(data: QueryRequest):
    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        result = model.generate_content(data.query)
        return {"status": "success", "query": data.query, "response": result.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
