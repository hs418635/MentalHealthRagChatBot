import openai
import chromadb
import streamlit as st
from pdf_utils import extract_text_from_pdf, split_text_into_chunks, generate_embeddings_for_chunks
import chromadb_utils as db_utils
from auth_utils import register_user, authenticate_user
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_relevant_documents(question, collection, relevance_threshold=0.8):
    # Generate embedding for the question using the new OpenAI API
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=[question]
    )
    query_embedding = response['data'][0]['embedding']

    # Query ChromaDB to find relevant documents
    query_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5  # Get top 5 results
    )

    # Filter relevant documents based on distance
    relevant_documents = []
    for i, distance in enumerate(query_results["distances"]):
        if distance <= relevance_threshold:  # Check if relevance is above the threshold
            relevant_documents.append(query_results["documents"][i])

    return relevant_documents

def chatbot_response(question, collection):
    # Get relevant documents from ChromaDB
    relevant_docs = get_relevant_documents(question, collection)

    # Create context by concatenating relevant documents
    context = " ".join([doc for doc in relevant_docs])

    # Generate a response using OpenAI’s GPT model
    prompt = f"Context: {context}\nQuestion: {question}"

    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.7
    )

    return response['choices'][0]['message']['content'].strip()

def main():
    st.title("Mental Health Chatbot with PDF Embedding")

    # Menu for navigation
    menu = ["Login", "Register", "Chatbot"]
    choice = st.sidebar.selectbox("Select an option", menu)

    if choice == "Register":
        st.subheader("Register New Account")

        # Registration form
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Register"):
            if username and password:
                # Register the user
                success = register_user(username, password, OPENAI_API_KEY)  # API key from .env file
                if success:
                    st.success("Registration successful! You can now log in.")
                else:
                    st.error("Username already exists. Please choose a different username.")
            else:
                st.error("Please fill in all fields.")

    elif choice == "Login":
        st.subheader("Login")

        # Login form
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            api_key = authenticate_user(username, password)  # No need for API key here
            if api_key:
                # Store the API key in session state for later use
                st.session_state["logged_in"] = True
                st.session_state["api_key"] = OPENAI_API_KEY  # Use API key from .env
                st.session_state["page"] = "Chatbot"  # Set the page to "Chatbot"
                st.success("Login successful!")
            else:
                st.error("Invalid username or password.")

    elif choice == "Chatbot" or ("logged_in" in st.session_state and st.session_state["logged_in"] and st.session_state.get("page") == "Chatbot"):
        if "logged_in" in st.session_state and st.session_state["logged_in"]:
            api_key = st.session_state["api_key"]

            uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

            if uploaded_file:
                # Extract text from the uploaded PDF
                pdf_text = extract_text_from_pdf(uploaded_file)

                if len(pdf_text.strip()) == 0:
                    st.error("No text found in the PDF file.")
                    return

                # Split the text into chunks
                chunks = split_text_into_chunks(pdf_text)
                st.write(f"Extracted {len(chunks)} chunks.")

                # Generate embeddings
                embeddings = generate_embeddings_for_chunks(chunks, api_key)
                st.success("Embeddings generated successfully")

                # Create or update the ChromaDB collection
                collection = db_utils.create_or_update_collection()

                # Store the embeddings in ChromaDB
                metadata = {
                    "file_name": uploaded_file.name,
                    "file_size": uploaded_file.size,
                    "content_length": len(pdf_text)
                }
                document_ids = db_utils.store_embeddings_in_chromadb(collection, chunks, embeddings, metadata)

                st.success("Embeddings stored in ChromaDB successfully!")
                st.write("Stored Document IDs:")
                st.write(document_ids[:5])  # Show only the first 5 IDs for brevity

                # Handle the chatbot interaction
                question = st.text_input("Ask your question about the PDF content:")
                if question:
                    st.info("Generating response...")
                    response = chatbot_response(question, collection)
                    st.write("Chatbot Response:")
                    st.success(response)

        else:
            st.error("Please log in to access the chatbot functionality.")

if __name__ == "__main__":
    main()
