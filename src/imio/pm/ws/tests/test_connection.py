# -*- coding: utf-8 -*-
#
# File: testItemMethods.py
#
# Copyright (c) 2012 by CommunesPlone
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

from AccessControl import Unauthorized
from plone.app.testing import logout
from imio.pm.ws.tests.WS4PMTestCase import WS4PMTestCase
from imio.pm.ws.WS4PM_client import testConnectionRequest, testConnectionResponse
from imio.pm.ws.soap.soapview import SOAPView


class testSOAPConnection(WS4PMTestCase):
    """
        Tests the soap.connectionRequest method by accessing the real SOAP service
    """

    def test_connectionRequest(self):
        """
          Test that we can connect to the webservice if we are authenticated in PloneMeeting
        """
        # try without being connected
        logout()
        req = testConnectionRequest()
        responseHolder = testConnectionResponse()
        self.assertRaises(Unauthorized, SOAPView(self.portal, req).testConnectionRequest, req, responseHolder)
        # now try with a connected user
        self.changeUser('pmManager')
        response = SOAPView(self.portal, req).testConnectionRequest(req, responseHolder)
        self.assertEquals(response._connectionState, True)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # add a prefix because we heritate from testMeeting and we do not want every tests of testMeeting to be run here...
    suite.addTest(makeSuite(testSOAPConnection, prefix='test_'))
    return suite