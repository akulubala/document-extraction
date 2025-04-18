import asyncio, base64, time, json
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI as LLMOpenAI
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.extractors import PydanticProgramExtractor

from pathlib import Path
from llama_index.core.node_parser import SentenceSplitter
from document_extraction.models.product import Product
from openai import OpenAI
import base64
import pandas as pd

from .utils import loadEnv
from .extract_from_excel import process_excel

env = loadEnv()
BASE_DOCUMENT_PATH = env.str('BASE_DOCUMENT_PATH', '/code/booking_v2/mediafiles/extract-files/')
class Extraction:
    def __init__(self, **kwargs):
        self.document_type = kwargs.get("document_type")
        self.document_name = kwargs.get("document_name", None)
        self.images = kwargs.get('images', [])
        self.llm = LLMOpenAI(model="gpt-4o-mini")
        self.s_llm = self.llm.as_structured_llm(Product)

    def doExtract(self):
        try:
            if self.document_type == "pdf":
                loaded_data = self.load_from_pdf()
            if self.document_type == "docx":
                loaded_data = self.load_from_docx()
            if self.document_type == "xlsx":
                loaded_data = self.load_from_excel()
            if self.document_type == 'excel':
                loaded_data = self.load_from_xlsx()
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

    def load_from_pdf(self):

        try:
            pdf_reader = SimpleDirectoryReader(
                input_files=[Path(f"{BASE_DOCUMENT_PATH}{self.document_name}")])
            return self.node_parse(pdf_reader.load_data())
        except Exception as e:
            raise Exception(f"Error loading PDF: {e}")

    def load_from_docx(self):
        try:
            docx_reader = SimpleDirectoryReader(
                input_files=[Path(f"{BASE_DOCUMENT_PATH}{self.document_name}")])
            documents = docx_reader.load_data()
            return self.node_parse(documents)
        except Exception as e:
            raise Exception(f"Error loading DOCX: {e}")

    def load_from_xlsx(self):
        try:
            extracted_data = process_excel(Path(f"{BASE_DOCUMENT_PATH}{self.document_name}"))
            if not extracted_data:
                raise ValueError("Failed to extract data from the Excel file.")
            return extracted_data
        except Exception as e:
            raise Exception(f"Error loading Excel: {e}")
        
    def load_from_excel(self):
        try:
            df = pd.read_excel("1.xlsx")
            print(df.to_markdown())
            xlsx_reader = SimpleDirectoryReader(
                input_files=[Path(f"{BASE_DOCUMENT_PATH}{self.document_name}")])
            documents = xlsx_reader.load_data()
            return self.node_parse(documents)
        except Exception as e:
            raise Exception(f"Error loading DOCX: {e}")
        

    def load_from_image(self) -> list:
        # get image url from paramters
        contents = [
            {
                "type": "text",
                "text": '''
                            * Analyze this image data and identify:
                            
                              1. sku (product identifier string or alphanumeric code)

                              2. product_description (textual name or title of the product)

                              3. quantity (numeric count of items)

                            * Requirements:

                              1. Return only these three fields in JSON format.

                              2. Preserve all original formatting, including spaces, symbols, and capitalization.

                              3. If a field contains extra information (e.g., material codes merged with SKU), keep it intact.

                              4. Do not assume column headers—analyze the data structure to identify the correct fields.
                        '''
            }
        ]
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")

        for image_path in self.images:
            base64_image = encode_image(Path(f"{BASE_DOCUMENT_PATH}{image_path}"))
            image_type = image_path.split(".")[-1]
            if image_type not in ["png", "jpg", "jpeg"]:
                raise ValueError("Unsupported image type. Supported types are: png, jpg, jpeg.")
            else:
                image_type = "jpeg" if image_type == "jpg" else image_type
            contents.append({
                "type": "image_url",
                "image_url": {
                    "url":  f"data:image/{image_type};base64,{base64_image}",
                }
            })
        client = OpenAI(
            api_key=env.str('OPENAI_API_KEY')
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                "role": "user",
                "content": contents
                }
            ],
            max_tokens=4096,
        )
        print("Response from OpenAI:", response)
        response = response.choices[0]
        json_string = response.message.content.split('```json\n')[
            1].split('```')[0]
        json_data = json.loads(json_string)
        return json_data


if __name__ == "__main__":
    # Example usage
    extractor = Extraction("image", "1.png")
    result = extractor.doExtract()
    print(result)
