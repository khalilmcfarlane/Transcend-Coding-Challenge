import sys
import json
import mailgunDatapoints as dp
import requests_mock

# Modify this list to add the identifiers you want to use.
sample_identifiers_list = [
    "spongebob@transcend.io",
    "squidward@transcend.io",
    "patrick_star@transcend.io",
    "sandy_cheeks@transcend.io",
]


# The various action types.
class ActionType:
    # Fetch data for a given identifier
    # from the remote system, e.g. Mailgun.
    Access = "ACCESS"
    # Delete data for a given identifier
    # from the remote system.
    Erasure = "ERASURE"
    # Seed data into the remote system
    # creatine a profile with the given identifier.
    Seed = "SEED"


def verify_action_args(args):
    """
    Validate arguments.
    """
    valid_actions = [ActionType.Seed, ActionType.Erasure, ActionType.Access]
    if len(args) != 2:
        raise ValueError(
            "This module accepts a single argument: python3 runIntegration.py <action>, where <action> can be one of: "
            "{}".format(
                ", ".join(valid_actions)
            )
        )
    action = args[1]
    if action not in valid_actions:
        raise ValueError(
            "Action argument must be one of {}".format(", ".join(valid_actions))
        )
    return action


def run_integration(identifier, action_type):
    """
    Run the ACCESS and/or ERASURE flows for the given identifier.
    """
    print(f"Running access for {identifier}...\n")
    with requests_mock.Mocker() as m:
        with open(f"{ActionType.Access}.json") as fp:
            access_mocks = json.load(fp)
            for mock in access_mocks:
                m.register_uri(
                    mock["method"],
                    mock["scope"] + mock.get("path"),
                    json=mock["response"],
                    status_code=mock.get("status", 200),
                )
        access_result = dp.access(identifier)
        print("Data retrieved for " + identifier + ":")
        print(json.dumps(access_result, indent=2))

        if action_type == ActionType.Access:
            return

    context = {"mailingLists": access_result}
    print("Context for the erasure:\n", json.dumps(context, indent=2))
    print(f"\nRunning erasure for {identifier}...")
    with requests_mock.Mocker() as m:
        with open(f"{ActionType.Erasure}.json") as fp:
            erasure_mocks = json.load(fp)
            mailing_lists_to_delete = []
            for mock in erasure_mocks:
                m.register_uri(
                    mock["method"],
                    mock["scope"] + mock.get("path"),
                    json=mock["response"],
                    status_code=mock.get("status", 200),
                )

                # Add mailing list to list of communities to remove the user from.
                # You can also just pass in full url via mock["scope"] + mock.get("path") for API.
                # Only delete if mock address matches identifier.
                if "member" in mock["response"] and "address" in mock["response"]["member"]:
                    mocked_address = mock["response"]["member"]["address"]

                if mock["method"] == "DELETE" and mocked_address == identifier:
                    mailing_list = dp.extract_mailing_list(mock["path"])
                    mailing_lists_to_delete.append(mailing_list)
        dp.erasure(identifier, mailing_lists_to_delete)
    print("All done!")


def run_seed(identifier):
    seeded_runs = 0
    print(f"Seeding data for {identifier}...\n")
    with requests_mock.Mocker() as m:
        with open(f"{ActionType.Seed}.json") as fp:
            seed_mocks = json.load(fp)
            for mock in seed_mocks:
                m.register_uri(
                    mock["method"],
                    mock["scope"] + mock.get("path"),
                    json=mock["response"],
                    status_code=mock.get("status", 200),
                )
                if "member" in mock["response"] and "address" in mock["response"]["member"]:
                    mocked_address = mock["response"]["member"]["address"]

                if mock["method"] == "POST" and mocked_address == identifier:
                    mailing_list = dp.extract_mailing_list(mock["path"])
                    dp.seed(identifier, mock["scope"], mailing_list)
                    seeded_runs += 1
    return seeded_runs


def main():
    """
    Main entry point.
    """
    action = verify_action_args(sys.argv)
    data = sample_identifiers_list

    # Run the functions for all the identifiers we want to test
    for identifier in data:
        if action == ActionType.Seed:
            runs = run_seed(identifier)
            print(f"Successfully seeded {runs} identifiers.\n")

        elif action == ActionType.Access or action == ActionType.Erasure:
            run_integration(identifier, action)
    return


if __name__ == "__main__":
    main()
