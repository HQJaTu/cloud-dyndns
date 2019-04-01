# Cloud DynDNS

Bring up dynamic DNS updates up-to-speed with current cloud computing.

When a host with a dynamic IP-address boots, it should be able to do a simple request to a chosen DNS-provider like AWS, Azure or Rackspace to inform its current IP-address.

There shouldn't be any need to keep pinging a daemon somewhere or do dynamic DNS-updates with complex authentication.
Just make sure there is an automated API-request sent to your own provider during system boot (or IP-address change) and be done with it!

## Installation
Given the early stage of development, some manual tinkering is required to get this working.

1. Copy file `cloud_dyndns.py` into `/usr/sbin/`
1. Copy directory `clouddns/` into your local Python 3 library path. I'm using `/usr/lib64/python3.6/site-packages` on my distro.
   * To find your library paths, run: `python3 -c 'import sys; print(sys.path)'`

## To Do:
1. Create a proper Pip-package out of this
1. Add more service providers
1. Add documentation of appropriate `ifup`-hook to run DNS update.

## systemd support

See file `cloud-dyndns@.service`.
It is a systemd template service of type _oneshot_.

### systemd example usage
```bash
systemctl start cloud-dyndns@rackspace-eth1
```
This would read the YAML-configuration from file `/etc/cloud-dyndns/rackspace-eth1.yaml` and do a DNS-update, if one is needed.

```bash
systemctl status cloud-dyndns@rackspace-eth1
```
A _status_ request will see how the previous run was went.

Note: When status displays "_inactive (dead)_", that's prefectly normal. This service is not running for a very long time.

```bash
systemctl enable cloud-dyndns@rackspace-eth1
```
An _enable_ will make sure the service is run on system boot.

## Updating DNS on interface up
Running update on system boot will do it for most of us.
Sometimes the network interface keeps flapping and an update will be needed on any `ifup`.
All Linux distros provide a hook, which is run on interface up.

TBD: Explain how to run systemd-service on `ifup`.

## Service providers

### Currently supported:
* Rackspace Cloud DNS

### Soon supported:
* Amazon Web Services, Route 53
