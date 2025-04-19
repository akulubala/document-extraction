from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document
import pandas as pd
from llama_index.core import Settings

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
    # 不做任何清洗，最大程度保留原始内容
    df = df.copy()
    df.reset_index(drop=True, inplace=True)
    df.columns = [f"Column_{i}" for i in range(len(df.columns))]
    return df

def load_excel_to_documents(file_path, max_rows_per_chunk=100):
    """加载 Excel 文件并将其转换为文档列表，最大程度保留所有数据"""
    sheets = pd.read_excel(file_path, sheet_name=None, engine="openpyxl", header=None, dtype=object)

    documents = []
    for sheet_name, df in sheets.items():
        print(f"{sheet_name} 原始行数: {len(df)}")
        df = clean_dataframe(df)
        print(f"{sheet_name} 清洗后行数: {len(df)}")
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

if __name__ == "__main__":
    Settings.chunk_size = 100000
    Settings.chunk_overlap = 0

    file_path = "../media_files/f.xlsx"
    documents = load_excel_to_documents(file_path, max_rows_per_chunk=100)
    index = VectorStoreIndex.from_documents(documents)

    query_engine = index.as_query_engine(
        response_mode="tree_summarize",
        verbose=True
    )

    all_results = []
    for i, doc in enumerate(documents):
        result = query_engine.query(
            f"请从以下内容中提取每行的 'product_sku'，'QTE' 和 'description' 字段，输出JSON数组：\n{doc.text}"
        )
        all_results.append(str(result))

    # 合并所有结果
    with open("all_json_results.txt", "w", encoding="utf-8") as f:
        for i, res in enumerate(all_results):
            f.write(res)
    print(f"已分批处理所有分块内容，共 {len(documents)} 个分块。请查看 all_json_results.txt。")