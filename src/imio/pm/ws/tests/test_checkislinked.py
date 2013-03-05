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

import ZSI
from imio.pm.ws.tests.WS4PMTestCase import WS4PMTestCase
from imio.pm.ws.WS4PM_client import checkIsLinkedRequest, checkIsLinkedResponse
from imio.pm.ws.soap.soapview import SOAPView


class testSOAPCheckIsLinked(WS4PMTestCase):
    """
        Tests the soap.checkItemIsLinkedRequest method by accessing the real SOAP service
    """

    def test_checkIsLinkedRequest(self):
        """
          Test that we can ckech that an item is linked to a given externalIdentifier even
          if the MeetingManager doing the can can not actually see the item... (we use unrestricted search)
        """
        # try as a non MeetingManager
        self.changeUser('pmCreator1')
        checkIsLinkedReq = checkIsLinkedRequest()
        checkIsLinkedResponseHolder = checkIsLinkedResponse()
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, checkIsLinkedReq).checkIsLinkedRequest(checkIsLinkedReq,
                                                                         checkIsLinkedResponseHolder)
        self.assertEquals(cm.exception.string,
                          "You need to be 'Manager' or 'MeetingManager' to check if an element is linked to an item!")
        # now create an item as 'pmCreator2', aka a user in a group 'pmManager' can not access
        self.changeUser('pmCreator2')
        req = self._prepareCreationData()
        req._proposingGroupId = 'vendors'
        req._creationData._externalIdentifier = 'my-external-identifier'
        newItem, response = self._createItem(req)
        # check that using getItemInfos, MeetingManager can not get informations about created item
        self.changeUser('pmManager')
        self.failIf(self._getItemInfos(newItem.UID(), toBeDeserialized=False)._itemInfo)
        # but while checking if an item is linked, it works...
        # first check for anotherexternalIdentifier
        checkIsLinkedReq._meetingConfigId = None
        checkIsLinkedReq._externalIdentifier = 'my-unexisting-external-identifier'
        res = SOAPView(self.portal, checkIsLinkedReq).checkIsLinkedRequest(checkIsLinkedReq,
                                                                           checkIsLinkedResponseHolder)
        self.assertFalse(res._isLinked)
        # now with the values corresponding to the created item
        checkIsLinkedReq._externalIdentifier = 'my-external-identifier'
        res = SOAPView(self.portal, checkIsLinkedReq).checkIsLinkedRequest(checkIsLinkedReq,
                                                                           checkIsLinkedResponseHolder)
        self.assertTrue(res._isLinked)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # add a prefix because we heritate from testMeeting and we do not want every tests of testMeeting to be run here...
    suite.addTest(makeSuite(testSOAPCheckIsLinked, prefix='test_'))
    return suite
