# Azure DNS

## Authentication
Note: This code can only utilize service principals for authentication.

Prerequirements:
* Azure tenant ID
* Azure subscription ID of DNS zone
* Service principal ID and secret
* Python module `azure-mgmt-dns`. Those not familiar with Python, you need to `pip3 install` the package.

To confuse you, all four of those look like a GUID.

### Example `cloud-dyndns.py` configuration file:
```yaml

---

dyndns:
  provider: azure
  interface: eth1
  hostname: foo-bar.com
  api_credentials_file: /etc/cloud-dyndns/.azure-redentials.json
```

### Example authentication JSON-file:

In above example, this would be `/etc/cloud-dyndns/.azure-redentials.json`:
```json
{
  "tenant-id": "11111111-aaaa-3333-bbbb-555555555555",
  "subscription-id": "ffffffff-6666-eeee-7777-dddddddddddd",
  "spn-user": "22222222-cccc-4444-bbbb-888888888888",
  "password": "12345678-1234-1234-1234-123456789abc"
}
```

### Authentication from command-line
Cannot be done. CLI doesn't have suitable arguments for receiving tenant nor subscription IDs.

## Recipes for creating service principals for updating DNS-records

### Create new service principal from Azure Portal
TBD.
(Tons of screen captures needed for this)

### Create new service principal from Azure CLI
For people not familiar with Azure or Azure terminology: A service principal (or SPN) is restricted "machine user"
intended to be used only for a specific purpose. An example of SPN usage would be to grant access to update DNS from
external server.

Recipe for Azure CLI:

1. Login (if not already done so)
    * `az login`
1. Find out the DNS zone ID/IDs this principal will be updating:
    * Command for that would be something like:
    * `az network dns zone list` 
    * From the listing, get a zone ID. It is very long path-like thing starting with a:
    /subscriptions/_\<your Azure subscription ID here\>_/resourceGroups/_\<resource group name here\>_/providers/Microsoft.Network/...
1. Create new service principal with access limited to a specific DNS-zone with access to read/write/delete any
records in that zone (role: Contributor).
    * Choose suitable user name for your SPN
    * `az ad sp create-for-rbac --name <username> --role "DNS Zone Contributor" --scopes <comma separated list of DNS zone IDs here>`
1. Command will output two necessary items:
    1. App ID of the newly created SPN
    1. Secret (password) of the newly created SPN
1. Tenant and subscription IDs can be shown with a:
    * `az account show`

### Create new service principal from Powershell (RM-library)
Note: RM-library has been deprecated. Recommended way is to go for PowerShell 6 (core) and install Az-module.

Recipe for Powershell:

1. Login (if not already done so)
    * `Login-AzureRmAccount`
1. Find out the DNS zone ID/IDs this principal will be updating:
    * Command for that would be something like:
    * `Get-AzureRmDnsZone`
    * From the listing, get a zone ID. It is very long path-like thing starting with a:
    /subscriptions/_\<your Azure subscription ID here\>_/resourceGroups/_\<resource group name here\>_/providers/Microsoft.Network/...
1. Create new service principal with access limited to a specific DNS-zone with access to read/write/delete any
records in that zone (role: Contributor).
    * Choose suitable user name for your SPN
    * `New-AzureRmADServicePrincipal -DisplayName <username> -Role "DNS Zone Contributor" -Scope <DNS zone IDs here>`
1. Command will output two necessary items:
    1. App ID of the newly created SPN
    1. Secret (password) of the newly created SPN
1. Tenant and subscription IDs can be shown with a:
    * `Get-AzureRmContext`
1. Any addtitional zone need to be added with a:
    * `New-AzureRmRoleAssignment`-cmdlet
