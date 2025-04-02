from typing import Union
from fastapi.params import Form
from typing_extensions import Annotated

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from document_extraction.extraction import Extraction  # Adjusted import


app = FastAPI()

@app.exception_handler(503)
async def service_unavailable_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=503,
        content={"message": "Service temporarily unavailable, please try again later"},
    )

@app.post("/analyze-file")
def data_extract(file_name: Annotated[str, Form()], file_type: Annotated[str, Form()]):
    try:
        file_name = "1.jpg"
        file_type = "image"
        result = Extraction(file_type, file_name).doExtract()
        print(result)
        all_line_items = []
        if file_type == "image":
            result = Extraction(file_type, file_name).doExtract()
        else:
            result = Extraction(file_type, file_name).doExtract()
            for entry in result:
                line_items = entry["raw"].get("line_items", [])
                if line_items:
                    all_line_items.extend(line_items)
        return all_line_items
    except Exception as e:
        return {"message": f"error: {e}"}

@app.get("/test")
async def test():
    import time
    time.sleep(300)
    return {"item_id": 'hello long rong'}