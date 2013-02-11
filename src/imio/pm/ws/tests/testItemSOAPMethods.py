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

import base64
import os
from time import localtime
import ZSI
from ZSI.schema import GTD
from ZSI.TCtimes import gDateTime
from AccessControl import Unauthorized
from plone.app.testing import logout
from imio.pm.ws.tests.WS4PMTestCase import WS4PMTestCase
from imio.pm.ws.WS4PM_client import testConnectionRequest, testConnectionResponse, \
                                    createItemRequest, createItemResponse, \
                                    searchItemsRequest, searchItemsResponse, \
                                    getItemInfosRequest, getItemInfosResponse, \
                                    getConfigInfosRequest, getConfigInfosResponse
from imio.pm.ws.tests.WS4PMTestCase import serializeRequest, deserialize
from imio.pm.ws.soap.soapview import SOAPView
from imio.pm.ws.soap.soapview import WRONG_HTML_WARNING, MULTIPLE_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING

validMeetingConfigId = 'plonegov-assembly'

class testItemSOAPMethods(WS4PMTestCase):
    """
        Tests the soap.soapview methods by accessing the real SOAP service
    """

    def test_testConnectionRequest(self):
        """ """
        # try without being connected
        logout()
        req = testConnectionRequest()
        responseHolder = testConnectionResponse()
        self.assertRaises(Unauthorized, SOAPView(self.portal, req).testConnectionRequest, req, responseHolder)
        # now try with a connected user
        self.changeUser('pmManager')
        response = SOAPView(self.portal, req).testConnectionRequest(req, responseHolder)
        self.assertEquals(response._connectionState, True)

    def test_createItemRequest(self):
        """
          In the default test configuration, the user 'pmCreator1' can create an item for
          proposingGroup 'developers' in the MeetingConfig 'plonegov-assembly'
        """
        #by default no item exists
        self.changeUser('pmCreator1')
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingItemPga')) == 0)
        req = self._prepareCreationData()
        #This is what the sent enveloppe should looks like, note that the decision is "Décision"
        #instead of '<p>Décision</p>' so we check accents and missing <p></p>
        req._creationData._decision = 'Décision'
        #Serialize the request so it can be easily tested
        request = serializeRequest(req)
        expected =  """POST /plone/createItemRequest HTTP/1.0
Authorization: Basic %s:%s
Content-Length: 102
Content-Type: text/xml
SOAPAction: /
<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body xmlns:ns1="http://ws4pm.imio.be"><ns1:createItemRequest><meetingConfigId>plonegov-assembly</meetingConfigId><proposingGroupId>developers</proposingGroupId><creationData xsi:type="ns1:CreationData"><title>My new item title</title><category>development</category><description>&lt;p&gt;Description&lt;/p&gt;</description><decision>D\xc3\xa9cision</decision></creationData></ns1:createItemRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>""" % ('pmCreator1', 'meeting')
        result = """POST /plone/createItemRequest HTTP/1.0
Authorization: Basic %s:%s
Content-Length: 102
Content-Type: text/xml
SOAPAction: /
%s""" % ('pmCreator1', 'meeting', request)
        self.assertEquals(expected, result)
        #now really use the SOAP method to create an item
        newItem, response = self._createItem(req)
        newItemUID = newItem.UID()
        resp = deserialize(response)
        expected = """<ns1:createItemResponse xmlns:ns1="http://ws4pm.imio.be" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <UID>%s</UID>
  <warnings>%s</warnings>
</ns1:createItemResponse>
""" % (newItemUID, WRONG_HTML_WARNING % ('/'.join(newItem.getPhysicalPath()), self.portal.portal_membership.getAuthenticatedMember().getId()))
        self.assertEquals(expected, resp)
        #the item is actually created
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingItemPga', UID=newItemUID)) == 1)
        #responseHolder for tests here above
        responseHolder = createItemResponse()
        #check that we can create an item with an empty HTML field
        req._creationData._decision = ''
        newItemWithEmptyDecisionUID = SOAPView(self.portal, req).createItemRequest(req, responseHolder)._UID
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingItemPga', UID=newItemWithEmptyDecisionUID)) == 1)
        #No matter how the item is created, with or without a decision, every HTML fields are surrounded by <p></p>
        self.failIf(self.portal.portal_catalog(portal_type='MeetingItemPga', UID=newItemWithEmptyDecisionUID)[0].getObject().getDecision() != "<p></p>")
        #if the user can not create the item, a ZSI.Fault is returned
        #the meetingConfigId must exists
        req._meetingConfigId = 'wrong-meeting-config-id'
        self.assertRaises(ZSI.Fault, SOAPView(self.portal, req).createItemRequest, req, responseHolder)
        req._meetingConfigId = validMeetingConfigId
        #the connected user must be able to create an item for the given proposingGroupId
        req._proposingGroupId = 'vendors'
        self.assertRaises(ZSI.Fault, SOAPView(self.portal, req).createItemRequest, req, responseHolder)
        #the connected user must be able to create an item with the given category
        req._category = 'wrong-category-id'
        self.assertRaises(ZSI.Fault, SOAPView(self.portal, req).createItemRequest, req, responseHolder)

    def test_createItemWithOneAnnexRequest(self):
        """
          Test SOAP service behaviour when creating items with one annex
        """
        #by default no item exists
        self.changeUser('pmCreator1')
        req = self._prepareCreationData()
        data = {'title': 'My annex 1', 'filename': 'smallTestFile.pdf', 'file': 'smallTestFile.pdf'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data)]
        annex = req._creationData._annexes[0]
        #Serialize the request so it can be easily tested
        request = serializeRequest(req)
        #This is what the sent enveloppe should looks like
        expected =  """POST /plone/createItemRequest HTTP/1.0
Authorization: Basic %s:%s
Content-Length: 102
Content-Type: text/xml
SOAPAction: /
<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body xmlns:ns1="http://ws4pm.imio.be"><ns1:createItemRequest><meetingConfigId>plonegov-assembly</meetingConfigId><proposingGroupId>developers</proposingGroupId><creationData xsi:type="ns1:CreationData"><title>My new item title</title><category>development</category><description>&lt;p&gt;Description&lt;/p&gt;</description><decision>&lt;p&gt;Décision&lt;/p&gt;</decision><annexes xsi:type="ns1:AnnexInfo"><title>%s</title><annexTypeId>%s</annexTypeId><filename>%s</filename><file>
%s</file></annexes></creationData></ns1:createItemRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>""" % ('pmCreator1', 'meeting', annex._title, annex._annexTypeId, annex._filename, base64.encodestring(annex._file))
        result = """POST /plone/createItemRequest HTTP/1.0
Authorization: Basic %s:%s
Content-Length: 102
Content-Type: text/xml
SOAPAction: /
%s""" % ('pmCreator1', 'meeting', request)
        self.assertEquals(expected, result)
        newItem, response = self._createItem(req)
        #now check the created item have the annex
        annexes = newItem.getAnnexes()
        #the annex is actually created
        self.failUnless(len(annexes) == 1)
        #the annex mimetype is correct
        annex = annexes[0]
        self.failUnless(annex.getContentType() == 'application/pdf')
        #the annex metadata are ok
        self.failUnless(annex.Title() == 'My annex 1' and annex.getMeetingFileType().getId() == 'financial-analysis')

    def test_createItemWithSeveralAnnexesRequest(self):
        """
          Test SOAP service behaviour when creating items with several annexes of different types
        """
        #by default no item exists
        self.changeUser('pmCreator1')
        req = self._prepareCreationData()
        #add 4 extra annexes
        #no data give, some default values are used (smallTestFile.pdf)
        data1 = {'title': 'My annex 1', 'filename': 'smallTestFile.pdf', 'file': 'smallTestFile.pdf'}
        #other annexTypeId than the default one
        data2 = {'title': 'My annex 2', 'filename': 'arbitraryFilename.odt', 'file': 'mediumTestFile.odt', 'annexTypeId': 'budget-analysis'}
        #a wrong annexTypeId and a test with a large msword document
        data3 = {'title': 'My annex 3', 'filename': 'largeTestFile.doc', 'file': 'largeTestFile.doc', 'annexTypeId': 'wrong-annexTypeId'}
        #empty file data provided, at the end, the annex is not created but the item is correctly created
        data4 = {'title': 'My annex 4', 'filename': 'emptyTestFile.txt', 'file': 'emptyTestFile.txt', 'annexTypeId': 'budget-analysis'}
        #a file that will have several extensions found in mimetyps_registry is not handled if no valid filename is provided
        data5 = {'title': 'My annex 5', 'filename': 'notValidFileNameNoExtension', 'file': 'octetStreamTestFile.bin', 'annexTypeId': 'budget-analysis'}
        #but if the filename is valid, then the annex is handled
        data6 = {'title': 'My annex 6', 'filename': 'validExtension.bin', 'file': 'octetStreamTestFile.bin', 'annexTypeId': 'budget-analysis'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data1), self._prepareAnnexInfo(**data2), self._prepareAnnexInfo(**data3),
                                      self._prepareAnnexInfo(**data4), self._prepareAnnexInfo(**data5), self._prepareAnnexInfo(**data6)]
        #Serialize the request so it can be easily tested
        request = serializeRequest(req)
        #build annexes part of the envelope
        annexesEnveloppePart = ""
        for annex in req._creationData._annexes:
            annexesEnveloppePart = annexesEnveloppePart + """<annexes xsi:type="ns1:AnnexInfo"><title>%s</title><annexTypeId>%s</annexTypeId><filename>%s</filename><file>
%s</file></annexes>""" % (annex._title, annex._annexTypeId, annex._filename, base64.encodestring(annex._file))
        
        #This is what the sent enveloppe should looks like
        expected =  """POST /plone/createItemRequest HTTP/1.0
Authorization: Basic %s:%s
Content-Length: 102
Content-Type: text/xml
SOAPAction: /
<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body xmlns:ns1="http://ws4pm.imio.be"><ns1:createItemRequest><meetingConfigId>plonegov-assembly</meetingConfigId><proposingGroupId>developers</proposingGroupId><creationData xsi:type="ns1:CreationData"><title>My new item title</title><category>development</category><description>&lt;p&gt;Description&lt;/p&gt;</description><decision>&lt;p&gt;Décision&lt;/p&gt;</decision>%s</creationData></ns1:createItemRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>""" % ('pmCreator1', 'meeting', annexesEnveloppePart)
        result = """POST /plone/createItemRequest HTTP/1.0
Authorization: Basic %s:%s
Content-Length: 102
Content-Type: text/xml
SOAPAction: /
%s""" % ('pmCreator1', 'meeting', request)
        self.assertEquals(expected, result)
        newItem, response = self._createItem(req)
        # use objectValues so order is kept because getAnnexes is a ReferenceField
        annexes = newItem.objectValues('MeetingFile')
        #4 annexes are actually created
        self.failUnless(len(annexes) == 4)
        #the annexes mimetype are corrects
        self.failUnless(annexes[0].getContentType() == 'application/pdf')
        self.failUnless(annexes[1].getContentType() == 'application/vnd.oasis.opendocument.text')
        self.failUnless(annexes[2].getContentType() == 'application/msword')
        self.failUnless(annexes[3].getContentType() == 'application/octet-stream')
        #the annexes metadata are ok
        self.failUnless(annexes[0].Title() == 'My annex 1' and annexes[0].getMeetingFileType().getId() == 'financial-analysis')
        self.failUnless(annexes[1].Title() == 'My annex 2' and annexes[1].getMeetingFileType().getId() == 'budget-analysis')
        #meetingFileType is back to default one when a wrong file type is given in the annexInfo
        self.failUnless(annexes[2].Title() == 'My annex 3' and annexes[2].getMeetingFileType().getId() == 'financial-analysis')
        self.failUnless(annexes[3].Title() == 'My annex 6' and annexes[3].getMeetingFileType().getId() == 'budget-analysis')
        #annexes filename are the ones defined in the 'filename', either it is generated
        self.failUnless(annexes[0].getFile().filename == 'smallTestFile.pdf')
        self.failUnless(annexes[1].getFile().filename == 'arbitraryFilename.odt')
        self.failUnless(annexes[2].getFile().filename == 'largeTestFile.doc')
        self.failUnless(annexes[3].getFile().filename == 'validExtension.bin')

    def test_createItemWithWarnings(self):
        """
          Test that during item creation, if non blocker errors occur (warnings), it is displayed in the response
        """
        #if the proposed HTML of one of the rich field is wrong
        #it is reworked by BeautifulSoup and a warning is displayed
        self.changeUser('pmCreator1')
        req = self._prepareCreationData()
        wrongHTML = '<p>Wrong HTML<strong></p></strong>'
        req._creationData._decision = wrongHTML
        newItem, response = self._createItem(req)
        resp = deserialize(response)
        expected = """<ns1:createItemResponse xmlns:ns1="http://ws4pm.imio.be" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <UID>%s</UID>
  <warnings>%s</warnings>
</ns1:createItemResponse>
""" % (newItem.UID(), WRONG_HTML_WARNING % (newItem.absolute_url_path(), 'pmCreator1'))
        self.assertEquals(expected, resp)
        #now test warnings around file mimetype
        data = {'title': 'My annex', 'filename': 'notValidFileNameNoExtension', 'file': 'octetStreamTestFile.bin', 'annexTypeId': 'budget-analysis'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data)]
        #several extensions found and no valid filename extension, the annex is not created and a warning is added
        newItem, response = self._createItem(req)
        resp = deserialize(response)
        #2 warnings are returned
        expected = """<ns1:createItemResponse xmlns:ns1="http://ws4pm.imio.be" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <UID>%s</UID>
  <warnings>%s</warnings>
  <warnings>%s</warnings>
</ns1:createItemResponse>
""" % (newItem.UID(),
       MULTIPLE_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING % ('application/octet-stream', 'notValidFileNameNoExtension', newItem.absolute_url_path()),
       WRONG_HTML_WARNING % (newItem.absolute_url_path(), 'pmCreator1'),)
        self.assertEquals(expected, resp)

    def test_getItemInfosRequest(self):
        """
          Test that getting an item with a given UID returns valuable informations
        """
        #by default no item exists
        self.changeUser('pmCreator1')
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingItemPga')) == 0)
        #use the SOAP service to create one
        req = self._prepareCreationData()
        newItem, response = self._createItem(req)
        newItemUID = newItem.UID()
        #now an item exists, get informations about it
        req = getItemInfosRequest()
        req._UID = newItemUID
        #Serialize the request so it can be easily tested
        request = serializeRequest(req)
        #This is what the sent enveloppe should looks like
        expected =  """<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body xmlns:ns1="http://ws4pm.imio.be"><ns1:getItemInfosRequest><UID>%s</UID><showExtraInfos>false</showExtraInfos><showAnnexes>false</showAnnexes></ns1:getItemInfosRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>""" % newItemUID
        result = """%s""" % request
        self.assertEquals(expected, result)
        #now really use the SOAP method to get informations about the item
        resp = self._getItemInfos(newItemUID)
        #the item is not in a meeting so the meeting date is 1950-01-01
        expected = """<ns1:getItemInfosResponse xmlns:ns1="http://ws4pm.imio.be" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>%s</UID>
    <id>my-new-item-title</id>
    <title>My new item title</title>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <review_state>itemcreated</review_state>
    <meeting_date>1950-01-01T00:00:00.006Z</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmCreator1/mymeetings/plonegov-assembly/my-new-item-title</absolute_url>
    <externalIdentifier/>
    <extraInfos/>
  </itemInfo>
</ns1:getItemInfosResponse>
""" % (newItemUID)
        self.assertEquals(expected, resp)
        #if the item is in a meeting, the result is a bit different because we have valid informations about the meeting_date
        #use the 'plonegov-assembly' MeetingConfig that use real categories, not useGroupsAsCategories
        self.meetingConfig = self.meetingConfig2
        self.changeUser('pmManager')
        meeting = self._createMeetingWithItems()
        itemInMeeting = meeting.getItemsInOrder()[0]
        #by default, PloneMeeting creates item without title/description/decision...
        itemInMeeting.setTitle('My new item title')
        itemInMeeting.setDescription('<p>Description</p>', mimetype='text/x-html-safe')
        itemInMeeting.setDecision('<p>Décision</p>', mimetype='text/x-html-safe')
        resp = self._getItemInfos(itemInMeeting.UID())
        meetingDate = gDateTime.get_formatted_content(gDateTime(), localtime(meeting.getDate()))
        expected = """<ns1:getItemInfosResponse xmlns:ns1="http://ws4pm.imio.be" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>%s</UID>
    <id>o3</id>
    <title>My new item title</title>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <review_state>presented</review_state>
    <meeting_date>%s</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmManager/mymeetings/plonegov-assembly/o3</absolute_url>
    <externalIdentifier/>
    <extraInfos/>
  </itemInfo>
</ns1:getItemInfosResponse>
""" % (itemInMeeting.UID(), meetingDate)
        self.assertEquals(expected, resp)
        #if the item with this UID has not been found (user can not access or item does not exists), an empty response is returned
        #unexisting item UID
        resp = self._getItemInfos('aWrongUID')
        expected = """<ns1:getItemInfosResponse xmlns:ns1="http://ws4pm.imio.be" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>
"""
        self.assertEquals(expected, resp)
        #item UID the logged in user can not access
        self.changeUser('pmReviewer1')
        resp = self._getItemInfos(newItemUID)
        self.assertEquals(expected, resp)

    def test_getItemInfosWithExtraInfosRequest(self):
        """
          Test that getting an item with a given UID and specifying that we want extraInfos returns every available informations of the item
        """
        self.changeUser('pmCreator1')
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingItemPga')) == 0)
        #prepare data for a default item
        req = self._prepareCreationData()
        #add one annex
        data = {'title': 'My annex 1', 'filename': 'smallTestFile.pdf', 'file': 'smallTestFile.pdf'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data)]
        #create the item
        newItem, reponse = self._createItem(req)
        newItemUID = newItem.UID()
        #get informations about the item, by default 'showExtraInfos' is False
        resp = self._getItemInfos(newItemUID, showExtraInfos=True)
        extraInfosFields = SOAPView(self.portal, req)._getExtraInfosFields(newItem)
        #check that every field considered as extra informations is returned in the response
        for extraInfosField in extraInfosFields:
            self.failUnless(extraInfosField.getName() in resp)

    def test_getItemInfosWithAnnexesRequest(self):
        """
          Test that getting an item with a given UID returns valuable informations and linked annexes
        """
        self.changeUser('pmCreator1')
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingItemPga')) == 0)
        #prepare data for a default item
        req = self._prepareCreationData()
        #add one annex
        data = {'title': 'My annex 1', 'filename': 'smallTestFile.pdf', 'file': 'smallTestFile.pdf'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data)]
        #create the item
        newItem, reponse = self._createItem(req)
        newItemUID = newItem.UID()
        #get informations about the item, by default 'showAnnexes' is False
        resp = self._getItemInfos(newItemUID)
        expected = """<ns1:getItemInfosResponse xmlns:ns1="http://ws4pm.imio.be" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>%s</UID>
    <id>my-new-item-title</id>
    <title>My new item title</title>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <review_state>itemcreated</review_state>
    <meeting_date>1950-01-01T00:00:00.006Z</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmCreator1/mymeetings/plonegov-assembly/my-new-item-title</absolute_url>
    <externalIdentifier/>
    <extraInfos/>
  </itemInfo>
</ns1:getItemInfosResponse>
""" % (newItemUID)
        #annexes are not shown by default
        self.assertEquals(expected, resp)
        #now with 'showAnnexes=True'
        resp = self._getItemInfos(newItemUID, showAnnexes=True)
        expected = """<ns1:getItemInfosResponse xmlns:ns1="http://ws4pm.imio.be" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>%s</UID>
    <id>my-new-item-title</id>
    <title>My new item title</title>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <review_state>itemcreated</review_state>
    <meeting_date>1950-01-01T00:00:00.006Z</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmCreator1/mymeetings/plonegov-assembly/my-new-item-title</absolute_url>
    <externalIdentifier/>
    <extraInfos/>
    <annexes xsi:type="ns1:AnnexInfo">
      <title>My annex 1</title>
      <annexTypeId>financial-analysis</annexTypeId>
      <filename>smallTestFile.pdf</filename>
      <file>
%s</file>
    </annexes>
  </itemInfo>
</ns1:getItemInfosResponse>
""" % (newItemUID, base64.encodestring(newItem.getAnnexes()[0].getFile().data))
        #one annex is shown
        self.assertEquals(expected, resp)
        #now check with several (2) annexes...
        annex_type = getattr(self.meetingConfig.meetingfiletypes, 'item-annex')
        afile = open(os.path.join(os.path.dirname(__file__), 'mediumTestFile.odt'))
        annex_file = afile.read()
        afile.close()
        kwargs = {'filename': 'myBeautifulTestFile.odt'}
        newItem.addAnnex('myBeautifulTestFile.odt', '', 'My BeautifulTestFile title', annex_file, False, annex_type, **kwargs)
        resp = self._getItemInfos(newItemUID, showAnnexes=True)
        expected = """<ns1:getItemInfosResponse xmlns:ns1="http://ws4pm.imio.be" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>%s</UID>
    <id>my-new-item-title</id>
    <title>My new item title</title>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <review_state>itemcreated</review_state>
    <meeting_date>1950-01-01T00:00:00.006Z</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmCreator1/mymeetings/plonegov-assembly/my-new-item-title</absolute_url>
    <externalIdentifier/>
    <extraInfos/>
    <annexes xsi:type="ns1:AnnexInfo">
      <title>My annex 1</title>
      <annexTypeId>financial-analysis</annexTypeId>
      <filename>smallTestFile.pdf</filename>
      <file>
%s</file>
    </annexes>
    <annexes xsi:type="ns1:AnnexInfo">
      <title>My BeautifulTestFile title</title>
      <annexTypeId>item-annex</annexTypeId>
      <filename>myBeautifulTestFile.odt</filename>
      <file>
%s</file>
    </annexes>
  </itemInfo>
</ns1:getItemInfosResponse>
""" % (newItemUID, base64.encodestring(newItem.getAnnexesByType(realAnnexes=True)[0][0].getFile().data), base64.encodestring(newItem.getAnnexesByType(realAnnexes=True)[1][0].getFile().data))
        #2 annexes are shown
        self.assertEquals(expected, resp)

    def test_getConfigInfosRequest(self):
        """
          Test that getting informations about the configuration returns valuable informations
        """
        #any PM user can have these configuration informations
        self.changeUser('pmCreator1')
        req = getConfigInfosRequest()
        #Serialize the request so it can be easily tested
        request = serializeRequest(req)
        #This is what the sent enveloppe should looks like
        expected =  """<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body xmlns:ns1="http://ws4pm.imio.be"><ns1:getConfigInfosRequest><dummy>dummy</dummy></ns1:getConfigInfosRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>"""
        result = """%s""" % request
        self.assertEquals(expected, result)
        #now really use the SOAP method to get informations about the configuration
        responseHolder = getConfigInfosResponse()
        response = SOAPView(self.portal, req).getConfigInfosRequest(req, responseHolder)
        resp = deserialize(response)
        #construct the expected result : header + content + footer
        #header
        expected = """<ns1:getConfigInfosResponse xmlns:ns1="http://ws4pm.imio.be" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">"""
        elements = self.tool.getActiveConfigs() + self.tool.getActiveGroups()
        #content
        for element in elements:
            expected += """
  <configInfo xsi:type="ns1:ConfigInfo">
    <UID>%s</UID>
    <id>%s</id>
    <title>%s</title>
    <description>%s</description>
    <type>%s</type>
  </configInfo>""" % (element.UID(), element.getId(), element.Title(), element.Description(), element.portal_type)
        #footer.  Empty description is represented like <description/>
        expected = expected.replace('<description></description>', '<description/>') + "\n</ns1:getConfigInfosResponse>\n"
        self.assertEquals(expected, resp)

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
        expected =  """<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body xmlns:ns1="http://ws4pm.imio.be"><ns1:searchItemsRequest><Title>%s</Title><getCategory>%s</getCategory></ns1:searchItemsRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>""" % (req._Title, req._getCategory)
        result = """%s""" % request
        self.assertEquals(expected, result)
        #now really use the SOAP method to get informations about the item
        resp = self._searchItems(req)
        #the item is not in a meeting so the meeting date is 1950-01-01
        expected = """<ns1:searchItemsResponse xmlns:ns1="http://ws4pm.imio.be" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>%s</UID>
    <id>my-new-item-title</id>
    <title>My new item title</title>
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
        #if the item is in a meeting, the result is a bit different because we have valid informations about the meeting_date
        #use the 'plonegov-assembly' MeetingConfig that use real categories, not useGroupsAsCategories
        self.meetingConfig = self.meetingConfig2
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
        expected = """<ns1:searchItemsResponse xmlns:ns1="http://ws4pm.imio.be" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>%s</UID>
    <id>o3</id>
    <title>My new item title</title>
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
        expected = """<ns1:searchItemsResponse xmlns:ns1="http://ws4pm.imio.be" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>
"""
        self.assertEquals(resp, expected)
        #if not search params is pass, a ZSI.Fault is raised
        req._Title = ''
        responseHolder = searchItemsResponse()
        self.assertRaises(ZSI.Fault, SOAPView(self.portal, req).searchItemsRequest, req, responseHolder)
        #if a 'meetingConfigId' is passed, items of this meetingConfig are taken into account
        #create an item for 'plonemeeting-assembly' with same data as one created for 'plonegov-assembly' here above
        req = self._prepareCreationData()
        req._meetingConfigId = 'plonemeeting-assembly'
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
        #passing a wrong meetingConfigId will raise an ZSI.Fault
        req._meetingConfigId = 'wrongMeetingConfigId'
        self.assertRaises(ZSI.Fault, SOAPView(self.portal, req).searchItemsRequest, req, responseHolder)

    def test_renderedWSDL(self):
        """
          Check that the rendered WSDL correspond to what we expect
        """
        from renderedWSDL import renderedWSDL
        #set self.maxDiff to None to show diffs
        self.maxDiff=None
        self.assertEquals(self.portal.restrictedTraverse('@@ws4pm.wsdl').index(), renderedWSDL)

    def test_WS4PMBrowserLayer(self):
        """
          Test that soap methods and schemaextender is not available until
          the imio.pm.ws.layer BrowserLayer is available
        """
        #by default, the WSDL is available and the schemaextender
        self.portal.portal_quickinstaller.installProducts(['imio.pm.ws', ])
        #does not seem to work in tests?
        #self.assertEquals(self.portal.restrictedTraverse('@@ws4pm.wsdl').context.absolute_url(), self.portal.absolute_url())
        self.changeUser('pmManager')
        item = self.create('MeetingItem')
        self.failUnless('externalIdentifier' in item.Schema().keys())
        #now uninstall imio.pm.ws
        self.portal.portal_quickinstaller.uninstallProducts(['imio.pm.ws', ])
        #no more schemaextender
        self.failIf('externalIdentifier' in item.Schema().keys())
        #the WSDL is no more available

    def _prepareCreationData(self):
        """
          Helper method for creating an item using the SOAP method createItem
        """
        req = createItemRequest()
        req._meetingConfigId = validMeetingConfigId
        req._proposingGroupId = 'developers'
        CreationData = GTD('http://ws4pm.imio.be', 'CreationData')('').pyclass()
        CreationData._title = 'My new item title'
        CreationData._category = 'development'
        CreationData._description = '<p>Description</p>'
        CreationData._decision = '<p>Décision</p>'
        req._creationData = CreationData
        return req

    def _prepareAnnexInfo(self, **data):
        """
          Helper method for adding an annex to a created item
        """
        #create one annex
        AnnexInfo = GTD('http://ws4pm.imio.be', 'AnnexInfo')('').pyclass()
        AnnexInfo._title = data.get('title')
        #optional
        AnnexInfo._annexTypeId = data.get('annexTypeId', '')
        #optional
        AnnexInfo._filename = data.get('filename', '')
        if data.get('file'):
            annex_file = open(os.path.join(os.path.dirname(__file__), data.get('file')))
            AnnexInfo._file = annex_file.read()
            annex_file.close()
        return AnnexInfo

    def _createItem(self, req):
        """
          Create the item with data given in req parameter
        """
        responseHolder = createItemResponse()
        response = SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        newItem = self.portal.uid_catalog(UID=response._UID)[0].getObject()
        return newItem, response

    def _getItemInfos(self, itemUID, showAnnexes=False, showExtraInfos=False):
        """
          Call getItemInfos SOAP method with given itemUID parameter
        """
        req = getItemInfosRequest()
        req._UID = itemUID
        if showAnnexes:
            req._showAnnexes = True
        if showExtraInfos:
            req._showExtraInfos = True
        responseHolder = getItemInfosResponse()
        response = SOAPView(self.portal, req).getItemInfosRequest(req, responseHolder)
        return deserialize(response)

    def _searchItems(self, req):
        """
          Search items with data of req parameter
        """
        responseHolder = searchItemsResponse()
        response = SOAPView(self.portal, req).searchItemsRequest(req, responseHolder)
        return deserialize(response)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # add a prefix because we heritate from testMeeting and we do not want every tests of testMeeting to be run here...
    suite.addTest(makeSuite(testItemSOAPMethods, prefix='test_'))
    return suite
