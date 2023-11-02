import json
import time
from flask import Flask, redirect, request, render_template
from google_auth_oauthlib.flow import InstalledAppFlow
import utils
import os


app = Flask(__name__)

auth_scopes = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/cloudplatformprojects',
    'https://www.googleapis.com/auth/firebase',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/iam',
    'openid'
]

# JUST FOR TESTING PURPOSES
projectName = '' # tmp
projectId = '' # tmp

serviceAccountKeyFile = 'serviceAccounKey.json'
registeredAndroidApps = []

# load the config file if it exists
if os.path.exists('config.json'):
    with open('config.json', 'r') as f:
        registeredAndroidApps = json.loads(f.read())

# END ---- JUST FOR TESTING PURPOSES


@app.get('/')
def index():
    keyfile = utils.getServiceAccount(serviceAccountKeyFile)
    return render_template('index.html', keyfile=keyfile, registeredAndroidApps=registeredAndroidApps)

@app.post('/')
def create_project():
    global projectName
    action = request.form['action']
    if action == 'add_project':
        projectName = request.form['project_name']
        return redirect('/auth/google')
    elif action == 'register_android':
        package_name = request.form['package_name']
        config = utils.registerAndroidApp(package_name, serviceAccountKeyFile)
        global registeredAndroidApps
        registeredAndroidApps.append({
            'package_name': package_name,
            'config': config
        })
        # dump the config to a file
        with open('config.json', 'w') as f:
            f.write(json.dumps(registeredAndroidApps, indent=4))
        return redirect('/')
    
    return redirect('/')

@app.get('/auth/google')
def auth_google():
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes=auth_scopes)
    flow.redirect_uri = 'http://localhost:3000/auth/callback'
    url, _ = flow.authorization_url(prompt='consent')
    return redirect(url)

@app.get('/auth/callback')
def auth_callback():
    # fetch access token
    code = request.args.get('code')
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes=auth_scopes)
    flow.redirect_uri = 'http://localhost:3000/auth/callback'
    payload = flow.fetch_token(code=code)
    access_token = payload['access_token']

    # access global variables
    global projectName
    global projectId

    # create the project
    projectId = utils.createProject(projectName, access_token)

    print(projectId)

    # delay for 5 seconds
    time.sleep(7)

    # add firebase to the project
    utils.addFirebaseToGCPProject(projectId, access_token)

    # generate firebase service account and associate admin role
    serviceAccountEmail = utils.generateFirebaseServiceAccount(projectId, access_token)

    # generate firebase service account key
    serviceAccountKey = utils.generateKeysServiceAccount(serviceAccountEmail, access_token)
    serviceAccountKeyString = json.dumps(serviceAccountKey, indent=4)

    # store the service account key in `serviceAccountKeyFile`
    with open(serviceAccountKeyFile, 'w') as f:
        f.write(serviceAccountKeyString)
    
    # revoke access token
    utils.revoke_access_token(access_token)

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, port=3000)