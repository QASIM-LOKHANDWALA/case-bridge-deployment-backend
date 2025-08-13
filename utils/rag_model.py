from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate 
from langchain_community.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
import os

def get_legal_answer(user_query):
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    base_dir = os.path.dirname(__file__)
    index_path = os.path.join(base_dir, "legal_vectorstore")
    vectorstore = FAISS.load_local(index_path, embedding, allow_dangerous_deserialization=True)

    llm = OllamaLLM(model="mistral")

    prompt = ChatPromptTemplate.from_template("""
        You are a legal expert. Answer the question based on the provided context.
        If the context is not relevant generate the ansswer on your own.
        Think step by step and provide a detailed answer.
        <context>
        {context}
        </context>   
        Question: {input}                                     
    """)

    doc_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)

    retriever = vectorstore.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, doc_chain)

    response = retrieval_chain.invoke({"input": user_query})
    return response.get("answer", "No answer generated.")
