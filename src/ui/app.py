import sys
from pathlib import Path

# Add the project root to sys.path so "from src.…" imports work
# when Streamlit runs this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
from src.rag.rag_pipeline import generate_answer

st.set_page_config(page_title="Legal RAG Assistant", page_icon="⚖️", layout="wide")

# Sidebar requirements
with st.sidebar:
    st.title("⚖️ Legal RAG Assistant")
    st.markdown("**Model Info:**\n- LLM: `llama3.2`\n- Embeddings: `nomic-embed-text`")
    st.info("Answers grounded in uploaded documents only.")

st.title("Indian Legal RAG Chatbot 🇮🇳")
st.markdown("Ask a question about the indexed legal documents.")

# Maintain chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display context expander if available
        if message["role"] == "assistant" and message.get("context"):
            with st.expander("View Retrieved Context & Distance Scores"):
                st.caption(f"{len(message['context'])} chunks retrieved below threshold")
                for chunk in message["context"]:
                    st.markdown(f"**Distance Score: {chunk['distance']:.4f}**")
                    st.markdown(chunk["text"])
                    st.divider()
        
        # Rule: No hallucination warning under every assistant message
        if message["role"] == "assistant":
            st.caption("_This answer is based solely on the indexed documents. Always verify with a qualified legal professional._")

# Handle new user input
if prompt := st.chat_input("E.g., What are the requirements for a valid contract?"):
    
    # 1. Display user query
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating grounded answer..."):
            try:
                # Call the pipeline
                answer, retrieved_chunks = generate_answer(prompt)
                
                # Show the generated answer prominently
                st.markdown(answer)
                
                # Show retrieved context in expandable section (for transparency)
                if retrieved_chunks:
                    with st.expander("View Retrieved Context & Distance Scores"):
                        st.caption(f"{len(retrieved_chunks)} chunks retrieved below threshold")
                        for chunk in retrieved_chunks:
                            st.markdown(f"**Distance Score: {chunk['distance']:.4f}**")
                            st.markdown(chunk["text"])
                            st.divider()
                
                # Display the hallucination disclaimer
                st.caption("_This answer is based solely on the indexed documents. Always verify with a qualified legal professional._")
                
                # Append to session history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "context": retrieved_chunks
                })
                
            except ValueError as ve:
                st.error(str(ve))
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
