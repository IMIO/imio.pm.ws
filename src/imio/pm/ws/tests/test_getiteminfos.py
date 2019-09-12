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

import base64
import os
from time import localtime
import ZSI
from ZSI.TCtimes import gDateTime
from plone import api
from plone import namedfile
from Products.CMFPlone.utils import safe_unicode
from Products.PloneMeeting.utils import get_annexes
from collective.iconifiedcategory.utils import calculate_category_id
from imio.helpers.cache import cleanRamCacheFor
from imio.pm.ws.config import POD_TEMPLATE_ID_PATTERN
from imio.pm.ws.soap.soapview import SOAPView
from imio.pm.ws.tests.WS4PMTestCase import serializeRequest
from imio.pm.ws.tests.WS4PMTestCase import WS4PMTestCase
from imio.pm.ws.WS4PM_client import getItemInfosRequest, getItemInfosResponse


class testSOAPGetItemInfos(WS4PMTestCase):
    """
        Tests the soap.getItemInfosRequest method by accessing the real SOAP service
    """

    def test_ws_getItemInfosRequest(self):
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
        expected = """<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
            """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
            """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
            """xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">""" \
            """<SOAP-ENV:Header></SOAP-ENV:Header>""" \
            """<SOAP-ENV:Body xmlns:ns1="http://ws4pm.imio.be"><ns1:getItemInfosRequest>""" \
            """<UID>%s</UID><showExtraInfos>false</showExtraInfos><showAnnexes>false</showAnnexes>""" \
            """<showTemplates>false</showTemplates></ns1:getItemInfosRequest>""" \
            """</SOAP-ENV:Body></SOAP-ENV:Envelope>""" % newItemUID
        result = """%s""" % request
        self.assertEquals(expected, result)
        #now really use the SOAP method to get informations about the item
        resp = self._getItemInfos(newItemUID)
        #the item is not in a meeting so the meeting date is 1950-01-01
        expected = """<ns1:getItemInfosResponse xmlns:ns1="http://ws4pm.imio.be" """ \
            """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
            """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
            """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" """ \
            """xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>%s</UID>
    <id>my-new-item-title</id>
    <title>My new item title</title>
    <creator>pmCreator1</creator>
    <creation_date>%s</creation_date>
    <modification_date>%s</modification_date>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <detailedDescription>&lt;p&gt;Detailed description&lt;/p&gt;</detailedDescription>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <preferredMeeting/>
    <preferred_meeting_date>1950-01-01T00:00:00.006Z</preferred_meeting_date>
    <review_state>itemcreated</review_state>
    <meeting_date>1950-01-01T00:00:00.006Z</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmCreator1/mymeetings/plonegov-assembly/my-new-item-title</absolute_url>
    <externalIdentifier/>
    <extraInfos/>
  </itemInfo>
</ns1:getItemInfosResponse>
""" % (
            newItemUID,
            gDateTime.get_formatted_content(gDateTime(), localtime(newItem.created())),
            gDateTime.get_formatted_content(gDateTime(), localtime(newItem.modified())))
        self.assertEquals(expected, resp)
        # if the item is in a meeting, the result is a bit different because
        # we have valid informations about the meeting_date
        self.changeUser('pmManager')
        meeting = self._createMeetingWithItems()
        itemInMeeting = meeting.getItemsInOrder()[0]
        # by default, PloneMeeting creates item without title/description/decision...
        itemInMeeting.setTitle('My new item title')
        itemInMeeting.setDescription('<p>Description</p>', mimetype='text/x-html-safe')
        itemInMeeting.setDecision('<p>Décision</p>', mimetype='text/x-html-safe')
        resp = self._getItemInfos(itemInMeeting.UID())
        meetingDate = gDateTime.get_formatted_content(gDateTime(), localtime(meeting.getDate()))
        expected = """<ns1:getItemInfosResponse xmlns:ns1="http://ws4pm.imio.be" """ \
            """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
            """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
            """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
            """xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>%s</UID>
    <id>item-2</id>
    <title>My new item title</title>
    <creator>pmManager</creator>
    <creation_date>%s</creation_date>
    <modification_date>%s</modification_date>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <detailedDescription/>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <preferredMeeting/>
    <preferred_meeting_date>1950-01-01T00:00:00.006Z</preferred_meeting_date>
    <review_state>presented</review_state>
    <meeting_date>%s</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmManager/mymeetings/plonegov-assembly/item-2</absolute_url>
    <externalIdentifier/>
    <extraInfos/>
  </itemInfo>
</ns1:getItemInfosResponse>
""" % (
            itemInMeeting.UID(),
            gDateTime.get_formatted_content(gDateTime(), localtime(itemInMeeting.created())),
            gDateTime.get_formatted_content(gDateTime(), localtime(itemInMeeting.modified())),
            meetingDate)
        self.assertEquals(expected, resp)
        # if the item with this UID has not been found (user can not access or item does not exists),
        # an empty response is returned
        # unexisting item UID
        resp = self._getItemInfos('aWrongUID')
        expected = """<ns1:getItemInfosResponse xmlns:ns1="http://ws4pm.imio.be" """ \
            """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
            """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
            """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
            """xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>
"""
        self.assertEquals(expected, resp)
        #item UID the logged in user can not access
        self.changeUser('pmReviewer1')
        resp = self._getItemInfos(newItemUID)
        self.assertEquals(expected, resp)

    def test_ws_getItemInfosWithExtraInfosRequest(self):
        """
          Test that getting an item with a given UID and specifying that we want
          extraInfos returns every available informations of the item
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

    def test_ws_getItemInfosWithAnnexesRequest(self):
        """
          Test that getting an item with a given UID returns valuable informations and linked annexes
        """
        cfg = self.meetingConfig
        self.changeUser('pmCreator1')
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingItemPga')) == 0)
        # prepare data for a default item
        req = self._prepareCreationData()
        # add one annex
        data = {'title': 'My annex 1', 'filename': 'smallTestFile.pdf', 'file': 'smallTestFile.pdf'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data)]
        # create the item
        newItem, reponse = self._createItem(req)
        newItemUID = newItem.UID()
        # get informations about the item, by default 'showAnnexes' is False
        resp = self._getItemInfos(newItemUID)
        expected = """<ns1:getItemInfosResponse xmlns:ns1="http://ws4pm.imio.be" """ \
            """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
            """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
            """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" """ \
            """xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>%s</UID>
    <id>%s</id>
    <title>My new item title</title>
    <creator>pmCreator1</creator>
    <creation_date>%s</creation_date>
    <modification_date>%s</modification_date>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <detailedDescription>&lt;p&gt;Detailed description&lt;/p&gt;</detailedDescription>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <preferredMeeting/>
    <preferred_meeting_date>1950-01-01T00:00:00.006Z</preferred_meeting_date>
    <review_state>itemcreated</review_state>
    <meeting_date>1950-01-01T00:00:00.006Z</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmCreator1/mymeetings/plonegov-assembly/%s</absolute_url>
    <externalIdentifier/>
    <extraInfos/>
  </itemInfo>
</ns1:getItemInfosResponse>
""" % (
            newItemUID,
            newItem.getId(),
            gDateTime.get_formatted_content(gDateTime(), localtime(newItem.created())),
            gDateTime.get_formatted_content(gDateTime(), localtime(newItem.modified())),
            newItem.getId())
        #annexes are not shown by default
        self.assertEquals(expected, resp)
        #now with 'showAnnexes=True'
        financial_annex_type_id = calculate_category_id(cfg.annexes_types.item_annexes.get('financial-analysis'))
        item_annex_type_id = calculate_category_id(cfg.annexes_types.item_annexes.get('item-annex'))
        resp = self._getItemInfos(newItemUID, showAnnexes=True)
        expected = """<ns1:getItemInfosResponse xmlns:ns1="http://ws4pm.imio.be" """ \
            """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
            """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
            """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
            """xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>%s</UID>
    <id>%s</id>
    <title>My new item title</title>
    <creator>pmCreator1</creator>
    <creation_date>%s</creation_date>
    <modification_date>%s</modification_date>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <detailedDescription>&lt;p&gt;Detailed description&lt;/p&gt;</detailedDescription>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <preferredMeeting/>
    <preferred_meeting_date>1950-01-01T00:00:00.006Z</preferred_meeting_date>
    <review_state>itemcreated</review_state>
    <meeting_date>1950-01-01T00:00:00.006Z</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmCreator1/mymeetings/plonegov-assembly/%s</absolute_url>
    <externalIdentifier/>
    <extraInfos/>
    <annexes xsi:type="ns1:AnnexInfo">
      <title>My annex 1</title>
      <annexTypeId>%s</annexTypeId>
      <filename>smallTestFile.pdf</filename>
      <file>
%s</file>
    </annexes>
  </itemInfo>
</ns1:getItemInfosResponse>
""" % (
            newItemUID,
            newItem.getId(),
            gDateTime.get_formatted_content(gDateTime(), localtime(newItem.created())),
            gDateTime.get_formatted_content(gDateTime(), localtime(newItem.modified())),
            newItem.getId(),
            financial_annex_type_id,
            base64.encodestring(get_annexes(newItem)[0].file.data))
        # one annex is shown
        self.assertEquals(expected, resp)
        # now check with several (2) annexes...
        afile = open(os.path.join(os.path.dirname(__file__),
                                  'mediumTestFile.odt'))
        annex_file = afile.read()
        afile.close()
        api.content.create(
            title='My BeautifulTestFile title',
            type='annex',
            file=namedfile.NamedBlobFile(
                annex_file,
                filename=safe_unicode(u'myBeautifulTestFile.odt')),
            container=newItem,
            content_category=item_annex_type_id,
            to_print=False,
            confidential=False)

        resp = self._getItemInfos(newItemUID, showAnnexes=True)
        expected = """<ns1:getItemInfosResponse xmlns:ns1="http://ws4pm.imio.be" """ \
            """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
            """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
            """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
            """xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>%s</UID>
    <id>%s</id>
    <title>My new item title</title>
    <creator>pmCreator1</creator>
    <creation_date>%s</creation_date>
    <modification_date>%s</modification_date>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <detailedDescription>&lt;p&gt;Detailed description&lt;/p&gt;</detailedDescription>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <preferredMeeting/>
    <preferred_meeting_date>1950-01-01T00:00:00.006Z</preferred_meeting_date>
    <review_state>itemcreated</review_state>
    <meeting_date>1950-01-01T00:00:00.006Z</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmCreator1/mymeetings/plonegov-assembly/%s</absolute_url>
    <externalIdentifier/>
    <extraInfos/>
    <annexes xsi:type="ns1:AnnexInfo">
      <title>My annex 1</title>
      <annexTypeId>%s</annexTypeId>
      <filename>smallTestFile.pdf</filename>
      <file>
%s</file>
    </annexes>
    <annexes xsi:type="ns1:AnnexInfo">
      <title>My BeautifulTestFile title</title>
      <annexTypeId>%s</annexTypeId>
      <filename>myBeautifulTestFile.odt</filename>
      <file>
%s</file>
    </annexes>
  </itemInfo>
</ns1:getItemInfosResponse>
""" % (
            newItemUID,
            newItem.getId(),
            gDateTime.get_formatted_content(gDateTime(), localtime(newItem.created())),
            gDateTime.get_formatted_content(gDateTime(), localtime(newItem.modified())),
            newItem.getId(),
            financial_annex_type_id,
            base64.encodestring(get_annexes(newItem)[0].file.data),
            item_annex_type_id,
            base64.encodestring(get_annexes(newItem)[1].file.data))
        # 2 annexes are shown
        self.assertEquals(expected, resp)

    def test_ws_getItemInfosWithTemplatesRequest(self):
        """
          Test that getting an item with a given UID and specifying that we want
          showTemplates returns informations about generatable POD templates
        """
        # in the PM test profile, some templates are only defined for the plonemeeting-assembly
        self.usedMeetingConfigId = "plonemeeting-assembly"
        self.changeUser('pmCreator1')
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingItemPma')) == 0)
        # prepare data for a default item
        req = self._prepareCreationData()
        # remove unuseable catagory
        req._creationData._category = ''
        # create the item
        newItem, reponse = self._createItem(req)
        # get informations about the item, by default 'showTemplates' is False
        resp = self._getItemInfos(newItem.UID(), showTemplates=True, toBeDeserialized=False)
        # we have templates
        self.assertTrue(len(resp._itemInfo[0]._templates) == 1)
        mc = self.portal.portal_plonemeeting.getMeetingConfig(newItem)
        # the returned template correspond to the one present in the 'plonemeeting-assembly' meetingConfig
        self.assertEqual(resp._itemInfo[0]._templates[0]._templateId,
                         POD_TEMPLATE_ID_PATTERN.format(mc.podtemplates.itemTemplate.getId(),
                                                        mc.podtemplates.itemTemplate.pod_formats[0]))
        self.assertEqual(resp._itemInfo[0]._templates[0]._templateFilename, u'Item.odt')
        self.assertEqual(resp._itemInfo[0]._templates[0]._templateFormat, 'odt')

    def test_ws_getItemInfosInTheNameOf(self):
        """
          Test that getting an item inTheNameOf antother user works
          Create an item by 'pmCreator1', member of the 'developers' group
          Item will be viewable :
          - by 'pmManager'
          - while getting informations in the name of 'pmCreator1'
          Item will NOT be viewable :
          - while getting informations in the name of 'pmCreator2'
            that is not in the 'developers' group
        """
        # create an item by 'pmCreator1'
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        # check first a working example the degrades it...
        req = getItemInfosRequest()
        req._inTheNameOf = None
        req._UID = item.UID()
        responseHolder = getItemInfosResponse()
        # 'pmCreator1' can get infos about the item
        result = SOAPView(self.portal, req).getItemInfosRequest(req, responseHolder)
        self.assertTrue(result._itemInfo[0].UID == item.UID())
        # now begin, we need to be a 'MeetingManager' or 'Manager' to
        # getItemInfos(inTheNameOf)
        req._inTheNameOf = 'pmCreator1'
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).getItemInfosRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "You need to be 'Manager' or 'MeetingManager' to get item informations 'inTheNameOf'!")
        # now has a 'MeetingManager'
        self.changeUser('pmManager')
        # a MeetingManager can get informations inTheNameOf 'pmCreator1'
        # and it will return relevant result as 'pmCreator1' can see the item
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        result = SOAPView(self.portal, req).getItemInfosRequest(req, responseHolder)
        self.assertTrue(result._itemInfo[0].UID == item.UID())
        # as we switch user while using inTheNameOf, make sure we have
        # falled back to original user
        self.assertTrue(self.portal.portal_membership.getAuthenticatedMember().getId() == 'pmManager')
        # as 'pmCreator2', we can not get item informations
        req._inTheNameOf = 'pmCreator2'
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        result = SOAPView(self.portal, req).getItemInfosRequest(req, responseHolder)
        self.assertTrue(result._itemInfo == [])
        # now for an unexisting inTheNameOf userid
        req._inTheNameOf = 'unexistingUserId'
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).getItemInfosRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "Trying to get item informations 'inTheNameOf' an unexisting user 'unexistingUserId'!")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # add a prefix because we heritate from testMeeting and we do not want every tests of testMeeting to be run here...
    suite.addTest(makeSuite(testSOAPGetItemInfos, prefix='test_ws_'))
    return suite
