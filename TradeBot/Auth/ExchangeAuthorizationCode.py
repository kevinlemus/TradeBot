import requests

client_id = "fnB6k1X6JSFlQHravRt6T9m86AZlkD04"
client_secret = "RRx7K9Cf6Nco7mwf"
redirect_uri = "https://developer.schwab.com/oauth2-redirect.html"
authorization_code = "C0.b2F1dGgyLmNkYy5zY2h3YWIuY29t.0AhtrwB44JTgDbjMtuXCRXm_jK1i3p4HzC4sMv7S-hg%40"  # Only the code portion

token_url = "https://api.schwabapi.com/v1/oauth/token"
payload = {
    "grant_type": "authorization_code",
    "client_id": client_id,
    "client_secret": client_secret,
    "redirect_uri": redirect_uri,
    "code": authorization_code,
}

response = requests.post(token_url, data=payload)
print(f"Token response status code: {response.status_code}")
print(f"Token response text: {response.text}")

if response.status_code == 200:
    tokens = response.json()
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    print(f"Access Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")
else:
    print(f"Error: {response.text}")
