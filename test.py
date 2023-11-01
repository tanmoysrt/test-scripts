from dotenv import load_dotenv
from flask import Flask, redirect, request
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

auth_scopes = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/cloudplatformprojects',
    'https://www.googleapis.com/auth/firebase',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/iam',
    'openid'
]

@app.route('/auth/google')
def auth_google():
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes=auth_scopes)
    flow.redirect_uri = 'http://localhost:3000/auth/callback'
    url, _ = flow.authorization_url(prompt='consent')
    return redirect(url)

@app.route('/auth/callback')
def auth_callback():
    code = request.args.get('code')
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes=auth_scopes)
    flow.redirect_uri = 'http://localhost:3000/auth/callback'
    token = flow.fetch_token(code=code)
    print(token)

    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True, port=3000)