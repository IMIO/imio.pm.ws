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

from time import localtime
import ZSI
from ZSI.TCtimes import gDateTime
from imio.pm.ws.tests.WS4PMTestCase import WS4PMTestCase
from imio.pm.ws.WS4PM_client import searchItemsRequest, searchItemsResponse
from imio.pm.ws.tests.WS4PMTestCase import serializeRequest, deserialize
from imio.pm.ws.soap.soapview import SOAPView


class testSOAPSearchItems(WS4PMTestCase):
    """
        Tests the soap.searchItemsRequest method by accessing the real SOAP service
    """

    def test_searchItemsRequest(self):
        """
          Test that searching with given parameters returns valuable informations
        """
        #by default no item exists
        self.changeUser('pmCreator1')
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingItemPga')) == 0)
        #prepare data for a default item
        req = self._prepareCreationData()
        req._creationData._externalIdentifier = 'my_external_app_identifier'
        #use the SOAP service to create one
        newItem, response = self._createItem(req)
        newItemUID = newItem.UID()
        #externalIdentifier is actually set
        self.assertEquals(newItem.externalIdentifier, 'my_external_app_identifier')
        #now an item exists, get informations about it
        req = searchItemsRequest()
        req._Title = 'item'
        req._getCategory = 'development'
        #Serialize the request so it can be easily tested
        request = serializeRequest(req)
        #This is what the sent enveloppe should looks like
        expected = """<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
"""xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
"""xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">""" \
"""<SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body xmlns:ns1="http://ws4pm.imio.be"><ns1:searchItemsRequest>""" \
"""<Title>%s</Title><getCategory>%s</getCategory></ns1:searchItemsRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>""" \
% (req._Title, req._getCategory)
        result = """%s""" % request
        self.assertEquals(expected, result)
        #now really use the SOAP method to get informations about the item
        resp = self._searchItems(req)
        #the item is not in a meeting so the meeting date is 1950-01-01
        expected = """<ns1:searchItemsResponse xmlns:ns1="http://ws4pm.imio.be" """ \
"""xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
"""xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
"""xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>%s</UID>
    <id>my-new-item-title</id>
    <title>My new item title</title>
    <creator>pmCreator1</creator>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <review_state>itemcreated</review_state>
    <meeting_date>1950-01-01T00:00:00.006Z</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmCreator1/mymeetings/plonegov-assembly/my-new-item-title</absolute_url>
    <externalIdentifier>my_external_app_identifier</externalIdentifier>
    <extraInfos/>
  </itemInfo>
</ns1:searchItemsResponse>
""" % (newItemUID)
        self.assertEquals(expected, resp)
        # if the item is in a meeting, the result is a bit different because
        # we have valid informations about the meeting_date
        # use the 'plonegov-assembly' MeetingConfig that use real categories,
        # not useGroupsAsCategories
        self.changeUser('pmManager')
        meeting = self._createMeetingWithItems()
        itemInMeeting = meeting.getItemsInOrder()[0]
        #by default, PloneMeeting creates item without title/description/decision...
        itemInMeeting.setTitle('My new item title')
        itemInMeeting.setDescription('<p>Description</p>', mimetype='text/x-html-safe')
        itemInMeeting.setDecision('<p>Décision</p>', mimetype='text/x-html-safe')
        itemInMeeting.reindexObject()
        req._Title = 'item title'
        req._getCategory = ''
        resp = self._searchItems(req)
        itemInMeetingUID = itemInMeeting.UID()
        meetingDate = gDateTime.get_formatted_content(gDateTime(), localtime(meeting.getDate()))
        #searching for items can returns several items
        #for example here, searching for 'item title' in existing items title will returns 2 items...
        expected = """<ns1:searchItemsResponse xmlns:ns1="http://ws4pm.imio.be" """ \
"""xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
"""xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
"""xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>%s</UID>
    <id>o3</id>
    <title>My new item title</title>
    <creator>pmManager</creator>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <review_state>presented</review_state>
    <meeting_date>%s</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmManager/mymeetings/plonegov-assembly/o3</absolute_url>
    <externalIdentifier/>
    <extraInfos/>
  </itemInfo>
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>%s</UID>
    <id>my-new-item-title</id>
    <title>My new item title</title>
    <creator>pmCreator1</creator>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <review_state>itemcreated</review_state>
    <meeting_date>1950-01-01T00:00:00.006Z</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmCreator1/mymeetings/plonegov-assembly/my-new-item-title</absolute_url>
    <externalIdentifier>my_external_app_identifier</externalIdentifier>
    <extraInfos/>
  </itemInfo>
</ns1:searchItemsResponse>
""" % (itemInMeetingUID, meetingDate, newItemUID)
        self.assertEquals(expected, resp)
        #if the search params do not return an existing UID, the response is empty
        req._Title = 'aWrongTitle'
        resp = self._searchItems(req)
        expected = """<ns1:searchItemsResponse xmlns:ns1="http://ws4pm.imio.be" """ \
"""xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
"""xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
"""xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>
"""
        self.assertEquals(resp, expected)
        #if not search params is pass, a ZSI.Fault is raised
        req._Title = ''
        responseHolder = searchItemsResponse()
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).searchItemsRequest(req, responseHolder)
        self.assertEquals(cm.exception.string, 'Define at least one search parameter!')
        #if a 'meetingConfigId' is passed, items of this meetingConfig are taken into account
        #create an item for 'plonemeeting-assembly' with same data as one created for 'plonegov-assembly' here above
        req = self._prepareCreationData()
        req._meetingConfigId = 'plonemeeting-assembly'
        # in 'plonemeeting-assembly', the category is not used, useGroupsAsCategories is True
        req._creationData._category = ''
        newItem, response = self._createItem(req)
        pmItem = self.portal.portal_catalog(UID=response._UID)[0].getObject()
        pmItemUID = pmItem.UID()
        #searching items with Title like 'item title' returns the 3 created elements
        req = searchItemsRequest()
        req._Title = 'item title'
        responseHolder = searchItemsResponse()
        response = SOAPView(self.portal, req).searchItemsRequest(req, responseHolder)
        resp = deserialize(response)
        self.failUnless(itemInMeetingUID in resp and newItemUID in resp and pmItemUID in resp)
        req._meetingConfigId = 'plonemeeting-assembly'
        response = SOAPView(self.portal, req).searchItemsRequest(req, responseHolder)
        resp = deserialize(response)
        self.failUnless(itemInMeetingUID not in resp and newItemUID not in resp and pmItemUID in resp)
        # passing a wrong meetingConfigId will raise a ZSI.Fault
        req._meetingConfigId = 'wrongMeetingConfigId'
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).searchItemsRequest(req, responseHolder)
        self.assertEquals(cm.exception.string, "Unknown meetingConfigId : 'wrongMeetingConfigId'!")

    def test_searchItemsInTheNameOf(self):
        """
          Test that searching items inTheNameOf antother user works
          Create 2 items, one by 'pmCreator1', member of the 'developers' group
          and one by 'pmCreator2', member of the 'vendors' group
          Item 1 will be viewable :
          - by 'pmManager' and 'pmCreator1'
          Item 1 will NOT be viewable :
          - while getting informations in the name of 'pmCreator2'
            that is not in the 'developers' group
          Item 2 will be viewable :
          - by 'pmManager' and 'pmCreator2'
          Item 2 will NOT be viewable :
          - while getting informations in the name of 'pmCreator1'
            that is not in the 'vendors' group
        """
        # put pmManager in the 'vendors_creators' so he can have
        # access to itemcreated items of 'pmCreator2'
        self.portal.portal_groups.addPrincipalToGroup('pmManager', 'vendors_creators')
        SAME_TITLE = 'sameTitleForBothItems'
        # create an item by 'pmCreator1'
        self.changeUser('pmCreator1')
        item1 = self.create('MeetingItem')
        item1.setTitle(SAME_TITLE)
        item1.reindexObject(idxs=['Title', ])
        # create an item by 'pmCreator2'
        self.changeUser('pmCreator2')
        item2 = self.create('MeetingItem')
        item2.setTitle(SAME_TITLE)
        item2.reindexObject(idxs=['Title', ])
        req = searchItemsRequest()
        req._inTheNameOf = None
        req._Title = SAME_TITLE
        responseHolder = searchItemsResponse()
        # 'pmCreator1' can get infos about item1
        self.changeUser('pmCreator1')
        result = SOAPView(self.portal, req).searchItemsRequest(req, responseHolder)
        # only one result and about item1
        self.assertTrue(result._itemInfo[0].UID == item1.UID() and len(result._itemInfo) == 1)
        # 'pmCreator2' can get infos about item2
        self.changeUser('pmCreator2')
        result = SOAPView(self.portal, req).searchItemsRequest(req, responseHolder)
        # only one result and about item2
        self.assertTrue(result._itemInfo[0].UID == item2.UID() and len(result._itemInfo) == 1)
        # None of 'pmCreatorx' can searchItems inTheNameOf
        req._inTheNameOf = 'pmCreator1'
        self.changeUser('pmCreator1')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).searchItemsRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "You need to be 'Manager' or 'MeetingManager' to get item informations 'inTheNameOf'!")
        req._inTheNameOf = 'pmCreator2'
        self.changeUser('pmCreator2')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).searchItemsRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "You need to be 'Manager' or 'MeetingManager' to get item informations 'inTheNameOf'!")
        # now working examples with a 'Manager'
        self.changeUser('pmManager')
        req._inTheNameOf = None
        result = SOAPView(self.portal, req).searchItemsRequest(req, responseHolder)
        # both items are returned
        self.assertTrue(len(result._itemInfo) == 2)
        # returned items are item1 and item2
        createdItemsUids = set((item1.UID(), item2.UID()))
        resultUids = set((result._itemInfo[0].UID, result._itemInfo[1].UID))
        self.assertTrue(createdItemsUids == resultUids)
        # now searchItems inTheNameOf 'pmCreator1'
        req._inTheNameOf = 'pmCreator1'
        result = SOAPView(self.portal, req).getItemInfosRequest(req, responseHolder)
        self.assertTrue(len(result._itemInfo) == 1)
        self.assertTrue(result._itemInfo[0].UID == item1.UID())
        # now searchItems inTheNameOf 'pmCreator2'
        req._inTheNameOf = 'pmCreator2'
        result = SOAPView(self.portal, req).getItemInfosRequest(req, responseHolder)
        self.assertTrue(len(result._itemInfo) == 1)
        self.assertTrue(result._itemInfo[0].UID == item2.UID())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # add a prefix because we heritate from testMeeting and we do not want every tests of testMeeting to be run here...
    suite.addTest(makeSuite(testSOAPSearchItems, prefix='test_'))
    return suite