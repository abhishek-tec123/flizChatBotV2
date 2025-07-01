# # groq chat with text string input ---------------------------------------------------------------------
# import os
# from pydantic import BaseModel
# from langchain_groq import ChatGroq
# from langchain.schema import HumanMessage
# from dotenv import load_dotenv

# # Load environment variables from .env
# load_dotenv()

# # Define request model
# class QueryRequest(BaseModel):
#     query: str

# def generate_response_from_groq(input_text: str, query: str = "", custom_prompt: str = None) -> str:
#     base_prompt = custom_prompt or (
#         "Summarize the following JSON data in clear, complete sentences.\n"
#         "Do not include any image URLs or references to images.\n"
#         "Ignore any fields containing URLs or media links.\n"
#         "Only describe textual and numeric data relevant to the company and vehicles/equipment.\n"
#         "Do not include any leading phrases like 'Here is a summary'. Keep the response clean and factual.\n\n"
#     )

#     # Include the user query to provide additional context
#     full_input = f"{base_prompt}User Query: {query}\n\nJSON Data:\n{input_text}"

#     groq_api_key = os.getenv("GROQ_API_KEY")
#     if not groq_api_key:
#         raise ValueError("GROQ_API_KEY is not set in environment variables.")

#     llm = ChatGroq(
#         model_name="llama3-70b-8192",
#         api_key=groq_api_key
#     )

#     messages = [HumanMessage(content=full_input)]
#     response = llm.invoke(messages)

#     return response.content


import os
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Define request model
class QueryRequest(BaseModel):
    query: str

def truncate_to_token_limit(text: str, max_tokens: int = 6000, buffer: int = 500) -> str:
    """
    Truncate the input text to fit within token limit.
    Approximate 1 token ≈ 4 characters.
    The buffer reserves tokens for prompt/query content.
    """
    max_chars = (max_tokens - buffer) * 4
    return text[:max_chars]

def generate_response_from_groq(input_text: str, query: str = "", custom_prompt: str = None) -> str:
    base_prompt = custom_prompt or (
        "Summarize the following JSON data in clear, complete sentences.\n"
        "Do not include any image URLs or references to images.\n"
        "Ignore any fields containing URLs or media links.\n"
        "Only describe textual and numeric data relevant to the company and vehicles/equipment.\n"
        "Do not include any leading phrases like 'Here is a summary'. Keep the response clean and factual.\n\n"
    )

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is not set in environment variables.")

    # Truncate input to avoid exceeding token limits
    truncated_input = truncate_to_token_limit(input_text)

    full_input = f"{base_prompt}User Query: {query}\n\nJSON Data:\n{truncated_input}"

    llm = ChatGroq(
        model_name="llama3-70b-8192",
        api_key=groq_api_key
    )

    messages = [HumanMessage(content=full_input)]
    response = llm.invoke(messages)

    return response.content
