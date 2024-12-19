import fitz # PyMuPDF
import openai

def extract_text_from_pdf(pdf_file):
    """
    Extract text from a PDF file.
    """
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def split_text_into_chunks(text, max_tokens=8192):
    """
    Split the extracted text into chunks of a maximum token size.
    """
    # This is a simple implementation, the actual chunking logic may require
    # you to take word boundaries into account (to avoid splitting in the middle of words).
    chunks = [text[i:i + max_tokens] for i in range(0, len(text), max_tokens)]
    return chunks


def generate_embeddings_for_chunks(chunks, api_key):
    openai.api_key = api_key
    embeddings = []

    for chunk in chunks:
        response = openai.embeddings.create(  # Updated method
            model="text-embedding-ada-002",
            input=chunk
        )
        embeddings.append(response.data[0].embedding)  # Updated access to response data

    return embeddings
        