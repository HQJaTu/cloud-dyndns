# Cloud DynDNS

Bring up dynamic DNS updates up-to-speed with current cloud computing.

When a host with a dynamic IP-address boots, it should be able to do a simple request to a chosen DNS-provider like AWS, Azure or Rackspace to inform its current IP-address.

There shouldn't be any need to keep pinging a daemon somewhere or do dynamic DNS-updates with complex authentication.
Just make sure there is an automated API-request sent to your own provider during system boot (or IP-address change) and be done with it!

## Installation

### Prerequisites
1. Prerequisite: clone the git-repo into a local machine
1. (optional) Prerequisite: Install Python-package _wheel_

### Using `pip`
1. Run local install:
   * `pip install .`
1. Done!

### Manually
If automation is not your thing, some manual tinkering to get this working.

1. Copy file `cloud-dyndns.py` into `/usr/local/sbin/`
   * Note: `pip` will land `cloud-dyndns.py` into `/usr/local/bin/`. It cannot
     deploy into any `sbin/`.
1. Copy directory `clouddns/` into your local Python 3 library path. I'm using
   `/usr/local/lib64/python3.9/site-packages` on my distro.
   * To find your library paths, run: `python3 -c 'import sys; print(sys.path)'`
1. Done!

## To Do:
1. Add more service providers
1. Add documentation of appropriate `ifup`-hook to run DNS update.

## systemd support

See file `systemd/cloud-dyndns@.service`.
It is a systemd template service of type _oneshot_.

Read https://www.freedesktop.org/software/systemd/man/systemd.unit.html for
more information on `systemd.unit`s. Among all the information,
documentation states following:
> As mentioned above, a unit may be instantiated from a template file.
> This allows creation of multiple units from a single configuration file.

Addressing a template unit requires specifying the identifying detail after at (@) sign.
See examples below.

### Installation
1. Copy `systemd/cloud-dyndns@.service` into `/etc/systemd/system/`
1. Reload systemd with `systemctl daemon-reload` to see the newly added unit
1. (if `pip install`) Symlink `ln -s /usr/local/bin/cloud-dyndns.py /usr/sbin/` for tool to exist in `sbin/`.
1. Done!

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
systemctl enable --now cloud-dyndns@rackspace-eth1
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
