from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.document_handler import extract_text, split_text
from app.vector_store import add_to_index, get_similar_chunks
from app.llm_gemini import ask_gemini
from pydantic import BaseModel
from typing import List
import tempfile
import os

router = APIRouter()

class SubmissionRequest(BaseModel):
    documents: str
    questions: List[str]

@router.post("/upload")
async def upload_doc(file: UploadFile = File(...)):
    try:
        text = extract_text(file)
        chunks = split_text(text)
        for chunk in chunks:
            add_to_index(chunk)
        return {"message": f"{file.filename} uploaded and indexed", "chunks": len(chunks)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/query")
async def query_doc(query: str = Form(...)):
    try:
        top_chunks = get_similar_chunks(query, k=3)
        answer = ask_gemini(top_chunks, query)
        return {"query": query, "matched_chunks": top_chunks, "response": answer}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/hackrx/run")
async def run_submission(payload: SubmissionRequest):
    try:
        doc_url = payload.documents
        questions = payload.questions

        # 1. Download the document
        import requests
        resp = requests.get(doc_url, timeout=30)
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download document")

        # 2. Save to a temporary file and create a file-like object
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(resp.content)
            tmp.flush()
            tmp_path = tmp.name

        class DummyFile:
            def __init__(self, path, filename):
                self.file = open(path, "rb")
                self.filename = filename

        dummy = DummyFile(tmp_path, os.path.basename(doc_url.split("?")[0]))
        try:
            text = extract_text(dummy)
            chunks = split_text(text)
            for chunk in chunks:
                add_to_index(chunk)
        finally:
            try:
                dummy.file.close()
            except:
                pass
            try:
                os.remove(tmp_path)
            except:
                pass

        answers = []
        for q in questions:
            context = get_similar_chunks(q, k=3)
            ans = ask_gemini(context, q)
            answers.append(ans.strip())
        return {"answers": answers}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
