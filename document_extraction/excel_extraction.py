import asyncio
import json
from pathlib import Path
import re
from llama_index.core.schema import Document
import pandas as pd
import openai

from document_extraction.utils import BASE_DOCUMENT_PATH, OPENAI_API_KEY

def split_text_into_chunks(text, chunk_size=2000):
    """将文本分块，确保每块不超过指定大小"""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def is_effectively_empty(val):
    """判断单元格是否为空（NaN、空字符串、全空格）"""
    if pd.isna(val):
        return True
    if isinstance(val, str) and val.strip() == "":
        return True
    return False

def clean_dataframe(df):
    # 仅填充必要的空值，避免完全填充空白单元格
    df = df.copy()
    df.reset_index(drop=True, inplace=True)
    df.columns = [f"Column_{i}" for i in range(len(df.columns))]
    return df

def load_excel_to_documents(file_path, max_rows_per_chunk=100):
    """加载 Excel 文件并将其转换为文档列表，最大程度保留所有数据"""
    sheets = pd.read_excel(file_path, sheet_name=None, engine="openpyxl", header=None, dtype=object)

    documents = []
    for sheet_name, df in sheets.items():
        df = clean_dataframe(df)
        # 只按行分块，不再按字符数分块
        total_rows = 0
        for start_row in range(0, len(df), max_rows_per_chunk):
            chunk_df = df.iloc[start_row:start_row + max_rows_per_chunk]
            total_rows += len(chunk_df)
            text = f"=== 工作表 '{sheet_name}' (行 {start_row + 1} - {start_row + len(chunk_df)}) ===\n"
            text += chunk_df.to_csv(index=False, header=False, sep="\t", lineterminator="\n")
            documents.append(Document(
                text=text,
                metadata={"sheet_name": sheet_name, "source": file_path, "start_row": start_row + 1},
                excluded_llm_metadata_keys=["source"]
            ))
        print(f"{sheet_name} 分块累计行数: {total_rows}")
    return documents

async def async_query_chunk(client, prompt):
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一个结构化信息抽取助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
            max_tokens=2048,
        )
        content = response.choices[0].message.content
        # 提取 markdown 代码块中的 JSON
        match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            json_str = content
        return json.loads(json_str)
    except Exception as e:
        print(f"分块解析失败: {e}")
        return []

def process_excel(document_name: str) -> list:
    documents = load_excel_to_documents(Path(f"{BASE_DOCUMENT_PATH}/xlsx/{document_name}"), max_rows_per_chunk=100)
    client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def extract_product(semaphore, prompt):
        async with semaphore:
            return await async_query_chunk(client, prompt)
    async def process_nodes():
        print(f"准备启动 {len(documents)} 个异步任务")
        tasks = []
        semaphore = asyncio.Semaphore(5)
        for doc in documents:
            prompt = f"请从以下内容中提取每行的 'product_sku'，'QTE' 和 'description' 字段，输出JSON数组：\n{doc.text}"
            tasks.append(extract_product(semaphore, prompt))
        results = await asyncio.gather(*tasks)
        print("所有异步任务已完成")
        return results     
        
    results = asyncio.run(process_nodes())
    all_results = []
    for idx, r in enumerate(results):
        print(f"分块 {idx} 返回: {r}")
        if isinstance(r, list):
            all_results.extend(r)
        elif isinstance(r, dict):
            # 兼容 {"data": [...]}
            if "data" in r and isinstance(r["data"], list):
                all_results.extend(r["data"])
            # 兼容 {"result": [...]}
            elif "result" in r and isinstance(r["result"], list):
                all_results.extend(r["result"])
            # 兼容单个对象
            elif "product_sku" in r and "QTE" in r and "description" in r:
                all_results.append(r)
            else:
                print(f"警告：分块 {idx} 返回格式异常，已跳过")
        else:
            print(f"警告：分块 {idx} 返回格式异常，已跳过")
    return all_results