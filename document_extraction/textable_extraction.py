import asyncio
from pathlib import Path
import time
from document_extraction.models.product import Product
from document_extraction.utils import BASE_DOCUMENT_PATH
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI as LLMOpenAI

def process_docx(document_name: str) -> list:
        try:
            docx_reader = SimpleDirectoryReader(
                input_files=[Path(f"{BASE_DOCUMENT_PATH}{document_name}")])
            documents = docx_reader.load_data()
            return node_parse(documents)
        except Exception as e:
            raise Exception(f"Error loading DOCX: {e}")
        
def process_pdf(document_name: str) -> list:

        try:
            pdf_reader = SimpleDirectoryReader(
                input_files=[Path(f"{BASE_DOCUMENT_PATH}{document_name}")])
            return node_parse(pdf_reader.load_data())
        except Exception as e:
            raise Exception(f"Error loading PDF: {e}")
        

def node_parse(documents):
        splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=0)
        nodes = splitter.get_nodes_from_documents(documents)
        semaphore = asyncio.Semaphore(10)
        llm = LLMOpenAI(model="gpt-4o-mini")
        s_llm = llm.as_structured_llm(Product)
        async def extract_product(semaphore, node):
            async with semaphore:
                start_time = time.time()
                result = await s_llm.acomplete(f"""
                                                    * analyze data you are given and extract the product sku(treat each size as a SKU, e.g., XS, S, M, L, etc.), description, and quantity.
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