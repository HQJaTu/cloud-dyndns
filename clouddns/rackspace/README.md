# Rackspace Cloud DNS

## Installation
1. Dependencies:
    * `pip install -r clouddns/rackspace/requirements.txt`
1. Dependency, Pyrax:
    * See: https://github.com/HQJaTu/cloud-dyndns/blob/master/clouddns/rackspace/README-Pyrax.md
    * `pip install git+https://github.com/HQJaTu/pyrax.git`
1. Done!

## Authentication

In Rackspace management console, create an API-user with permissions:
_DNS, Creator (View, Create, Edit)_

The API-username and password can be:
* used directly in configuration file (insecure)
* stored to JSON-file with user-only access (secure)

### Example `cloud-dyndns.py` configuration file:
```yaml

---

dyndns:
  provider: rackspace
  interface: eth1
  hostname: foo-bar.com
  api_credentials_file: /etc/cloud-dyndns/.rackspace-api-credentials.json
```

### Example authentication JSON-file:

In above example, this would be `/etc/cloud-dyndns/.rackspace-api-credentials.json`:
```json
{
  "user": "my rackspace user",
  "key": "my rackspace API key"
}
```

## See other:
* https://github.com/HQJaTu/acme.sh/blob/rackspace_api/dnsapi/dns_rackspace.sh, Let's Encrypt Acme.sh utility DNS-plugin to automatically verify SSL certificate domains via Rackspace DNS.
