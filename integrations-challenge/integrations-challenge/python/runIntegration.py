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
            "This module accepts a single argument: python3 runIntegration.py <action>, where <action> can be one of: {}".format(
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
    print("Running access...\n")
    with requests_mock.Mocker() as m:
        with open(f"{ActionType.Access}.json") as fp:
            access_mocks = json.load(fp)
            for mock in access_mocks:
                m.register_uri(
                    mock["method"],
                    mock["scope"] + mock.get("path"),
                    json=mock["response"],
                    status_code=mock.get("status_code", 200),
                )
        access_result = dp.access(identifier)
        data = access_result["data"]
        print("Data retrieved for " + identifier + ":")
        print
        print(json.dumps(data, indent=2))
        print

        if action_type == ActionType.Access:
            return

    context = access_result["context"]
    print("Context for the erasure: ", context)
    print("\nRunning erasure...")
    with requests_mock.Mocker() as m:
        with open(f"{ActionType.Erasure}.json") as fp:
            erasure_mocks = json.load(fp)
            for mock in erasure_mocks:
                m.register_uri(
                    mock["method"],
                    mock["scope"] + mock.get("path"),
                    json=mock["response"],
                    status_code=mock.get("status_code", 200),
                )
        dp.erasure(identifier, context)
    print("All done!")


def main():
    action = verify_action_args(sys.argv)

    # For now, we only want to run our application code
    # with the first identifier.
    # Once you're confident your code works, you can modify
    # this to refer to the entire list of identifiers!
    data = [sample_identifiers_list[0]]

    # Run the functions for all the identifiers we want to test
    for identifier in data:
        if action == ActionType.Seed:
            dp.seed(identifier)

        elif action == ActionType.Access or action == ActionType.Erasure:
            run_integration(identifier, action)
    return


if __name__ == "__main__":
    main()
