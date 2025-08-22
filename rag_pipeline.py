
import os
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from langchain_community.document_loaders import JSONLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate


load_dotenv()

class RAGPipeline:
    """
    Handles retrieval using Google Gemini for embeddings and hypothetical answer generation.
    """
    def __init__(self, file_path: str = "enriched_cases.json"):
        
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")
        
        print("Initializing RAG Pipeline...")
        self.file_path = file_path
        
        # 1. Load documents
        self.documents = self._load_documents()
        if not self.documents:
            raise ValueError(f"No documents loaded from {file_path}. Check the file.")

        # 2. Initialize Gemini Embeddings Model
        print("Initializing Embeddings...")
        self.embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

        # 3. Create and persist the Vector Store
        print("Creating FAISS vector store...")
        self.vector_store = FAISS.from_documents(self.documents, self.embeddings_model)

        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature =0)
        
        # 4. Set up the Hypothetical Answer Generator (HyDE)
        hyde_prompt = PromptTemplate(
            input_variables=["question"],
            template="You are a legal expert. Given the following legal question, please write a brief, hypothetical passage that contains the most likely answer. This passage will be used to find relevant legal precedents.\nQuestion: {question}\nPassage:"
        )
        
        self.hyde_chain = hyde_prompt | self.llm | StrOutputParser()

    def _load_documents(self) -> List[Any]:
    
        loader = JSONLoader(
        file_path=self.file_path,
        jq_schema='.[]',  
        content_key='full_text', 
        metadata_func=lambda record, metadata: record.get("metadata", {}), 
        text_content=False
        )
        return loader.load()

    def retrieve(self, query: str, filters: Optional[Dict] = None, top_k: int = 3) -> List[Any]:
        # Step 1: Generate a hypothetical answer to the query
        hypothetical_answer = self.hyde_chain.invoke({"question":query})
        
        # Step 2: Use the hypothetical answer to perform a semantic search
     
        results = self.vector_store.similarity_search(hypothetical_answer, k=top_k * 2)

        # Step 3: Metadata Filtering
        if filters:
            filtered_results = []
            for doc in results:
                match = True
                for key, value in filters.items():
                    if key not in doc.metadata or str(doc.metadata[key]).lower() != str(value).lower():
                        match = False
                        break
                if match:
                    filtered_results.append(doc)
            return filtered_results[:top_k]
        
        return results[:top_k]

    def generate_context(self, query: str, filters: Optional[Dict] = None) -> str:
        """Retrieves the most relevant case and formats it into a context string."""
        print(f"\n Searching for precedents: '{query}' with filters: {filters}")
        best_docs = self.retrieve(query, filters=filters)

        if not best_docs:
            return "No relevant legal precedent found matching the criteria."

        top_doc = best_docs[0]
        metadata = top_doc.metadata
        context = f"""--- RELEVANT PRECEDENT FOUND ---
Case Name: {metadata.get('case_name', 'N/A')} ({metadata.get('year', 'N/A')})
Jurisdiction: {metadata.get('jurisdiction', 'N/A')}
Key Principles: {', '.join(metadata.get('key_legal_principles', []))}
Outcome: {metadata.get('outcome', 'N/A')}
Summary: "{top_doc.page_content[:1000]}..."
"""
        return "\n".join([line.strip() for line in context.strip().split('\n')])

# Example of how to use the pipeline
if __name__ == "__main__":
    pipeline = RAGPipeline(file_path="enriched_cases.json")
    case_query = "teacher promotion based on new qualifications"
    
    context = pipeline.generate_context(
        case_query, 
        filters={"case_type":"Service Law"}
    )
    print(context)

