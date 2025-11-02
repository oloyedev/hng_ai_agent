from fastapi import FastAPI, Request
from .telex import handle_telex_message

app = FastAPI(title="InboxCompanion AI")

@app.get("/")
async def root():
    return {"message": "Welcome to InboxCompanion AI 👋"}

@app.post("/telex")
async def telex_endpoint(request: Request):
    return await handle_telex_message(request)
