from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from .a2a import JSONRPCRequest, JSONRPCResponse
from .clarity import process_contract_messages

load_dotenv()

app = FastAPI(
    title="Contract Clarity Agent",
    description="Analyzes legal contracts using Groq and returns plain-language insights",
    version="1.0.0",
)


@app.post("/a2a")
async def clarity_a2a(request: Request):
    try:
        body = await request.json()

        if body.get("jsonrpc") != "2.0" or "id" not in body:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request: jsonrpc must be '2.0' and id is required"
                    }
                }
            )

        rpc_request = JSONRPCRequest(**body)

        if rpc_request.method == "message/send":
            messages = [rpc_request.params.message]
            config = rpc_request.params.configuration
            context_id, task_id = None, None
        else:
            messages = rpc_request.params.messages
            context_id = rpc_request.params.contextId
            task_id = rpc_request.params.taskId
            config = None

        result = await process_contract_messages(messages, context_id, task_id, config)

        response = JSONRPCResponse(
            id=rpc_request.id,
            result=result
        )

        return response.model_dump()

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
             "jsonrpc": "2.0",
             "id": body.get("id") if "body" in locals() else None,
            "error": {
            "code": -32603,
            "message": "Internal error",
            "data": {"details": str(e)}
        }
    }
)


@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "contract-clarity"}
