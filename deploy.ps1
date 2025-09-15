# Azure AI RAG Infrastructure Deployment Script (PowerShell)
# This script deploys the Azure infrastructure needed for the AI RAG project

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory=$false)]
    [string]$ProjectName = "airag",
    
    [Parameter(Mandatory=$false)]
    [switch]$Help
)

function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Status {
    param([string]$Message)
    Write-ColoredOutput "[INFO] $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColoredOutput "[WARNING] $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColoredOutput "[ERROR] $Message" "Red"
}

function Show-Usage {
    Write-Host ""
    Write-Host "Azure AI RAG Infrastructure Deployment Script"
    Write-Host ""
    Write-Host "USAGE:"
    Write-Host "    .\deploy.ps1 -ResourceGroupName <name> [-SubscriptionId <id>] [-Location <location>] [-ProjectName <name>]"
    Write-Host ""
    Write-Host "PARAMETERS:"
    Write-Host "    -ResourceGroupName    (Required) Name of the Azure resource group to create/use"
    Write-Host "    -SubscriptionId       (Optional) Azure subscription ID"
    Write-Host "    -Location            (Optional) Azure region (default: eastus)"
    Write-Host "    -ProjectName         (Optional) Project name prefix for resources (default: airag)"
    Write-Host "    -Help                Show this help message"
    Write-Host ""
    Write-Host "EXAMPLE:"
    Write-Host "    .\deploy.ps1 -ResourceGroupName 'my-ai-rag-rg' -Location 'westus2' -ProjectName 'myaiproject'"
    Write-Host ""
}

# Show help if requested
if ($Help) {
    Show-Usage
    exit 0
}

# Validate required parameters
if ([string]::IsNullOrEmpty($ResourceGroupName)) {
    Write-Error "ResourceGroupName is required"
    Show-Usage
    exit 1
}

Write-Status "Starting Azure AI RAG infrastructure deployment..."

# Check if Azure PowerShell module is installed
try {
    Import-Module Az -ErrorAction Stop
} catch {
    Write-Error "Azure PowerShell module is not installed. Please install it using: Install-Module -Name Az -AllowClobber -Scope CurrentUser"
    exit 1
}

# Connect to Azure if not already connected
try {
    $context = Get-AzContext
    if ($null -eq $context) {
        Write-Status "Connecting to Azure..."
        Connect-AzAccount
    }
} catch {
    Write-Error "Failed to connect to Azure. Please run Connect-AzAccount first."
    exit 1
}

# Set subscription if provided
if (![string]::IsNullOrEmpty($SubscriptionId)) {
    Write-Status "Setting subscription to $SubscriptionId"
    Set-AzContext -SubscriptionId $SubscriptionId
}

# Get current subscription info
$currentContext = Get-AzContext
$currentSubscription = $currentContext.Subscription.Name
$currentSubscriptionId = $currentContext.Subscription.Id
Write-Status "Using subscription: $currentSubscription ($currentSubscriptionId)"

# Create resource group if it doesn't exist
Write-Status "Creating resource group '$ResourceGroupName' in location '$Location'"
$resourceGroup = New-AzResourceGroup -Name $ResourceGroupName -Location $Location -Force

# Create temporary parameters file
$timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
$deployedBy = $env:USERNAME
if ([string]::IsNullOrEmpty($deployedBy)) {
    $deployedBy = $env:USER
}

$parametersObject = @{
    projectName = @{ value = $ProjectName }
    location = @{ value = $Location }
    openAiSku = @{ value = "S0" }
    searchSku = @{ value = "basic" }
    storageSku = @{ value = "Standard_LRS" }
    tags = @{ 
        value = @{
            project = "hackathon2025"
            purpose = "ai-rag"
            environment = "dev"
            deployedBy = $deployedBy
            deployedAt = $timestamp
        }
    }
}

# Deploy the infrastructure
Write-Status "Deploying Azure infrastructure..."
$deploymentName = "ai-rag-deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

try {
    $deployment = New-AzResourceGroupDeployment `
        -ResourceGroupName $ResourceGroupName `
        -Name $deploymentName `
        -TemplateFile "infrastructure/main.bicep" `
        -TemplateParameterObject $parametersObject `
        -Verbose
    
    Write-Status "Deployment completed successfully!"
    
    # Display deployment outputs
    $outputs = $deployment.Outputs
    
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "DEPLOYMENT SUMMARY" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "Resource Group: $ResourceGroupName"
    Write-Host "Location: $Location"
    Write-Host "Project Name: $ProjectName"
    Write-Host ""
    Write-Host "KEY ENDPOINTS:" -ForegroundColor Yellow
    Write-Host "OpenAI Endpoint: $($outputs.openAiEndpoint.Value)"
    Write-Host "Search Endpoint: $($outputs.searchEndpoint.Value)"
    Write-Host "Key Vault: $($outputs.keyVaultName.Value)"
    Write-Host "Storage Account: $($outputs.storageAccountName.Value)"
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Warning "IMPORTANT: API keys are stored in Key Vault '$($outputs.keyVaultName.Value)'"
    Write-Warning "Make sure you have appropriate permissions to access the Key Vault"
    
    Write-Status "Next steps:"
    Write-Host "1. Configure your application with the endpoints above"
    Write-Host "2. Retrieve API keys from Key Vault"
    Write-Host "3. Upload your documents to the storage account"
    Write-Host "4. Set up your RAG application using the provided Python code"
    
} catch {
    Write-Error "Deployment failed: $($_.Exception.Message)"
    exit 1
}

Write-Status "Deployment script completed!"