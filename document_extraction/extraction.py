import asyncio, base64, time, json

from pathlib import Path
from document_extraction.models.product import Product
import base64

from document_extraction.excel_extraction import process_excel
from document_extraction.image_extraction import process_images
from document_extraction.textable_extraction import process_docx, process_pdf


class Extraction:
    def __init__(self, **kwargs):
        self.document_type = kwargs.get("document_type")
        self.document_name = kwargs.get("document_name", None)
        self.images = kwargs.get('images', [])

    async def doExtract(self):
        try:
            if self.document_type == "pdf":
                loaded_data = process_pdf(self.document_name)
            if self.document_type == "docx":
                loaded_data = process_docx(self.document_name)
            if self.document_type == "image":
                loaded_data = process_images(self.images)
            if self.document_type == 'xlsx':
                loaded_data = await process_excel(self.document_name)
            return loaded_data
        except Exception as e:
            return {"message": f"error: {e}"}
