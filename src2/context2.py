# # groq chat with text string input ---------------------------------------------------------------------

import os
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from dotenv import load_dotenv
import logging
import tiktoken
from sumary2 import summarize_extracted_text
# Load environment variables from .env
load_dotenv()

# Define request model
class QueryRequest(BaseModel):
    query: str

def generate_response_from_groq(input_text: str, query: str = "", custom_prompt: str = None) -> str:
    base_prompt = custom_prompt or (
        "give the consise and exact response of user query and not show any type of id like Company id and other\n"
    )

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is not set in environment variables.")

    # Use the full input_text without truncation
    full_input = f"{base_prompt}User Query: {query}\n\nJSON Data:\n{input_text}"

    def count_tokens(text):
        if tiktoken:
            enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
            return len(enc.encode(text))
        else:
            # Approximate: 1 token ≈ 4 characters
            return len(text) // 4

    # logging.info(f"[Token Log] base_prompt tokens: {count_tokens(base_prompt)}")
    # logging.info(f"[Token Log] input_text tokens: {count_tokens(input_text)}")
    # logging.info(f"[Token Log] full_input tokens: {count_tokens(full_input)}")

    llm = ChatGroq(
        model_name="meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=groq_api_key
    )

    messages = [HumanMessage(content=full_input)]
    response = llm.invoke(messages)

    # Try to log response token count
    response_text = getattr(response, 'content', str(response))
    logging.info(f"[Token Log] response tokens: {count_tokens(response_text)}")
    # print(response.content)

    return response.content


import asyncio

def process_full_api_response(input_text: str, query: str = "", custom_prompt: str = None) -> str:
    # First, summarize the input text asynchronously
    summary = asyncio.run(summarize_extracted_text(input_text))
    # print("this is summary : ",summary)
    # Now pass the summary to your Groq-based response generator
    final_response = generate_response_from_groq(summary, query=query, custom_prompt=custom_prompt)
    
    return final_response

