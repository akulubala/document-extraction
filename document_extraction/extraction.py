import asyncio
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.extractors import PydanticProgramExtractor

from pathlib import Path
from llama_index.core.node_parser import SentenceSplitter
import pprint
import json

from document_extraction.models.product import Product


class Extraction:
    def __init__(self, document_type, document_path):
        self.document_path = document_path
        self.document_type = document_type
        self.llm = OpenAI(model="gpt-4o-mini")
        self.s_llm = self.llm.as_structured_llm(Product)

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
             # Process each chunk if the data is a list
            return loaded_data
        except Exception as e:
            return {"message": f"error: {e}"}

    def load_from_pdf(self):

        try:
            pdf_reader = SimpleDirectoryReader(
                input_files=[Path("./media_files/1.pdf")])
            documents = pdf_reader.load_data()
            return documents[0].text
        except Exception as e:
            raise Exception(f"Error loading PDF: {e}")

    def load_from_docx(self):
        try:
            docx_reader = SimpleDirectoryReader(
                input_files=[Path("../media_files/1.docx")])
            documents = docx_reader.load_data()
            splitter = SentenceSplitter(chunk_size=1024)
            nodes = splitter.get_nodes_from_documents(documents)

            async def extract_product(node):
                # Removed 'await' since 'self.s_llm.complete' is not awaitable
                return self.s_llm.complete(f"{node.text}")

            async def process_nodes():
                tasks = [extract_product(node) for node in nodes]
                return await asyncio.gather(*tasks)

            products = asyncio.run(process_nodes())
            return [product.model_dump() for product in products]
        except Exception as e:
            raise Exception(f"Error loading DOCX: {e}")

    def load_from_excel(self):
        try:
            excel_reader = SimpleDirectoryReader(
                input_files=[Path("./media_files/1.xlsx")])
            documents = excel_reader.load_data()
            return documents[0].text
        except Exception as e:
            raise Exception(f"Error loading Excel: {e}")

    def load_from_image(self):
        try:
            image_reader = SimpleDirectoryReader(
                input_files=[Path("./media_files/1.png")])
            documents = image_reader.load_data()
            return documents[0].text
        except Exception as e:
            raise Exception(f"Error loading Image: {e}")


if __name__ == "__main__":
    # Example usage
    extractor = Extraction("docx", "1.docx")
    result = extractor.doExtract()
    print(result)
