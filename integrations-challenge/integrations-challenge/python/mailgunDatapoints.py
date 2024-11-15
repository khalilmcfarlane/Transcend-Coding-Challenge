import requests
import re

# The api key
MAILGUN_API_KEY = 'NOT_REAL'
# The api username
USERNAME = 'api'
# Set timeout for api requests
TIMEOUT = 30
# Mailgun's URL
URL = "https://api.mailgun.net/v3/lists"


# create mailing lists and seed users into them
def seed(identifier, scope_url,  mailing_list):
    """
    Add user to mailing list.

    :param str identifier: User Email Address.
    :param str mailing_list: Full URL for Add Member API.
    API to add member to mailing list referenced here:
    https://documentation.mailgun.com/docs/mailgun/api-reference/openapi-final/tag/Mailing-Lists/#tag/Mailing-Lists/operation/post-lists-string:list_address-members
    """

    # Add logging for address and mailing list
    print(f"Adding {identifier} to {mailing_list}.")
    add_member_url = f"{scope_url}/v3/lists/{mailing_list}/members"
    # Add query parameters
    params = {
        "address": identifier,
        "upsert": "yes"
    }
    headers = {"Content-Type": "multipart/form-data"}

    try:
        response = requests.post(add_member_url, auth=(USERNAME, MAILGUN_API_KEY), params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(data)

    except requests.exceptions.RequestException as error:
        print(f"Error connecting to {URL}: {error}")


def extract_mailing_list(url):
    # Regex to capture the mailing list address between /lists/ and /members
    match = re.search(r"(?<=/lists/)[^/]+", url)
    if match:
        return match.group(0)
    else:
        return None


def access(identifier):
    """
    Return all the mailing lists the user belongs to.
    Get mailing lists per user API:
    https://documentation.mailgun.com/docs/mailgun/api-reference/openapi-final/tag/Mailing-Lists/#tag/Mailing-Lists
    /operation/get-v3-lists-pages :param str identifier: email address :return: List of addresses
    """

    # Set email address as query parameter.
    params = {
        "address": identifier,
    }
    mailing_list_url = URL + "/pages"
    try:
        response = requests.get(mailing_list_url, auth=(USERNAME, MAILGUN_API_KEY), params=params, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(f"Error connecting to {URL}: {error}")

    data = response.json()
    items = data["items"]

    # Parse addresses from mailing lists
    address_list = get_addresses_from_mailing_list(items)
    return address_list


def get_addresses_from_mailing_list(mailing_list):
    """
    Return a list of address from a mailing list.
    """
    address_list = [entry["address"] for entry in mailing_list if "address" in entry]
    return address_list


# remove the user from all mailing lists
def erasure(identifier, context):
    """
    Remove email address from all Mailgun mailing lists.
    Context is list of mailing lists to delete user from.
    Delete member from mailing list API:
    https://documentation.mailgun.com/docs/mailgun/api-reference/openapi-final/tag/Mailing-Lists/#tag
    /Mailing-Lists/operation/delete-lists-list_address-members-member_address
    """

    for address in context:
        delete_member_url = f"{URL}/{address}/members/{identifier}"
        print(f"Removing {identifier} from {address} mailing list.")

        try:
            response = requests.delete(delete_member_url, auth=(USERNAME, MAILGUN_API_KEY), timeout=TIMEOUT)
            response.raise_for_status()
            print(response.json())
        except requests.exceptions.RequestException as error:
            print(f"Error connecting to {URL}: {error}")
