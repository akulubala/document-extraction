from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.schema import Document
import pandas as pd
from pathlib import Path
from llama_index.core import Settings

# 步骤1：用 Pandas 读取 Excel
def load_excel_to_documents(file_path):
    sheets = pd.read_excel(file_path, sheet_name=None, engine="openpyxl", header=None)  # 不自动识别表头
    documents = []
    
    for sheet_name, df in sheets.items():
        # 优化点1：处理合并单元格，填充空值
        df = df.fillna(method="ffill", axis=0)  # 向下填充空值（处理合并单元格）
        df.columns = [f"Column_{i}" for i in range(len(df.columns))]  # 避免表头错位，重命名列
        
        # 优化点2：确保所有列和行转为字符串，避免截断
        text = f"=== 工作表 '{sheet_name}' ===\n"
        text += df.to_string(index=False)  # 使用 to_string 保留所有数据
        print(text)
        
        # 优化点3：显式定义文档ID和元数据
        documents.append(Document(
            text=text,
            metadata={"sheet_name": sheet_name, "source": file_path},
            excluded_llm_metadata_keys=["source"]  # 避免元数据干扰LLM
        ))
    
    return documents
if __name__ == "__main__":
    # 步骤2：构建索引
    Settings.chunk_size = 100000  # 调大分块大小（避免切割）
    Settings.chunk_overlap = 0  

    file_path = "../media_files/2.xlsx"
    documents = load_excel_to_documents(file_path)
    index = VectorStoreIndex.from_documents(documents)

    # 步骤3：查询引擎
    query_engine = index.as_query_engine(
    response_mode="compact",
    verbose=True
    )

    # 明确查询指令（示例）
    response = query_engine.query(
        "请严格按以下步骤操作：\n"
        "1. 遍历所有工作表\n"
        "2. 提取每张表中所有行的 'product_sku'， 'quantity' 和 'description'\n"
        "3. 以JSON格式输出完整结果，包括工作表名称和提取的数据\n"
    )
    print(response)
