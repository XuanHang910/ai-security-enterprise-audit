from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os
from typing import List, Dict, Any
from langchain_core.language_models.llms import LLM

class DummyLLM(LLM):
    """Dummy LLM for testbed isolation (replace with real LLM)."""
    def _call(self, prompt: str, stop: List[str] | None = None, **kwargs: Any) -> str:
        return f"Simulated Response based on prompt:\n{prompt[:100]}..."
        
    @property
    def _llm_type(self) -> str:
        return "dummy"

class EnterpriseRAG:
    def __init__(self, data_dir: str = "data", persist_dir: str = "./chroma_db"):
        self.data_dir = data_dir
        self.persist_dir = persist_dir
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = self._init_vectorstore()
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 2})
        self.llm = DummyLLM()
        self.chain = self._build_chain()

    def _init_vectorstore(self) -> Chroma:
        if os.path.exists(self.persist_dir) and os.listdir(self.persist_dir):
            return Chroma(persist_directory=self.persist_dir, embedding_function=self.embeddings)
            
        loader = DirectoryLoader(self.data_dir, glob="**/*.txt", loader_cls=TextLoader)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = text_splitter.split_documents(documents)
        
        return Chroma.from_documents(
            documents=splits, 
            embedding=self.embeddings, 
            persist_directory=self.persist_dir
        )

    def _build_chain(self) -> Any:
        template = """Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Context: {context}
        
        Question: {question}
        
        Answer:"""
        prompt = PromptTemplate.from_template(template)
        
        def format_docs(docs: List[Any]) -> str:
            return "\n\n".join(doc.page_content for doc in docs)
            
        return (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def query(self, question: str) -> Dict[str, Any]:
        """Extracts context and answers"""
        docs = self.retriever.invoke(question)
        context = [doc.page_content for doc in docs]
        answer = self.chain.invoke(question)
        
        return {
            "answer": answer,
            "context": context
        }
