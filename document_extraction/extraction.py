import asyncio
import pprint
import time
import json
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.extractors import PydanticProgramExtractor

from pathlib import Path
from llama_index.core.node_parser import SentenceSplitter
from document_extraction.models.product import Product


class Extraction:
    def __init__(self, document_type, document_name):
        self.document_type = document_type
        self.document_name = document_name
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

    def node_parse(self, documents):
        splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=0)
        nodes = splitter.get_nodes_from_documents(documents)
        semaphore = asyncio.Semaphore(10)

        async def extract_product(semaphore, node):
            async with semaphore:
                start_time = time.time()
                result = await self.s_llm.acomplete(f"""
                                                    * analyze data you are given and extract the product sku, description, and quantity.
                                                    * Carefully find and double-check the values of these elements.
                                                    * Extract all raw data of product sku, description and quantity.
                                                    * If there have multiple rows of same sku, please return all of them and do not combine them.
                                                    * Additionally, be aware that "qty" may be used as a synonym for quantity.
                                                    * Please only provide accurate and verified information. Avoid generating any data or content that may be fabricated, unverified, or hypothetical.
                                                    {node.text}""")
                end_time = time.time()
                print(f"Task duration: {end_time - start_time:.2f} seconds")
                return result

        async def process_nodes():
            tasks = [extract_product(semaphore, node) for node in nodes if len(node.text.strip()) > 0]
            return await asyncio.gather(*tasks)

        products = asyncio.run(process_nodes())
        return [product.model_dump() for product in products]

    def load_from_pdf(self):

        try:
            pdf_reader = SimpleDirectoryReader(
                input_files=[Path(f"./media_files/{self.document_name}")])
            return self.node_parse(pdf_reader.load_data())
        except Exception as e:
            raise Exception(f"Error loading PDF: {e}")

    def load_from_docx(self):
        try:
            docx_reader = SimpleDirectoryReader(
                input_files=[Path(f"./media_files/{self.document_name}")])
            documents = docx_reader.load_data()
            return self.node_parse(documents)
        except Exception as e:
            raise Exception(f"Error loading DOCX: {e}")

    def load_from_excel(self):
        try:
            excel_reader = SimpleDirectoryReader(
                input_files=[Path(f"./media_files/{self.document_name}")])
            documents = excel_reader.load_data()
            return self.node_parse(documents)
        except Exception as e:
            raise Exception(f"Error loading Excel: {e}")

    def load_from_image(self):
        try:
            image_reader = SimpleDirectoryReader(
                input_files=[Path(f"./media_files/{self.document_name}")])
            documents = image_reader.load_data()
            return self.s_llm.complete(f"""
                                * analyze data you are given and extract the product sku, description, and quantity.
                                * Carefully find and double-check the values of these elements.
                                * Extract all raw data of product sku, description and quantity.
                                * If there have multiple rows of same sku, please return all of them and do not combine them.
                                * Additionally, be aware that "qty" may be used as a synonym for quantity.
                                {documents[0].text}""")
        except Exception as e:
            raise Exception(f"Error loading Image: {e}")


if __name__ == "__main__":
    # Example usage
    extractor = Extraction("docx", "1.docx")
    result = extractor.doExtract()
    print(result)
