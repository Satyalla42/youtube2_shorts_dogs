from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]

flow = InstalledAppFlow.from_client_secrets_file(
    "client_secret_1046233653826-84ruhm7o8hb9mmel4bg1n8voqqf7pdjo.apps.googleusercontent.com.json",  # your downloaded file's name
    SCOPES
)

credentials = flow.run_local_server(port=8080)

print("ACCESS TOKEN:", credentials.token)
print("REFRESH TOKEN:", credentials.refresh_token)

