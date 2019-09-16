# -*- coding: utf-8 -*-
#
# File: test_getiteminfos.py
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

from imio.pm.ws.soap.soapview import SOAPView
from imio.pm.ws.tests.WS4PMTestCase import WS4PMTestCase
from imio.pm.ws.WS4PM_client import meetingsAcceptingItemsRequest
from imio.pm.ws.WS4PM_client import meetingsAcceptingItemsResponse
from time import localtime

import ZSI


class testSOAPMeetingsAcceptingItems(WS4PMTestCase):
    """
        Tests the soap.meetingsAcceptingItems method by accessing the real SOAP service
    """

    def test_ws_meetingAcceptingItems(self):
        """
          Test that getting meetings accepting items works
        """
        # create 2 meetings and test
        # we are not testing the MeetingConfig.getMeetingsAcceptingItems method
        # but we are testing that using the WS works...
        self.changeUser('pmManager')
        # by default, no Meeting exists...
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingPga')) == 0)
        meeting1 = self.create('Meeting', date='2015/01/01')
        meeting2 = self.create('Meeting', date='2015/02/02')
        req = meetingsAcceptingItemsRequest()
        responseHolder = meetingsAcceptingItemsResponse()
        # a known MeetingConfig id is required
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).meetingsAcceptingItemsRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "Unknown meetingConfigId : 'None'!")
        req._meetingConfigId = self.meetingConfig.getId()
        response = SOAPView(self.portal, req).meetingsAcceptingItemsRequest(req, responseHolder)
        # returned meetings are sorted by getDate ascending
        self.assertTrue(len(response._meetingInfo) == 2)
        self.assertTrue(response._meetingInfo[0]._UID == meeting1.UID())
        self.assertTrue(response._meetingInfo[0]._date == localtime(meeting1.getDate()))
        self.assertTrue(response._meetingInfo[1]._UID == meeting2.UID())
        self.assertTrue(response._meetingInfo[1]._date == localtime(meeting2.getDate()))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # add a prefix because we heritate from testMeeting and we do not want every tests of testMeeting to be run here...
    suite.addTest(makeSuite(testSOAPMeetingsAcceptingItems, prefix='test_ws_'))
    return suite
