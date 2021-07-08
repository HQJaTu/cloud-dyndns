#!/usr/bin/env python3

# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python

import pyrax
import pyrax.exceptions
import pytz
import os.path
import sys
import json
from tzlocal import get_localzone
from pathlib import Path
from ..base_cloud import BaseCloud


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


class Rackspace(BaseCloud):
    """
    Rackspace Cloud DNS implementation
    """

    # Rackspace API token cache file.
    # Same format than Let's Encrypt tool acme.sh has for Rackspace DNS plugin.
    token_file = '/tmp/.acme.rackspace.%s.token' % os.geteuid()

    def is_authenticated(self):
        """
        We do cache the authentication token, which is get by exchanging API credentials.
        If the cache exists and is still valid, no authentication is made.
        :return:
        """
        if not os.path.isfile(self.token_file):
            # No data in cache --> no token --> not authenticated
            return False

        data = json.load(open(self.token_file))
        token = data['access']['token']['id']
        tenant_id = data['access']['token']['tenant']['id']
        tenant_name = data['access']['token']['tenant']['name']

        pyrax.settings._settings['default']["identity_class"] = pyrax.rax_identity.RaxIdentity
        try:
            pyrax.auth_with_token(token, tenant_id=tenant_id, tenant_name=tenant_name)
        except pyrax.exceptions.AuthenticationFailed:
            return False

        return True

    def authenticate(self, api_creds):
        pyrax.set_setting('identity_type', 'rackspace')
        pyrax.set_credentials(api_creds[0], password=api_creds[1], authenticate=True)

        # Construct the authentication response body and store it as JSON.
        local_tz = get_localzone()
        expiry_in_utc = pyrax.identity.expires.astimezone(local_tz)
        expiry_in_utc = expiry_in_utc.astimezone(pytz.utc)

        json_out = {
            "access": {
                "token": {
                    "id": pyrax.identity.token,
                    "tenant": {
                        "name": pyrax.identity.tenant_name,
                        "id": pyrax.identity.tenant_id,
                    },
                    "expires": expiry_in_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                },
                "user": {
                    "id": pyrax.identity.user['id'],
                    "name": pyrax.identity.username,
                    "roles": pyrax.identity.user['roles']
                },
                "serviceCatalog": pyrax.identity.service_catalog
            }
        }

        # The file is rw- only for the current user.
        with open(os.open(self.token_file, os.O_CREAT | os.O_WRONLY, 0o600), 'w') as fp:
            json.dump(json_out, fp)

    def get_current_ip_from_dns(self, host, domain):
        """
        Get the current recurd
        :param host: hostname of the FQDN, without dot
        :param domain: domain part of the FQDN
        :return: Object|None, currently set IP-address
        """

        # Find the given domain
        domain_object = pyrax.cloud_dns.find(name=domain)

        # Find the given host
        current = domain_object.search_records('A', name='%s.%s' % (host, domain))
        if not len(current):
            return None

        if len(current) > 1:
            sys.stderr.write("Error: Multiple records for %s in domain %s. Won't continue!\n" % (host, domain))
            exit(1)

        return current[0], current[0].data

    def update_rr(self, host, domain, ip, record_to_update):
        """
        Update existing DNS-record
        :param host: hostname of the FQDN, without dot
        :param domain: domain part of the FQDN
        :param ip: IPv4-address to update
        :param record_to_update: existing DNS-record object to update, if None - add a record
        :return:
        """

        # Find the given domain
        domain_object = pyrax.cloud_dns.find(name=domain)

        if record_to_update:
            # Update!
            domain_object.update_record(record_to_update, ip)
        else:
            # Add!
            rec = {'type': 'A',
                   'name': '%s.%s' % (host, domain),
                   'data': ip}
            domain_object.add_record(rec)

    @staticmethod
    def _read_credentials_file(creds_file):
        """
        Read given credentials file
        :param creds_file:
        :return: tuple, API user and API key
        """
        if not os.path.isfile(creds_file):
            sys.stderr.write("Error: Rackspace credentials file %s doesn't exist! Exiting.\n" % creds_file)
            exit(2)

        data = json.load(open(creds_file))

        return data['user'], data['key']

    @staticmethod
    def default_credentials_file():
        if 'HOME' in os.environ:
            default_credentials_filename = os.environ['HOME'] + "/.rackspace.auth"
        else:
            default_credentials_filename = str(Path.home()) + "/.rackspace.auth"

        return default_credentials_filename

    def debug(self, debugging):
        pyrax.set_http_debug(debugging)
