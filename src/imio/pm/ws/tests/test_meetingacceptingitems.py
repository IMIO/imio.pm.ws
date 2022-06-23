# -*- coding: utf-8 -*-
#
# File: test_getiteminfos.py
#
# GNU General Public License (GPL)
#

from datetime import datetime
from imio.pm.ws.soap.soapview import SOAPView
from imio.pm.ws.tests.WS4PMTestCase import WS4PMTestCase
from imio.pm.ws.WS4PM_client import meetingsAcceptingItemsRequest
from imio.pm.ws.WS4PM_client import meetingsAcceptingItemsResponse

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
        meeting1 = self.create('Meeting', datetime(2015, 1, 1))
        meeting2 = self.create('Meeting', datetime(2015, 2, 2))
        self.decideMeeting(meeting2)
        req = meetingsAcceptingItemsRequest()
        responseHolder = meetingsAcceptingItemsResponse()
        # a known MeetingConfig id is required
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).meetingsAcceptingItemsRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "Unknown meetingConfigId : 'None'!")
        req._meetingConfigId = self.meetingConfig.getId()
        response = SOAPView(self.portal, req).meetingsAcceptingItemsRequest(req, responseHolder)
        # returned meetings are sorted by date ascending
        self.assertTrue(len(response._meetingInfo) == 2)
        self.assertTrue(response._meetingInfo[0]._UID == meeting1.UID())
        self.assertTrue(response._meetingInfo[0]._date == meeting1.date.utctimetuple())
        self.assertTrue(response._meetingInfo[1]._UID == meeting2.UID())
        self.assertTrue(response._meetingInfo[1]._date == meeting2.date.utctimetuple())
        # inTheNameOf a normal user, we do not get the decided meeting
        req._inTheNameOf = "pmCreator1"
        response = SOAPView(self.portal, req).meetingsAcceptingItemsRequest(req, responseHolder)
        self.assertTrue(len(response._meetingInfo) == 1)
        # only get meeting1 that was not decided
        self.assertTrue(response._meetingInfo[0]._UID == meeting1.UID())
        self.assertTrue(response._meetingInfo[0]._date == meeting1.date.utctimetuple())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # add a prefix because we heritate from testMeeting and we do not want every tests of testMeeting to be run here...
    suite.addTest(makeSuite(testSOAPMeetingsAcceptingItems, prefix='test_ws_'))
    return suite
