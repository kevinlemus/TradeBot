import webbrowser

client_id = "fnB6k1X6JSFlQHravRt6T9m86AZlkD04"
redirect_uri = "https://developer.schwab.com/oauth2-redirect.html"
scope = "readonly"
authorization_url = f"https://api.schwabapi.com/v1/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"

print("Go to the following URL to authorize the application:")
print(authorization_url)

webbrowser.open(authorization_url)
