import logging
import json
import uuid
import time
from datetime import datetime
from functools import wraps

import requests
from firebase_admin import initialize_app
from firebase_functions import https_fn
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from google.cloud import secretmanager

# Configure logging with structured format
class StructuredLogger:
    def __init__(self, logger):
        self.logger = logger

    def _log(self, level, msg, **kwargs):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'message': msg,
            'correlation_id': getattr(g, 'correlation_id', 'N/A'),
            **kwargs
        }
        getattr(self.logger, level)(json.dumps(log_data))

    def info(self, msg, **kwargs):
        self._log('info', msg, **kwargs)

    def error(self, msg, **kwargs):
        self._log('error', msg, **kwargs)

    def debug(self, msg, **kwargs):
        self._log('debug', msg, **kwargs)

    def warning(self, msg, **kwargs):
        self._log('warning', msg, **kwargs)

# Configure base logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
base_logger = logging.getLogger(__name__)
logger = StructuredLogger(base_logger)

initialize_app()
app = Flask(__name__)
CORS(app, resources={r"/organizations*": {"origins": "http://localhost:4200"}})
base_url = 'https://api-staging.muralpay.com/api'

def log_request_info():
    """Log detailed request information"""
    g.correlation_id = str(uuid.uuid4())
    g.start_time = time.time()
    
    request_data = {
        'method': request.method,
        'path': request.path,
        'headers': dict(request.headers),
        'query_params': dict(request.args),
        'body': request.get_json(silent=True)
    }
    
    logger.info('Incoming request', request_data=request_data)

def log_response_info(response):
    """Log detailed response information"""
    duration = time.time() - g.start_time
    
    response_data = {
        'status_code': response.status_code,
        'headers': dict(response.headers),
        'duration_ms': round(duration * 1000, 2)
    }
    
    logger.info('Outgoing response', response_data=response_data)
    return response

@app.before_request
def before_request():
    log_request_info()

@app.after_request
def after_request(response):
    response = log_response_info(response)
    response = apply_cors_headers(response)
    return response

@app.after_request
def apply_cors_headers(response):
    logger.debug(f"Applying CORS headers to response: {response.status_code}")
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:4200'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# --- Secret Helper ---
def get_secret(secret_id: str) -> str:
    logger.info('Fetching secret', secret_id=secret_id)
    try:
        client = secretmanager.SecretManagerServiceClient()
        project_id = 'mural-take-home-e3b8b'
        name = f'projects/{project_id}/secrets/{secret_id}/versions/latest'
        response = client.access_secret_version(request={"name": name})
        logger.debug('Secret retrieved successfully', secret_id=secret_id)
        return response.payload.data.decode("UTF-8").strip()
    except Exception as e:
        logger.error('Failed to fetch secret', 
                    secret_id=secret_id,
                    error=str(e),
                    error_type=type(e).__name__)
        raise


# --- MuralPay API Calls ---
def tos_call(org, headers):
    logger.info('Checking TOS status', org_id=org['id'])
    if org['tosStatus'] != 'ACCEPTED':
        tos_url = f"{base_url}/organizations/{org['id']}/tos-link"
        logger.debug('Making TOS API call', url=tos_url)
        try:
            response = requests.get(tos_url, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            logger.info('TOS link generated', 
                       org_id=org['id'],
                       tos_link=response_json['tosLink'])
            return response_json['tosLink']
        except requests.exceptions.RequestException as e:
            logger.error('TOS API call failed',
                        org_id=org['id'],
                        error=str(e),
                        status_code=getattr(e.response, 'status_code', None))
            raise
    logger.info('TOS already accepted', org_id=org['id'])
    return org['tosStatus']


def kyc_call(org, headers):
    logger.info('Checking KYC status', org_id=org['id'])
    if org['tosStatus'] != 'INACTIVE':
        kyc_url = f"{base_url}/organizations/{org['id']}/kyc-link"
        logger.debug('Making KYC API call', url=kyc_url)
        try:
            response = requests.get(kyc_url, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            logger.info('KYC link generated',
                       org_id=org['id'],
                       kyc_link=response_json['kycLink'])
            return response_json['kycLink']
        except requests.exceptions.RequestException as e:
            logger.error('KYC API call failed',
                        org_id=org['id'],
                        error=str(e),
                        status_code=getattr(e.response, 'status_code', None))
            raise
    logger.info('KYC status inactive', org_id=org['id'])
    return org['kycStatus']


def organization_call(api_key: str, id: str):
    url = f"{base_url}/organizations/{id}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    logger.info('Fetching organization', org_id=id)
    try:
        start_time = time.time()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        duration = time.time() - start_time
        logger.debug('Organization data retrieved',
                    org_id=id,
                    duration_ms=round(duration * 1000, 2),
                    response_data=response.json())
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        logger.error('Failed to fetch organization',
                    org_id=id,
                    error=str(e),
                    status_code=getattr(e.response, 'status_code', None))
        raise


def organization_list_call(api_key: str):
    url = base_url + "/organizations/search"
    payload = {"filter": {"type": "name"}}
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    logger.info('Fetching organization list')
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        duration = time.time() - start_time
        org_list = response.json()['results']
        logger.debug('Retrieved organizations',
                    count=len(org_list),
                    duration_ms=round(duration * 1000, 2))
        
        for org in org_list:
            logger.info('Processing organization', org_id=org['id'])
            org['tosStatus'] = tos_call(org, headers)
            if org['tosStatus'] == 'ACCEPTED' and org['kycStatus']['type'] == 'INACTIVE':
                kyc_dict = org['kycStatus']
                kyc_dict['kycUrl'] = kyc_call(org, headers)
                org['kycStatus'] = kyc_dict
                logger.debug('Updated KYC status', org_id=org['id'])
        
        return org_list, response.status_code
    except requests.exceptions.RequestException as e:
        logger.error('Failed to fetch organization list',
                    error=str(e),
                    status_code=getattr(e.response, 'status_code', None))
        raise


def create_organization_call(api_key: str, body: dict):
    url = base_url + "/organizations"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    logger.info("Creating new organization...")
    response = requests.post(url, json=body, headers=headers)
    response.raise_for_status()
    return response.json(), response.status_code


def account_call(api_key: str, org_id: str, account_id: str):
    url = f"{base_url}/accounts/{account_id}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
        "on-behalf-of": org_id
    }
    logger.info("Fetching account ...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    account_response = response.json()
    return account_response, response.status_code


def account_list_call(api_key: str, org_id: str):
    url = base_url + "/accounts"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
        "on-behalf-of": org_id
    }
    logger.info("Fetching account list...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    accounts_list = response.json()
    return accounts_list, response.status_code


def create_account_call(api_key: str, org_id: str, body: dict):
    url = base_url + "/accounts"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
        "on-behalf-of": org_id
    }
    logger.info("Creating new account...")
    response = requests.post(url, json=body, headers=headers)
    response.raise_for_status()
    return response.json(), response.status_code


def create_payout_request(api_key: str, org_id: str, body: dict):
    url = base_url + "/payouts/payout"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
        "on-behalf-of": org_id
    }
    logger.info("Creating new payout request...")
    response = requests.post(url, json=body, headers=headers)
    response.raise_for_status()
    return response.json(), response.status_code


def execute_payout_request(api_key: str, transfer_api_key: str, org_id: str, payout_id: str):
    url = f"{base_url}/payouts/payout/{payout_id}/execute"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "transfer-api-key": transfer_api_key,
        "authorization": f"Bearer {api_key}",
        "on-behalf-of": org_id
    }
    logger.info("Executing new payout request...")
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json(), response.status_code


def search_payout_requests(api_key: str, org_id: str, payload: dict):
    url = 'https://api-staging.muralpay.com/api/payouts/search'
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
        "on-behalf-of": org_id
    }
    logger.info("Executing new payout request...")
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json(), response.status_code


# --- Flask Routes ---
@app.route("/organizations/<org_id>", methods=["GET", "OPTIONS"])
def get_organization(org_id):
    if request.method == 'OPTIONS':
        logger.debug('Handling OPTIONS request', org_id=org_id)
        return '', 204
    try:
        logger.info('Processing GET request', org_id=org_id)
        api_key = get_secret("API_KEY")
        data, status = organization_call(api_key, org_id)
        logger.debug('Organization data retrieved', 
                    org_id=org_id,
                    status_code=status)
        return jsonify(data), status
    except Exception as e:
        logger.error('Error fetching organization',
                    org_id=org_id,
                    error=str(e),
                    error_type=type(e).__name__)
        return jsonify({"error": str(e)}), 500


@app.route("/organizations", methods=["GET", "OPTIONS"])
def get_organizations():
    if request.method == 'OPTIONS':
        logger.debug('Handling OPTIONS request for organizations list')
        return '', 204
    try:
        logger.info('Processing GET request for organizations list')
        api_key = get_secret("API_KEY")
        data, status = organization_list_call(api_key)
        logger.debug('Organizations list retrieved',
                    count=len(data),
                    status_code=status)
        return jsonify(data), status
    except Exception as e:
        logger.error('Error fetching organizations list',
                    error=str(e),
                    error_type=type(e).__name__)
        return jsonify({"error": str(e)}), 500


@app.route("/organizations", methods=["POST", "OPTIONS"])
def create_organization():
    if request.method == 'OPTIONS':
        logger.debug('Handling OPTIONS request for organization creation')
        return '', 204
    try:
        logger.info('Processing POST request for organization creation')
        api_key = get_secret("API_KEY")
        body = request.get_json()
        logger.debug('Organization creation request',
                    request_body=body)
        data, status = create_organization_call(api_key, body)
        logger.info('Organization created successfully',
                   org_id=data.get('id'),
                   status_code=status)
        return jsonify(data), status
    except Exception as e:
        logger.error('Error creating organization',
                    error=str(e),
                    error_type=type(e).__name__)
        return jsonify({"error": str(e)}), 500


@app.route("/accounts/<org_id>", methods=["GET", "OPTIONS"])
def get_accounts(org_id):
    if request.method == 'OPTIONS':
        logger.debug('Handling OPTIONS request for accounts list', org_id=org_id)
        return '', 204
    try:
        logger.info('Processing GET request for accounts list', org_id=org_id)
        api_key = get_secret("API_KEY")
        data, status = account_list_call(api_key, org_id)
        logger.debug('Accounts list retrieved',
                    org_id=org_id,
                    count=len(data),
                    status_code=status)
        return jsonify(data), status
    except Exception as e:
        logger.error('Error fetching accounts list',
                    org_id=org_id,
                    error=str(e),
                    error_type=type(e).__name__)
        return jsonify({"error": str(e)}), 500


@app.route("/accounts/<org_id>/<account_id>", methods=["GET", "OPTIONS"])
def get_account_by_id(org_id, account_id):
    if request.method == 'OPTIONS':
        logger.debug('Handling OPTIONS request for account',
                    org_id=org_id,
                    account_id=account_id)
        return '', 204
    try:
        logger.info('Processing GET request for account',
                   org_id=org_id,
                   account_id=account_id)
        api_key = get_secret("API_KEY")
        data, status = account_call(api_key, org_id, account_id)
        logger.debug('Account data retrieved',
                    org_id=org_id,
                    account_id=account_id,
                    status_code=status)
        return jsonify(data), status
    except Exception as e:
        logger.error('Error fetching account',
                    org_id=org_id,
                    account_id=account_id,
                    error=str(e),
                    error_type=type(e).__name__)
        return jsonify({"error": str(e)}), 500

@app.route("/accounts/<org_id>", methods=["POST", "OPTIONS"])
def create_account(org_id):
    if request.method == 'OPTIONS':
        logger.debug('Handling OPTIONS request for account creation', org_id=org_id)
        return '', 204
    try:
        logger.info('Processing POST request for account creation', org_id=org_id)
        api_key = get_secret("API_KEY")
        body = request.get_json()
        logger.debug('Account creation request',
                    org_id=org_id,
                    request_body=body)
        data, status = create_account_call(api_key, org_id, body)
        logger.info('Account created successfully',
                   org_id=org_id,
                   account_id=data.get('id'),
                   status_code=status)
        return jsonify(data), status
    except Exception as e:
        logger.error('Error creating account',
                    org_id=org_id,
                    error=str(e),
                    error_type=type(e).__name__)
        return jsonify({"error": str(e)}), 500


@app.route("/payouts/<org_id>/<acc_id>", methods=["POST", "OPTIONS"])
def get_payout_requests(org_id, acc_id):
    if request.method == 'OPTIONS':
        logger.debug('Handling OPTIONS request for payout requests',
                    org_id=org_id,
                    account_id=acc_id)
        return '', 204
    try:
        logger.info('Processing POST request for payout requests',
                   org_id=org_id,
                   account_id=acc_id)
        api_key = get_secret("API_KEY")
        body = request.get_json()
        logger.debug('Payout requests search request',
                    org_id=org_id,
                    account_id=acc_id,
                    request_body=body)
        data, status = search_payout_requests(api_key, org_id, body)
        logger.info('Payout requests retrieved successfully',
                   org_id=org_id,
                   account_id=acc_id,
                   count=len(data.get('results', [])),
                   status_code=status)
        return jsonify(data), status
    except Exception as e:
        logger.error('Error fetching payout requests',
                    org_id=org_id,
                    account_id=acc_id,
                    error=str(e),
                    error_type=type(e).__name__)
        return jsonify({"error": str(e)}), 500


@app.route("/payouts/<org_id>/<acc_id>/<payout_id>", methods=["POST", "OPTIONS"])
def execute_payout_requests(org_id, acc_id, payout_id):
    if request.method == 'OPTIONS':
        logger.debug('Handling OPTIONS request for payout execution',
                    org_id=org_id,
                    account_id=acc_id,
                    payout_id=payout_id)
        return '', 204
    try:
        logger.info('Processing POST request for payout execution',
                   org_id=org_id,
                   account_id=acc_id,
                   payout_id=payout_id)
        api_key = get_secret("API_KEY")
        transfer_api_key = get_secret("TRANSFER_API_KEY")
        data, status = execute_payout_request(api_key, transfer_api_key, org_id, payout_id)
        logger.info('Payout executed successfully',
                   org_id=org_id,
                   account_id=acc_id,
                   payout_id=payout_id,
                   status_code=status)
        return jsonify(data), status
    except Exception as e:
        logger.error('Error executing payout',
                    org_id=org_id,
                    account_id=acc_id,
                    payout_id=payout_id,
                    error=str(e),
                    error_type=type(e).__name__)
        return jsonify({"error": str(e)}), 500

@app.route("/payouts/create/<org_id>", methods=["POST", "OPTIONS"])
def create_payout_requests(org_id):
    if request.method == 'OPTIONS':
        logger.debug('Handling OPTIONS request for payout creation', org_id=org_id)
        return '', 204
    try:
        logger.info('Processing POST request for payout creation', org_id=org_id)
        api_key = get_secret("API_KEY")
        body = request.get_json()
        logger.debug('Payout creation request',
                    org_id=org_id,
                    request_body=body)
        data, status = create_payout_request(api_key, org_id, body)
        logger.info('Payout created successfully',
                   org_id=org_id,
                   payout_id=data.get('id'),
                   status_code=status)
        return jsonify(data), status
    except Exception as e:
        logger.error('Error creating payout',
                    org_id=org_id,
                    error=str(e),
                    error_type=type(e).__name__)
        return jsonify({"error": str(e)}), 500

# --- Firebase Entry Point ---
@https_fn.on_request()
def main_function(request):
    logger.info('Processing main function request',
                method=request.method,
                path=request.path)
    try:
        with app.request_context(request.environ):
            return app.full_dispatch_request()
    except Exception as e:
        logger.error('Error in main function',
                    error=str(e),
                    error_type=type(e).__name__)
        return jsonify({"error": str(e)}), 500
