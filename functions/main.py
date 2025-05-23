import logging

import requests
from firebase_admin import initialize_app
from firebase_functions import https_fn
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import secretmanager

logging.basicConfig(level=logging.INFO)

initialize_app()
app = Flask(__name__)
CORS(app, resources={r"/organizations*": {"origins": "http://localhost:4200"}})


@app.after_request
def apply_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:4200'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# --- Secret Helper ---
def get_secret(secret_id: str) -> str:
    logging.info(f"Fetching secret: {secret_id}")
    client = secretmanager.SecretManagerServiceClient()
    project_id = 'mural-take-home-e3b8b'
    name = f'projects/{project_id}/secrets/{secret_id}/versions/latest'
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8").strip()


# --- MuralPay API Calls ---
def tos_call(org, headers):
    if org['tosStatus'] != 'ACCEPTED':
        tos_url = f"https://api-staging.muralpay.com/api/organizations/{org['id']}/tos-link"
        response = requests.get(tos_url, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        return response_json['tosLink']
    return org['tosStatus']


def kyc_call(org, headers):
    if org['tosStatus'] != 'INACTIVE':
        kyc_url = f"https://api-staging.muralpay.com/api/organizations/{org['id']}/kyc-link"
        response = requests.get(kyc_url, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        return response_json['kycLink']
    return org['kycStatus']


def organization_call(api_key: str, id: str):
    url = f"https://api-staging.muralpay.com/api/organizations/{id}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    logging.info(f"Fetching organization with ID {id}...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json(), response.status_code


def organization_list_call(api_key: str):
    url = "https://api-staging.muralpay.com/api/organizations/search"
    payload = {"filter": {"type": "name"}}
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    logging.info("Fetching organization list...")
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    org_list = response.json()['results']
    for org in org_list:
        org['tosStatus'] = tos_call(org, headers)
        if org['tosStatus'] == 'ACCEPTED' and org['kycStatus']['type'] == 'INACTIVE':
            kyc_dict = org['kycStatus']
            kyc_dict['kycUrl'] = kyc_call(org, headers)
            org['kycStatus'] = kyc_dict
    return org_list, response.status_code


def create_organization_call(api_key: str, body: dict):
    url = "https://api-staging.muralpay.com/api/organizations"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    logging.info("Creating new organization...")
    response = requests.post(url, json=body, headers=headers)
    response.raise_for_status()
    return response.json(), response.status_code


def account_call(api_key: str, org_id: str, account_id: str):
    url = f"https://api-staging.muralpay.com/api/accounts/{account_id}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
        "on-behalf-of": org_id
    }
    logging.info("Fetching account ...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    account_response = response.json()
    return account_response, response.status_code


def account_list_call(api_key: str, org_id: str):
    url = "https://api-staging.muralpay.com/api/accounts"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
        "on-behalf-of": org_id
    }
    logging.info("Fetching account list...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    accounts_list = response.json()
    return accounts_list, response.status_code


def create_account_call(api_key: str, org_id: str, body: dict):
    url = "https://api-staging.muralpay.com/api/accounts"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
        "on-behalf-of": org_id
    }
    logging.info("Creating new account...")
    response = requests.post(url, json=body, headers=headers)
    response.raise_for_status()
    return response.json(), response.status_code


def create_payout_request(api_key: str, org_id: str, body: dict):
    url = "https://api-staging.muralpay.com/api/payouts/payout"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
        "on-behalf-of": org_id
    }
    logging.info("Creating new payout request...")
    response = requests.post(url, json=body, headers=headers)
    response.raise_for_status()
    return response.json(), response.status_code


def execute_payout_request(api_key: str, transfer_api_key: str, org_id: str, payout_id: str):
    url = f"https://api-staging.muralpay.com/api/payouts/payout/{payout_id}/execute"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "transfer-api-key": transfer_api_key,
        "authorization": f"Bearer {api_key}",
        "on-behalf-of": org_id
    }
    logging.info("Executing new payout request...")
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json(), response.status_code


def search_payout_requests(api_key: str, org_id: str,):
    url = 'https://api-staging.muralpay.com/api/payouts/search'
    payload = {"filter": {
        "type": "payoutStatus",
        "statuses": ["AWAITING_EXECUTION","CANCELED", "PENDING","EXECUTED", "FAILED"]
    }}
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
        "on-behalf-of": org_id
    }
    logging.info("Executing new payout request...")
    response = requests.post(url,json=payload, headers=headers)
    response.raise_for_status()
    r = response.json()
    return response.json(), response.status_code


# --- Flask Routes ---
@app.route("/organizations/<org_id>", methods=["GET", "OPTIONS"])
def get_organization(org_id):
    if request.method == 'OPTIONS':
        return '', 204
    try:
        api_key = get_secret("API_KEY")
        data, status = organization_call(api_key, org_id)
        return jsonify(data), status
    except Exception as e:
        logging.exception("Error fetching organization:")
        return jsonify({"error": str(e)}), 500


@app.route("/organizations", methods=["GET", "OPTIONS"])
def get_organizations():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        api_key = get_secret("API_KEY")
        data, status = organization_list_call(api_key)
        return jsonify(data), status
    except Exception as e:
        logging.exception("Error listing organizations:")
        return jsonify({"error": str(e)}), 500


@app.route("/organizations", methods=["POST", "OPTIONS"])
def create_organization():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        api_key = get_secret("API_KEY")
        body = request.get_json()
        data, status = create_organization_call(api_key, body)
        return jsonify(data), status
    except Exception as e:
        logging.exception("Error creating organization:")
        return jsonify({"error": str(e)}), 500


@app.route("/accounts/<org_id>", methods=["GET", "OPTIONS"])
def get_accounts(org_id):
    if request.method == 'OPTIONS':
        return '', 204
    try:
        api_key = get_secret("API_KEY")
        data, status = account_list_call(api_key, org_id)
        return jsonify(data), status
    except Exception as e:
        logging.exception("Error listing organizations:")
        return jsonify({"error": str(e)}), 500


@app.route("/accounts/<org_id>/<account_id>", methods=["GET", "OPTIONS"])
def get_account_by_id(org_id, account_id):
    if request.method == 'OPTIONS':
        return '', 204
    try:
        api_key = get_secret("API_KEY")
        data, status = account_call(api_key, org_id, account_id)
        return jsonify(data), status
    except Exception as e:
        logging.exception("Error listing organizations:")
        return jsonify({"error": str(e)}), 500

@app.route("/accounts/<org_id>", methods=["POST", "OPTIONS"])
def create_account(org_id):
    if request.method == 'OPTIONS':
        return '', 204
    try:
        api_key = get_secret("API_KEY")
        data, status = create_account_call(api_key, org_id, request.get_json())
        return jsonify(data), status
    except Exception as e:
        logging.exception("Error listing organizations:")
        return jsonify({"error": str(e)}), 500


# --- Firebase Entry Point ---
@https_fn.on_request()
def main_function(request):
    return app(request.environ, start_response=lambda *a, **k: None)


# if __name__ == '__main__':
#     api_key = 'af3c4c9a81048415cb20d344:a8826b1e7b583e720a81682aaea980eb8568c5ae91a1e4621968cde2978fa5dfe30b65c4:9513247a62f3c46899d509d2c5eac889.856ce7ec710d47f62d3f2459c142a9ccc92b79a2bd1c78c3376654aa3ff4c262'
#     transfer_api_key = '55c733176e867cfe949688ef:43bf33f8e38dd6b4fa19bf99a5d5e46f31503d770fa7a61af582e27a5717bf5338ee8102:07f2af0dc2c5e79a190130058025aa5c.94717a395bc45e4901aa43b6297dc8c74e323469a515051d60da842deea77814'
#
#     sample_payload = {
#         "sourceAccountId": "639bb127-0b32-4e63-90fd-099356b046c6",
#         "memo": "December contract",
#         "payouts": [
#             {
#                 "amount": {
#                     "tokenSymbol": "USDC",
#                     "tokenAmount": 2
#                 },
#                 "payoutDetails": {
#                     "type": "fiat",
#                     "bankName": "Bancamia S.A.",
#                     "bankAccountOwner": "test",
#                     "fiatAndRailDetails": {
#                         "type": "cop",
#                         "symbol": "COP",
#                         "accountType": "CHECKING",
#                         "phoneNumber": "+57 601 555 5555",
#                         "bankAccountNumber": "1234567890123456",
#                         "documentNumber": "1234563",
#                         "documentType": "NATIONAL_ID"
#                     }
#                 },
#                 "recipientInfo": {
#                     "type": "individual",
#                     "firstName": "Javier",
#                     "lastName": "Gomez",
#                     "email": "jgomez@gmail.com",
#                     "dateOfBirth": "1980-02-22",
#                     "physicalAddress": {
#                         "address1": "Cra. 37 #10A 29",
#                         "country": "CO",
#                         "state": "Antioquia",
#                         "city": "Medellin",
#                         "zip": "050015"
#                     }
#                 }
#             }
#         ]
#     }
#
#     # accounts = account_list_call(api_key, '9f6e67a5-f268-4ec2-a191-6f1fd799d9b1')
#     # a = create_payout_request(api_key, '9f6e67a5-f268-4ec2-a191-6f1fd799d9b1',
#     #                         sample_payload)
#     # id_2 = '0f35fd95-7df8-4db1-89eb-0f4da070a2ef'
#     # execute_payout_request(api_key,transfer_api_key, '9f6e67a5-f268-4ec2-a191-6f1fd799d9b1',
#     #                        id_2)
#     # search_payout_requests(api_key, '9f6e67a5-f268-4ec2-a191-6f1fd799d9b1')