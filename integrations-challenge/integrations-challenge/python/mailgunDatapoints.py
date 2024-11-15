import requests
import re

# The api key
MAILGUN_API_KEY = 'NOT_REAL'
# The api username
USERNAME = 'api'
# Set timeout for api requests
TIMEOUT = 60
# Mailgun's URL
MAILGUN_BASE_URL = "https://api.mailgun.net/v3/lists"


def extract_mailing_list(url):
    """
    :param str url: URL to extract the mailing list from.
    Regex to capture the mailing list address between /lists/ and /members
    :return: Mailing list address or None if not found.
    """
    match = re.search(r"(?<=/lists/)[^/]+", url)
    if match:
        return match.group(0)
    else:
        return None


def get_addresses_from_mailing_list(mailing_list):
    """
    Extract addresses from a mailing list.
    :param mailing_list: List of mailing list items.
    :return: List of addresses.
    """
    address_list = [entry["address"] for entry in mailing_list if "address" in entry]
    return address_list


def seed(identifier, scope_url, mailing_list):
    """
    Add user to a mailing list.
    :param str identifier: User's email address.
    :param str scope_url: The base URL scope.
    :param str mailing_list: Full URL for Add Member API.
    API to add member to mailing list referenced here:
    https://documentation.mailgun.com/docs/mailgun/api-reference/openapi-final/tag/Mailing-Lists/#tag/Mailing-Lists/operation/post-lists-string:list_address-members
    """

    # Log the user being added to the mailing list.
    print(f"Adding {identifier} to {mailing_list}.")
    add_member_url = f"{scope_url}/v3/lists/{mailing_list}/members"
    # Add query parameters
    params = {
        "address": identifier,
        "upsert": "yes"
    }
    headers = {"Content-Type": "multipart/form-data"}

    try:
        response = requests.post(add_member_url, auth=(USERNAME, MAILGUN_API_KEY), params=params, headers=headers,
                                 timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        print(data)

    except requests.exceptions.RequestException as error:
        print(f"Error connecting to {MAILGUN_BASE_URL}: {error}")


def access(identifier):
    """
    Return all the mailing lists the user belongs to.
    Get mailing lists per user API:
    https://documentation.mailgun.com/docs/mailgun/api-reference/openapi-final/tag/Mailing-Lists/#tag/Mailing-Lists
    /operation/get-v3-lists-pages :param str identifier: email address :return: List of addresses
    :param identifier: The user's email address.
    :return: List of mailing list addresses.
    """

    # Set email address as query parameter.
    params = {"address": identifier}
    mailing_list_url = MAILGUN_BASE_URL + "/pages"

    try:
        response = requests.get(mailing_list_url, auth=(USERNAME, MAILGUN_API_KEY), params=params, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        items = data["items"]

        # Parse mailing addresses from mailing lists.
        address_list = get_addresses_from_mailing_list(items)
        return address_list

    except requests.exceptions.RequestException as error:
        print(f"Error connecting to {MAILGUN_BASE_URL}: {error}")

    return []


def erasure(identifier, context):
    """
    Remove user from all provided mailing lists.
    Context is list of mailing lists to delete user from.
    Delete member from mailing list API:
    https://documentation.mailgun.com/docs/mailgun/api-reference/openapi-final/tag/Mailing-Lists/#tag
    /Mailing-Lists/operation/delete-lists-list_address-members-member_address
    :param identifier: The user's email address.
    :param context: List of mailing lists to remove the user from.
    """

    for address in context:
        delete_member_url = f"{MAILGUN_BASE_URL}/{address}/members/{identifier}"
        print(f"Removing {identifier} from {address} mailing list.")

        try:
            response = requests.delete(delete_member_url, auth=(USERNAME, MAILGUN_API_KEY), timeout=TIMEOUT)
            response.raise_for_status()
            print(response.json())
        except requests.exceptions.RequestException as error:
            print(f"Error connecting to {MAILGUN_BASE_URL}: {error}")
