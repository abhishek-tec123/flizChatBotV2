from api_function2 import (
    get_booking_list,
    get_usr_favourite_list,
    company_cat_list,
)
from usr_filter import(
    filter_category_details_key,
    filter_favourite_equipments_key,
    filter_favourite_usr_companies_key,
    filter_user_orders_key,
    # filter_booking_data
)
def get_user_booking_list(ststus):
    normalized_status = ststus.lower()
    if normalized_status == "completed":
        data = get_booking_list(status="Completed")
        # filter_data = filter_booking_data(data)
    elif normalized_status == "cancelled":
        data = get_booking_list(status="Cancelled")
        # filter_data = filter_booking_data(data)
    else:
        data = get_booking_list(status=None)
    return data

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
    """
    Calls the appropriate user utility function based on the function name.
    Args:
        function_name (str): The name of the function to call.
        arg: The argument to pass to the function (if needed).
    Returns:
        The result of the called function.
    """
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


# anns = call_user_function("get_usr_favourite_list", "vehicle")
# print(anns)
# ans = call_user_function("company_cat_list",'Excavators')
# print(ans)