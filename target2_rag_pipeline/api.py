from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from .rag import EnterpriseRAG
import os

app = FastAPI(title="Target 2: Enterprise RAG API", description="API for testing Prompt Injection, Data Leakage (OWASP Top 10)")

# Ensure data dir exists
os.makedirs("target2_rag_pipeline/data", exist_ok=True)
rag_pipeline = EnterpriseRAG(data_dir="target2_rag_pipeline/data", persist_dir="target2_rag_pipeline/chroma_db")

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    context: List[str]

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest) -> QueryResponse:
    result = rag_pipeline.query(request.question)
    return QueryResponse(
        answer=result["answer"],
        context=result["context"]
    )
