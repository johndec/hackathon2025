@description('The name of the Azure OpenAI service')
param openAIServiceName string = 'openai-${uniqueString(resourceGroup().id)}'

@description('The location where resources will be deployed')
param location string = resourceGroup().location

@description('The SKU name for the Azure OpenAI service')
@allowed([
  'S0'
])
param skuName string = 'S0'

@description('The name of the model deployment')
param modelDeploymentName string = 'gpt-35-turbo'

@description('The model name to deploy')
@allowed([
  'gpt-35-turbo'
  'gpt-4'
  'gpt-4-turbo'
  'text-embedding-ada-002'
])
param modelName string = 'gpt-35-turbo'

@description('The model version to deploy')
param modelVersion string = '0613'

@description('The capacity for the model deployment')
param modelCapacity int = 10

@description('Network access configuration for OpenAI service')
@allowed([
  'Enabled'
  'Disabled'
])
param publicNetworkAccess string = 'Enabled'

@description('Tags to apply to all resources')
param tags object = {
  project: 'hackathon2025'
  environment: 'dev'
}

// Deploy Azure OpenAI Service using module
module openAIService 'modules/openai.bicep' = {
  name: 'openai-deployment'
  params: {
    openAIServiceName: openAIServiceName
    location: location
    skuName: skuName
    modelDeploymentName: modelDeploymentName
    modelName: modelName
    modelVersion: modelVersion
    modelCapacity: modelCapacity
    publicNetworkAccess: publicNetworkAccess
    tags: tags
  }
}

// Outputs - passing through from the module
@description('The name of the Azure OpenAI service')
output openAIServiceName string = openAIService.outputs.openAIServiceName

@description('The endpoint URL of the Azure OpenAI service')
output openAIEndpoint string = openAIService.outputs.openAIEndpoint

@description('The resource ID of the Azure OpenAI service')
output openAIResourceId string = openAIService.outputs.openAIResourceId

@description('The name of the model deployment')
output modelDeploymentName string = openAIService.outputs.modelDeploymentName

@description('The location of the deployed OpenAI service')
output openAILocation string = openAIService.outputs.openAILocation

@description('Instructions for retrieving the API key')
output keyInstructions string = openAIService.outputs.keyInstructions