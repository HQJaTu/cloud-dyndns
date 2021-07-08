#!/usr/bin/env python3

# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python

from azure.mgmt.dns import DnsManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from msrestazure.azure_exceptions import CloudError
import os.path
import sys
import json
from pathlib import Path
import re
from ..base_cloud import BaseCloud
import logging

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

log = logging.getLogger(__name__)


class Azure(BaseCloud):
    """
    Azure DNS implementation
    See: https://docs.microsoft.com/en-us/python/api/overview/azure/dns?view=azure-python
    """
    dns_client = None
    dns_zone = None
    dns_zone_rg = None

    def is_authenticated(self):
        if self.dns_client is not None:
            return True

        return False

    def authenticate(self, api_creds):
        """
        See: https://docs.microsoft.com/en-us/python/azure/python-sdk-azure-authenticate?view=azure-python
        :param api_creds: tuple of access credentials, see _read_credentials_file()
        :return:
        """
        credentials = ServicePrincipalCredentials(
            client_id=api_creds[2],
            secret=api_creds[3],
            tenant=api_creds[0]
        )

        self.dns_client = DnsManagementClient(
            credentials,
            api_creds[1]
        )

        # Sanity: See that an access token exists.
        if not self.dns_client._client.config.credentials.token['is_mrrt']:
            log.error("Could not login into Azure!")
            raise RuntimeError("Could not login into Azure!")

        log.info("Authenticated into Azure ok")

    def get_current_ip_from_dns(self, host, domain):
        """
        Get the current recurd
        :param host: hostname of the FQDN, without dot
        :param domain: domain part of the FQDN
        :return: Object|None, currently set IP-address
        """
        self.dns_zone = None
        self.dns_zone_rg = None
        zones = self.dns_client.zones.list()
        for zone in zones:
            if zone.name == domain:
                self.dns_zone = zone
                break
        if not self.dns_zone:
            log.error("Didn't find domain {0}".format(domain))
            raise RuntimeError("Didn't find domain {0}".format(domain))

        resource_group_match = re.search("/resourceGroups/([^/]+)/", self.dns_zone.id)
        if not resource_group_match:
            log.error("Invalid internal Azure resource ID for domain {0}".format(domain))
            raise RuntimeError("Invalid internal Azure resource ID for domain {0}".format(domain))

        self.dns_zone_rg = resource_group_match.group(1)

        try:
            record_set = self.dns_client.record_sets.get(
                self.dns_zone_rg,
                self.dns_zone.name,
                host,
                'A'
            )
        except CloudError as exc:
            if exc.status_code == 404:
                log.debug("No A-record for {0}.{1}. Ignored.".format(host, domain))
                # Nope, that record doesn't exist.
                return None, None

            log.exception("Failed to read A-record for {0}.{1}".format(host, domain))
            raise exc

        current_ipv4 = record_set.arecords[0].ipv4_address
        log.info("Current IPv4 address for {0}.{1} is {2}".format(host, domain, current_ipv4))

        # Oh yes, we have that!
        return record_set, current_ipv4

    def update_rr(self, host, domain, ip, record_to_update):
        record_set = self.dns_client.record_sets.create_or_update(
            self.dns_zone_rg,
            domain,
            host,
            'A',
            {
                "ttl": 300,
                "arecords": [
                    {
                        "ipv4_address": ip
                    }
                ]
            }
        )
        log.info("Updated IPv4 address for {0}.{1} as {2}".format(host, domain, ip))

        return record_set

    @staticmethod
    def _read_credentials_file(creds_file):
        """
        Read given credentials file
        :param creds_file:
        :return: tuple, API user and API key
        """
        if not os.path.isfile(creds_file):
            log.error("Azure service principal credentials file {0} doesn't exist!".format(creds_file))
            raise RuntimeError("Azure service principal credentials file {0} doesn't exist!".format(creds_file))

        data = json.load(open(creds_file))
        log.debug("Loaded Azure credentials from {0}".format(creds_file))

        return data['tenant-id'], data['subscription-id'], data['spn-user'], data['password']

    @staticmethod
    def default_credentials_file():
        if 'HOME' in os.environ:
            default_credentials_filename = os.environ['HOME'] + "/.azure.auth"
        else:
            default_credentials_filename = str(Path.home()) + "/.azure.auth"

        return default_credentials_filename

    def debug(self, debugging):
        #pyrax.set_http_debug(debugging)
        pass
