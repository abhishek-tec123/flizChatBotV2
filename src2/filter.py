def filter_company_info(data):
    """Filter essential company info for company list responses."""
    keys = [
        "_id", "uniqueId", "name", "company_rating", "city", "role", "totalAvailable_Equipments_quantity","company_description","address"
    ]
    if not data or not isinstance(data, dict) or not data.get("data") or not data["data"].get("itemList"):
        return {"totalCount": 0, "items": []}
    
    key_summary = {
        "totalCount": data["data"].get("totalCount", 0),
        "items": []
    }
    for item in data["data"]["itemList"]:
        filtered = {k: item.get(k) for k in keys if k in item}
        key_summary["items"].append(filtered)
    return key_summary

def filter_company_assets_keys(company_type, raw_data):
    """Filter and format essential asset details for chatbot use (no image, includes totalCount)."""
    if not raw_data or "data" not in raw_data:
        return {"company": {}, "assets": [], "totalCount": 0}

    company_details = raw_data["data"].get("companyDetails", {})
    item_list = raw_data["data"].get("itemList", [])
    total_count = raw_data["data"].get("totalCount", 0)

    company_info = {
        "company_id": company_details.get("_id"),
        "company_name": company_details.get("name"),
    }

    assets = []

    for item in item_list:
        if company_type == "get_renter_companies":
            equip = item.get("equipmentDetails", {})
            asset = {
                "company_id": company_info["company_id"],
                "equipment_id": equip.get("_id"),
                "company_name": company_info["company_name"],
                "equipment_name": equip.get("equipmentName"),
                "address": item.get("address"),
                "city": item.get("city"),
                "price_per_day": equip.get("equipmentPrice_perDay"),
                "available_quantity": equip.get("available_equipments"),
            }
        else:  # get_delivery_companies (assuming similar structure)
            vehicle = item.get("vehicleDetails", {})
            asset = {
                "company_id": company_info["company_id"],
                "vehicle_id": vehicle.get("_id"),
                "vehicle_name": company_info["company_name"],
                "equipment_name": vehicle.get("sizeType"),
                "address": item.get("address"),
                "city": item.get("city"),
                "price_per_day_inside_city": vehicle.get("priceInside_city_perDay"),
                "price_per_day_outside_city": vehicle.get("priceInoutSide_city_perKm"),
                "isPriceBreaking": vehicle.get("isPriceBreaking"),
                "available_quantity": vehicle.get("available_trucks"),
            }

        assets.append(asset)

    return {
        "company": company_info,
        "assets": assets,
        "totalCount": total_count
    }

def filter_all_asset_details_from_company_id(item, company_type, company_details=None):
    """
    Filter and format a single asset's details for chatbot use.

    :param item: One item from data['itemList']
    :param company_type: 'get_renter_companies' or 'get_delivery_companies'
    :param company_details: The parent company details (needed for vehicle assets)
    :return: dict with simplified asset details
    """
    if company_type == "get_renter_companies":
        asset = item.get("equipmentDetails", {})
        return {
            "company_id": asset.get("companyProviderId"),
            "equipment_id": asset.get("_id"),
            "company_name": company_details.get("name") if company_details else None,
            "equipment_name": asset.get("equipmentName"),
            "address": item.get("address"),
            "city": item.get("city"),
            "price_per_day": asset.get("equipmentPrice_perDay"),
            "available_quantity": asset.get("available_equipments"),
            "price_options": {
                "per_week": asset.get("equipmentPrice_1_week"),
                "per_month": asset.get("equipmentPrice_1_month")
            },
            "instalments": asset.get("price_perDay_with_instalment", {}),
            "is_active": asset.get("isActive", False),
            "is_delivery_included": asset.get("isDeliveryInclude", False),
        }

    elif company_type == "get_delivery_companies":
        asset = item.get("vehicleDetails", {})
        return {
            "company_id": asset.get("company_deliveryId"),
            "vehicle_id": asset.get("_id"),
            "company_name": company_details.get("name") if company_details else None,
            "vehicle_name": asset.get("sizeType"),
            "address": item.get("address"),
            "city": item.get("city"),
            "price_per_day": asset.get("priceInside_city_perDay"),
            "price_per_km_outside": asset.get("priceInoutSide_city_perKm"),
            "available_quantity": asset.get("available_trucks"),
            "is_repeating_delivery": asset.get("isRepeatingDelivery"),
            "repeating_delivery_amount": asset.get("repeatingDeliveryAmount"),
            "is_active": asset.get("isApproved", False),
            "is_price_breaking": asset.get("isPriceBreaking", False),
        }

    return {}

def filter_equipment_details(data):
    equipment = data.get("data")
    if not equipment:
        return None

    address = equipment.get("equipmentAddress", {})
    one_week_installments = equipment.get("price_1_week_with_instalment", {})
    one_month_installments = equipment.get("price_1_month_with_instalment", {})

    return {
        "id": equipment.get("_id"),
        "uniqueId": equipment.get("uniqueId"),
        "name": equipment.get("equipmentName"),
        "price": {
            "perDay": equipment.get("equipmentPrice_perDay"),
            "oneWeek": equipment.get("equipmentPrice_1_week"),
            "oneMonth": equipment.get("equipmentPrice_1_month"),
        },
        "location": address.get("address", "Not specified"),
        "city": address.get("city", ""),
        "state": address.get("state", ""),
        "country": address.get("country", ""),
        "isDeliveryIncluded": equipment.get("isDeliveryInclude", False),
        "isPriceBreaking": equipment.get("isPriceBreaking", False),
        "taxPercent": equipment.get("tax", 0),
        "availableQuantity": equipment.get("available_equipments", 0),
        "isInstallmentAvailable": {
            "oneWeek": one_week_installments.get("enable_instalments", False),
            "oneMonth": one_month_installments.get("enable_instalments", False),
        }
    }


def filter_vehicle_details(data):
    vehicle = data.get("data")
    if not vehicle:
        return None

    address = vehicle.get("address_details", {})

    return {
        "id": vehicle.get("_id"),
        "uniqueId": vehicle.get("uniqueId"),
        "type": vehicle.get("type"),
        "sizeType": vehicle.get("sizeType"),
        "loadingCapacity": vehicle.get("loadingCapacity"),
        "price": {
            "insideCityPerDay": vehicle.get("priceInside_city_perDay", 0),
            "outsideCityPerKm": vehicle.get("priceInoutSide_city_perKm", 0),
        },
        "location": address.get("address", "Not specified"),
        "city": address.get("city", ""),
        "state": address.get("state", ""),
        "country": address.get("country", ""),
        "isPriceBreaking": vehicle.get("isPriceBreaking", False),
        "availableTrucks": vehicle.get("available_trucks", 0),
        "totalTrucks": vehicle.get("total_trucks", 0),
    }