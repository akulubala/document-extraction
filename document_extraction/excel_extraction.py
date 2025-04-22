import json
import re
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document
import pandas as pd
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI

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

def process_excel(file_path: str) -> list:
    """处理 Excel 文件，返回所有工作表的提取结果"""
    Settings.chunk_size = 100000
    Settings.chunk_overlap = 0
    Settings.llm = OpenAI(model="gpt-4o")
    file_path = "../media_files/f.xlsx"
    documents = load_excel_to_documents(file_path, max_rows_per_chunk=100)
    index = VectorStoreIndex.from_documents(documents)

    query_engine = index.as_query_engine(
        response_mode="tree_summarize",
        verbose=True
    )

    all_results = []
    for i, doc in enumerate(documents):
        # 处理每个分块的文本
        result = query_engine.query(
            f"请从以下内容中提取每行的 'product_sku'，'QTE' 和 'description' 字段，输出JSON数组：\n{doc.text}"
        )
        # print(f"第 {i + 1} 个分块的提取结果: {result}")
        try:
            # 提取 markdown 代码块中的 JSON
            result_str = str(result)
            match = re.search(r"```json\s*(.*?)\s*```", result_str, re.DOTALL)
            if match:
                json_str = match.group(1)
            else:
                json_str = result_str  # 如果没有代码块，直接用原始内容
            result_json = json.loads(json_str)
            all_results += result_json
        except Exception as e:
            print(f"第 {i + 1} 个分块解析失败: {e}")
    return all_results