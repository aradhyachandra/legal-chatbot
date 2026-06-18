import os
from pypdf import PdfReader
from langchain_core.documents import Document

def load_documents(data_dir: str = "data/raw"):
    """
    Loads all PDF documents from the specified directory.
    Returns a list of LangChain Document objects.
    """
    print(f"Loading documents from {data_dir}...")
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Directory {data_dir} does not exist.")
    
    documents = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(data_dir, filename)
            print(f"Loading {filename}...")
            reader = PdfReader(pdf_path)
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                doc = Document(
                    page_content=text,
                    metadata={"source": pdf_path, "page": page_num}
                )
                documents.append(doc)
    
    print(f"Successfully loaded {len(documents)} document pages.")
    return documents

if __name__ == "__main__":
    docs = load_documents()
    if docs:
        print(f"Sample content: {docs[0].page_content[:200]}")