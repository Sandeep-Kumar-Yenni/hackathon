#!/bin/bash
# Azure App Service Deployment Script for FastAPI Python App
# App Service: vendorxapi
# Resource Group: NeoCode Nexus

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Configuration
APP_SERVICE_NAME="${1:-vendorxapi}"
RESOURCE_GROUP="${2:-NeoCode Nexus}"

echo -e "${GREEN}🚀 Deploying FastAPI App to Azure App Service...${NC}"
echo -e "${CYAN}App Service: $APP_SERVICE_NAME${NC}"
echo -e "${CYAN}Resource Group: $RESOURCE_GROUP${NC}"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Error: Azure CLI is not installed.${NC}"
    echo -e "${YELLOW}Please install Azure CLI from: https://aka.ms/installazurecli${NC}"
    exit 1
fi

# Check if logged in
echo -e "${YELLOW}🔐 Checking Azure login status...${NC}"
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Please log in to Azure...${NC}"
    az login
fi

# Navigate to script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python is installed
echo ""
echo -e "${YELLOW}🐍 Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Error: Python is not installed or not in PATH${NC}"
    exit 1
fi

PYTHON_CMD=$(command -v python3 || command -v python)
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo -e "${GREEN}✅ Found: $PYTHON_VERSION${NC}"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: requirements.txt not found in backend directory${NC}"
    exit 1
fi

# Create deployment package
echo ""
echo -e "${YELLOW}📦 Creating deployment package...${NC}"
rm -f deploy.zip

# Create a temporary directory for deployment
TEMP_DIR=$(mktemp -d)
echo -e "${GRAY}📁 Using temporary directory: $TEMP_DIR${NC}"

# Copy all necessary files
echo -e "${YELLOW}📋 Copying application files...${NC}"
cp -r app "$TEMP_DIR/app"
cp requirements.txt "$TEMP_DIR/requirements.txt"

# Create startup script for Azure App Service
echo -e "${YELLOW}📝 Creating startup script...${NC}"
cat > "$TEMP_DIR/startup.sh" << 'EOF'
#!/bin/bash
gunicorn app.main:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120
EOF
chmod +x "$TEMP_DIR/startup.sh"

# Create startup command
STARTUP_CMD="gunicorn app.main:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120"
echo -e "${GRAY}   Startup command: $STARTUP_CMD${NC}"

# Create .deployment file for Azure
cat > "$TEMP_DIR/.deployment" << 'EOF'
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
EOF

# Create web.config for Azure App Service (optional, for custom configuration)
cat > "$TEMP_DIR/web.config" << 'EOF'
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
EOF

# Create deployment zip
echo -e "${YELLOW}📦 Compressing deployment package...${NC}"
cd "$TEMP_DIR"
zip -r "$SCRIPT_DIR/deploy.zip" . -q
cd "$SCRIPT_DIR"
echo -e "${GREEN}✅ Deployment package created${NC}"

# Clean up temp directory
rm -rf "$TEMP_DIR"

# Configure startup command in Azure App Service
echo ""
echo -e "${YELLOW}⚙️  Configuring Azure App Service startup command...${NC}"
az webapp config set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_SERVICE_NAME" \
    --startup-file "gunicorn app.main:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120"

# Set Python version and build settings
echo -e "${YELLOW}🐍 Setting Python version and build settings...${NC}"
az webapp config appsettings set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_SERVICE_NAME" \
    --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true PYTHON_VERSION=3.11

# Deploy to Azure App Service
echo ""
echo -e "${YELLOW}📤 Deploying to Azure App Service: $APP_SERVICE_NAME...${NC}"
az webapp deployment source config-zip \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_SERVICE_NAME" \
    --src deploy.zip

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
    echo ""
    echo -e "${CYAN}🌐 Your FastAPI app is now live at:${NC}"
    echo -e "${WHITE}   https://$APP_SERVICE_NAME.azurewebsites.net${NC}"
    echo -e "${WHITE}   https://$APP_SERVICE_NAME.azurewebsites.net/docs (Swagger UI)${NC}"
    echo -e "${WHITE}   https://$APP_SERVICE_NAME.azurewebsites.net/redoc (ReDoc)${NC}"
    echo ""
    echo -e "${YELLOW}📝 Next steps:${NC}"
    echo -e "${WHITE}   1. Configure environment variables in Azure Portal:${NC}"
    echo -e "${GRAY}      App Service → Configuration → Application settings${NC}"
    echo -e "${WHITE}   2. Add your database connection string:${NC}"
    echo -e "${GRAY}      SQLALCHEMY_DATABASE_URL or individual SQL Server settings${NC}"
    echo -e "${WHITE}   3. Verify the app is running:${NC}"
    echo -e "${GRAY}      https://$APP_SERVICE_NAME.azurewebsites.net/${NC}"
else
    echo ""
    echo -e "${RED}❌ Deployment failed. Please check the error messages above.${NC}"
    exit 1
fi

# Clean up
echo ""
echo -e "${YELLOW}🧹 Cleaning up temporary files...${NC}"
rm -f deploy.zip
echo -e "${GREEN}✅ Done!${NC}"

