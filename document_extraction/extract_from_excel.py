import pandas as pd
from openai import OpenAI
import json
import os
from tqdm import tqdm
from pathlib import Path

from utils import loadEnv
env = loadEnv()
# Set your OpenAI API key
openai = OpenAI(
            api_key=env.str('OPENAI_API_KEY')
        )
def analyze_sheet(df_sample):
    """Use OpenAI to analyze a sheet sample and identify key columns"""
    excerpt = df_sample.head(5).to_string()
    
    system_prompt = """Analyze this Excel sheet data and identify:
    1. Column containing product SKUs (barcodes/unique IDs)
    2. Column containing quantities (numbers)
    3. Columns to combine for descriptions (product name, specs, etc.)
    
    Return JSON with:
    - "sku_column": column identifier (letter or index)
    - "qty_column": column identifier
    - "description_columns": array of column identifiers
    - "header_row": row number (0-based) containing headers
    - "confidence": your confidence score (0-1)
    """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": excerpt}
        ],
        temperature=0.3
    )
    
    return json.loads(response.choices[0].message.content)

def extract_data(df, analysis):
    """Extract data from a DataFrame based on analysis results"""
    results = []
    
    for _, row in df.iterrows():
        try:
            # Get SKU
            sku = str(df[analysis['sku_column']].iloc[row.name])
            if pd.isna(sku) or sku.lower() in ['nan', 'none', '']:
                continue
                
            # Get quantity
            qty = str(df[analysis['qty_column']].iloc[row.name])
            try:
                qty = int(float(qty)) if qty.replace('.','').isdigit() else 0
                if qty <= 0:
                    continue
            except:
                continue
                
            # Build description
            desc_parts = []
            for col in analysis['description_columns']:
                part = str(df[col].iloc[row.name])
                if part and part.lower() not in ['nan', 'none']:
                    desc_parts.append(part.strip())
            
            if not desc_parts:
                continue
                
            results.append({
                "sku": sku.strip(),
                "quantity": qty,
                "description": ", ".join(desc_parts),
                "sheet": df.attrs.get('sheet_name', 'unknown')
            })
            
        except Exception as e:
            continue
            
    return results

def process_excel(file_path):
    """Process all sheets in an Excel file"""
    xls = pd.ExcelFile(file_path)
    all_results = []
    
    for sheet_name in tqdm(xls.sheet_names, desc="Processing sheets"):
        try:
            # Read sample of sheet for analysis
            df_sample = pd.read_excel(xls, sheet_name=sheet_name, nrows=10)
            if df_sample.empty:
                continue
                
            # Analyze sheet structure
            analysis = analyze_sheet(df_sample)
            print(f"\nAnalysis for {sheet_name}:")
            print(json.dumps(analysis, indent=2))
            
            # Read full sheet with proper headers
            df = pd.read_excel(xls, 
                              sheet_name=sheet_name,
                              header=analysis.get('header_row', 0))
            df.attrs['sheet_name'] = sheet_name  # Store sheet name
            
            # Extract data
            sheet_results = extract_data(df, analysis)
            all_results.extend(sheet_results)
            
        except Exception as e:
            print(f"Error processing {sheet_name}: {str(e)}")
            continue
            
    return all_results

# Main execution
if __name__ == "__main__":
    excel_path = "../media_files/1.xlsx"  # Change to your file path
    extracted_data = process_excel(Path(f"../media_files/1.xlsx"))
    
    # Save results
    with open('multi_sheet_extraction.json', 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nExtracted {len(extracted_data)} items from {len(set(x['sheet'] for x in extracted_data))} sheets")


