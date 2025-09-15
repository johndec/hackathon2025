@description('The name of the Azure OpenAI service')
param openAIServiceName string

@description('The location where the OpenAI service will be deployed')
param location string = resourceGroup().location

@description('The SKU name for the Azure OpenAI service')
@allowed([
  'S0'
])
param skuName string = 'S0'

@description('The name of the model deployment')
param modelDeploymentName string

@description('The model name to deploy')
@allowed([
  'gpt-35-turbo'
  'gpt-4'
  'gpt-4-turbo'
  'text-embedding-ada-002'
])
param modelName string

@description('The model version to deploy')
param modelVersion string

@description('The capacity for the model deployment')
param modelCapacity int

@description('Tags to apply to the OpenAI resources')
param tags object = {}

@description('Network access configuration')
@allowed([
  'Enabled'
  'Disabled'
])
param publicNetworkAccess string = 'Enabled'

// Azure OpenAI Service
resource openAIAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: openAIServiceName
  location: location
  kind: 'OpenAI'
  tags: tags
  sku: {
    name: skuName
  }
  properties: {
    customSubDomainName: openAIServiceName
    networkAcls: {
      defaultAction: 'Allow'
      virtualNetworkRules: []
      ipRules: []
    }
    publicNetworkAccess: publicNetworkAccess
  }
}

// Model Deployment
resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openAIAccount
  name: modelDeploymentName
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
    raiPolicyName: 'Microsoft.Default'
  }
  sku: {
    name: 'Standard'
    capacity: modelCapacity
  }
}

// Outputs
@description('The name of the Azure OpenAI service')
output openAIServiceName string = openAIAccount.name

@description('The endpoint URL of the Azure OpenAI service')
output openAIEndpoint string = openAIAccount.properties.endpoint

@description('The resource ID of the Azure OpenAI service')
output openAIResourceId string = openAIAccount.id

@description('The name of the model deployment')
output modelDeploymentName string = modelDeployment.name

@description('The location of the deployed OpenAI service')
output openAILocation string = openAIAccount.location

@description('Instructions for retrieving the API key')
output keyInstructions string = 'Use Azure CLI: az cognitiveservices account keys list --name ${openAIAccount.name} --resource-group ${resourceGroup().name}'