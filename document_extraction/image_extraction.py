import base64
from pathlib import Path
from document_extraction.utils import BASE_DOCUMENT_PATH, OPENAI_API_KEY
from openai import OpenAI
import base64, json


def process_images(images: list) -> list:
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

        for image_path in images:
            base64_image = encode_image(Path(f"{BASE_DOCUMENT_PATH}/images/{image_path}"))
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
            api_key=OPENAI_API_KEY,
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