from typing import Union

from fastapi import FastAPI
from document_extraction import Extraction
app = FastAPI()


@app.post("/analyze-file")
def data_extract():
    result = Extraction("pdf", "test.pdf").extract()
    return {"result": result}

@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}