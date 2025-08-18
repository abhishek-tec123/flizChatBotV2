import os
import glob
import json
import logging
from dotenv import load_dotenv
from typing import Optional, Dict, Any

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# -------------------------
# Environment and Constants
# -------------------------
os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv()

logging.basicConfig(level=logging.INFO)

FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "fun_Vector_DB")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "Llama3-8b-8192")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

# -------------------------
# LLM and Prompt Setup
# -------------------------
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=LLM_MODEL_NAME, temperature=0)

prompt = ChatPromptTemplate.from_template(
    """Retrieve the most relevant function(s) name from the provided context based on the user's query. 
    Focus on returning a valid JSON object with the function name, parameters, and code snippet. 
    Respond only with a valid JSON object. Do not include any explanation or extra text. 
    The format must be:

    {{
      "function_name": "<function_name>",
      "parameters": {{
        "param1": "<value>",
        "param2": "<value>",
        "param3": "<value>"
      }},
      "code": "<function_code>"
    }}

    Context: {context}

    Query: {input}
    """
)

# -------------------------
# Core Class
# -------------------------
class FunctionRetriever:
    def __init__(self, file_path: str):
        """
        Initializes the FunctionRetriever with a target file.
        """
        logging.info(f"Initializing FunctionRetriever with file: {file_path}")
        self.file_path = file_path
        self.vectors = None

    def vector_embedding(self) -> Dict[str, str]:
        """
        Creates or loads FAISS vector embeddings for the provided file.
        """
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

        if self.vectors:
            logging.info("FAISS index already loaded.")
            return {"status": "FAISS index already loaded."}

        if os.path.exists(FAISS_INDEX_PATH) and glob.glob(f"{FAISS_INDEX_PATH}/*"):
            logging.info("Loading existing FAISS index from disk...")
            self.vectors = FAISS.load_local(
                FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
            )
            logging.info("FAISS index loaded successfully.")
            return {"status": "Loaded existing FAISS index."}

        logging.info("Creating vector embeddings from file content...")
        with open(self.file_path, 'r') as file:
            text = file.read()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=2000)
        chunks = text_splitter.split_text(text)
        logging.info(f"Split text into {len(chunks)} chunks.")

        documents = [Document(page_content=chunk) for chunk in chunks]
        self.vectors = FAISS.from_documents(documents, embeddings)
        self.vectors.save_local(FAISS_INDEX_PATH)
        logging.info(f"Embeddings saved at {FAISS_INDEX_PATH}.")

        return {"status": "Vector embeddings created and saved."}

    def retrieval(self, query: str) -> Optional[str]:
        """
        Retrieves the function matching the query using a retrieval chain.
        """
        if not self.vectors:
            logging.warning("Vectors not loaded. Call vector_embedding() first.")
            return None

        logging.info(f"Retrieving function for query: '{query}'")
        retriever = self.vectors.as_retriever(search_kwargs={"k": 2})
        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        response = retrieval_chain.invoke({'input': query})
        return response.get("answer", None)
    

def parse_json_response(response: str) -> Optional[Dict[str, Any]]:
    """
    Parses the LLM response JSON.
    """
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON: {e}")
        return None

def extract_function_details(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts function name and parameters from the parsed response.
    """
    return {
        "function_name": parsed.get("function_name", ""),
        "parameters": parsed.get("parameters", {})
    }
