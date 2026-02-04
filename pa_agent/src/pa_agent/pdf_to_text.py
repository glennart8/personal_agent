from pypdf import PdfReader
from backend.constants import DATA_PATH

def convert_pdf_to_txt(pdf_path, txt_export_path) -> str:
    """Extraherar text från PDF och sparar det direkt till en textfil."""
    reader = PdfReader(pdf_path)
    
    all_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            all_text += text + "\n"
    
    with open(txt_export_path, "w", encoding="utf-8") as file:
        file.write(all_text)
    
    return all_text

if __name__ == "__main__":
    for pdf_path in DATA_PATH.glob("*.pdf"):
        filename = f"{pdf_path.stem.casefold()}.txt"
        convert_pdf_to_txt(pdf_path, DATA_PATH / filename)
           