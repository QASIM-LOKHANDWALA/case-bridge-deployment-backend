from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaLLM
from PyPDF2 import PdfReader

def summarize_document(file):
    reader = PdfReader(file)
    
    llm = OllamaLLM(model="llama2")
    
    text = ""
    for i, page in enumerate(reader.pages):
        content = page.extract_text()
        if content:
            text += content
            
    if not text:
        return "No Text Found"
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=200)
    chunks = text_splitter.create_documents([text])
    
    main_prompt = """
    You are a legal expert, Summarize the following legal document.
    Provide a concise summary that captures the key points and legal implications.
    Document: {text}
    """
    prompt = PromptTemplate(
        input_variables=["text"],
        template=main_prompt
    )
    
    
    chain = load_summarize_chain(
        llm=llm,
        chain_type="map_reduce",
        map_prompt=prompt,
        verbose=False
    )
    
    summary = chain.invoke({"input_documents": chunks})
    return summary if summary else "No Summary Generated"
    