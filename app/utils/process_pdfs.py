import os
from hybrid_rag import pdf_to_documents

def process_all_pdfs(directory, org_id):
    """Process all PDFs in the specified directory."""
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory, filename)
            pdf_to_documents(pdf_path, org_id)
            print(f"Processed and indexed {pdf_path}")

if __name__ == "__main__":
    pdf_directory = "data/documents/"
    organization_id = 1  # Adjust based on your organization ID logic
    process_all_pdfs(pdf_directory, organization_id)