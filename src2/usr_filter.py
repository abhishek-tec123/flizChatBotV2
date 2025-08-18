def filter_category_details_key(data):
    if not data or not isinstance(data, dict):
        return []
    filtered_items = []

    for item in data.get("data", {}).get("itemList", []):
        # Extract all company details as-is
        company_info = {key: value for key, value in item.items() if key != "categoryDetails"}

        # Keep only required fields in categoryDetails
        category = item.get("categoryDetails", {})
        filtered_category = {
            "_id": category.get("_id"),
            "name": category.get("name"),
            "ar_name": category.get("ar_name")
        }

        # Combine both
        company_info["categoryDetails"] = filtered_category
        filtered_items.append(company_info)

    return filtered_items

def filter_favourite_equipments_key(data):
    filtered_items = []

    for item in data.get("data", {}).get("itemList", []):
        equipment = item.get("equipmentDetails", {})
        address = equipment.get("equipmentAddress", {})

        filtered_item = {
            "_id": item.get("_id"),
            "equipmentId": item.get("equipmentId"),
            "companyId": item.get("companyId"),
            "equipmentDetails": {
                "equipmentName": equipment.get("equipmentName"),
                "equipmentPrice_perDay": equipment.get("equipmentPrice_perDay"),
                "equipmentAddress": {
                    "address": address.get("address"),
                    "city": address.get("city")
                }
            }
        }

        filtered_items.append(filtered_item)

    return filtered_items

def filter_favourite_usr_companies_key(api_response):
    result = []

    item_list = api_response.get("data", {}).get("itemList", [])

    for item in item_list:
        company = item.get("companyDetails", {})
        result.append({
            "company_id": company.get("_id"),
            "company_name": company.get("name"),
            "address": company.get("address"),
            "city": company.get("city"),
            "country": company.get("country"),
            "description": company.get("company_description"),
            "rating": company.get("company_rating"),
            "min_equipment_price": company.get("minEquipmentPrice"),
            "available_equipments": company.get("available_equipments"),
            # "image": company.get("image"),
            # "banner_image": company.get("bannerImage"),
            "is_verified": company.get("isVerified"),
        })

    return result



from typing import Dict, Any, List, Union

def filter_user_orders_key(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
    filtered_list = []

    # Case 1: API response with {"data": {"itemList": [...]}}
    if isinstance(data, dict):
        items = data.get("data", {}).get("itemList", [])
        total_count = data.get("data", {}).get("totalCount", len(items))
    # Case 2: Already a list of items
    elif isinstance(data, list):
        items = data
        total_count = len(items)
    else:
        return {"totalCount": 0, "bookings": []}

    for item in items:
        filtered_item = {
            "_id": item.get("_id"),
            "orderId": item.get("orderId"),
            # "invoiceNumber": item.get("invoiceNumber"),
            "bookingStatus": item.get("bookingStatus"),
            "transport_cost": item.get("transport_cost"),
            "totalAmount": item.get("totalAmount"),
            "paidAmount": item.get("paidAmount"),
            "remaining_amount": item.get("remaining_amount"),
            # # Vehicle details
            # "vehicleType": item.get("vehicleDetails", {}).get("vehicleType"),
            # "vehicleSize": item.get("vehicleDetails", {}).get("vehicleSize"),
            # "vehiclePricePerDay": item.get("vehicleDetails", {}).get("priceInside_city_perDay"),
            # # Equipment details
            # "equipmentDayCost": item.get("equipmentDetails", {}).get("day_cost"),
            # "equipmentDeliveryIncluded": item.get("equipmentDetails", {}).get("deliveryIncluded"),
            # # Addresses
            # "pickupAddress": item.get("pickup_addressDetails", {}).get("address"),
            # "deliveryAddress": item.get("delivery_addressDetails", {}).get("address"),
            # # Company
            # "companyName": item.get("companyDetails", {}).get("name"),
            # Price Breaking
            # "priceBreaking_details": [
            #     {
            #         "amount": p.get("amount"),
            #         "paymentDate": p.get("paymentDate"),
            #         "paymentTime": p.get("paymentTime"),
            #         "paid": p.get("paid"),
            #     } for p in item.get("priceBreaking_details", [])
            # ],
        }

        filtered_list.append(filtered_item)

    return {
        "totalCount": total_count,
        # "bookings": filtered_list
    }
