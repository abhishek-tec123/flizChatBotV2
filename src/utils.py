import json
from typing import Dict, List, Optional, Tuple, Any
from fastapi import HTTPException
from context import generate_response_from_groq
import re
from retrever import (
    get_vehicle_list, get_equipment_list,
    get_delivery_companies, get_renter_companies , get_vehicle_details, get_equipment_details
)

def get_delivery_company_names(full_response):
    item_list = full_response.get("data", {}).get("itemList", [])
    return [company['name'] for company in item_list]

def get_rental_company_names(full_response):
    item_list = full_response.get("data", {}).get("itemList", [])
    return [company['name'] for company in item_list]

delivery_companies = get_delivery_companies(page=1, per_page=100)
delivery_company_names = get_delivery_company_names(delivery_companies)
rental_companies = get_renter_companies(page=1, per_page=100)
rental_company_names = get_rental_company_names(rental_companies)


def generate_llm_response(response_data: Dict, query: str) -> str:
    """Generate response using Groq LLM."""
    try:
        response_text = json.dumps(response_data, indent=3)
        return generate_response_from_groq(response_text, query=query)
    except Exception as e:
        return f"Error generating response: {str(e)}"

def find_company_by_name(company_list: List[Dict], company_name: str) -> Optional[str]:
    """Find company ID by name in the company list."""
    search_name_lower = company_name.lower()
    for company in company_list:
        company_name_lower = company.get("name", "").lower()
        if search_name_lower == company_name_lower or search_name_lower in company_name_lower:
            return company.get("_id")
    return None

def get_company_list(function_name: str, company_name: str) -> Tuple[List[Dict], str]:
    """Get company list based on function type."""
    if function_name == "get_vehicle_list":
        companies = get_delivery_companies(
            page=1,
            per_page=10,
            search=company_name,
            cat_id=None,
            type=None,
            sizeTypetype=None
        )
    else:  # get_equipment_list
        companies = get_renter_companies(
            role="renter",
            search=company_name,
            page=1,
            per_page=10
        )
    
    company_list = companies.get("data", {}).get("itemList", [])
    return company_list, "delivery" if function_name == "get_vehicle_list" else "renter"

def extract_entity_details(query: str, entity_type: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract company name and entity type from query."""
    query_lower = query.lower()
    prefix = f"show {entity_type} details of "
    
    if prefix not in query_lower:
        return None, None
        
    remaining = query_lower.replace(prefix, "").strip()
    entity_name = None
    company_name = None
    
    for separator in [" of ", " from ", " in "]:
        if separator in remaining:
            parts = remaining.split(separator)
            if len(parts) >= 2:
                entity_name = parts[0].strip()
                company_name = " ".join(parts[1:]).strip()
                break
    
    if company_name:
        company_name = company_name.replace("company", "").strip()
    
    return entity_name, company_name

def find_entity_by_type(entity_list: List[Dict], entity_type: str, is_vehicle: bool) -> Optional[str]:
    """Find entity ID by type in the entity list."""
    for entity in entity_list:
        details = entity.get("vehicleDetails" if is_vehicle else "equipmentDetails", {})
        if details:
            name_field = "sizeType" if is_vehicle else "equipmentName"
            if entity_type.lower() in details.get(name_field, "").lower():
                return details.get("_id")
    return None

def parse_detail_query(query: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parse queries like 'vehicle details of truck of ABC company' or 'equipment details of crane from XYZ'
    Returns: (entity_type, entity_name, company_name)
    """
    query_lower = query.lower()
    
    # Check if it's a vehicle or equipment details query
    entity_type = None
    if "vehicle details" in query_lower or "vehicle detail" in query_lower:
        entity_type = "vehicle"
    elif "equipment details" in query_lower or "equipment detail" in query_lower:
        entity_type = "equipment"
    else:
        return None, None, None
    
    # Remove common words and normalize
    query_cleaned = re.sub(r'\b(details?|of|from|in|the|company)\b', ' ', query_lower)
    query_cleaned = re.sub(r'\s+', ' ', query_cleaned).strip()
    
    # Extract parts after entity type
    if entity_type == "vehicle":
        pattern = r'vehicle\s+(.+)'
    else:
        pattern = r'equipment\s+(.+)'
    
    match = re.search(pattern, query_cleaned)
    if not match:
        return entity_type, None, None
    
    remaining = match.group(1).strip()
    
    # Split on common separators to find entity name and company
    words = remaining.split()
    if len(words) >= 2:
        # Last word is likely company name, everything else is entity name
        entity_name = ' '.join(words[:-1])
        company_name = words[-1]
        return entity_type, entity_name, company_name
    elif len(words) == 1:
        # Only one word, could be either entity or company
        return entity_type, words[0], None
    
    return entity_type, None, None

def find_entity_in_list(entity_list: List[Dict], entity_name: str, is_vehicle: bool) -> Optional[str]:
    """
    Find entity ID by name in the entity list.
    """
    entity_name_lower = entity_name.lower()
    
    for entity in entity_list:
        if is_vehicle:
            details = entity.get("vehicleDetails", {})
            # Check multiple fields for vehicle
            fields_to_check = ["sizeType", "vehicleName", "name", "title"]
        else:
            details = entity.get("equipmentDetails", {})
            # Check multiple fields for equipment
            fields_to_check = ["equipmentName", "name", "title", "type"]
        
        if details:
            for field in fields_to_check:
                field_value = details.get(field, "")
                if field_value and entity_name_lower in field_value.lower():
                    return details.get("_id")
    
    return None

def handle_details_query(query: str) -> Dict[str, Any]:
    """
    Handle detailed queries for vehicles and equipment.
    """
    entity_type, entity_name, company_name = parse_detail_query(query)
    
    if not entity_type:
        raise HTTPException(
            status_code=400,
            detail="Unable to parse query. Please specify 'vehicle details' or 'equipment details'"
        )
    
    if not entity_name or not company_name:
        raise HTTPException(
            status_code=400,
            detail="Please specify both the entity name and company name in your query"
        )
    
    is_vehicle = entity_type == "vehicle"
    
    # Get company list based on entity type
    if is_vehicle:
        companies = get_delivery_companies(page=1, per_page=10, search=company_name)
        available_companies = delivery_company_names
    else:
        companies = get_renter_companies(role="renter", search=company_name, page=1, per_page=10)
        available_companies = rental_company_names
    
    company_list = companies.get("data", {}).get("itemList", [])
    company_id = find_company_by_name(company_list, company_name)
    
    if not company_id:
        available_str = ", ".join(available_companies)
        raise HTTPException(
            status_code=404,
            detail=f"Company '{company_name}' not found. Available companies: {available_str}"
        )
    
    # Get entity list from the company
    if is_vehicle:
        entity_list_response = get_vehicle_list(company_id)
    else:
        entity_list_response = get_equipment_list(company_id)
    
    if not entity_list_response or not entity_list_response.get("data"):
        raise HTTPException(
            status_code=404,
            detail=f"No {entity_type}s found for company '{company_name}'"
        )
    
    entity_list = entity_list_response.get("data", {}).get("itemList", [])
    entity_id = find_entity_in_list(entity_list, entity_name, is_vehicle)
    
    if not entity_id:
        # Get available entity names for error message
        available_entities = []
        for entity in entity_list:
            if is_vehicle:
                details = entity.get("vehicleDetails", {})
                name = details.get("sizeType") or details.get("vehicleName") or details.get("name", "")
            else:
                details = entity.get("equipmentDetails", {})
                name = details.get("equipmentName") or details.get("name", "")
            
            if name:
                available_entities.append(name)
        
        available_str = ", ".join(available_entities[:10])  # Limit to first 10
        raise HTTPException(
            status_code=404,
            detail=f"{entity_type.title()} '{entity_name}' not found in company '{company_name}'. Available {entity_type}s: {available_str}"
        )
    
    # Get detailed information
    if is_vehicle:
        details_response = get_vehicle_details(entity_id)
    else:
        details_response = get_equipment_details(entity_id)
    
    if not details_response:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve {entity_type} details"
        )
    
    generated_response = generate_llm_response(details_response, query)
    
    return {
        "function_called": f"get_{entity_type}_details",
        "entity_id": entity_id,
        "generated_response": generated_response
    }

def handle_company_based_query(function_name: str, company_name: str, query: str) -> Dict[str, Any]:
    """Handle queries that require company lookup."""
    company_list, company_type = get_company_list(function_name, company_name)
    print("company_list :", "success" if company_list else "failed")
    
    company_id = find_company_by_name(company_list, company_name)
    print("company_id :", company_id)

    if not company_id:
        if function_name == "get_vehicle_list":
            available_companies = delivery_company_names
        else:  # get_equipment_list
            available_companies = rental_company_names

        available_str = ", ".join(available_companies)
        raise HTTPException(
            status_code=404,
            detail=f"Company '{company_name}' not found. Available companies: {available_str}"
        )

    # Get entity list based on function type
    if function_name == "get_vehicle_list":
        response = get_vehicle_list(company_id)
        print("response of company id {}:".format(company_id), "success" if response else "failed")
    else:
        response = get_equipment_list(company_id)
        print("response of company id {}:".format(company_id), "success" if response else "failed")

    generated_response = generate_llm_response(response, query)
    print("generated_response :", generated_response)
    return {
        "function_called": function_name,
        "generated_response": generated_response
    }

def handle_generic_query(function_name: str, parameters: Dict, query: str) -> Dict[str, Any]:
    """Handle generic function calls."""
    from retrever import call_function_by_name
    response = call_function_by_name(function_name, parameters)
    print("response :", "success" if response else "failed")
    generated_response = generate_llm_response(response, query)
    print("generated_response :", generated_response)
    return {
        "function_called": function_name,
        "generated_response": generated_response
    }

