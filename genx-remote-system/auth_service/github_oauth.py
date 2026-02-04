from flask import Flask, request, redirect, jsonify
import requests
import os
from urllib.parse import urlencode

# --- GitHub OAuth Configuration ---
# These should be stored as environment variables in a production environment.
# Example:
# export GITHUB_CLIENT_ID="your_client_id"
# export GITHUB_CLIENT_SECRET="your_client_secret"
# export REDIRECT_URI="your_callback_url"

GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", "0b2a311d5d0c1c62c1f6")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", "4e6aa3f4f9f9f3e99a411b5d0a71fc01f2e1c7d1")
# The callback URL for your application
REDIRECT_URI = os.environ.get("REDIRECT_URI", "https://genxai.vercel.app/api/auth/callback/github")

# --- Firebase and Device Auth ---
# In a complete application, you would import your existing modules.
# from firebase_integration.firebase_client import initialize_firebase, create_user_session
# from device_auth import verify_device_fingerprint, generate_device_fingerprint

# For demonstration, these will be mocked.
def initialize_firebase(): return True
def create_user_session(db, user_id, github_username, build_number, fingerprint): return "mock_session_123"
def verify_device_fingerprint(build_number, fingerprint): return True
def generate_device_fingerprint(build_number): return "mock_fingerprint"


app = Flask(__name__)
# A secret key is needed for session management in Flask
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "a-secure-random-string")

# Initialize Firebase (mocked for this example)
db_client = initialize_firebase()

@app.route('/login/github')
def github_login():
    """
    Redirects the user to GitHub to authorize the application.
    """
    # Define the parameters for the GitHub authorization request
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "user:email",  # Request read access to the user's email addresses
        "state": "some_random_string_for_security" # A random string to prevent CSRF attacks
    }

    # Construct the authorization URL
    auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"

    return redirect(auth_url)

@app.route('/api/auth/callback/github')
def github_callback():
    """
    Handles the callback from GitHub after user authorization.
    """
    # Get the authorization code from the query parameters
    code = request.args.get("code")
    state = request.args.get("state")

    # --- Security Check ---
    # Verify the 'state' parameter to prevent CSRF attacks.
    # if state != expected_state:
    #     return "Invalid state parameter", 400

    if not code:
        return "Error: No authorization code provided.", 400

    # --- Exchange Code for Access Token ---
    token_url = "https://github.com/login/oauth/access_token"
    token_params = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    headers = {"Accept": "application/json"}
    token_res = requests.post(token_url, params=token_params, headers=headers)

    if token_res.status_code != 200:
        return f"Error getting access token: {token_res.text}", 500

    token_data = token_res.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return "Error: Access token not found in response.", 500

    # --- Fetch User Data from GitHub API ---
    user_api_url = "https://api.github.com/user"
    user_headers = {"Authorization": f"token {access_token}"}
    user_res = requests.get(user_api_url, headers=user_headers)

    if user_res.status_code != 200:
        return f"Error fetching user data: {user_res.text}", 500

    user_data = user_res.json()
    github_id = user_data.get("id")
    github_username = user_data.get("login")

    # --- Device Verification and Session Creation ---
    # In a real implementation, you would get these from the request headers
    build_number = "15.1.1.109SP06(OP001PF001AZ)"
    fingerprint = generate_device_fingerprint(build_number) # Or get from header

    if not verify_device_fingerprint(build_number, fingerprint):
        return "Device verification failed.", 403

    # Create a session in Firebase
    session_id = create_user_session(
        db=db_client,
        user_id=str(github_id),
        github_username=github_username,
        build_number=build_number,
        fingerprint=fingerprint
    )

    return jsonify({
        "message": "Authentication successful!",
        "session_id": session_id,
        "github_user": user_data
    })


if __name__ == '__main__':
    # This server would typically be run with Gunicorn or another WSGI server.
    # This auth service would run alongside the secure_gateway, likely on a different port.
    app.run(host='127.0.0.1', port=5002, debug=True)