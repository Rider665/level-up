import pdfplumber
import pandas as pd

def extract_tables_from_pdf(pdf_path: str) -> dict[str, pd.DataFrame]:
    """Extract all tables from SSR PDF into DataFrames."""
    tables = {}
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            for table in page.extract_tables():
                # Clean table headers/empty rows
                df = pd.DataFrame(table[1:], columns=table[0])
                df = df.dropna(how='all')
                tables[f"page_{i+1}"] = df
    return tables

# Example usage
if __name__ == "__main__":
    pdf_path = "../../data/raw/sample_ssr.pdf"
    tables = extract_tables_from_pdf(pdf_path)
    for page, df in tables.items():
        print(f"Table from {page}:")
        print(df.head())