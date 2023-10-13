# -*- coding: utf-8 -*-

from collective.iconifiedcategory.utils import calculate_category_id
from imio.helpers.cache import cleanRamCacheFor
from imio.pm.ws.config import POD_TEMPLATE_ID_PATTERN
from imio.pm.ws.soap.soapview import SOAPView
from imio.pm.ws.tests.WS4PMTestCase import serializeRequest
from imio.pm.ws.tests.WS4PMTestCase import WS4PMTestCase
from imio.pm.ws.WS4PM_client import getItemInfosRequest
from imio.pm.ws.WS4PM_client import getItemInfosResponse
from plone import api
from plone import namedfile
from Products.CMFPlone.utils import safe_unicode
from Products.PloneMeeting.utils import get_annexes
from time import localtime
from ZSI.TCtimes import gDateTime

import base64
import os
import ZSI


class testSOAPGetItemInfos(WS4PMTestCase):
    """
        Tests the soap.getItemInfosRequest and soap.getItemInfosRequest methods
        by accessing the real SOAP service
    """

    def test_ws_getItemInfosRequest(self):
        """
          Test that getting an item with a given UID returns valuable informations
        """
        # by default no item exists
        self.changeUser('pmCreator1')
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingItemPga')) == 0)
        # use the SOAP service to create one
        req = self._prepareCreationData()
        newItem, response = self._createItem(req)
        newItemUID = newItem.UID()
        # now an item exists, get informations about it
        req = getItemInfosRequest()
        req._UID = newItemUID
        # Serialize the request so it can be easily tested
        request = serializeRequest(req)
        # This is what the sent enveloppe should looks like
        expected = """<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
            """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
            """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
            """xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">""" \
            """<SOAP-ENV:Header></SOAP-ENV:Header>""" \
            """<SOAP-ENV:Body xmlns:ns1="http://ws4pm.imio.be"><ns1:getItemInfosRequest>""" \
            """<UID>%s</UID><showExtraInfos>false</showExtraInfos><showAnnexes>false</showAnnexes>""" \
            """<include_annex_binary>true</include_annex_binary>""" \
            """<showAssembly>false</showAssembly><showTemplates>false</showTemplates>""" \
            """<showEmptyValues>true</showEmptyValues></ns1:getItemInfosRequest>""" \
            """</SOAP-ENV:Body></SOAP-ENV:Envelope>""" % newItemUID
        result = """%s""" % request
        self.assertEqual(expected, result)
        # now really use the SOAP method to get informations about the item
        resp = self._getItemInfos(newItemUID)
        # the item is not in a meeting so the meeting date is 1950-01-01
        expected = """<ns1:getItemInfosResponse xmlns:ns1="http://ws4pm.imio.be" """ \
            """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
            """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
            """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" """ \
            """xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>{0}</UID>
    <id>my-new-item-title</id>
    <title>My new item title</title>
    <creator>pmCreator1</creator>
    <creation_date>{1}</creation_date>
    <modification_date>{2}</modification_date>
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
""".format(newItemUID,
                gDateTime.get_formatted_content(gDateTime(), localtime(newItem.created())),
                gDateTime.get_formatted_content(gDateTime(), localtime(newItem.modified())))
        self.assertEqual(expected, resp)
        # if the item is in a meeting, the result is a bit different because
        # we have valid informations about the meeting_date
        self.changeUser('pmManager')
        meeting = self._createMeetingWithItems()
        meeting_uid = meeting.UID()
        itemInMeeting = meeting.get_items(ordered=True)[0]
        # by default, PloneMeeting creates item without title/description/decision...
        itemInMeeting.setTitle('My new item title')
        itemInMeeting.setDescription('<p>Description</p>', mimetype='text/x-html-safe')
        itemInMeeting.setDecision('<p>Décision</p>', mimetype='text/x-html-safe')
        itemInMeeting.setPreferredMeeting(meeting_uid)
        itemInMeeting.reindexObject()
        resp = self._getItemInfos(itemInMeeting.UID())
        meetingDate = gDateTime.get_formatted_content(gDateTime(), meeting.date.utctimetuple())
        expected = """<ns1:getItemInfosResponse xmlns:ns1="http://ws4pm.imio.be" """ \
            """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
            """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
            """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
            """xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>{0}</UID>
    <id>item-2</id>
    <title>My new item title</title>
    <creator>pmManager</creator>
    <creation_date>{1}</creation_date>
    <modification_date>{2}</modification_date>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <detailedDescription/>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <preferredMeeting>{3}</preferredMeeting>
    <preferred_meeting_date>{4}</preferred_meeting_date>
    <review_state>presented</review_state>
    <meeting>{3}</meeting>
    <meeting_date>{4}</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmManager/mymeetings/plonegov-assembly/item-2</absolute_url>
    <externalIdentifier/>
    <extraInfos/>
  </itemInfo>
</ns1:getItemInfosResponse>
""".format(itemInMeeting.UID(),
                gDateTime.get_formatted_content(gDateTime(), localtime(itemInMeeting.created())),
                gDateTime.get_formatted_content(gDateTime(), localtime(itemInMeeting.modified())),
                meeting.UID(),
                meetingDate)
        self.assertEqual(expected, resp)
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
        self.assertEqual(expected, resp)
        # item UID the logged in user can not access
        self.changeUser('pmReviewer2')
        resp = self._getItemInfos(newItemUID)
        self.assertEqual(expected, resp)

    def test_ws_getItemInfosWithExtraInfosRequest(self):
        """
          Test that getting an item with a given UID and specifying that we want
          extraInfos returns every available informations of the item
        """
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
        # get informations about the item, by default 'showExtraInfos' is False
        resp = self._getItemInfos(newItemUID, showExtraInfos=True)
        extraInfosFields = SOAPView(self.portal, req)._getExtraInfosFields(newItem)
        # check that every field considered as extra informations is returned in the response
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
    <UID>{0}</UID>
    <id>{1}</id>
    <title>My new item title</title>
    <creator>pmCreator1</creator>
    <creation_date>{2}</creation_date>
    <modification_date>{3}</modification_date>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <detailedDescription>&lt;p&gt;Detailed description&lt;/p&gt;</detailedDescription>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <preferredMeeting/>
    <preferred_meeting_date>1950-01-01T00:00:00.006Z</preferred_meeting_date>
    <review_state>itemcreated</review_state>
    <meeting_date>1950-01-01T00:00:00.006Z</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmCreator1/mymeetings/plonegov-assembly/{4}</absolute_url>
    <externalIdentifier/>
    <extraInfos/>
  </itemInfo>
</ns1:getItemInfosResponse>
""".format(newItemUID,
                newItem.getId(),
                gDateTime.get_formatted_content(gDateTime(), localtime(newItem.created())),
                gDateTime.get_formatted_content(gDateTime(), localtime(newItem.modified())),
                newItem.getId())
        # annexes are not shown by default
        self.assertEqual(expected, resp)
        # now with 'showAnnexes=True'
        financial_annex_type_id = calculate_category_id(cfg.annexes_types.item_annexes.get('financial-analysis'))
        item_annex_type_id = calculate_category_id(cfg.annexes_types.item_annexes.get('item-annex'))
        resp = self._getItemInfos(newItemUID, showAnnexes=True)
        expected = """<ns1:getItemInfosResponse xmlns:ns1="http://ws4pm.imio.be" """ \
            """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
            """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
            """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
            """xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <itemInfo xsi:type="ns1:ItemInfo">
    <UID>{0}</UID>
    <id>{1}</id>
    <title>My new item title</title>
    <creator>pmCreator1</creator>
    <creation_date>{2}</creation_date>
    <modification_date>{3}</modification_date>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <detailedDescription>&lt;p&gt;Detailed description&lt;/p&gt;</detailedDescription>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <preferredMeeting/>
    <preferred_meeting_date>1950-01-01T00:00:00.006Z</preferred_meeting_date>
    <review_state>itemcreated</review_state>
    <meeting_date>1950-01-01T00:00:00.006Z</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmCreator1/mymeetings/plonegov-assembly/{4}</absolute_url>
    <externalIdentifier/>
    <extraInfos/>
    <annexes xsi:type="ns1:AnnexInfo">
      <id>smalltestfile.pdf</id>
      <title>My annex 1</title>
      <annexTypeId>{5}</annexTypeId>
      <filename>smallTestFile.pdf</filename>
      <file>
{6}</file>
    </annexes>
  </itemInfo>
</ns1:getItemInfosResponse>
""".format(newItemUID,
                newItem.getId(),
                gDateTime.get_formatted_content(gDateTime(), localtime(newItem.created())),
                gDateTime.get_formatted_content(gDateTime(), localtime(newItem.modified())),
                newItem.getId(),
                financial_annex_type_id,
                base64.encodestring(get_annexes(newItem)[0].file.data))
        # one annex is shown
        self.assertEqual(expected, resp)
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
    <UID>{0}</UID>
    <id>{1}</id>
    <title>My new item title</title>
    <creator>pmCreator1</creator>
    <creation_date>{2}</creation_date>
    <modification_date>{3}</modification_date>
    <category>development</category>
    <description>&lt;p&gt;Description&lt;/p&gt;</description>
    <detailedDescription>&lt;p&gt;Detailed description&lt;/p&gt;</detailedDescription>
    <decision>&lt;p&gt;Décision&lt;/p&gt;</decision>
    <preferredMeeting/>
    <preferred_meeting_date>1950-01-01T00:00:00.006Z</preferred_meeting_date>
    <review_state>itemcreated</review_state>
    <meeting_date>1950-01-01T00:00:00.006Z</meeting_date>
    <absolute_url>http://nohost/plone/Members/pmCreator1/mymeetings/plonegov-assembly/{4}</absolute_url>
    <externalIdentifier/>
    <extraInfos/>
    <annexes xsi:type="ns1:AnnexInfo">
      <id>{5}</id>
      <title>My annex 1</title>
      <annexTypeId>{6}</annexTypeId>
      <filename>smallTestFile.pdf</filename>
      <file>
{7}</file>
    </annexes>
    <annexes xsi:type="ns1:AnnexInfo">
      <id>{8}</id>
      <title>My BeautifulTestFile title</title>
      <annexTypeId>{9}</annexTypeId>
      <filename>myBeautifulTestFile.odt</filename>
      <file>
{10}</file>
    </annexes>
  </itemInfo>
</ns1:getItemInfosResponse>
""".format(newItemUID,
                newItem.getId(),
                gDateTime.get_formatted_content(gDateTime(), localtime(newItem.created())),
                gDateTime.get_formatted_content(gDateTime(), localtime(newItem.modified())),
                newItem.getId(),
                get_annexes(newItem)[0].id,
                financial_annex_type_id,
                base64.encodestring(get_annexes(newItem)[0].file.data),
                get_annexes(newItem)[1].id,
                item_annex_type_id,
                base64.encodestring(get_annexes(newItem)[1].file.data))
        # 2 annexes are shown
        self.assertEqual(expected, resp)

    def test_ws_getItemInfosWithPODTemplatesRequest(self):
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
        # we have 1 template
        self.assertEqual(len(resp._itemInfo[0]._templates), 1)
        cfg = self.meetingConfig
        # the returned template correspond to the one present in the 'plonemeeting-assembly' meetingConfig
        self.assertEqual(resp._itemInfo[0]._templates[0]._templateId,
                         POD_TEMPLATE_ID_PATTERN.format(cfg.podtemplates.itemTemplate.getId(),
                                                        cfg.podtemplates.itemTemplate.pod_formats[0]))
        self.assertEqual(resp._itemInfo[0]._templates[0]._templateFilename, u'Item.odt')
        self.assertEqual(resp._itemInfo[0]._templates[0]._templateFormat, 'odt')

    def test_ws_getItemInfosWithReusedPODTemplates(self):
        """
          Test when some returned POD templates are reusing another POD template
          so do not have an odt_file.
        """
        # in the PM test profile, some templates are only defined for the plonemeeting-assembly
        self.usedMeetingConfigId = "plonegov-assembly"
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        # first check that the only returned template is a template rusing another
        viewlet = self._get_viewlet(
            context=item,
            manager_name='plone.belowcontenttitle',
            viewlet_name='document-generation-link')
        templates = viewlet.get_generable_templates()
        self.assertEqual(len(templates), 1)
        self.assertTrue(templates[0].pod_template_to_use)
        self.assertIsNone(templates[0].odt_file)
        # get the reponse
        resp = self._getItemInfos(item.UID(), showTemplates=True, toBeDeserialized=False)
        # we have 1 template
        self.assertEqual(len(resp._itemInfo[0]._templates), 1)
        # templateFilename was taken from template to use
        self.assertEqual(resp._itemInfo[0]._templates[0]._templateFilename, u'Item.odt')
        self.assertEqual(resp._itemInfo[0]._templates[0]._templateFormat, 'odt')

    def test_ws_getItemInfosWithAnnexesTypes(self):
        """
          Test that getting an item with an annex_type return only the annexes
          with the corresponding annexTypeId attribute.
        """
        cfg = self.meetingConfig
        self.changeUser('pmCreator1')
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingItemPma')) == 0)
        # prepare data for a default item
        req = self._prepareCreationData()
        # add one annex
        data = {'title': 'My annex 1',
                'filename': 'smallTestFile.pdf',
                'file': 'smallTestFile.pdf'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data)]
        # create the item
        newItem, reponse = self._createItem(req)
        financial_annex_type_id = calculate_category_id(
            cfg.annexes_types.item_annexes.get('financial-analysis'))
        item_annex_type_id = calculate_category_id(
            cfg.annexes_types.item_annexes.get('item-annex'))
        allowed_annexes_types = [financial_annex_type_id, item_annex_type_id]
        # get informations about the item, by default 'allowed_annexes_types' is empty
        resp = self._getItemInfos(newItem.UID(),
                                  showAnnexes=True,
                                  toBeDeserialized=False)
        # we have 1 annex
        self.assertEqual(len(resp._itemInfo[0]._annexes), 1)
        # the returned annex is the one created
        self.assertEqual(resp._itemInfo[0]._annexes[0]._title, 'My annex 1')
        self.assertEqual(resp._itemInfo[0]._annexes[0]._filename, 'smallTestFile.pdf')
        # filter on 'item_annex_type' annex type
        allowed_annexes_types = [financial_annex_type_id]
        resp = self._getItemInfos(newItem.UID(),
                                  showAnnexes=True,
                                  allowed_annexes_types=allowed_annexes_types,
                                  toBeDeserialized=False)
        # we have 1 annex
        self.assertEqual(len(resp._itemInfo[0]._annexes), 1)
        # the returned annex is the one created
        self.assertEqual(resp._itemInfo[0]._annexes[0]._title, 'My annex 1')
        self.assertIn(resp._itemInfo[0]._annexes[0]._annexTypeId, allowed_annexes_types)
        # filter on 'financial_annex_type_id' annex type
        allowed_annexes_types = [item_annex_type_id]
        resp = self._getItemInfos(newItem.UID(),
                                  showAnnexes=True,
                                  allowed_annexes_types=allowed_annexes_types,
                                  toBeDeserialized=False)
        # we have 0 annex
        self.assertEqual(len(resp._itemInfo[0]._annexes), 0)

    def test_ws_getItemInfosWithBinary(self):
        """
          Test that getting an item with include_annex_binary return the annex
          binary file.
        """
        self.changeUser('pmCreator1')
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingItemPma')) == 0)
        # prepare data for a default item
        req = self._prepareCreationData()
        # add one annex
        data = {'title': 'My annex 1', 'filename': 'smallTestFile.pdf', 'file': 'smallTestFile.pdf'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data)]
        # create the item
        newItem, reponse = self._createItem(req)
        # get informations about the item, by default include_annex_binary is True
        resp = self._getItemInfos(newItem.UID(), showAnnexes=True, toBeDeserialized=False)
        # we have 1 annex
        self.assertEqual(len(resp._itemInfo[0]._annexes), 1)
        # the returned annex is the one created
        self.assertEqual(resp._itemInfo[0]._annexes[0]._title, 'My annex 1')
        # file content is preserved correctly
        annex_file = open(os.path.join(os.path.dirname(__file__), data.get('file')))
        self.assertEqual(resp._itemInfo[0]._annexes[0]._file, annex_file.read())
        # get informations about the item, set include_annex_binary to False
        resp = self._getItemInfos(newItem.UID(),
                                  showAnnexes=True,
                                  include_annex_binary=False,
                                  toBeDeserialized=False)
        # we have 1 annex
        self.assertEqual(len(resp._itemInfo[0]._annexes), 1)
        # the returned annex is the one created
        self.assertEqual(resp._itemInfo[0]._annexes[0]._title, 'My annex 1')
        # attribute _file of the annex should be empty
        self.assertFalse(resp._itemInfo[0]._annexes[0]._file)

    def test_ws_getItemInfosShowEmptyValues(self):
        """
          Parameter showEmptyValues=False will remove empty values from returned result.
        """
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        resp = self._getItemInfos(item.UID(), toBeDeserialized=False)
        # empty values are returned
        self.assertTrue('_decision' in resp._itemInfo[0].__dict__)
        self.assertEqual(resp._itemInfo[0]._decision, '')
        resp = self._getItemInfos(item.UID(), showEmptyValues=False, toBeDeserialized=False)
        # empty values are no more returned
        self.assertFalse('_decision' in resp._itemInfo[0].__dict__)
        self.assertEqual(
            len(resp._itemInfo[0].__dict__),
            len([k for k, v in resp._itemInfo[0].__dict__.items() if v]))

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
        self.assertEqual(
            cm.exception.string,
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
        self.assertEqual(
            cm.exception.string,
            "Trying to get item informations 'inTheNameOf' an unexisting user 'unexistingUserId'!")
        self._check_after_inTheNameOf()

    def test_ws_getItemInfosWithShowAssembly(self):
        """When showAssembly=True, assembly is returned in a text form
           when using assembly fields or contacts."""
        self.changeUser('pmManager')
        # item out of a meeting
        item = self.create('MeetingItem')
        item_uid = item.UID()
        resp = self._getItemInfos(item_uid, showAssembly=True, toBeDeserialized=False)
        self.assertIsNone(resp.ItemInfo[0]._item_assembly)

        # item in a meeting
        meeting = self._createMeetingWithItems()
        item = meeting.get_items(ordered=True)[0]
        item_uid = item.UID()
        # showAssembly=False
        resp = self._getItemInfos(item_uid, showAssembly=False, toBeDeserialized=False)
        self.assertIsNone(resp.ItemInfo[0]._item_assembly)
        # itemAssembly
        resp = self._getItemInfos(item_uid, showAssembly=True, toBeDeserialized=False)
        self.assertEqual(resp.ItemInfo[0]._item_assembly,
                         'itemAssembly|<p>Bill Gates, Steve Jobs</p>|itemAssemblyExcused||'
                         'itemAssemblyAbsents||itemAssemblyGuests|')
        item.setItemAssembly('Local assembly')
        item.setItemAssemblyAbsents('Local assembly absents')
        item.setItemAssemblyExcused('Local assembly excused')
        item.setItemAssemblyGuests('Local assembly guests')
        resp = self._getItemInfos(item_uid, showAssembly=True, toBeDeserialized=False)
        self.assertEqual(resp.ItemInfo[0]._item_assembly,
                         'itemAssembly|<p>Local assembly</p>|'
                         'itemAssemblyExcused|<p>Local assembly excused</p>|'
                         'itemAssemblyAbsents|<p>Local assembly absents</p>|'
                         'itemAssemblyGuests|<p>Local assembly guests</p>')
        # contacts
        cfg = self.meetingConfig
        cfg.setUsedMeetingAttributes(('attendees', 'excused', 'absents', 'signatories', ))
        ordered_contacts = cfg.getField('orderedContacts').Vocabulary(cfg).keys()
        cfg.setOrderedContacts(ordered_contacts)
        meeting = self._createMeetingWithItems()
        item = meeting.get_items(ordered=True)[0]
        item_uid = item.UID()
        resp = self._getItemInfos(item_uid, showAssembly=False, toBeDeserialized=False)
        self.assertIsNone(resp.ItemInfo[0]._item_assembly)
        resp = self._getItemInfos(item_uid, showAssembly=True, toBeDeserialized=False)
        self.assertEqual(resp.ItemInfo[0]._item_assembly,
                         u'Attendees|Monsieur Person1FirstName Person1LastName, Assembly member 1\n'
                         u'Monsieur Person2FirstName Person2LastName, Assembly member 2\n'
                         u'Madame Person3FirstName Person3LastName, Assembly member 3\n'
                         u'Madame Person4FirstName Person4LastName, Assembly member 4 & 5|'
                         u'Absents||Excused||itemAssemblyGuests|')
        # define absent on item
        item_attendees = item.get_attendees()
        meeting.item_absents[item_uid] = [item_attendees[0], item_attendees[2]]
        resp = self._getItemInfos(item_uid, showAssembly=True, toBeDeserialized=False)
        self.assertEqual(resp.ItemInfo[0]._item_assembly,
                         u'Attendees|Monsieur Person2FirstName Person2LastName, Assembly member 2\n'
                         u'Madame Person4FirstName Person4LastName, Assembly member 4 & 5|'
                         u'Absents|Monsieur Person1FirstName Person1LastName, Assembly member 1\n'
                         u'Madame Person3FirstName Person3LastName, Assembly member 3|'
                         u'Excused||itemAssemblyGuests|')

    def test_ws_getSingleItemInfos(self):
        """The getSingleItemInfos method behaves like getItemInfos
            but returns one single item infos instead list of ItemInfo instances."""
        self.changeUser('pmManager')
        # item out of a meeting
        item = self.create('MeetingItem')
        item_uid = item.UID()
        # informations returned by getItemInfos and getSingleItemInfos are equal
        resp_getiteminfos = self._getItemInfos(item_uid, toBeDeserialized=False)
        resp_getsimpleiteminfos = self._getItemInfos(item_uid, toBeDeserialized=False, useSingleItemInfos=True)
        self.assertEqual(resp_getiteminfos._itemInfo[0].__dict__,
                         resp_getsimpleiteminfos.__dict__)
        # as well when using showEmptyValues=False
        resp_getnotemptyiteminfos = self._getItemInfos(item_uid,
                                                       showEmptyValues=False,
                                                       toBeDeserialized=False)
        resp_getnotemptysimpleiteminfos = self._getItemInfos(item_uid,
                                                             showEmptyValues=False,
                                                             toBeDeserialized=False,
                                                             useSingleItemInfos=True)
        self.assertEqual(resp_getnotemptyiteminfos._itemInfo[0].__dict__,
                         resp_getnotemptysimpleiteminfos.__dict__)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # add a prefix because we heritate from testMeeting and
    # we do not want every tests of testMeeting to be run here...
    suite.addTest(makeSuite(testSOAPGetItemInfos, prefix='test_ws_'))
    return suite
