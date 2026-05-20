# pyrefly: ignore [missing-import]
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3.2")

response = llm.invoke("What is RAG in AI? Answer in 3 sentences.")

print(response)