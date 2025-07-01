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
    call_function_by_name, get_vehicle_details, get_equipment_details
)
from utils import (
    handle_company_based_query,
    parse_detail_query,
    handle_details_query,
    handle_generic_query
)

# === Initialize retriever ===
retriever = FunctionRetriever("C:\\Users\\Lenovo\\flizChatBot\\flizChatBot\\src\\function.txt")
retriever.vector_embedding()

# === Route Handlers ===
@app.post("/query")
def handle_query(request: QueryRequest) -> Dict[str, Any]:
    """Handle incoming queries and route to appropriate handlers."""
    query = request.query
    # Check if it's a detail query first (vehicle details of X of Y company)
    entity_type, entity_name, company_name = parse_detail_query(query)
    if entity_type and entity_name and company_name:
        return handle_details_query(query)

    result = retriever.retrieval(query)

    if not result:
        raise HTTPException(status_code=404, detail="No matching function retrieved from the model.")

    parsed = parse_json_response(result)
    if not parsed:
        raise HTTPException(status_code=400, detail="Failed to parse model response.")

    details = extract_function_details(parsed)
    function_name = details['function_name']
    parameters = details['parameters']
    
    # Handle company-based queries
    if function_name in ["get_vehicle_list", "get_equipment_list"] and "company_id" in parameters:
        return handle_company_based_query(function_name, parameters["company_id"], query)
    # Handle direct detail queries (get_vehicle_details, get_equipment_details)
    elif function_name in ["get_vehicle_details", "get_equipment_details"]:
        # For direct detail queries, the parameters should contain the ID 
        if function_name == "get_vehicle_details" and "vehicle_id" in parameters:
            response = get_vehicle_details(parameters["vehicle_id"])
        elif function_name == "get_equipment_details" and "equipment_id" in parameters:
            response = get_equipment_details(parameters["equipment_id"])
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required parameter for {function_name}"
            )
        generated_response = generate_response_from_groq(json.dumps(response, indent=3), query=query)
        return {"function_called": function_name,"generated_response": generated_response}
    else:
        None
    
    # Fallback to generic function call
    return handle_generic_query(function_name, parameters, query)

@app.get("/")
def read_root():
    return {"message": "Hello!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)