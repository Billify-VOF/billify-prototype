import os
import time
import requests
import json
from requests.auth import HTTPBasicAuth

# Replace with your actual credentials
client_id = '27ea36d6-f477-4ff1-9ed2-bae3a021ea54'  # Your client_id
client_secret = 'fd1e03de-1374-40e1-905b-ebe27e9e6d71'  # Your client_secret

# The token endpoint
url = "https://api.myponto.com/oauth2/token"

# Directory and file to store the access token
token_dir = "tokens"  # Directory where token will be saved
token_file_path = os.path.join(token_dir, "token.json")  # Path to token file

# Ensure the directory exists
def ensure_dir_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created.")
    else:
        print(f"Directory '{directory}' already exists.")

# Function to fetch and save access token
def fetch_and_save_token():
    data = {
        "grant_type": "client_credentials"
    }

    # Make the POST request with Basic Authentication (client_id:client_secret)
    response = requests.post(url, data=data, auth=HTTPBasicAuth(client_id, client_secret))

    # Check if the response was successful
    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data['access_token']
        expires_in = response_data['expires_in']

        # Save token and expiration time to a JSON file
        token_data = {
            "access_token": access_token,
            "expires_in": expires_in,
            "last_fetched_time": time.time()  # Save the current time when the token was fetched
        }

        with open(token_file_path, "w") as file:
            json.dump(token_data, file)

        print(f"New Access Token generated and saved: {access_token}")
        return access_token, expires_in
    else:
        print(f"Failed to get access token: {response.status_code}, {response.text}")
        return None, None

# Function to get the saved access token and expiration data
def get_saved_token():
    try:
        with open(token_file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None

# Function to check if the token has expired
def is_token_expired(expires_in, last_fetched_time):
    current_time = time.time()
    return current_time - last_fetched_time >= expires_in - 60  # 60 seconds margin

# Main loop to check token validity and refresh if needed
def token_scheduler():
    ensure_dir_exists(token_dir)
    while True:
        saved_data = get_saved_token()

        if saved_data:
            saved_token = saved_data['access_token']
            last_fetched_time = saved_data['last_fetched_time']
            expires_in = saved_data['expires_in']

            print(f"Using saved access token: {saved_token}")

            if is_token_expired(expires_in, last_fetched_time):
                print("Token expired, fetching new token.")
                fetch_and_save_token()
            else:
                print("Token is still valid.")
        else:
            print("No saved token found, generating new one.")
            fetch_and_save_token()
        print("Sleeping for 29 minutes before next check...\n")
        time.sleep(1740)
# Run the scheduler every 1 minute
if __name__ == "__main__":
    token_scheduler()  
