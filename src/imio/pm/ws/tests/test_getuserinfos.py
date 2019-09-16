# -*- coding: utf-8 -*-
#
# File: test_getuserinfos.py
#
# Copyright (c) 2013 by Imio.be
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

from imio.helpers.cache import cleanRamCacheFor
from imio.pm.ws.soap.soapview import SOAPView
from imio.pm.ws.tests.WS4PMTestCase import deserialize
from imio.pm.ws.tests.WS4PMTestCase import WS4PMTestCase
from imio.pm.ws.WS4PM_client import getUserInfosRequest
from imio.pm.ws.WS4PM_client import getUserInfosResponse

import ZSI


class testSOAPGetUserInfos(WS4PMTestCase):
    """
        Tests the soap.getUserInfosRequest method by accessing the real SOAP service
    """

    def test_ws_canNotGetUserInfosForAnotherUser(self):
        """
          Test that getting informations about another user is not possible
          except if the connected user is MeetingManager or Manager
        """
        # any PM user can have his own informations
        self.changeUser('pmCreator1')
        req = getUserInfosRequest()
        req._userId = 'pmCreator2'
        responseHolder = getUserInfosResponse()
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).getUserInfosRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "You need to be 'Manager' or 'MeetingManager' to get "
                          "user informations for another user than 'pmCreator1'!")
        self.changeUser('pmManager')
        # pmManager can get informations for another user as it is a MeetingManager
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        response = SOAPView(self.portal, req).getUserInfosRequest(req, responseHolder)
        self.assertTrue(response._fullname == 'M. PMCreator Two')

    def test_ws_queriedUserMustExists(self):
        """
          Test that getting informations fails if the queried user does not exist
        """
        self.changeUser('pmManager')
        req = getUserInfosRequest()
        req._userId = 'unexistingUserId'
        responseHolder = getUserInfosResponse()
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).getUserInfosRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "Trying to get user informations for an unexisting user 'unexistingUserId'!")

    def test_ws_getOwnUserInfosRequest(self):
        """
          Test that getting informations about a user returns valuable informations
        """
        # any PM user can have his own informations
        self.changeUser('pmCreator1')
        req = getUserInfosRequest()
        req._userId = 'pmCreator1'
        responseHolder = getUserInfosResponse()
        response = SOAPView(self.portal, req).getUserInfosRequest(req, responseHolder)
        self.assertTrue(response._fullname == 'M. PMCreator One')
        self.assertTrue(response._email == 'pmcreator1@plonemeeting.org')
        self.assertTrue(response._groups == [])
        # now as 'pmCreator2'
        self.changeUser('pmCreator2')
        req = getUserInfosRequest()
        req._userId = 'pmCreator2'
        responseHolder = getUserInfosResponse()
        response = SOAPView(self.portal, req).getUserInfosRequest(req, responseHolder)
        self.assertTrue(response._fullname == 'M. PMCreator Two')
        self.assertTrue(response._email == 'pmcreator2@plonemeeting.org')
        self.assertTrue(response._groups == [])

    def test_ws_getUserInfosShowGroups(self):
        """
          Test getting user informations including groups
        """
        # use pmManager that is member of 2 groups but only creator for one
        self.changeUser('pmManager')
        req = getUserInfosRequest()
        req._userId = 'pmManager'
        req._showGroups = True
        responseHolder = getUserInfosResponse()
        response = SOAPView(self.portal, req).getUserInfosRequest(req, responseHolder)
        resp = deserialize(response)
        expected = """<ns1:getUserInfosResponse xmlns:ns1="http://ws4pm.imio.be" """ \
                   """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
                   """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
                   """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
                   """xmlns:xsd="http://www.w3.org/2001/XMLSchema" """ \
                   """xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <fullname>M. PMManager</fullname>
  <email>pmmanager@plonemeeting.org</email>
  <groups xsi:type="ns1:BasicInfo">
    <UID>%s</UID>
    <id>developers</id>
    <title>Developers</title>
    <description/>
  </groups>
  <groups xsi:type="ns1:BasicInfo">
    <UID>%s</UID>
    <id>vendors</id>
    <title>Vendors</title>
    <description/>
  </groups>
</ns1:getUserInfosResponse>\n""" % (self.developers_uid, self.vendors_uid)
        self.assertEquals(expected, resp)
        # if we specify a particular suffix, only groups of this suffix are returned
        req._suffix = 'creators'
        responseHolder = getUserInfosResponse()
        response = SOAPView(self.portal, req).getUserInfosRequest(req, responseHolder)
        resp = deserialize(response)
        expected = """<ns1:getUserInfosResponse xmlns:ns1="http://ws4pm.imio.be" """ \
                   """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
                   """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
                   """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
                   """xmlns:xsd="http://www.w3.org/2001/XMLSchema" """ \
                   """xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <fullname>M. PMManager</fullname>
  <email>pmmanager@plonemeeting.org</email>
  <groups xsi:type="ns1:BasicInfo">
    <UID>%s</UID>
    <id>developers</id>
    <title>Developers</title>
    <description/>
  </groups>
</ns1:getUserInfosResponse>\n""" % (self.developers_uid, )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # add a prefix because we heritate from testMeeting and we do not want every tests of testMeeting to be run here...
    suite.addTest(makeSuite(testSOAPGetUserInfos, prefix='test_ws_'))
    return suite
