import json
from typing import Dict, List, Optional, Tuple, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from context import generate_response_from_groq

# === Initialize FastAPI app ===
app = FastAPI()

# === Models ===
class QueryRequest(BaseModel):
    query: str

# === Imports from your retriever module ===
from retrever import (
    FunctionRetriever, parse_json_response, extract_function_details,
    get_vehicle_list, get_equipment_list,
    get_delivery_companies, get_renter_companies,
    call_function_by_name
)
from utils import (
    handle_company_based_query,
    handle_vehicle_details,
    handle_equipment_details,
    handle_generic_query,
    handle_payment_query,
    handle_favourite_query
)

# === Initialize retriever ===
retriever = FunctionRetriever("/Users/abhishek/Desktop/flizChatBot/src/function.txt")
retriever.vector_embedding()

# === Route Handlers ===
@app.post("/query")
def handle_query(request: QueryRequest) -> Dict[str, Any]:
    query = request.query
    if "payment" in query.lower() and "list" in query.lower():
        return handle_payment_query(query)
    result = retriever.retrieval(query)

    if not result:
        raise HTTPException(status_code=404, detail="No matching function retrieved from the model.")

    parsed = parse_json_response(result)
    print("model reterever : ", parsed)
    if not parsed:
        raise HTTPException(status_code=400, detail="Failed to parse model response.")

    details = extract_function_details(parsed)
    function_name = details['function_name']
    parameters = details['parameters']

    # if function_name == "get_payment_list":
    #     return handle_payment_query(query)
    if function_name == "get_usr_favourite_list":
        return handle_favourite_query(query)
    elif function_name in ["get_vehicle_list", "get_equipment_list"] and "company_id" in parameters:
        return handle_company_based_query(function_name, parameters["company_id"], query)
    elif function_name == "get_vehicle_details":
        return handle_vehicle_details(query)
    elif function_name == "get_equipment_details":
        return handle_equipment_details(query)
    return handle_generic_query(function_name, parameters, query)

@app.get("/")
def read_root():
    return {"message": "Hello!"}