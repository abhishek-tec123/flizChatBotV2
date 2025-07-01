# from typing import List, Dict, Optional, Tuple

# # --- Your existing functions ---

# def extract_entity_details(query: str, entity_type: str) -> Tuple[Optional[str], Optional[str]]:
#     """Extract company name and entity type from query."""
#     query_lower = query.lower()
#     prefix = f"show {entity_type} details of "
    
#     if prefix not in query_lower:
#         return None, None
        
#     remaining = query_lower.replace(prefix, "").strip()
#     entity_name = None
#     company_name = None
    
#     for separator in [" of ", " from ", " in "]:
#         if separator in remaining:
#             parts = remaining.split(separator)
#             if len(parts) >= 2:
#                 entity_name = parts[0].strip()
#                 company_name = " ".join(parts[1:]).strip()
#                 break
    
#     if company_name:
#         company_name = company_name.replace("company", "").strip()
    
#     return entity_name, company_name


# def find_entity_by_type(entity_list: List[Dict], entity_type: str, is_vehicle: bool) -> Optional[str]:
#     """Find entity ID by type in the entity list."""
#     for entity in entity_list:
#         details = entity.get("vehicleDetails" if is_vehicle else "equipmentDetails", {})
#         if details:
#             name_field = "sizeType" if is_vehicle else "equipmentName"
#             if entity_type.lower() in details.get(name_field, "").lower():
#                 return details.get("_id")
#     return None

# # --- Main function that uses the above ---

# def main():
#     # Example query from user
#     user_query = "Show vehicle details of mini truck from DHL company"
#     entity_type = "vehicle"

#     # Step 1: Extract entity name and company name from query
#     entity_name, company_name = extract_entity_details(user_query, entity_type)
#     print("Extracted entity:", entity_name)
#     print("Extracted company:", company_name)

#     # Step 2: Simulate a list of vehicles
#     vehicle_list = [
#         {
#             "vehicleDetails": {
#                 "_id": "veh001",
#                 "sizeType": "Mini Truck"
#             }
#         },
#         {
#             "vehicleDetails": {
#                 "_id": "veh002",
#                 "sizeType": "Container Truck"
#             }
#         }
#     ]

#     # Step 3: Find the matching entity ID
#     entity_id = find_entity_by_type(vehicle_list, entity_name, is_vehicle=True)
    
#     if entity_id:
#         print(f"✅ Found entity ID: {entity_id}")
#     else:
#         print("❌ No matching entity found.")

# # Run the main function
# if __name__ == "__main__":
#     main()


file = open("/Users/abhishek/Desktop/flizChatBot/src/function.txt", "rb")
file.seek(10)
file.seek(10, 1)
file.seek(50, 0)
content = file.read()
print("File content:", content.decode('utf-8'))
file.close()
