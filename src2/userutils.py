from api_function2 import (
    get_booking_list,
    get_usr_favourite_list,
    company_cat_list,
    get_payment_list
)
from usr_filter import(
    filter_category_details_key,
    filter_favourite_equipments_key,
    filter_favourite_usr_companies_key,
    filter_user_orders_key,
    filter_user_payment_data
)
def get_user_booking_list(ststus: str | None):
    if not ststus:  # covers None or empty string
        # No status passed → return all bookings
        return get_booking_list(status=None)

    normalized_status = ststus.lower()
    if normalized_status == "completed":
        return get_booking_list(status="Completed")
    elif normalized_status == "cancelled":
        return get_booking_list(status="Cancelled")
    else:
        # If some unknown status, default to all
        return get_booking_list(status=None)


def get_favourite_list(type):
    if type == "company":
        data = get_usr_favourite_list(type="company")
        # print(data)
        filter_data = filter_favourite_usr_companies_key(data)
    elif type == "vehicle":
        data = get_usr_favourite_list(type="vehicle")
    elif type == "equipment":
        data = get_usr_favourite_list(type="equipment")
        # print(data)
        filter_data = filter_favourite_equipments_key(data)
    else:
        data = get_usr_favourite_list(type=None)
        # filter_data = filter_favourite_usr_companies_key(data)
    return data

def renter_company_category(cat):
    data = company_cat_list(cat_search=cat)
    filter = filter_category_details_key(data)
    return filter


def call_user_function(function_name, arg=None):

    if function_name == "get_booking_list":
        data =  get_user_booking_list(arg)
        filter_data = filter_user_orders_key(data)
        # print(filter_data)
        return filter_data
    elif function_name == "get_usr_favourite_list":
        data = get_favourite_list(type=arg)
        return data
    elif function_name == "company_cat_list":
        data = renter_company_category(arg)
        return data
    else:
        raise ValueError(f"Unknown function name: {function_name}")

def call_payment_list_fun(start_date: str, end_date: str):
    result = get_payment_list(start_date=start_date, end_date=end_date)
    filtered_res = filter_user_payment_data(result)
    return filtered_res

# anns = call_user_function("get_usr_favourite_list", "vehicle")
# print(anns)
# ans = call_user_function("company_cat_list",'Excavators')
# print(ans)