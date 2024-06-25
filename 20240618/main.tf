# Configure the Azure provider
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.108.0"
    }
  }
  required_version = ">= 0.14.9"
}
provider "azurerm" {
  features {}
}

variable "AZURE_RESOURCE_GROUP" {
  type = string
}

variable "AZURE_APP_SERVICE_REPO_URL" {
  type = string
}

variable "AZURE_REGION" {
  type    = string
  default = "eastus"
}

# Generate a random integer to create a globally unique name
resource "random_integer" "ri" {
  min = 10000
  max = 99999
}

# Create the resource group
resource "azurerm_resource_group" "rg" {
  name     = var.AZURE_RESOURCE_GROUP
  location = "westus"
}

# Create the Linux App Service Plan
resource "azurerm_service_plan" "appserviceplan" {
  name                = "webapp-${random_integer.ri.result}"
  location            = var.AZURE_REGION
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "S1"
}

# Create the web app, pass in the App Service Plan ID
resource "azurerm_linux_web_app" "nodered" {
  name                = "nodered-${random_integer.ri.result}"
  location            = var.AZURE_REGION
  resource_group_name = azurerm_resource_group.rg.name
  service_plan_id     = azurerm_service_plan.appserviceplan.id
  https_only          = true
  app_settings = {
    # https://learn.microsoft.com/en-us/azure/app-service/reference-app-settings
    # For a custom container, the custom port number on the container for App Service to route requests to. By default, App Service attempts automatic port detection of ports 80 and 8080. This setting isn't injected into the container as an environment variable.
    WEBSITES_PORT = "1880"
  }
  site_config {
    minimum_tls_version = "1.2"
    always_on           = "true"
    application_stack {
    # https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/linux_web_app#application_stack
      docker_image_name   = "nodered/node-red:3.1.10-14"
      docker_registry_url = "https://index.docker.io"
    }
  }
}

resource "azurerm_linux_web_app" "python" {
  name                = "python-${random_integer.ri.result}"
  location            = var.AZURE_REGION
  resource_group_name = azurerm_resource_group.rg.name
  service_plan_id     = azurerm_service_plan.appserviceplan.id
  https_only          = true
  app_settings = {
  }
  site_config {
    minimum_tls_version = "1.2"
    app_command_line = ". 20240000/a-flask-app/entrypoint.sh"
    application_stack {
      python_version = "3.10"
    }
  }
}

resource "azurerm_app_service_source_control" "python_scm" {
  app_id   = azurerm_linux_web_app.python.id
  repo_url = var.AZURE_APP_SERVICE_REPO_URL
  branch   = "master"
  use_manual_integration = true
  use_mercurial      = false
}

resource "azurerm_mysql_flexible_server" "example" {
  name                   = "its-rizzoli-idt-mysql-${random_integer.ri.result}"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  administrator_login    = "psqladmin"
  // WARN DONT DO THIS, USE SecOps services like Doppler and Azure Key Vault
  administrator_password = "H@Sh1CoR3!"
  sku_name = "GP_Standard_D2ds_v4"
}

output "mysql_fqdn" {
  value = azurerm_mysql_flexible_server.example.fqdn
}
