from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from tiktoken import get_encoding
import logging
import asyncio
import json

log = logging.getLogger(__name__)

# Set up Groq client
groq_api_key = "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"  # Replace securely
llm = ChatGroq(
    model_name="meta-llama/llama-4-scout-17b-16e-instruct",
    api_key=groq_api_key
)

# Tokenizer setup
encoding = get_encoding("gpt2")
MAX_TOKENS_PER_CHUNK = 14000

def count_tokens(text: str) -> int:
    return len(encoding.encode(text))

def split_text_into_chunks(text: str, max_tokens: int = MAX_TOKENS_PER_CHUNK) -> list:
    words = text.split()
    chunks = []
    current_chunk = []
    current_tokens = 0

    for word in words:
        word_tokens = len(encoding.encode(word))
        if current_tokens + word_tokens > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_tokens = word_tokens
        else:
            current_chunk.append(word)
            current_tokens += word_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

async def summarize_extracted_text(input_text: str, custom_prompt: str = None) -> str:
    summarization_prompt = custom_prompt or (
        "You are a highly skilled AI tasked with generating a concise yet comprehensive summary of the following input text.\n\n"
        "Instructions:\n"
        "- Cover every major topic and subtopic, but use as few words as possible.\n"
        "- Focus on essential facts, data, and arguments; omit unnecessary elaboration or repetition.\n"
        "- Use bullet points or short sections for clarity.\n"
        "- Avoid generalizations, but do not include excessive detail.\n"
        "- Retain important terminology and technical information.\n"
        "- Do NOT include phrases like 'In conclusion' or 'The text discusses...'; simply present the extracted information.\n\n"
        "Output a brief, accurate summary that allows someone to understand all key points without reading the original text."
    )

    input_token_count = count_tokens(input_text)

    # CASE 1: Short input – summarize in one call
    if input_token_count <= MAX_TOKENS_PER_CHUNK:
        full_input = f"{summarization_prompt}\n\nInput Text:\n{input_text}\n\nSummary:"
        response = await llm.ainvoke(full_input)
        output_token_count = count_tokens(response.content)
        result = {
            "summary": response.content,
            "log": {
                "input_tokens": input_token_count,
                "output_tokens": output_token_count,
                "total_output_tokens": output_token_count
            }
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    # CASE 2: Long input – chunk and summarize
    log.info(f"Input exceeds {MAX_TOKENS_PER_CHUNK} tokens. Splitting...")
    chunks = split_text_into_chunks(input_text)

    summaries = []
    token_logs = []
    total_input_tokens = 0
    total_output_tokens = 0

    for i, chunk in enumerate(chunks):
        full_input = f"{summarization_prompt}\n\nInput Text:\n{chunk}\n\nSummary:"
        input_tokens = count_tokens(full_input)
        response = await llm.ainvoke(full_input)
        output_text = response.content
        output_tokens = count_tokens(output_text)

        total_input_tokens += input_tokens
        total_output_tokens += output_tokens

        summaries.append(output_text)
        token_logs.append({
            "chunk": i+1,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        })

    combined_summary = "\n\n".join(summaries)
    result = {
        "summary": combined_summary,
        "log": {
            "total_chunks": len(chunks),
            "chunk_logs": token_logs,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens
        }
    }
    return json.dumps(result, ensure_ascii=False, indent=2)

# async def main():
#     text = "The Coordinator Workflow dispatches queries to various specialized agents, each responsible for handling specific types of requests:Policy Agent: Manages queries related to customer policies. It interacts with the CRM System (Customer Relationship Management) to retrieve or update policy information.Billing Agent: Handles billing-related inquiries. It interfaces with the Billing DB (Database) to access and process billing records.Claims Agent: Processes customer claims. It communicates with the Claims Backend system to manage claim submissions, statuses, and resolutions.AI Agent: This agent is designed to handle queries that can be resolved automatically using artificial intelligence. It interacts directly with a Large Language Model (LLM), such as ChatGPT, to generate responses or perform automated tasks."
#     summary = await summarize_extracted_text(text)
#     print(summary)

# asyncio.run(main())
