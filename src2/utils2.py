from typing import Dict, List, Optional, Tuple, Any

from api_function2 import (
    get_delivery_companies,
    get_renter_companies,
    get_vehicle_list,
    get_equipment_list,
    get_vehicle_details,
    get_equipment_details
)

from filter import (
    filter_company_assets_keys,
    filter_all_asset_details_from_company_id,
    filter_company_info,
    filter_equipment_details,
    filter_vehicle_details
)


def get_companies_list(company_type):
    if company_type == "get_delivery_companies":
        return get_delivery_companies()
    elif company_type == "get_renter_companies":
        return get_renter_companies()
    else:
        raise ValueError("Invalid company_type. Use 'get_delivery_companies' or 'get_renter_companies'.")


def find_company_by_name(company_type, target_name):
    if not target_name or not isinstance(target_name, str):
        return None
    raw_data = get_companies_list(company_type)
    filtered_data = filter_company_info(raw_data)

    for item in filtered_data["items"]:
        if item.get("name", "").lower() == target_name.lower():
            return item
    return None


def get_vehicle_list_for_company(company_id):
    return get_vehicle_list(company_id)


def get_equipment_list_for_company(company_id):
    return get_equipment_list(company_id)


def get_company_assets_from_company_id(company_type, company_id):
    """Call the appropriate asset fetcher based on company_type."""
    if company_type == "get_delivery_companies":
        return get_vehicle_list_for_company(company_id)
    elif company_type == "get_renter_companies":
        return get_equipment_list_for_company(company_id)
    else:
        raise ValueError("Invalid company_type.")


def get_single_asset_details_from_asset_id(company_type, company_id, asset_id):
    """Get full asset details using company_id and asset_id."""
    if company_type == "get_delivery_companies":
        return get_vehicle_details(company_id, asset_id)
    elif company_type == "get_renter_companies":
        return get_equipment_details(company_id, asset_id)
    else:
        raise ValueError("Invalid company_type.")


def find_asset_by_name(company_type, target_name, asset_list):
    """
    Find an asset (equipment or vehicle) by name, using the provided asset_list.
    """
    if not asset_list or "data" not in asset_list or "itemList" not in asset_list["data"]:
        print("⚠️ No valid asset data found.")
        return None

    item_list = asset_list["data"]["itemList"]
    company_details = asset_list["data"].get("companyDetails", {})

    for item in item_list:
        asset_name = (
            item.get("equipmentDetails", {}).get("equipmentName", "")
            if company_type == "get_renter_companies"
            else item.get("vehicleDetails", {}).get("sizeType", "")
        )

        # Allow partial matches
        if target_name.lower() in asset_name.lower():
            return filter_all_asset_details_from_company_id(item, company_type, company_details)

    return None

def handle_company_asset_query(company_type: str, company_name: Optional[str] = None, asset_name: Optional[str] = None):
    # Case 1: Only company_type provided
    if not company_name and not asset_name:
        company_list = get_companies_list(company_type)
        filtered_companies = filter_company_info(company_list)
        return {"companies": filtered_companies}

    # Case 2: company_type and company_name provided
    company = find_company_by_name(company_type, company_name)
    if not company:
        return {"error": f"❌ Company '{company_name}' not found under type '{company_type}'."}

    if not asset_name:
        if company_type == "get_renter_companies":
            return {
                "company": company,
                "equipment_list": get_equipment_list_for_company(company["_id"])
            }
        elif company_type == "get_delivery_companies":
            return {
                "company": company,
                "vehicle_list": get_vehicle_list_for_company(company["_id"])
            }
        else:
            return {
                "company": company,
                "note": f"⚠ No asset list handler defined for company_type '{company_type}'."
            }

    # Case 3: All three provided
    assets = get_company_assets_from_company_id(company_type, company["_id"])
    if not assets or "data" not in assets or "itemList" not in assets["data"]:
        return {"error": f"❌ No assets found for company '{company_name}'."}

    filtered_assets = filter_company_assets_keys(company_type, assets)

    print(f"🔍 Searching for asset by name: '{asset_name}'...")

    asset = find_asset_by_name(company_type, asset_name, assets)
    if asset:
        asset_id = asset.get("equipment_id") or asset.get("vehicle_id")
        if asset_id:
            print(f"✅ Asset found with ID: {asset_id}")
        else:
            print("⚠ Asset found but ID missing.")
    else:
        print(f"❌ Asset '{asset_name}' not found.")

    if not asset:
        return {
            "company": company,
            "filtered_assets": filtered_assets,
            "error": f"❌ Asset '{asset_name}' not found under company '{company_name}'."
        }

    details = None
    if company_type == "get_renter_companies" and asset.get("equipment_id"):
        details = get_equipment_details(asset["equipment_id"])
        filter_details = filter_equipment_details(details)
        return {
            "company": company,
            "filtered_assets": filtered_assets,
            "equipment_details": filter_details
        }
    elif company_type == "get_delivery_companies" and asset.get("vehicle_id"):
        details = get_vehicle_details(asset["vehicle_id"])
        filter_details = filter_vehicle_details(details)
        return {
            "company": company,
            "filtered_assets": filtered_assets,
            "vehicle_details": filter_details
        }

    return {
        "company": company,
        "filtered_assets": filtered_assets,
    }


# ans = handle_company_asset_query("get_delivery_companies","Force Motors","Non-potable water tank")
# print(ans)
# def main():
#     company_type = "get_delivery_companies"  # or "get_delivery_companies"
#     company_name = "Force Motors"
#     asset_name = "Non-potable water tank"

#     company_list = get_companies_list(company_type)
#     # print("Company List : ",company_list)

#     company = find_company_by_name(company_type, company_name)

#     if not company:
#         print(f"❌ Company with name '{company_name}' not found under type '{company_type}'.")
#         return

#     print("✅ Company found:", company)

#     assets = get_company_assets_from_company_id(company_type, company["_id"])

#     if not assets or "data" not in assets or "itemList" not in assets["data"]:
#         print("❌ No assets found for this company.")
#         return

#     filtered_assets = filter_company_assets_keys(company_type, assets)
#     print(f"📦 Filtered assets for company '{company_name}' ({company_type}):")
#     print(filtered_assets)

#     assets = get_company_assets_from_company_id(company_type, company["_id"])
#     asset = find_asset_by_name(company_type, asset_name, assets)

#     if asset:
#         print(f"🔍 Asset found with name '{asset_name}':")
#         print(asset)
#     else:
#         print(f"❌ Asset with name '{asset_name}' not found.")


# if __name__ == "__main__":
#     main()
