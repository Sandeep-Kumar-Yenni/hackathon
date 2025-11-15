# Azure App Service Deployment Script for FastAPI Python App
# App Service: vendorxapi
# Resource Group: NeoCode Nexus

param(
    [Parameter(Mandatory=$false)]
    [string]$AppServiceName = "vendorxapi",
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "NeoCode Nexus"
)

Write-Host "🚀 Deploying FastAPI App to Azure App Service..." -ForegroundColor Green
Write-Host "App Service: $AppServiceName" -ForegroundColor Cyan
Write-Host "Resource Group: $ResourceGroup" -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is installed
$azCliInstalled = Get-Command az -ErrorAction SilentlyContinue
if (-not $azCliInstalled) {
    Write-Host "❌ Error: Azure CLI is not installed." -ForegroundColor Red
    Write-Host "Please install Azure CLI from: https://aka.ms/installazurecliwindows" -ForegroundColor Yellow
    exit 1
}

# Check if logged in
Write-Host "🔐 Checking Azure login status..." -ForegroundColor Yellow
$account = az account show 2>$null
if (-not $account) {
    Write-Host "Please log in to Azure..." -ForegroundColor Yellow
    az login
}

# Navigate to backend directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if Python is installed
Write-Host ""
Write-Host "🐍 Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green

# Check if requirements.txt exists
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ Error: requirements.txt not found in backend directory" -ForegroundColor Red
    exit 1
}

# Create deployment package
Write-Host ""
Write-Host "📦 Creating deployment package..." -ForegroundColor Yellow
if (Test-Path "deploy.zip") {
    Remove-Item "deploy.zip" -Force
}

# Create a temporary directory for deployment
$tempDir = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_ }
Write-Host "📁 Using temporary directory: $tempDir" -ForegroundColor Gray

# Copy all necessary files
Write-Host "📋 Copying application files..." -ForegroundColor Yellow
Copy-Item -Path "app" -Destination "$tempDir\app" -Recurse -Force
Copy-Item -Path "requirements.txt" -Destination "$tempDir\requirements.txt" -Force

# Create startup script for Azure App Service
Write-Host "📝 Creating startup script..." -ForegroundColor Yellow
$startupScript = @"
#!/bin/bash
gunicorn app.main:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120
"@
$startupScript | Out-File -FilePath "$tempDir\startup.sh" -Encoding utf8 -NoNewline

# Alternative: Create startup command file (Azure App Service uses this)
$startupCommand = "gunicorn app.main:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120"
Write-Host "   Startup command: $startupCommand" -ForegroundColor Gray

# Create .deployment file for Azure
$deploymentFile = @"
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
"@
$deploymentFile | Out-File -FilePath "$tempDir\.deployment" -Encoding utf8

# Create web.config for Azure App Service (optional, for custom configuration)
$webConfig = @"
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="httpPlatformHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified" />
    </handlers>
    <httpPlatform processPath="D:\home\Python311\python.exe"
                  arguments="-m gunicorn app.main:app --bind 0.0.0.0:%HTTP_PLATFORM_PORT% --workers 4 --worker-class uvicorn.workers.UvicornWorker"
                  stdoutLogEnabled="true"
                  stdoutLogFile="D:\home\LogFiles\python.log"
                  startupTimeLimit="20"
                  startupRetryCount="10">
    </httpPlatform>
  </system.webServer>
</configuration>
"@
$webConfig | Out-File -FilePath "$tempDir\web.config" -Encoding utf8

# Create deployment zip
Write-Host "📦 Compressing deployment package..." -ForegroundColor Yellow
Compress-Archive -Path "$tempDir\*" -DestinationPath "deploy.zip" -Force
Write-Host "✅ Deployment package created" -ForegroundColor Green

# Clean up temp directory
Remove-Item -Path $tempDir -Recurse -Force

# Configure startup command in Azure App Service
Write-Host ""
Write-Host "⚙️  Configuring Azure App Service startup command..." -ForegroundColor Yellow
az webapp config set `
    --resource-group $ResourceGroup `
    --name $AppServiceName `
    --startup-file "gunicorn app.main:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120"

# Set Python version (if not already set)
Write-Host "🐍 Setting Python version..." -ForegroundColor Yellow
az webapp config appsettings set `
    --resource-group $ResourceGroup `
    --name $AppServiceName `
    --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true `
    PYTHON_VERSION=3.11

# Deploy to Azure App Service
Write-Host ""
Write-Host "📤 Deploying to Azure App Service: $AppServiceName..." -ForegroundColor Yellow
az webapp deployment source config-zip `
    --resource-group $ResourceGroup `
    --name $AppServiceName `
    --src deploy.zip

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Your FastAPI app is now live at:" -ForegroundColor Cyan
    Write-Host "   https://$AppServiceName.azurewebsites.net" -ForegroundColor White
    Write-Host "   https://$AppServiceName.azurewebsites.net/docs (Swagger UI)" -ForegroundColor White
    Write-Host "   https://$AppServiceName.azurewebsites.net/redoc (ReDoc)" -ForegroundColor White
    Write-Host ""
    Write-Host "📝 Next steps:" -ForegroundColor Yellow
    Write-Host "   1. Configure environment variables in Azure Portal:" -ForegroundColor White
    Write-Host "      App Service → Configuration → Application settings" -ForegroundColor Gray
    Write-Host "   2. Add your database connection string:" -ForegroundColor Gray
    Write-Host "      SQLALCHEMY_DATABASE_URL or individual SQL Server settings" -ForegroundColor Gray
    Write-Host "   3. Verify the app is running:" -ForegroundColor Gray
    Write-Host "      https://$AppServiceName.azurewebsites.net/" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "❌ Deployment failed. Please check the error messages above." -ForegroundColor Red
    exit 1
}

# Clean up
Write-Host ""
Write-Host "🧹 Cleaning up temporary files..." -ForegroundColor Yellow
Remove-Item deploy.zip -Force -ErrorAction SilentlyContinue
Write-Host "✅ Done!" -ForegroundColor Green

