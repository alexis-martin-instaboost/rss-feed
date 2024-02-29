import flask
import google_auth_oauthlib.flow
import os
import json
from handle_rss_feed import main
from helpers.credentials_to_dict import credentials_to_dict
import threading
from helpers.get_base_url import get_base_url
from dotenv import load_dotenv
from helpers.logger_setup import setup_logger

# Load environment variables from .env file
load_dotenv()
logger = setup_logger()

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = flask.Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure, random value in a real application
scopes = ["https://www.googleapis.com/auth/documents"]
state = 'instaboost'

@app.route("/login")
def redirect_to_authorization():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=scopes)

    base_url = get_base_url()
    flow.redirect_uri = base_url + "/oauth2callback"

    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=state,
        prompt='consent')
    return flask.redirect(authorization_url)

@app.route("/oauth2callback")
def oauth2callback():
    # Set up the OAuth flow with the client secrets file and state
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=scopes,
        state=state
    )
    flow.redirect_uri = http_to_https(flask.url_for('oauth2callback', _external=True))
    logger.info(f"flow.redirect_uri: {flow.redirect_uri}")

    # Process the authorization response and fetch the token
    authorization_response = http_to_https(flask.request.url)
    logger.info(f"authorization_response: {authorization_response}")

    flow.fetch_token(authorization_response=authorization_response)

    # Store the credentials in the session
    credentials = credentials_to_dict(flow.credentials)
    start_main(credentials)

    # You can customize the response or redirect the user to another page
    return {"message": "What's up Chris! You have successfully logged in and system has started."}

def start_main(credentials):
    background_thread = threading.Thread(target=main, args=(credentials,))
    background_thread.start()


def create_json_file(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=2)

    logger.info(f"JSON file '{file_path}' created successfully.")

    # Log the contents of the file
    with open(file_path, 'r') as read_file:
        file_contents = read_file.read()
        logger.info(f"Contents of '{file_path}':\n{file_contents}")

def http_to_https(url):
    if "http:" in url:
        url = "https:" + url[5:]
    return url

def split_and_get_list(env_variable):
    # Split the value by commas and remove leading/trailing spaces
    values = os.environ.get(env_variable, '').split(',')
    return [value.strip() for value in values]

client_secret_json = {
    "web": {
        "client_id": os.environ.get('GOOGLE_CLIENT_ID', ''),
        "project_id": os.environ.get('GOOGLE_PROJECT_ID', ''),
        "auth_uri": os.environ.get('GOOGLE_AUTH_URI', ''),
        "token_uri": os.environ.get('GOOGLE_TOKEN_URI', ''),
        "auth_provider_x509_cert_url": os.environ.get('GOOGLE_AUTH_PROVIDER_X509_CERT_URL', ''),
        "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET', ''),
        "redirect_uris": split_and_get_list('GOOGLE_REDIRECT_URIS'),
        "javascript_origins": split_and_get_list('GOOGLE_JAVASCRIPT_ORIGINS'),
    }
}

if __name__ == "__main__":
    from waitress import serve
    create_json_file(client_secret_json, 'client_secret.json')
    serve(app, host="0.0.0.0", port=5000)
