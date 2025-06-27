import json
from typing import Dict, List, Optional, Tuple, Any
from fastapi import HTTPException
from context import process_full_api_response
from retrever import (
    get_vehicle_list, get_equipment_list,
    get_delivery_companies, get_renter_companies
)

def get_delivery_company_names(full_response):
    if not full_response:
        return []
    item_list = full_response.get("data", {}).get("itemList", [])
    return [company['name'] for company in item_list]

def get_rental_company_names(full_response):
    if not full_response:
        return []
    item_list = full_response.get("data", {}).get("itemList", [])
    return [company['name'] for company in item_list]

# Cache for company data to avoid repeated API calls
_delivery_companies_cache = None
_rental_companies_cache = None
_delivery_company_names_cache = None
_rental_company_names_cache = None

def get_cached_delivery_companies():
    """Get delivery companies with caching to avoid repeated API calls."""
    global _delivery_companies_cache, _delivery_company_names_cache
    
    if _delivery_companies_cache is None:
        try:
            _delivery_companies_cache = get_delivery_companies(page=1, per_page=100)
            _delivery_company_names_cache = get_delivery_company_names(_delivery_companies_cache)
        except Exception as e:
            print(f"Error fetching delivery companies: {e}")
            _delivery_companies_cache = None
            _delivery_company_names_cache = []
    
    return _delivery_companies_cache, _delivery_company_names_cache

def get_cached_rental_companies():
    """Get rental companies with caching to avoid repeated API calls."""
    global _rental_companies_cache, _rental_company_names_cache
    
    if _rental_companies_cache is None:
        try:
            _rental_companies_cache = get_renter_companies(page=1, per_page=100)
            _rental_company_names_cache = get_rental_company_names(_rental_companies_cache)
        except Exception as e:
            print(f"Error fetching rental companies: {e}")
            _rental_companies_cache = None
            _rental_company_names_cache = []
    
    return _rental_companies_cache, _rental_company_names_cache

def generate_llm_response(response_data: Dict, query: str) -> str:
    """Generate response using Groq LLM."""
    try:
        response_text = json.dumps(response_data, indent=3)
        return process_full_api_response(response_text, query=query)
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

def handle_company_based_query(function_name: str, company_name: str, query: str) -> Dict[str, Any]:
    """Handle queries that require company lookup."""
    company_list, company_type = get_company_list(function_name, company_name)
    print("company_list :", "success" if company_list else "failed")
    
    company_id = find_company_by_name(company_list, company_name)
    print("company_id :", company_id)

    if not company_id:
        if function_name == "get_vehicle_list":
            _, available_companies = get_cached_delivery_companies()
        else:  # get_equipment_list
            _, available_companies = get_cached_rental_companies()

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


def handle_vehicle_details(query: str) -> Dict[str, Any]:
    """Handle vehicle details queries."""
    vehicle_type, company_name = extract_entity_details(query, "vehicle")
    
    if not company_name or not vehicle_type:
        raise HTTPException(
            status_code=400,
            detail="Could not extract company name and vehicle type from query. Please use format: 'show vehicle details of [vehicle type] of/from/in [company name]'"
        )

    company_list, _ = get_company_list("get_vehicle_list", company_name)
    company_id = find_company_by_name(company_list, company_name)
    print("company_id :", company_id)
    if not company_id:
        available_companies = [c.get("name") for c in company_list]
        raise HTTPException(
            status_code=404,
            detail=f"Company '{company_name}' not found. Available companies: {available_companies}"
        )

    vehicle_list_response = get_vehicle_list(company_id)
    vehicle_list = vehicle_list_response.get("data", {}).get("itemList", [])
    vehicle_id = find_entity_by_type(vehicle_list, vehicle_type, is_vehicle=True)
    print("vehicle_id :", vehicle_id)
    if not vehicle_id:
        raise HTTPException(
            status_code=404,
            detail=f"Vehicle type '{vehicle_type}' not found in company '{company_name}'."
        )

    from api_function import get_vehicle_details
    response = get_vehicle_details(vehicle_id)
    generated_response = generate_llm_response(response, query)
    
    return {
        "function_called": "get_vehicle_details",
        "generated_response": generated_response
    }

def handle_equipment_details(query: str) -> Dict[str, Any]:
    """Handle equipment details queries."""
    equipment_type, company_name = extract_entity_details(query, "equipment")
    
    if not company_name or not equipment_type:
        raise HTTPException(
            status_code=400,
            detail="Could not extract company name and equipment type from query. Please use format: 'show equipment details of [equipment type] of/from/in [company name]'"
        )

    company_list, _ = get_company_list("get_equipment_list", company_name)
    company_id = find_company_by_name(company_list, company_name)
    print("company_id :", company_id)
    if not company_id:
        available_companies = [c.get("name") for c in company_list]
        raise HTTPException(
            status_code=404,
            detail=f"Company '{company_name}' not found. Available companies: {available_companies}"
        )

    equipment_list_response = get_equipment_list(company_id)
    equipment_list = equipment_list_response.get("data", {}).get("itemList", [])
    equipment_id = find_entity_by_type(equipment_list, equipment_type, is_vehicle=False)
    print("equipment_id :", equipment_id)
    if not equipment_id:
        available_equipment = [e.get("equipmentDetails", {}).get("equipmentName", "") for e in equipment_list]
        raise HTTPException(
            status_code=404,
            detail=f"Equipment '{equipment_type}' not found in company '{company_name}'. Available equipment: {available_equipment}"
        )

    from api_function import get_equipment_details
    response = get_equipment_details(equipment_id)
    generated_response = generate_llm_response(response, query)
    
    return {
        "function_called": "get_equipment_details",
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