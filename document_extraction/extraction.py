import asyncio
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI

class Extraction:
    def __init__(self, document_type, document_path):
        self.document_path = document_path
        self.document_type = document_type
        self.agent = FunctionAgent(
                        tools=[self.extract_from_image],
                        llm=OpenAI(model="gpt-4o-mini"),
                        system_prompt="You are a helpful assistant that can multiply two numbers.",
                    )

    def extract_from_image(self, a: float, b: float) -> float:
        """Useful for multiplying two numbers."""
        return a * b

    async def extract(self):
        response = await self.agent.run("What is 1234 * 4567?")
        return response