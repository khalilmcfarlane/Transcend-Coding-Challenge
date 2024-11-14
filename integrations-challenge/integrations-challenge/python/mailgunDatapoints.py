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
def seed(add_member_url, identifier=None):
    """
    Add user to mailing list.

    :param str identifier: User Email Address.
    :param str add_member_url: Full URL for Add Member API.
    """

    """
    Set email address as query parameter.
    data = {
        "address": identifier,
        "upsert": "true"
    }
    headers = {"Content-Type": "multipart/form-data"}
    """
    # add_member_url = f"{add_member_url}//members"
    # Add logging for address and mailing list
    mailing_list = extract_mailing_list(add_member_url)
    print(f"Adding {identifier} to {mailing_list}.")
    try:
        response = requests.post(add_member_url, auth=(USERNAME, MAILGUN_API_KEY))
        data = response.json()
        print(data)
        # response = requests.post(add_member_url,
        # auth=(USERNAME, MAILGUN_API_KEY), data=data, headers=headers)
        response.raise_for_status()
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
    # for group in mailing_list:


# remove the user from all mailing lists
def erasure(identifier, context):
    """
    Remove email address from all Mailgun mailing lists.
    Context is API to delete member from specific mailing list
    Delete member from mailing list API:
    https://documentation.mailgun.com/docs/mailgun/api-reference/openapi-final/tag/Mailing-Lists/#tag
    /Mailing-Lists/operation/delete-lists-list_address-members-member_address
    """
    # for address in context["mailingLists"]:

    # delete_member_url = f"{URL}/{address}/members/{identifier}"
    # print(delete_member_url)
    # print(address)
    mailing_list = extract_mailing_list(context)
    print(f"Removing {identifier} from {mailing_list} mailing list.")
    try:
        response = requests.delete(context, auth=(USERNAME, MAILGUN_API_KEY))
        # response = requests.delete(delete_member_url, auth=(USERNAME, MAILGUN_API_KEY), timeout=TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(f"Error connecting to {URL}: {error}")

    print(response.json())
