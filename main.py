from typing import Union

from fastapi import FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from document_extraction.extraction import Extraction  # Adjusted import
from fastapi.responses import StreamingResponse


app = FastAPI()

@app.exception_handler(503)
async def service_unavailable_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=503,
        content={"message": "Service temporarily unavailable, please try again later"},
    )

@app.post("/analyze-file")
def data_extract():
    try:
        result = Extraction("docx", "1.pdf").doExtract()
        return result
    except Exception as e:
        return {"message": f"error: {e}"}

@app.get("/test")
async def test():
    import time
    time.sleep(300)
    return {"item_id": 'hello long rong'}