#!/usr/bin/env python3

# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python


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


class BaseCloud(object):
    """
    Abstract class to implement the intefrace for Cloud DNS providers
    """

    def is_authenticated(self):
        raise NotImplementedError("Base class doesn't have this.")

    def authenticate(self, api_creds):
        raise NotImplementedError("Base class doesn't have this.")

    def get_current_ip_from_dns(self, host, domain):
        raise NotImplementedError("Base class doesn't have this.")

    def update_rr(self, host, domain, ip, record_to_update):
        raise NotImplementedError("Base class doesn't have this.")

    def debug(self, debugging):
        raise NotImplementedError("Base class doesn't have this.")
