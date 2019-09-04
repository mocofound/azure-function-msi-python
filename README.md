# Use Azure Key Vault with Managed Service Identity from a Python Azure Function

## Prerequisites

These are the services needed:
1. A Managed Identity
1. An Azure Key vault
1. A Linux based Python Azure Function with an App Service Plan

Steps to configure the solution:
1. Define one secret on Azure Key Vault (e.g. mySecret=SupreSecretValue)
1. Define a Policy on Azure Key Vault that allows the Managed Identity to Get Secrets
1. Configure the Azure Function to use the previously created Managed Identity (as User Assigned Identity)
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

# Deploying from VSCode
The code is deployed from VSCode. When asked, make sure to choose the build native depndency options. This can also be specified on the settings.json file located under the .vscode folder
```json
"azureFunctions.preDeployTask": "func: pack --build-native-deps"
```

# Deploying from Azure DevOps
You can also use an Azure DevOps pipeline to deply the code into an Azure Function:
```yaml
# Python Function App to Linux on Azure
# Build a Python function app and deploy it to Azure as a Linux function app.
# Add steps that analyze code, save build artifacts, deploy, and more:
# https://docs.microsoft.com/azure/devops/pipelines/languages/python

trigger:
- master

variables:
  # Azure Resource Manager connection created during pipeline creation
  azureSubscription: 'xxxxxxx-xxxxx-xxxx-xxxx-xxxxxxxxxxx'

  # Function app name
  functionAppName: 'pythonapp'

  # Agent VM image name
  vmImageName: 'ubuntu-latest'

stages:
- stage: Build
  displayName: Build stage

  jobs:
  - job: Build
    displayName: Build
    pool:
      vmImage: $(vmImageName)

    steps:
    - bash: |
        if [ -f extensions.csproj ]
        then
            dotnet build extensions.csproj --runtime ubuntu.16.04-x64 --output ./bin
        fi
      displayName: 'Build extensions'

    - task: UsePythonVersion@0
      displayName: 'Use Python 3.6'
      inputs:
        versionSpec: 3.6

    - bash: |
        python -m venv worker_venv
        source worker_venv/bin/activate
        pip install -r requirements.txt
      displayName: 'Install application dependencies'

    - task: ArchiveFiles@2
      displayName: 'Archive files'
      inputs:
        rootFolderOrFile: '$(System.DefaultWorkingDirectory)'
        includeRootFolder: false
        archiveType: zip
        archiveFile: $(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip
        replaceExistingArchive: true

    - publish: $(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip
      artifact: drop

- stage: Deploy
  displayName: Deploy stage
  dependsOn: Build
  condition: succeeded()

  jobs:
  - deployment: Deploy
    displayName: Deploy
    environment: 'development'
    pool:
      vmImage: $(vmImageName)

    strategy:
      runOnce:
        deploy:

          steps:
          - task: AzureFunctionApp@1
            displayName: 'Azure functions app deploy'
            inputs:
              azureSubscription: '$(azureSubscription)'
              appType: functionAppLinux
              appName: $(functionAppName)
              package: '$(Pipeline.Workspace)/drop/$(Build.BuildId).zip'
```
