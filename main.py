from typing import Union

from fastapi import FastAPI
from document_extraction.extraction import Extraction  # Adjusted import
app = FastAPI()


@app.post("/analyze-file")
async def data_extract():
    result = await Extraction("pdf", "test.pdf").extract()
    print(result)
    return result

@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}