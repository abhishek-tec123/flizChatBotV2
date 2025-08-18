import requests

# ==== Configuration ====
BASE_URL = "https://dev.api.fliz.com.sa"

# Authentication Tokens
TOKENS = {
    "guest": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY4MjVkN2M5N2U3ZWY5ZTBmOTkxNWY0ZiIsInJvbGUiOiJ1c2VyIiwiaWF0IjoxNzU1NTE2MTAxLCJleHAiOjE3NTU5NDgxMDF9.kZYtgnn3BVPsMDoM90fMmqMNedUt7NAQr_GC1S9IgFs",
    "user": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY4MjVkN2M5N2U3ZWY5ZTBmOTkxNWY0ZiIsInJvbGUiOiJ1c2VyIiwiaWF0IjoxNzU1NTE2MTAxLCJleHAiOjE3NTU5NDgxMDF9.kZYtgnn3BVPsMDoM90fMmqMNedUt7NAQr_GC1S9IgFs"
}

ENDPOINTS = {
    "delivery_list": "/api/v1/user/home/renter_deliveryList",
    "vehicle_list": "/api/v1/user/home/vehilceList/{}",
    "equipment_list": "/api/v1/user/home/equipmentList/{}",
    "equipment_details": "/api/v1/user/home/equipmentDetails/{}",
    "vehicle_details": "/api/v1/user/home/vehicleDetails/{}",
    "user_profile_details": "/api/v1/user/profile/details",
    "payment_list": "/api/v1/common/payment/paymentList",
    "favourite_list": "/api/v1/user/favourite/fav_list",
    "booking_list": "/api/v1/user/booking/bookingList",
    "company_cat_list": "/api/v1/user/home/renterCompanyData",
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
        print(f"Request to {url} - Status Code: {response.status_code}")
        if response.status_code == 451:
            print("Warning: API returned 451 - Unavailable For Legal Reasons. This might be due to geographic restrictions or legal compliance issues.")
            return None
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error: {err}")
        if err.response.status_code == 451:
            print("The API is currently unavailable due to legal restrictions. Please check your location or try again later.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
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

def get_renter_companies(role="renter", search=None, page=1, per_page=15):
    url = BASE_URL + ENDPOINTS["delivery_list"]
    params = {
        "role": role,
        "page": page,
        "perPage": per_page
    }
    if search:
        params["search"] = search

    return make_request(url, params=params, token_type="guest")

def company_cat_list(cat_search=None):
    """
    Get renter company data for authenticated user with optional catSearch.
    This always uses role='renter', page=1, and perPage=18.
    Equivalent to:
    requests.get(
        "https://dev.api.fliz.com.sa/api/v1/user/home/renterCompanyData?role=renter&page=1&perPage=18&catSearch=Excavators",
        headers={"Authorization": "<user_token>"}
    )
    """
    url = BASE_URL + ENDPOINTS["company_cat_list"]
    params = {
        "role": "renter",
        "page": 1,
        "perPage": 18
    }
    if cat_search:
        params["catSearch"] = cat_search
    return make_request(url, params=params, method="GET", token_type="user")

def get_vehicle_list(company_id):
    url = BASE_URL + ENDPOINTS["vehicle_list"].format(company_id)
    return make_request(url, token_type="guest")

def get_equipment_list(company_id):
    url = BASE_URL + ENDPOINTS["equipment_list"].format(company_id)
    return make_request(url, token_type="guest")

def get_equipment_details(equipment_id):
    url = BASE_URL + ENDPOINTS["equipment_details"].format(equipment_id)
    return make_request(url, token_type="guest")

def get_vehicle_details(vehicle_id):
    url = BASE_URL + ENDPOINTS["vehicle_details"].format(vehicle_id)
    return make_request(url, token_type="guest")

# ==== Authenticated User API Functions ====
def get_booking_list(page=1, per_page=100, status=""):
    url = BASE_URL + ENDPOINTS["booking_list"]
    params = {
        "page": page,
        "perPage": per_page,
        "status": status
    }
    return make_request(url, params=params, token_type="user")

def get_user_profile_details():
    """Get the authenticated user's profile details."""
    url = BASE_URL + ENDPOINTS["user_profile_details"]
    return make_request(url, method="GET", token_type="user")

def get_payment_list(role="user", page=1, per_page=10, search="", start_date="", end_date=""):
    """Get the payment list for the authenticated user."""
    url = BASE_URL + ENDPOINTS["payment_list"]
    params = {
        "role": role,
        "page": page,
        "perPage": per_page,
        "search": search,
        "startDate": start_date,
        "endDate": end_date
    }
    return make_request(url, params=params, method="GET", token_type="user")

def get_usr_favourite_list(type="company", page=1, per_page=100):
    """Get the favourite list for the authenticated user. Type can be 'company', 'vehicle', or 'equipment'."""
    url = BASE_URL + ENDPOINTS["favourite_list"]
    params = {
        "type": type,
        "page": page,
        "perPage": per_page
    }
    return make_request(url, params=params, method="GET", token_type="user")

# ==== Main Function ====
if __name__ == "__main__":
    # Example usage of the functions
    delivery_companies = get_delivery_companies(page=1, per_page=3)
    if delivery_companies and 'data' in delivery_companies:
        print(delivery_companies['data']['itemList'])
    else:
        print("No delivery companies returned (possible legal restriction or 451 error).")

    # print("\n--- Renter Companies ---")
    # renter_companies = get_renter_companies(page=1, per_page=3)
    # print(renter_companies)

    # print("\n--- Vehicle Details ---")
    # vehicle_details = get_vehicle_details("6825f680064c919c60d06988")
    # print(vehicle_details)

    # print("\n--- Equipment Details ---")
    # equipment_details = get_equipment_details("682c6da5cd7a35d99f0b889a")
    # print(equipment_details)

    # print("\n--- Completed Bookings ---")
    # completed_bookings = get_booking_list(status="Completed")
    # print(completed_bookings)
# result = company_cat_list(cat_search="Excavators")
# print(result)