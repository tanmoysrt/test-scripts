import json
import os
import random
from dotenv import load_dotenv

import requests

load_dotenv()

token = os.getenv("ACCESS_TOKEN")


# ref - https://cloud.google.com/resource-manager/reference/rest/v1/projects#Project
# Cloud Resource Manager API enable
def createProject(name:str, bearerToken:str):
    url = "https://cloudresourcemanager.googleapis.com/v1/projects"
    projectId = name + "-project" + str(random.randint(1000, 9999))
    payload = {
        "projectId": projectId,
        "name": name
    }
    headers = {
        'Authorization': 'Bearer ' + bearerToken,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        raise Exception("failed to create project")
    responseJson = response.json()
    return responseJson["name"]

# createProject("test-420", token)

# ref - https://firebase.google.com/docs/reference/firebase-management/rest/v1beta1/projects/addFirebase
# enable Firebase Management API
def addFirebaseToGCPProject(projectId:str, bearerToken:str):
    url = "https://firebase.googleapis.com/v1beta1/projects/" + projectId + ":addFirebase"
    payload = {}
    headers = {
        'Authorization': 'Bearer ' + bearerToken,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        print(response.status_code)
        print(response.text)
        raise Exception("failed to add firebase to project")
    responseJson = response.json()
    return responseJson["name"]

# Generate Firerbase Service Account Key
def generateFirebaseServiceAccountKey(projectId:str, bearerToken:str):
    # Create a service accopunt
    # ref - https://cloud.google.com/iam/docs/reference/rest/v1/projects.serviceAccounts/create
    # Identity and Access Management (IAM) API enable
    url = "https://iam.googleapis.com/v1/projects/" + projectId + "/serviceAccounts"
    payload = {
        "accountId": "firebase-adminsdk-" + str(random.randint(1000, 9999)),
        "serviceAccount": {
            "displayName": "Firebase Admin SDK for project " + projectId
        }
    }
    headers = {
        'Authorization': 'Bearer ' + bearerToken,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        print(response.status_code)
        print(response.text)
        raise Exception("failed to create service account")
    responseJson = response.json()
    name = responseJson["name"]
    print(name)
    uniqueId = responseJson["uniqueId"]
    email = responseJson["email"]
    oauth2ClientId = responseJson["oauth2ClientId"]

    # Get IAM policy
    # ref - https://cloud.google.com/resource-manager/reference/rest/v1/projects/getIamPolicy
    url = "https://cloudresourcemanager.googleapis.com/v1/projects/" + projectId + ":getIamPolicy"
    headers = {
        'Authorization': 'Bearer ' + bearerToken,
        'Content-Type': 'application/json'
    }
    payload = {
        "options": {
            "requestedPolicyVersion": 3
        }
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        print(response.status_code)
        print(response.text)
        raise Exception("failed to get IAM policy")
    responseJson = response.json()
    iamRoles = responseJson["bindings"]

    # mdify to add current IAM in roles/firebase.admin role if required
    found = False
    for iamRole in iamRoles:
        if iamRole["role"] == "roles/firebase.admin":
            # check if current service account is already in the role
            foundUser = False
            for member in iamRole["members"]:
                if member == "serviceAccount:" + email:
                    foundUser = True
                    break
            if not foundUser:
                iamRole["members"].append("serviceAccount:" + email)
            found = True
            break
    if not found:
        iamRoles.append({
            "role": "roles/firebase.admin",
            "members": [
                "serviceAccount:" + email
            ]
        })

    # # add IAM role to service account
    # https://cloud.google.com/resource-manager/reference/rest/v1/projects/setIamPolicy
    # # ref - https://cloud.google.com/iam/docs/reference/rest/v1/projects.serviceAccounts/setIamPolicy
    url = "https://cloudresourcemanager.googleapis.com/v1/projects/" + projectId + ":setIamPolicy"
    
    payload = {
        "policy": {
            "bindings": iamRoles,
            "version": 3
        }
    }
    headers = {
        'Authorization': 'Bearer ' + bearerToken,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        print(response.status_code)
        print(response.text)
        raise Exception("failed to set IAM policy")
    responseJson = response.json()


def generate_keys_for_service_account(iam_account_detail:str):
    url = f"https://iam.googleapis.com/v1/projects/-/serviceAccounts/{iam_account_detail}/keys"
    payload = {}
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        print(response.status_code)
        print(response.text)
        raise Exception("failed to generate keys")
    responseJson = response.json()
    print(responseJson)

# addFirebaseToGCPProject("test-420-project8885", token)
# generateFirebaseServiceAccountKey("test-420-project8885", token)
# generate_keys_for_service_account("firebase-adminsdk-5382@test-420-project8885.iam.gserviceaccount.com")