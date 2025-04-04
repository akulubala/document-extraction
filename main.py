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
        all_line_items = []
        if file_type == "image":
            images =  file_name.split(",")
            print(f"images: {images}")
            all_line_items = Extraction(images=images, document_type=file_type).doExtract()
        elif file_type == "xlsx":
            all_line_items = Extraction(document_name=file_name, document_type=file_type).doExtract()
        else:
            result = Extraction(document_name=file_name, document_type=file_type).doExtract()
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