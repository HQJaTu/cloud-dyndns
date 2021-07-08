#!/usr/bin/env python3

# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python

import argparse
import os.path
import sys
import yaml
import socket
import netifaces
import requests
import json


# This file is part of Cloud DynDNS.  Cloud DynDNS is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright (c) Jari Turkia


def read_config_file(config_file, args_to_update):
    config_in = None
    with open(config_file, 'r') as stream:
        try:
            config_in = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            sys.stderr.write(
                "Error: Error reading configuration file %s. Cannot continue!\nError: %s\n\n" % (config_file, exc))
            exit(1)

    # Look for known tags in the configuration
    if 'dyndns' not in config_in.keys():
        sys.stderr.write(
            "Error: Malformed configuration file %s. Cannot continue!\n\n" % (config_file,))
        exit(1)

    dyndns_config = config_in['dyndns']
    for key in dyndns_config.keys():
        if isinstance(dyndns_config[key], str) or isinstance(dyndns_config[key], bool):
            pass
        else:
            sys.stderr.write(
                "Error: Malformed configuration file %s. Value of key '%s' invalid. Cannot continue!\n\n" % (config_file, key))
            exit(1)

        if key == 'provider':
            args_to_update.provider = dyndns_config[key]
        elif key == 'interface':
            args_to_update.interface = dyndns_config[key]
        elif key == 'ip_address':
            args_to_update.ip_address = dyndns_config[key]
        elif key == 'detect_public_ip':
            args_to_update.detect_public_ip = True
        elif key == 'public_ip_from_platform':
            args_to_update.detect_public_ip = dyndns_config[key]
        elif key == 'hostname':
            args_to_update.hostname = dyndns_config[key]
        elif key == 'api_user':
            args_to_update.api_user = dyndns_config[key]
        elif key == 'api_key':
            args_to_update.api_key = dyndns_config[key]
        elif key == 'api_credentials_file':
            args_to_update.api_credentials_file = dyndns_config[key]

    # Done!


def get_current_ip_from_interface(iface):
    """
    Query the IPv4-address for given interface
    :param iface:
    :return:
    """
    ips = netifaces.ifaddresses(iface)
    if not ips[netifaces.AF_INET]:
        sys.stderr.write("Error: Interface %s has no IPv4-addresses. Cannot continue!" % iface)
        exit(1)

    if len(ips[netifaces.AF_INET]) > 1:
        sys.stderr.write("Error: Interface %s has multiple IPv4-addresses. Cannot continue!" % iface)
        exit(1)

    # Return the only IPv4-address there is.
    return ips[netifaces.AF_INET][0]['addr']


def get_ipinfoio_address():
    resp = requests.get('http://ipinfo.io/json')
    data = resp.json()
    if resp.status_code != requests.codes.ok:
        return None

    return data['ip']


def main():
    provider = None
    default_hostname = socket.getfqdn()
    default_credentials_filename = None

    parser = argparse.ArgumentParser(description='Update interface IP-address to a Cloud DNS')
    parser.add_argument('-p', '--provider',
                        help='Cloud provider to use. Currently supported: Rackspace')
    parser.add_argument('-i', '--interface',
                        help='The interface to read IP-address from to set into DNS')
    parser.add_argument('--ip-address', metavar="IPV4-ADDRESS",
                        help="Don't try to read IP-address, just use a static one.")
    parser.add_argument('--ip-address-detect-public', '-d', dest='detect_public_ip', action='store_true',
                        help="Don't try to read IP-address, see what ipinfo.io detects.")
    parser.add_argument('--ip-address-from-platform', metavar="PLATFORM-TYPE",
                        dest='public_ip_from_platform',
                        help="Don't try to read IP-address, see what virtualisation platform has. "
                             "Works for AWS and Azure VMs.")
    parser.add_argument('--hostname', default=default_hostname,
                        help='The hostname to parse DNS zone and RR from. Default: %s' % default_hostname)
    parser.add_argument('--api-user',
                        help='Cloud provider API user to use for authentication')
    parser.add_argument('--api-key',
                        help='Cloud provider API key to use for authentication')
    parser.add_argument('--api-credentials-file',
                        help='JSON-file with Cloud provider API credentials.')
    parser.add_argument('--config',
                        help='YAML-configuration to use. Any command-line arguments will override config-file.')
    parser.add_argument('--dry-run', action='store_true',
                        help="Don't do any changes. Authenticate to Cloud provider and display what would be done.")
    parser.add_argument('--debug-cloud-api', action='store_true',
                        help="Display tons of information for Cloud provider API-access.")

    args = parser.parse_args()

    # Reading a configuration file?
    if args.config:
        if not os.path.isfile(args.config):
            sys.stderr.write("Error: Configuration file %s doesn't exist, cannot continue.\n\n" % args.config)
            parser.print_help()
            exit(2)

        read_config_file(args.config, args)

    # Need a provider to continue
    if not args.provider:
        sys.stderr.write("Error: Need --provider, cannot continue.\n\n")
        parser.print_help()
        exit(2)

    # Import the implementation of given provider
    if args.provider == 'rackspace':
        from clouddns.rackspace.rackspace import Rackspace
        provider = Rackspace()
        default_credentials_filename = provider.default_credentials_file()
    if args.provider == 'azure':
        from clouddns.azure.azure import Azure
        provider = Azure()
        default_credentials_filename = provider.default_credentials_file()
    else:
        sys.stderr.write("Error: Unknown provider %s, cannot continue.\n\n" % args.provider)
        parser.print_help()
        exit(2)

    # Confirm, that there exists credentials
    if args.api_user and args.api_key:
        api_credentials = (args.api_user, args.api_key)
    elif args.api_credentials_file and args.api_credentials_file != default_credentials_filename:
        # A credentials-file was given
        api_credentials = provider._read_credentials_file(args.api_credentials_file)
    elif default_credentials_filename and os.path.isfile(default_credentials_filename):
        # Using default credentials file for given provider
        api_credentials = provider._read_credentials_file(default_credentials_filename)
    elif not args.dry_run:
        sys.stderr.write("Error: Cloud provider API credentials missing, cannot continue.\n\n")
        parser.print_help()
        exit(2)

    # IPv4-address given on CLI?
    if args.ip_address:
        # Using static one. No need to check for interface.
        ip_to_use = args.ip_address
    elif args.detect_public_ip:
        ip_to_use = get_ipinfoio_address()
        if not ip_to_use:
            sys.stderr.write("Error: Failed to get IPv4 address from ipinfo.io")
            exit(1)
    elif args.public_ip_from_platform:
        if args.public_ip_from_platform.lower() == 'aws':
            ip_to_use = provider.get_current_ipv4_from_aws_vm_metadata()
        elif args.public_ip_from_platform.lower() == 'azure':
            ip_to_use = provider.get_current_ipv4_from_azure_vm_metadata()
        else:
            sys.stderr.write("Error: Given platform '%s' not known.\n\n" % args.public_ip_from_platform)
            parser.print_help()
            exit(2)

        if not ip_to_use:
            sys.stderr.write("Error: Failed to get IPv4 address from platform '%s'" % args.public_ip_from_platform)
            exit(1)
    else:
        # Detect, check that we have interface
        if not args.interface:
            sys.stderr.write("Error: Need interface to query IP-address for, cannot continue.\n\n")
            parser.print_help()
            exit(2)

        ip_to_use = get_current_ip_from_interface(args.interface)

    # Check the FQDN hostname
    hostname_to_use = args.hostname.split('.')[0]
    domain_to_use = '.'.join(args.hostname.split('.')[1:])
    if not hostname_to_use or not domain_to_use:
        sys.stderr.write("Error: Cannot parse hostname %s\n" % args.hostname)
        exit(2)

    # Debug API?:
    if args.debug_cloud_api:
        provider.debug(True)

    # Use the given credentials
    # Check if we have a valid token in cache.
    if not provider.is_authenticated():
        provider.authenticate(api_credentials)

    # Need to do anything?
    current_rr, current_ip = provider.get_current_ip_from_dns(hostname_to_use, domain_to_use)
    if current_ip and current_ip == ip_to_use:
        print("No need to update! %s already has address of %s" % (args.hostname, ip_to_use))
        exit(0)

    if args.dry_run:
        print("--dry-run specified!\nWould update %s to have address of %s. Quit." % (args.hostname, ip_to_use))
        exit(0)

    # Go update!
    provider.update_rr(hostname_to_use, domain_to_use, ip_to_use, current_rr)

    print("Updated %s to have address of %s. Done." % (args.hostname, ip_to_use))
    exit(0)


if __name__ == "__main__":
    main()
