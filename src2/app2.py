from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from utils2 import handle_company_asset_query
from userutils import call_user_function
from context2 import process_full_api_response
# === Initialize FastAPI app ===
app = FastAPI()

# === Models ===
class QueryRequest(BaseModel):
    query: str

# === Imports from your retriever module ===
from retrvr2 import (
    FunctionRetriever,
)

# === Initialize retriever ===
retriever = FunctionRetriever("/Users/abhishek/Desktop/flizChatBot/src2/function2.txt")
retriever.vector_embedding()

def generate_llm_response(response_data: Dict, query: str) -> Dict[str, Any]:
    """Generate response using Groq LLM."""
    try:
        response_text = json.dumps(response_data, indent=3)
        llm_response = process_full_api_response(response_text, query=query)
        return {"result": llm_response}
    except Exception as e:
        return {"error": f"Error generating response: {str(e)}"}

def parse_retriever_result(result: Any) -> Dict[str, Any]:
    if not result:
        return {"retriever_result": "No result found"}

    try:
        # Parse JSON string if necessary
        parsed_result = json.loads(result) if isinstance(result, str) else result

        function_name = parsed_result.get("function_name")
        parameters = parsed_result.get("parameters", {})

        # Print or log for debugging
        print("🔧 Function Name:", function_name)
        print("📦 Parameters:")
        for key, value in parameters.items():
            print(f"   {key}: {value}")

        return {
            "function_name": function_name,
            "parameters": parameters
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Failed to parse function data: {str(e)}")

# === Route Handlers ===
@app.post("/query")
def handle_query(request: QueryRequest) -> Dict[str, Any]:
    query = request.query
    result = retriever.retrieval(query)

    # Parse retriever result
    parsed_output = parse_retriever_result(result)
    print("Parsed Output:", parsed_output)

    # Extract function name and parameters
    function_name = parsed_output.get("function_name")
    parameters = parsed_output.get("parameters", {})

    if function_name == "handle_company_asset_query":
        # Print each parameter one by one (explicitly if known)
        company_type = parameters.get("company_type")
        company_name = parameters.get("company_name")
        asset_name = parameters.get("asset_name")
        output = handle_company_asset_query(company_type, company_name, asset_name)
        return generate_llm_response(output,query)
        # return output
    elif function_name == "call_user_function":
        fun_name = parameters.get("function_name")
        arguments = parameters.get("arg")
        output = call_user_function(fun_name, arguments)
        # Ensure output is a dictionary
        print(output)
        if not isinstance(output, dict):
            return {"result": generate_llm_response(output, query)}
        return generate_llm_response(output, query)
        # return output

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported function: {function_name}")
