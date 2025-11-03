# README.md — Contract Clarity Agent (Tolu the Lawyer)

**Contract Clarity Agent — “Tolu the Lawyer”**  
_A FastAPI A2A agent that classifies contracts (NDA, Service Agreement, etc.), detects ambiguous or risky clauses, and returns plain-English summaries and recommendations. Powered by Groq (Llama 3.3) and integrated with Telex.im via the A2A JSON-RPC protocol._

---

## Table of contents
- [Project overview](#project-overview)  
- [Features](#features)  
- [Tech stack](#tech-stack)  
- [Repository structure](#repository-structure)  
- [Requirements & env vars](#requirements--env-vars)  
- [Quick start — run locally](#quick-start---run-locally)  
- [A2A endpoint: request & response examples (Postman)](#a2a-endpoint-request--response-examples-postman)  
- [Testing with Telex.im](#testing-with-telexim)  
- [Deployment notes](#deployment-notes)  
- [Security & secrets handling](#security--secrets-handling)  
- [License](#license)

---

## Project overview
Tolu the Lawyer is an AI assistant that helps non-lawyers understand contracts. The agent accepts contract text (via Telex or direct JSON-RPC requests), uses Groq’s LLaMA model to analyze and produce structured JSON, and replies back in a human-friendly format. Designed for small businesses, freelancers, and procurement teams.

---

## Features
- Contract type classification (NDA, Service Agreement, Employment Contract, Lease, etc.)  
- Ambiguous-term detection (e.g., undefined phrases)  
- Risk clause identification (one-sided, high-liability items)  
- Simplified plain-English summary of key points  
- Practical recommendations to improve clarity or balance  
- A2A JSON-RPC interface to integrate with Telex.im

---

## Tech stack
- **FastAPI** — async backend API  
- **Groq API** — LLaMA 3.3 model for structured analysis (`llama-3.3-70b-versatile`)  
- **httpx** — async HTTP client  
- **Pydantic** — typed data models (JSON-RPC validation)  
- **Leapcell** (or any hosting) — example deployment used in demo  
- **Telex.im** — A2A conversational integration

---

## Repository structure
```
contract-clarity-agent/
├─ app/
│ ├─ init.py
│ ├─ main.py # FastAPI app with /a2a and /health
│ ├─ a2a.py # Pydantic A2A / JSON-RPC models
│ ├─ groq.py # Groq API client
│ └─ clarity.py # Functional contract-processing logic
├─ .env.example
├─ pyproject.toml
├─ requirements.txt
└─ workflow.json # Telex workflow JSON ready for import
```

---

## Requirements & env vars

### Python
- Python 3.11+ recommended

### Dependencies
Install via pip:
```bash
pip install -r requirements.txt
# or using pyproject.toml: pip install -e .
```

## Environment variables

Create a ```.env file ```(do not commit this file). See .env.example.

``` # .env
GROQ_API_KEY=sk-...          # your Groq API key
GROQ_MODEL=llama-3.3-70b-versatile
PORT=8000
TELEX_AUTH_TOKEN=optional   # if you want to validate incoming Telex requests
```


## Quick start — run locally

Create & activate a virtual environment:

``` bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

```
2. Install dependencies:

```bash
pip install -r requirements.txt
```
3.Create .env from .env.example and add your GROQ_API_KEY.

4. Start the server:

```bash
uvicorn app.main:app --reload --port 8000
```
5. Health check:

```bash
curl http://127.0.0.1:8000/health
# Response: {"status":"healthy","agent":"contract-clarity"}
```

## A2A endpoint — request & response examples (Postman)

This project exposes a single A2A JSON-RPC endpoint at /a2a. Telex sends JSON-RPC 2.0 requests; your endpoint validates and processes them.

Correct JSON-RPC message/send body (Postman → Body: raw JSON)
```json
{
  "jsonrpc": "2.0",
  "id": "test-001",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [
        {
          "kind": "text",
          "text": "This Non-Disclosure Agreement (NDA) is made between AlphaTech and BetaWorks..."
        }
      ]
    },
    "configuration": {}
  }
}
```

Typical successful JSON-RPC response
```json
{
  "jsonrpc": "2.0",
  "id": "test-001",
  "result": {
    "id": "task-uuid",
    "contextId": "context-uuid",
    "status": {
      "state": "completed",
      "message": {
        "role": "agent",
        "parts": [
          {
            "kind": "text",
            "text": "**Contract Type:** NDA\n\n**Simplified Summary:** ...\n\n**Ambiguous Terms:** ...\n\n**Recommendations:** ..."
          }
        ]
      }
    },
    "artifacts": [
      {
        "artifactId": "artifact-uuid",
        "name": "classification",
        "parts": [
          {"kind":"text","text":"NDA"}
        ]
      },
      {
        "artifactId": "artifact-uuid-2",
        "name": "analysis",
        "parts": [
          {"kind":"text","text":"{ \"contract_type\": \"NDA\", ... }"}
        ]
      }
    ],
    "history": [...]
  }
}
```
### Testing with Telex.im
1. Add the workflow (see workflow.json) in Telex’s workflow builder or import it.
2. Create a new AI colleague (e.g., Tolu the Lawyer) and attach the workflow URL:

```bash
https://<your-deployment-domain>/a2a
```
3. In Telex chat, paste a contract and ask Tolu to analyze it.

4. Verify logs: open agent logs:

```bash
https://api.telex.im/agent-logs/{channel-id}.txt
(the channel-id is the first UUID in the Telex address bar for your chat)
```

## Security & secrets handling

1. Never commit credentials. If you accidentally push a secret, revoke/regenerate it immediately (Groq API key in this case).
2. Add ```.env``` to .gitignore.
3. Optionally validate incoming Telex requests with ```TELEX_AUTH_TOKEN or HMAC``` if Telex provides signing info.
4. Sanitize any user-provided files before sending to third-party APIs.

## License

MIT License — feel free to reuse and adapt. Please don’t include secrets in commits.
