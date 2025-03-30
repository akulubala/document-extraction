import asyncio
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI
from llama_index.core import SimpleDirectoryReader
from pathlib import Path
import json

from document_extraction.models.product import Product

class Extraction:
    def __init__(self, document_type, document_path):
        self.document_path = document_path
        self.document_type = document_type
    
    def doExtract(self):
        try:
            if self.document_type == "pdf":
                loaded_data = self.load_from_pdf()
            if self.document_type == "docx":
                loaded_data = self.load_from_docx()
            if self.document_type == "xlsx":
                loaded_data = self.load_from_excel()
            if self.document_type == "image":
                loaded_data = self.load_from_image()

            return self.execute_with_llm(loaded_data)
            
        except Exception as e:
            return {"message": f"error: {e}"}

    def execute_with_llm(self, loaded_data):
        try:
            llm = OpenAI(model="gpt-4o-mini")
            s_llm = llm.as_structured_llm(Product)
            return s_llm.complete(loaded_data)
        except Exception as e:
            raise Exception(f"Error executing with llm: {e}")
        

    def load_from_pdf(self):

        try:
            pdf_reader = SimpleDirectoryReader(input_files=[Path("./media_files/1.pdf")])
            documents = pdf_reader.load_data()
            return documents[0].text
        except Exception as e:
            raise Exception(f"Error loading PDF: {e}")

    def load_from_docx(self):
        try:
            docx_reader = SimpleDirectoryReader(input_files=[Path("./media_files/1.docx")])
            documents = docx_reader.load_data()
            return documents[0].text
        except Exception as e:
            raise Exception(f"Error loading DOCX: {e}")

    def load_from_excel(self):
        try:
            excel_reader = SimpleDirectoryReader(input_files=[Path("./media_files/1.xlsx")])
            documents = excel_reader.load_data()
            return documents[0].text
        except Exception as e:
            raise Exception(f"Error loading Excel: {e}")
    
    def load_from_image(self):
        try:
            image_reader = SimpleDirectoryReader(input_files=[Path("./media_files/1.png")])
            documents = image_reader.load_data()
            return documents[0].text
        except Exception as e:
            raise Exception(f"Error loading Image: {e}")