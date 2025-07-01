import requests

# ==== Configuration ====
BASE_URL = "https://dev.api.fliz.com.sa"

# Authentication Tokens
TOKENS = {
    "guest": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY4NDY4MmQ3ODQ4ZjI2NmE0ZDUwNGE1NiIsInJvbGUiOiJndWVzdF91c2VyIiwiaWF0IjoxNzQ5NDUxNDc5LCJleHAiOjE3NTIwNDM0Nzl9.ePU8pFs6RQ4qeTuvu8BzvORx3oCXiVGi4CwotV1E3TE",
    "user": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY4MjVkN2M5N2U3ZWY5ZTBmOTkxNWY0ZiIsInJvbGUiOiJ1c2VyIiwiaWF0IjoxNzQ3NzQxNjU0LCJleHAiOjE3NDgxNzM2NTR9.mYE3kIqsf0-GkiLpRi7DpVZi6r8J25uLfmNvTC0YRHE"
}

ENDPOINTS = {
    "delivery_list": "/api/v1/common/guestUser/renter_deliveryList",
    "vehicle_list": "/api/v1/common/guestUser/vehilceList/{}",
    "equipment_list": "/api/v1/common/guestUser/equipmentList/{}",
    "booking_list": "/api/v1/user/booking/bookingList",
    "vehicle_details": "/api/v1/common/guestUser/vehicleDetails/{}",
    "equipment_details": "/api/v1/common/guestUser/equipmentDetails/{}"
}

COMMON_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'If-None-Match': 'W/"239c-x535R61dfiPcPeQlSRaNpyqK92U"',
    'Origin': 'http://dev.fliz.com.sa',
    'Referer': 'http://dev.fliz.com.sa/',
    'deviceType': 'web',
    'language': 'en',
    'timezone': 'Asia/Calcutta'
}

# ==== Helper Functions ====
def get_headers(token_type="guest"):
    """Get headers with the specified token type."""
    headers = COMMON_HEADERS.copy()
    headers['Authorization'] = TOKENS[token_type]
    return headers

def make_request(url, method="GET", headers=None, params=None, token_type="guest"):
    """Make an HTTP request with error handling."""
    if headers is None:
        headers = get_headers(token_type)
    
    try:
        response = requests.request(method, url, headers=headers, params=params)
        print(f"Request to {url} - Status Code:", response.status_code)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print("HTTP error:", err)
    except Exception as e:
        print("An error occurred:", e)
    return None

# ==== Guest User API Functions ====
def get_delivery_companies(page=1, per_page=10, search=None, cat_id=None, type=None, sizeTypetype=None):
    url = BASE_URL + ENDPOINTS["delivery_list"]
    params = {
        "role": "delivery",
        "page": page,
        "perPage": per_page
    }
    if search:
        params["search"] = search
    if cat_id:
        params["catId"] = cat_id
    if type:
        params["type"] = type
    if sizeTypetype:
        params["sizeTypetype"] = sizeTypetype

    return make_request(url, params=params, token_type="guest")

def get_renter_companies(role="renter", search=None, page=1, per_page=10):
    url = BASE_URL + ENDPOINTS["delivery_list"]
    params = {
        "role": role,
        "page": page,
        "perPage": per_page
    }
    if search:
        params["search"] = search

    return make_request(url, params=params, token_type="guest")

def get_vehicle_list(company_id):
    url = BASE_URL + ENDPOINTS["vehicle_list"].format(company_id)
    return make_request(url, token_type="guest")

def get_equipment_list(company_id):
    url = BASE_URL + ENDPOINTS["equipment_list"].format(company_id)
    return make_request(url, token_type="guest")


# ==== Authenticated User API Functions ====
def get_booking_list(page=1, per_page=10, status="Completed"):
    url = BASE_URL + ENDPOINTS["booking_list"]
    params = {
        "page": page,
        "perPage": per_page,
        "status": status
    }
    return make_request(url, params=params, token_type="user")

def get_equipment_details(equipment_id):
    url = BASE_URL + ENDPOINTS["equipment_details"].format(equipment_id)
    return make_request(url, token_type="guest")

def get_vehicle_details(vehicle_id):
    url = BASE_URL + ENDPOINTS["vehicle_details"].format(vehicle_id)
    return make_request(url, token_type="guest")

# ==== Main Function ====
# if __name__ == "__main__":
# #     # Example usage of the functions
#     print("\n--- Delivery Companies ---")
#     delivery_companies = get_delivery_companies(page=1, per_page=3)
#     print(delivery_companies['data']['itemList'])

#     print("\n--- Renter Companies ---")
#     renter_companies = get_renter_companies(page=1, per_page=3)
#     print(renter_companies)

#     print("\n--- Vehicle Details ---")
#     vehicle_details = get_vehicle_details("6825f680064c919c60d06988")
#     print(vehicle_details)

#     print("\n--- Completed Bookings ---")
#     completed_bookings = get_booking_list(status="Completed")
#     print(completed_bookings)
