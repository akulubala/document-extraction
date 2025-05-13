# Document Extraction

Document Extraction is an AI-powered tool for extracting structured data from unstructured documents (PDF, Word, images). It uses OpenAI and LlamaIndex for prompt-driven, flexible data extraction.

## Features

- Supports PDF, Word, Xlsx, images
- Customizable extraction via prompt
- Batch processing
- Outputs JSON
- FastAPI backend

## Quick Start

1. **Install dependencies**
   ```bash
   poetry install
   ```

2. **Configure environment**
   - Set your OpenAI API key and extraction `prompt`.

3. **Start the API**
   ```bash
   poetry run uvicorn main:app --reload
   ```

4. **Use the API**
   - Upload documents and set your prompt via `/extract` endpoint.
   - See docs at `http://localhost:8000/docs`.

## Example Prompt

```yaml
prompt: "Extract the contract parties and the signing date from the document."
```

## Tech Stack

- FastAPI, OpenAI, LlamaIndex, OCR tools

## Support

Open an issue for help or feedback.


## DeepWiki

https://deepwiki.com/akulubala/document-extraction/1-overview
