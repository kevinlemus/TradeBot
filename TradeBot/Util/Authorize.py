import sys
import os
import webbrowser
import logging

# Dynamically adjust sys.path to include the TradeBot directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.insert(0, project_root)

from TradeBot.Auth.OAuth import OAuth
from TradeBot.Config import API_KEYS, OAUTH_CONFIG


def construct_init_auth_url():
    client_id = API_KEYS["schwab_app_key"]
    redirect_uri = OAUTH_CONFIG["redirect_uri"]
    auth_url = f"{OAUTH_CONFIG['authorization_url']}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={OAUTH_CONFIG['scope']}"
    print("Click to authenticate:", auth_url)
    return auth_url


def main():
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s"
    )

    cs_auth_url = construct_init_auth_url()
    webbrowser.open(cs_auth_url)
    print("Paste Returned URL:")
    returned_url = input().strip()
    print(f"Returned URL: {returned_url}")

    try:
        # Extract the authorization code
        auth_code = returned_url.split("code=")[1].split("&")[0]
        print("Authorization Code:", auth_code)

        # Exchange authorization code for access token
        oauth = OAuth()
        tokens = oauth.get_access_token(auth_code)
        print("Tokens retrieved successfully.")
        print("Access Token:", tokens["access_token"])
        print("Refresh Token:", tokens["refresh_token"])

    except IndexError:
        print("Error: The returned URL does not contain an authorization code.")
    except Exception as e:
        logging.error(f"Error during token exchange: {e}")


if __name__ == "__main__":
    main()
