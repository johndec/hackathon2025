# Azure OpenAI Deployment Script
# This script deploys the Azure OpenAI infrastructure using Bicep

param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory = $false)]
    [string]$Location = "East US",
    
    [Parameter(Mandatory = $false)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory = $false)]
    [string]$ParametersFile = "parameters.json"
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "Starting Azure OpenAI deployment..." -ForegroundColor Green

try {
    # Check if Azure CLI is installed
    if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
        throw "Azure CLI is not installed. Please install it from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    }

    # Login to Azure if not already logged in
    Write-Host "Checking Azure login status..." -ForegroundColor Yellow
    $loginStatus = az account show --query "user.name" -o tsv 2>$null
    if (-not $loginStatus) {
        Write-Host "Please log in to Azure..." -ForegroundColor Yellow
        az login
    } else {
        Write-Host "Already logged in as: $loginStatus" -ForegroundColor Green
    }

    # Set subscription if provided
    if ($SubscriptionId) {
        Write-Host "Setting subscription to: $SubscriptionId" -ForegroundColor Yellow
        az account set --subscription $SubscriptionId
    }

    # Get current subscription info
    $currentSubscription = az account show --query "{name:name, id:id}" -o json | ConvertFrom-Json
    Write-Host "Using subscription: $($currentSubscription.name) ($($currentSubscription.id))" -ForegroundColor Cyan

    # Create resource group if it doesn't exist
    Write-Host "Creating resource group: $ResourceGroupName" -ForegroundColor Yellow
    az group create --name $ResourceGroupName --location $Location --output none
    Write-Host "Resource group ready" -ForegroundColor Green

    # Get the full path to the Bicep template and parameters file
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $bicepFile = Join-Path $scriptDir "main.bicep"
    $parametersFilePath = Join-Path $scriptDir $ParametersFile

    # Validate that files exist
    if (-not (Test-Path $bicepFile)) {
        throw "Bicep template not found at: $bicepFile"
    }
    
    if (-not (Test-Path $parametersFilePath)) {
        throw "Parameters file not found at: $parametersFilePath"
    }

    Write-Host "Using Bicep template: $bicepFile" -ForegroundColor Cyan
    Write-Host "Using parameters file: $parametersFilePath" -ForegroundColor Cyan

    # Deploy the Bicep template
    Write-Host "Deploying Azure OpenAI infrastructure..." -ForegroundColor Yellow
    $deploymentName = "openai-deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    
    $deploymentResult = az deployment group create `
        --resource-group $ResourceGroupName `
        --template-file $bicepFile `
        --parameters @$parametersFilePath `
        --name $deploymentName `
        --output json | ConvertFrom-Json

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Deployment completed successfully!" -ForegroundColor Green
        
        # Display outputs
        Write-Host "`nDeployment Outputs:" -ForegroundColor Cyan
        Write-Host "=====================================" -ForegroundColor Cyan
        
        $outputs = $deploymentResult.properties.outputs
        foreach ($output in $outputs.PSObject.Properties) {
            $outputName = $output.Name
            $outputValue = $output.Value.value
            
            Write-Host "$outputName`: $outputValue" -ForegroundColor White
        }
        
        # Retrieve and display API keys separately (more secure)
        Write-Host "`nRetrieving API Keys:" -ForegroundColor Cyan
        Write-Host "===================" -ForegroundColor Cyan
        $openAIServiceName = $outputs.openAIServiceName.value
        
        $keysResult = az cognitiveservices account keys list --name $openAIServiceName --resource-group $ResourceGroupName --output json | ConvertFrom-Json
        if ($keysResult) {
            $maskedKey1 = "*" * ($keysResult.key1.Length - 4) + $keysResult.key1.Substring($keysResult.key1.Length - 4)
            $maskedKey2 = "*" * ($keysResult.key2.Length - 4) + $keysResult.key2.Substring($keysResult.key2.Length - 4)
            Write-Host "Primary Key: $maskedKey1" -ForegroundColor Yellow
            Write-Host "Secondary Key: $maskedKey2" -ForegroundColor Yellow
        }
        
        Write-Host "`nAzure OpenAI service is now ready to use!" -ForegroundColor Green
        Write-Host "You can find your resources in the Azure portal at:" -ForegroundColor Cyan
        Write-Host "https://portal.azure.com/#@/resource/subscriptions/$($currentSubscription.id)/resourceGroups/$ResourceGroupName" -ForegroundColor Blue
        
    } else {
        throw "Deployment failed. Check the error messages above."
    }

} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`nDeployment script completed!" -ForegroundColor Green