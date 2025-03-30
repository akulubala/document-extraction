from typing import Union

from fastapi import FastAPI
from document_extraction.extraction import Extraction  # Adjusted import
app = FastAPI()


@app.post("/analyze-file")
def data_extract():
    result = Extraction("pdf", "1.pdf").doExtract()
    print(result)
    return result

@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}