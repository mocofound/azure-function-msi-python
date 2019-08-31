# Use Azure Key Vault with Managed Service Identity from a Python Azure Function

## Prerequisites

These are the services needed:
1. A Managed Identity
1. An Azure Key vault
1. A Linux based Python Azure Function with an App Service Plan

Steps to configure the solution:
1. Define one secret on Azure Key Vault (e.g. mySecret=SupreSecretValue)
1. Define a Policy on Azure Key Vault that allows the Managed Identity to Get Secrets
1. Configure the Azure Function to use the previously created Managed Identity
1. Register the Key Vault URL as an Application Setting in the Azure Function
1. Register the Application Id of the Managed Identity as an Application Setting in the Azure Function

## Development Environment Requirements
1. VSCode
1. Docker is needed as the Cryptographic libraries require native build.
1. Creae a Python3 environment
1. Install the msrestazure Python package
1. Install the azure-keyvault Python package. This dependency is also added to the requirements.txt file

## Code

The Function used in ths example is has a HTTP trigger and receives one parameter that represent the **secret** to return. The invocation looks like:
```javascript
https://myazurefunction.azurewebsites.net/api/HttpTriggerPythonTest?secret=mySecret
```
The function gets the **secret** parameter value from the request. 
```python
def main(req: func.HttpRequest) -> func.HttpResponse:
    secret = req.params.get('secret')
```
This value is used to get the secret from Azure Key Vault. The Key Vault location and Managed Idenity to used are extracted from the applicaiton settings:
```python
    managed_identity_client_id = os.environ.get("MANAGED_IDENTITY_CLIENT_ID")
    key_vault_url = os.environ.get("KEY_VAULT_URL")
```
They are used to query Azure Key Vault for the specific secret value:
```python
    credentials = MSIAuthentication(client_id = managed_identity_client_id)
    key_vault_client = KeyVaultClient(credentials)   
    secret_value = key_vault_client.get_secret(key_vault_url,secret,"")
```
The secret_value is finally returned to the caller
```python
return func.HttpResponse(f"Secret Value: {secret_value}!")
```

# Deploying
The code is deployed from VSCode. When asked, make sure to choose the build native depndency options. This can also be specified on the settings.json file located under the .vscode folder
```json
"azureFunctions.preDeployTask": "func: pack --build-native-deps"
```
