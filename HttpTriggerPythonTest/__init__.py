from msrestazure.azure_active_directory import MSIAuthentication, ServicePrincipalCredentials
from azure.keyvault import KeyVaultClient
import logging
import os
import azure.functions as func

def get_secret_value(secret):
    managed_identity_client_id = os.environ.get("MANAGED_IDENTITY_CLIENT_ID")
    key_vault_url = os.environ.get("KEY_VAULT_URL")
    credentials = MSIAuthentication(client_id = managed_identity_client_id)
    key_vault_client = KeyVaultClient(credentials)   
    secret_value = key_vault_client.get_secret(key_vault_url,secret,"")
    return secret_value.value

def main(req: func.HttpRequest) -> func.HttpResponse:
    secret = req.params.get('secret')
    #secret = "mySecret"
    if secret:
        secret_value = get_secret_value(secret)
        return func.HttpResponse(f"Secret Value: {secret_value}!")
    else:
        return func.HttpResponse(
             "Please pass a secret on the query string or in the request body",
             status_code=400
        )
