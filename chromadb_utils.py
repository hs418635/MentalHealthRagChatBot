import chromadb
import uuid

# Initialize ChromaDB client
client = chromadb.Client()

# Recreate ChromaDB collection if not exists
def create_or_update_collection(collection_name="pdf_embeddings"):
    if collection_name in [col.name for col in client.list_collections()]:
        collection = client.get_collection(collection_name)
    else:
        collection = client.create_collection(name=collection_name)
    return collection

# Function to store embeddings in ChromaDB
def store_embeddings_in_chromadb(collection, chunks, embeddings, metadata):
    document_ids = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        document_id = str(uuid.uuid4())  # Generate a unique ID for each chunk
        chunk_metadata = metadata.copy()
        chunk_metadata["chunk_index"] = i + 1
        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            metadatas=[chunk_metadata],
            ids=[document_id]
        )
        document_ids.append(document_id)
    return document_ids
