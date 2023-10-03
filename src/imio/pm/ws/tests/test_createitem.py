# -*- coding: utf-8 -*-
#
# File: test_createitem.py
#
# GNU General Public License (GPL)
#

from imio.helpers.cache import cleanRamCacheFor
from imio.pm.ws.soap.soapview import MIMETYPE_NOT_FOUND_OF_ANNEX_WARNING
from imio.pm.ws.soap.soapview import MULTIPLE_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING
from imio.pm.ws.soap.soapview import SOAPView
from imio.pm.ws.soap.soapview import WRONG_HTML_WARNING
from imio.pm.ws.tests.WS4PMTestCase import deserialize
from imio.pm.ws.tests.WS4PMTestCase import serializeRequest
from imio.pm.ws.tests.WS4PMTestCase import WS4PMTestCase
from imio.pm.ws.WS4PM_client import createItemResponse
from magic import MagicException
from Products.PloneMeeting.config import ITEM_NO_PREFERRED_MEETING_VALUE
from Products.PloneMeeting.utils import get_annexes
from zope.i18n import translate
from ZSI.schema import GTD

import base64
import magic
import unittest
import ZSI


class testSOAPCreateItem(WS4PMTestCase):
    """
        Tests the soap.createItemRequest method by accessing the real SOAP service
    """

    def test_ws_createItemRequest(self):
        """
          In the default test configuration, the user 'pmCreator1' can create an item for
          proposingGroup 'developers' in the MeetingConfig 'plonegov-assembly'
        """
        # by default no item exists
        self.changeUser('pmCreator1')
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingItemPga')) == 0)
        req = self._prepareCreationData()
        # This is what the sent enveloppe should looks like, note that the decision is "Décision<strong>wrongTagd</p>"
        # instead of '<p>Décision</p>' so we check accents and missing <p></p>
        req._creationData._decision = 'Décision<strong>wrongTagd</p>'
        # Serialize the request so it can be easily tested
        request = serializeRequest(req)
        expected = """POST /plone/createItemRequest HTTP/1.0
Authorization: Basic %s:%s
Content-Length: 102
Content-Type: text/xml
SOAPAction: /
<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
"""xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
"""xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">""" \
"""<SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body xmlns:ns1="http://ws4pm.imio.be"><ns1:createItemRequest>""" \
"""<meetingConfigId>plonegov-assembly</meetingConfigId><proposingGroupId>developers</proposingGroupId>""" \
"""<creationData xsi:type="ns1:CreationData"><title>My new item title</title><category>development</category>""" \
"""<description>&lt;p&gt;Description&lt;/p&gt;</description>""" \
"""<detailedDescription>&lt;p&gt;Detailed description&lt;/p&gt;</detailedDescription>""" \
"""<decision>D\xc3\xa9cision&lt;strong&gt;wrongTagd&lt;/p&gt;</decision></creationData><cleanHtml>true</cleanHtml>""" \
"""</ns1:createItemRequest>""" \
"""</SOAP-ENV:Body></SOAP-ENV:Envelope>""" % ('pmCreator1', 'meeting')
        result = """POST /plone/createItemRequest HTTP/1.0
Authorization: Basic %s:%s
Content-Length: 102
Content-Type: text/xml
SOAPAction: /
%s""" % ('pmCreator1', 'meeting', request)
        self.assertEqual(expected, result)
        # now really use the SOAP method to create an item
        newItem, response = self._createItem(req)
        newItemUID = newItem.UID()
        resp = deserialize(response)
        expected = """<ns1:createItemResponse xmlns:ns1="http://ws4pm.imio.be" """ \
            """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """\
            """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
            """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
            """xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <UID>%s</UID>
  <warnings>%s</warnings>
</ns1:createItemResponse>
""" % (newItemUID, translate(WRONG_HTML_WARNING,
                             domain='imio.pm.ws',
                             mapping={'item_path': newItem.absolute_url_path(),
                                      'creator': 'pmCreator1'},
                             context=self.request)
       )
        self.assertEqual(expected, resp)
        # the item is actually created
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingItemPga', UID=newItemUID)) == 1)
        # responseHolder for tests here above
        responseHolder = createItemResponse()
        # check that we can create an item with a NoneType HTML field
        req._creationData._decision = None
        newItemWithEmptyDecisionUID = SOAPView(self.portal, req).createItemRequest(req, responseHolder)._UID
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingItemPga',
                                                       UID=newItemWithEmptyDecisionUID)) == 1)
        # No matter how the item is created, with or without a decision, every HTML fields are surrounded by <p></p>
        obj = self.portal.portal_catalog(portal_type='MeetingItemPga', UID=newItemWithEmptyDecisionUID)[0].getObject()
        self.failIf(obj.getDecision(keepWithNext=False) != '<p></p>')

    def test_ws_createItemRaisedZSIFaults(self):
        """
          Test SOAP service behaviour when creating an item with some wrong arguments
        """
        # by default no item exists
        self.changeUser('pmCreator1')
        req = self._prepareCreationData(with_category=False)
        responseHolder = createItemResponse()
        # the title is mandatory
        req._creationData._title = None
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(cm.exception.string, "A 'title' is mandatory!")
        req._creationData._title = 'A valid title'
        # the meetingConfigId must exists
        req._meetingConfigId = 'wrongMeetingConfigId'
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(cm.exception.string, "Unknown meetingConfigId : 'wrongMeetingConfigId'!")
        req._meetingConfigId = self.usedMeetingConfigId
        # the connected user must be able to create an item for the given proposingGroupId
        req._proposingGroupId = 'vendors'
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(cm.exception.string, "'pmCreator1' can not create items for the 'vendors' group!")
        # the connected user must be able to create an item with the given category
        # set back correct proposingGroup
        req._proposingGroupId = 'developers'
        # if category is mandatory and empty, it raises ZSI.Fault
        self._enableField('category')
        req._creationData._category = None
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(cm.exception.string, "In this config, category is mandatory!")
        # wrong category and category not used, ZSI.Fault
        self._enableField('category', enable=False)
        req._creationData._category = 'wrong-category-id'
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(cm.exception.string,
                         'The optional field "category" is not activated in this configuration!')
        # wrong category and using category
        self._enableField('category')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(cm.exception.string,
                         "'wrong-category-id' is not available for the 'developers' group!")
        # if the user trying to create an item has no member area, a ZSI.Fault is raised
        # remove the 'pmCreator2' personal area
        self.changeUser('admin')
        self.portal.Members.manage_delObjects(ids=['pmCreator2'])
        req._proposingGroupId = 'vendors'
        self.changeUser('pmCreator2')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(cm.exception.string, "No member area for 'pmCreator2'.  Never connected to PloneMeeting?")

    def test_ws_createItemWithOptionalFields(self):
        """
          Test SOAP service behaviour when creating an item with some optional fields
        """
        # by default no item exists
        self.changeUser('pmCreator1')
        req = self._prepareCreationData()
        responseHolder = createItemResponse()
        # we can not use an optional field that is not activated in the current MeetingConfig
        self.assertTrue('motivation' not in self.meetingConfig.getUsedItemAttributes())
        req._creationData._motivation = '<p>Motivation sample text</p>'
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(cm.exception.string,
                         "The optional field \"motivation\" is not activated in this configuration!")
        # if we activate it, then the resulting item is correct
        self.meetingConfig.setUsedItemAttributes(self.meetingConfig.getUsedItemAttributes() + ('motivation', ))
        newItem, response = self._createItem(req)
        self.assertTrue(newItem.getMotivation() == '<p>Motivation sample text</p>')

    def test_ws_createItemToDiscuss(self):
        """
          Test SOAP service behaviour when creating an item using toDiscuss :
          - optional field so only useable when relevant;
          - if not set, then default value is used.
        """
        cfg = self.meetingConfig
        # by default no item exists
        self.changeUser('pmCreator1')
        req = self._prepareCreationData()
        responseHolder = createItemResponse()
        # we can not use an optional field that is not activated in the current MeetingConfig
        cfg.setUsedItemAttributes(('category', 'description', 'detailedDescription',))
        self.assertFalse('toDiscuss' in cfg.getUsedItemAttributes())
        # set toDiscuss to True
        req._creationData._toDiscuss = True
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(cm.exception.string,
                         "The optional field \"toDiscuss\" is not activated in this configuration!")
        # if we activate it, then the resulting item is correct
        cfg.setUsedItemAttributes(cfg.getUsedItemAttributes() + ('toDiscuss', ))

        # create item first time when default is True, then False
        # as given in soap request, it is True each time
        cfg.setToDiscussDefault(False)
        newItem, response = self._createItem(req)
        self.assertTrue(newItem.getToDiscuss())
        cfg.setToDiscussDefault(True)
        newItem, response = self._createItem(req)
        self.assertTrue(newItem.getToDiscuss())
        # if not set in soap request, parameter is ignored, again with default True and False
        # as not given in soap request, it is the default defined value
        req._creationData._toDiscuss = None
        cfg.setToDiscussDefault(False)
        newItem, response = self._createItem(req)
        self.assertFalse(newItem.getToDiscuss())
        cfg.setToDiscussDefault(True)
        newItem, response = self._createItem(req)
        self.assertTrue(newItem.getToDiscuss())

    def test_ws_createItemWithOneAnnexRequest(self):
        """
          Test SOAP service behaviour when creating items with one annex
        """
        # by default no item exists
        self.changeUser('pmCreator1')
        req = self._prepareCreationData()
        data = {'title': 'My annex 1', 'filename': 'smallTestFile.pdf', 'file': 'smallTestFile.pdf'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data)]
        annex = req._creationData._annexes[0]
        # Serialize the request so it can be easily tested
        request = serializeRequest(req)
        # This is what the sent enveloppe should looks like
        expected = """POST /plone/createItemRequest HTTP/1.0
Authorization: Basic %s:%s
Content-Length: 102
Content-Type: text/xml
SOAPAction: /
<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
"""xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
"""xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">""" \
"""<SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body xmlns:ns1="http://ws4pm.imio.be">""" \
"""<ns1:createItemRequest><meetingConfigId>plonegov-assembly</meetingConfigId>""" \
"""<proposingGroupId>developers</proposingGroupId><creationData xsi:type="ns1:CreationData">""" \
"""<title>My new item title</title><category>development</category>""" \
"""<description>&lt;p&gt;Description&lt;/p&gt;</description>""" \
"""<detailedDescription>&lt;p&gt;Detailed description&lt;/p&gt;</detailedDescription>""" \
"""<decision>&lt;p&gt;Décision&lt;/p&gt;</decision>""" \
"""<annexes xsi:type="ns1:AnnexInfo"><title>%s</title><annexTypeId>%s</annexTypeId><filename>%s</filename><file>
%s</file></annexes></creationData><cleanHtml>true</cleanHtml></ns1:createItemRequest>""" \
"""</SOAP-ENV:Body></SOAP-ENV:Envelope>""" % ('pmCreator1', 'meeting', annex._title, annex._annexTypeId,
                                              annex._filename, base64.encodestring(annex._file))
        result = """POST /plone/createItemRequest HTTP/1.0
Authorization: Basic %s:%s
Content-Length: 102
Content-Type: text/xml
SOAPAction: /
%s""" % ('pmCreator1', 'meeting', request)
        self.assertEqual(expected, result)
        newItem, response = self._createItem(req)
        # now check the created item have the annex
        annexes = get_annexes(newItem)
        # the annex is actually created
        self.failUnless(len(annexes) == 1)
        # the annex mimetype is correct
        annex = annexes[0]
        self.failUnless(annex.file.contentType == 'application/pdf')
        # the annex metadata are ok
        self.assertEqual(annex.Title(), 'My annex 1')
        self.assertEqual(annex.content_category,
                         'plonegov-assembly-annexes_types_-_item_annexes_-_financial-analysis')

    @unittest.skip("This test is skipped, remove decorator if you use libmagic/file < 5.10")
    def test_ws_createItemWithAnnexNotRecognizedByLibmagicRequest(self):
        """
          Test SOAP service behaviour when creating items with one annex that is not recognized
          by libmagic.  The annex used here is a MS Word .doc file that fails to be recognized when
          using libmagic/file 5.09
        """
        self.changeUser('pmCreator1')
        req = self._prepareCreationData()
        data = {'title': 'My crashing created annex',
                'filename': 'file_crash_libmagic.doc',
                'file': 'file_crash_libmagic.doc'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data)]
        annex = req._creationData._annexes[0]
        # first make sure this file crash libmagic
        self.assertRaises(MagicException, magic.Magic(mime=True).from_buffer, annex._file)
        newItem, response = self._createItem(req)
        # the annex is nevertheless created and correctly recognized because it had a correct file extension
        annexes = get_annexes(newItem)
        self.failUnless(len(annexes) == 1)
        # the annex mimetype is correct
        annex = annexes[0]
        self.failUnless(annex.file.contentType == 'application/msword')
        # the annex metadata are ok
        self.failUnless(annex.Title() == 'My crashing created annex' and
                        annex.getMeetingFileType().getId() == 'financial-analysis')
        # if libmagic crash and no valid filename provided, the annex is not created
        data = {'title': 'My crashing NOT created annex',
                'filename': 'file_crash_libmagic_without_extension',
                'file': 'file_crash_libmagic.doc'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data)]
        newItem2, response = self._createItem(req)
        self.failUnless(len(get_annexes(newItem2)) == 0)
        # a warning specifying that annex was not added because mimetype could
        # not reliabily be found is added in the response
        self.assertEqual(response._warnings, [translate(MIMETYPE_NOT_FOUND_OF_ANNEX_WARNING,
                                                        domain='imio.pm.ws',
                                                        mapping={'annex_path': (data['filename']),
                                                                 'item_path': newItem2.absolute_url_path()},
                                                        context=self.portal.REQUEST)])

    def test_ws_createItemWithSeveralAnnexesRequest(self):
        """
          Test SOAP service behaviour when creating items with several annexes of different types
        """
        # by default no item exists
        self.changeUser('pmCreator1')
        req = self._prepareCreationData()
        # add 4 extra annexes
        # no data give, some default values are used (smallTestFile.pdf)
        data1 = {'title': 'My annex 1',
                 'filename': 'smallTestFile.pdf',
                 'file': 'smallTestFile.pdf'}
        # other annexTypeId than the default one
        data2 = {'title': 'My annex 2',
                 'filename': 'arbitraryFilename.odt',
                 'file': 'mediumTestFile.odt',
                 'annexTypeId': 'budget-analysis'}
        # a wrong annexTypeId and a test with a large msword document
        data3 = {'title': 'My annex 3',
                 'filename': 'largeTestFile.doc',
                 'file': 'largeTestFile.doc',
                 'annexTypeId': 'wrong-annexTypeId'}
        # empty file data provided, at the end, the annex is not created but the item is correctly created
        data4 = {'title': 'My annex 4',
                 'filename': 'emptyTestFile.txt',
                 'file': 'emptyTestFile.txt',
                 'annexTypeId': 'budget-analysis'}
        # a file that will have several extensions found in mimetypes_registry
        # is not handled if no valid filename is provided
        data5 = {'title': 'My annex 5',
                 'filename': 'notValidFileNameNoExtension',
                 'file': 'octetStreamTestFile.bin',
                 'annexTypeId': 'budget-analysis'}
        # but if the filename is valid, then the annex is handled
        data6 = {'title': 'My annex 6',
                 'filename': 'validExtension.bin',
                 'file': 'octetStreamTestFile.bin',
                 'annexTypeId': 'budget-analysis'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data1), self._prepareAnnexInfo(**data2),
                                      self._prepareAnnexInfo(**data3), self._prepareAnnexInfo(**data4),
                                      self._prepareAnnexInfo(**data5), self._prepareAnnexInfo(**data6)]
        # serialize the request so it can be easily tested
        request = serializeRequest(req)
        # build annexes part of the envelope
        annexesEnveloppePart = ""
        for annex in req._creationData._annexes:
            annexesEnveloppePart = annexesEnveloppePart + """<annexes xsi:type="ns1:AnnexInfo"><title>%s</title>""" \
                """<annexTypeId>%s</annexTypeId><filename>%s</filename><file>
%s</file></annexes>""" % (annex._title, annex._annexTypeId, annex._filename, base64.encodestring(annex._file))
        # This is what the sent enveloppe should looks like
        expected = """POST /plone/createItemRequest HTTP/1.0
Authorization: Basic %s:%s
Content-Length: 102
Content-Type: text/xml
SOAPAction: /
<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
"""xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
"""xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">""" \
"""<SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body xmlns:ns1="http://ws4pm.imio.be"><ns1:createItemRequest>""" \
"""<meetingConfigId>plonegov-assembly</meetingConfigId><proposingGroupId>developers</proposingGroupId>""" \
"""<creationData xsi:type="ns1:CreationData"><title>My new item title</title><category>development</category>""" \
"""<description>&lt;p&gt;Description&lt;/p&gt;</description>""" \
"""<detailedDescription>&lt;p&gt;Detailed description&lt;/p&gt;</detailedDescription>""" \
"""<decision>&lt;p&gt;Décision&lt;/p&gt;</decision>""" \
"""%s</creationData><cleanHtml>true</cleanHtml></ns1:createItemRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>""" \
% ('pmCreator1', 'meeting', annexesEnveloppePart)
        result = """POST /plone/createItemRequest HTTP/1.0
Authorization: Basic %s:%s
Content-Length: 102
Content-Type: text/xml
SOAPAction: /
%s""" % ('pmCreator1', 'meeting', request)
        self.assertEqual(expected, result)
        newItem, response = self._createItem(req)
        annexes = get_annexes(newItem)
        # 4 annexes are actually created
        self.failUnless(len(annexes) == 4)
        # the annexes mimetype are corrects
        self.failUnless(annexes[0].file.contentType == 'application/pdf')
        self.failUnless(annexes[1].file.contentType == 'application/vnd.oasis.opendocument.text')
        self.failUnless(annexes[2].file.contentType == 'application/msword')
        self.failUnless(annexes[3].file.contentType == 'application/octet-stream')
        # the annexes metadata are ok
        self.failUnless(
            annexes[0].Title() == 'My annex 1' and
            annexes[0].content_category == 'plonegov-assembly-annexes_types_-_item_annexes_-_financial-analysis')
        self.failUnless(
            annexes[1].Title() == 'My annex 2' and
            annexes[1].content_category == 'plonegov-assembly-annexes_types_-_item_annexes_-_budget-analysis')
        # meetingFileType is back to default one when a wrong file type is given in the annexInfo
        self.failUnless(
            annexes[2].Title() == 'My annex 3' and
            annexes[2].content_category == 'plonegov-assembly-annexes_types_-_item_annexes_-_financial-analysis')
        self.failUnless(
            annexes[3].Title() == 'My annex 6' and
            annexes[3].content_category == 'plonegov-assembly-annexes_types_-_item_annexes_-_budget-analysis')
        # annexes filename are the ones defined in the 'filename', either it is generated
        self.failUnless(annexes[0].file.filename == u'smallTestFile.pdf')
        self.failUnless(annexes[1].file.filename == u'arbitraryFilename.odt')
        self.failUnless(annexes[2].file.filename == u'largeTestFile.doc')
        self.failUnless(annexes[3].file.filename == u'validExtension.bin')
        # now try to create an item with an annex that has no file
        # when file attribute is not provided, the annex is not created
        data = {'title': 'My annex 7',
                'filename': 'validExtension.bin',
                'annexTypeId': 'budget-analysis'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data), ]
        self.assertEqual(req._creationData._annexes[0]._file, None)
        newItem, response = self._createItem(req)
        annexes = get_annexes(newItem)
        # no annexes have been added
        self.assertEqual(len(annexes), 0)

    def test_ws_createItemWithWarnings(self):
        """
          Test that during item creation, if non blocker errors occur (warnings), it is displayed in the response
        """
        # if the proposed HTML of one of the rich field is wrong
        # it is reworked by BeautifulSoup and a warning is displayed
        self.changeUser('pmCreator1')
        req = self._prepareCreationData()
        wrongHTML = '<p>Wrong HTML<strong></p></strong>'
        req._creationData._decision = wrongHTML
        newItem, response = self._createItem(req)
        resp = deserialize(response)
        expected = """<ns1:createItemResponse xmlns:ns1="http://ws4pm.imio.be" """ \
            """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
            """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
            """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
            """xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <UID>%s</UID>
  <warnings>%s</warnings>
</ns1:createItemResponse>
""" % (newItem.UID(), translate(WRONG_HTML_WARNING,
                                domain='imio.pm.ws',
                                mapping={'item_path': newItem.absolute_url_path(),
                                         'creator': 'pmCreator1'},
                                context=self.request))
        self.assertEqual(expected, resp)
        # now test warnings around file mimetype
        data = {'title': 'My annex with spécial char and no filename',
                'filename': '',
                'file': 'octetStreamTestFile.bin',
                'annexTypeId': 'budget-analysis'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data)]
        # several extensions found and no valid filename extension, the annex is not created and a warning is added
        newItem, response = self._createItem(req)
        resp = deserialize(response)
        # 2 warnings are returned
        expected = """<ns1:createItemResponse xmlns:ns1="http://ws4pm.imio.be" """ \
            """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
            """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
            """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
            """xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <UID>%s</UID>
  <warnings>%s</warnings>
  <warnings>%s</warnings>
</ns1:createItemResponse>
""" % (newItem.UID(), translate(
                WRONG_HTML_WARNING,
                domain='imio.pm.ws',
                mapping={'item_path': newItem.absolute_url_path(),
                         'creator': 'pmCreator1'},
                context=self.request),
                translate(
                    MULTIPLE_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING,
                    domain='imio.pm.ws',
                    mapping={'mime': 'application/octet-stream',
                             'annex_path': unicode(data['title'], 'utf-8'),
                             'item_path': newItem.absolute_url_path()},
                    context=self.request))
        expected = expected.encode('utf-8')
        self.assertEqual(expected, resp)

    def test_ws_createItemInTheNameOf(self):
        """
          It is possible for Managers and MeetingManagers to create an item inTheNameOf another user
          Every other checks are made except that for using the inTheNameOf functionnality :
          - the calling user must be 'Manager' or 'MeetingManager'
          - the created item is finally like if created by the inTheNameOf user
        """
        self._enableField('category')
        # check first a working example the degrades it...
        # and every related informations (creator, ownership, ...) are corretly linked to inTheNameOf user
        self.changeUser('pmManager')
        req = self._prepareCreationData()
        req._inTheNameOf = 'pmCreator2'
        req._proposingGroupId = 'vendors'
        req._creationData._category = 'development'
        data = {'title': 'My annex 1', 'filename': 'smallTestFile.pdf', 'file': 'smallTestFile.pdf'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data)]
        responseHolder = createItemResponse()
        response = SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        # as we switch user while using inTheNameOf, make sure we have
        # falled back to original user
        self.assertTrue(self.portal.portal_membership.getAuthenticatedMember().getId() == 'pmManager')
        # make also sure that cached methods using user_id are correct as well
        newItem = self.portal.uid_catalog(UID=response._UID)[0].getObject()
        # as the item is really created by the inTheNameOf user, everything is correct
        self.assertEqual(newItem.Creator(), 'pmCreator2')
        self.assertEqual(newItem.owner_info()['id'], 'pmCreator2')
        # with those data but with a non 'Manager'/'MeetingManager', it fails
        self.changeUser('pmCreator1')
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(cm.exception.string,
                         "You need to be 'Manager' or 'MeetingManager' to create an item 'inTheNameOf'!")
        # now use the MeetingManager but specify a proposingGroup the inTheNameOf user can not create for
        self.changeUser('pmManager')
        req._proposingGroupId = 'developers'
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(cm.exception.string, "'pmCreator2' can not create items for the 'developers' group!")
        # now for an unexisting inTheNameOf userid
        req._inTheNameOf = 'unexistingUserId'
        # set back correct proposingGroupId
        req._proposingGroupId = 'vendors'
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(cm.exception.string,
                         "Trying to create an item 'inTheNameOf' an unexisting user 'unexistingUserId'!")
        # create an itemInTheNameOf a user having no personal area...
        # if the user trying to create an item has no member area, a ZSI.Fault is raised
        # remove the 'pmCreator2' personal area
        self.changeUser('admin')
        # remove the created item because we can not remove a folder containing items
        # it would raise a BeforeDeleteException in PloneMeeting
        newItem.aq_inner.aq_parent.manage_delObjects(ids=[newItem.getId(), ])
        self.portal.Members.manage_delObjects(ids=['pmCreator2'])
        self.changeUser('pmManager')
        req._inTheNameOf = 'pmCreator2'
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(cm.exception.string, "No member area for 'pmCreator2'.  Never connected to PloneMeeting?")
        # test that _listAllowedRolesAndUsers is not messed up
        # this happened before because ToolPloneMeeting.get_plone_groups_for_user
        # had a different value between request.AUTHENTICATED_USER and api.user.get_current
        self._check_after_inTheNameOf()

    def test_ws_createItemWithPreferredMeeting(self):
        """
          It is possible to specify a preferred meeting, but the given
          preferred meeting UID must be a meeting accepting items.
        """
        self.changeUser('pmManager')
        # create a fresh meeting that will accept items
        meeting = self.create('Meeting')
        req = self._prepareCreationData()
        req._creationData._preferredMeeting = 'unexisting_meeting_UID'
        responseHolder = createItemResponse()
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(cm.exception.string,
                         "The given preferred meeting UID (unexisting_meeting_UID) is not a meeting accepting items!")
        req._creationData._preferredMeeting = meeting.UID()
        response = SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        # an item has been created with correct preferredMeeting
        item = self.portal.portal_catalog(UID=response._UID)[0].getObject()
        self.assertTrue(item.getPreferredMeeting() == meeting.UID())
        # if no preferredMeeting is provided, the default value 'whatever' is used
        req._creationData._preferredMeeting = None
        response = SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        item = self.portal.portal_catalog(UID=response._UID)[0].getObject()
        self.assertTrue(item.getPreferredMeeting() == ITEM_NO_PREFERRED_MEETING_VALUE)

    def test_ws_createItemWithExtraAttrs(self):
        """
          It is possible to specify arbitraty extraAttrs so we may create items even
          when using a specific profile adding is own fields.  For now it only works with
          XHTML TextFields.
        """
        self.changeUser('pmManager')
        req = self._prepareCreationData()
        ExtraAttr = GTD('http://ws4pm.imio.be', 'ExtraAttr')('').pyclass()
        ExtraAttr._key = 'unexisting_key'
        ExtraAttr._value = '<p>XHTML content</p>'
        req._creationData._extraAttrs = [ExtraAttr]
        responseHolder = createItemResponse()

        # key must be found in the MeetingItem's schema
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(cm.exception.string,
                         "The extraAttr 'unexisting_key' was not found the the MeetingItem schema!")

        # only works with RichText fields
        req._creationData._extraAttrs[0]._key = 'privacy'
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(
            cm.exception.string,
            "The extraAttr 'privacy' must correspond to a field using a 'RichWidget' in the MeetingItem schema!")

        # working example, use RichText field 'notes'
        req._creationData._extraAttrs[0]._key = 'notes'
        response = SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        item = self.portal.portal_catalog(UID=response._UID)[0].getObject()
        self.assertEqual(item.getNotes(), '<p>XHTML content</p>')

    def test_ws_createItemCleanHtml(self):
        """
          Special characters like &#xa0; in the html breaks PortalTransforms
          that is why we clean the HTML from wrong characters and styles
        """

        self.changeUser('pmCreator1')
        req = self._prepareCreationData()
        HTML = "<p style='padding-left: 5em'>My HTML</p><p>&#xa0;</p>"
        req._creationData._decision = HTML
        newItem, response = self._createItem(req)
        self.assertEqual(
            newItem.getDecision(keepWithNext=False),
            '<p>My HTML</p><p>\xc2\xa0</p>')

    def test_ws_createItemCleanHtmlEnabledDisabled(self):
        """
          It is possible to disable cleanHtml (enabled by default),
          this will not clean HTML data while creating the item.
        """
        # by default no item exists
        self.changeUser('pmCreator1')
        req = self._prepareCreationData()
        req._creationData._description = '<p style="font-size: 11pt">Description sample text</p>'
        # cleanHtml enabled
        self.assertEqual(req._cleanHtml, 1)
        newItem, response = self._createItem(req)
        self.assertEqual(newItem.Description(), '<p>Description sample text</p>')
        # cleanHtml disabled
        req._cleanHtml = 0
        newItem, response = self._createItem(req)
        self.assertEqual(newItem.Description(), '<p style="font-size: 11pt">Description sample text</p>')

    def test_ws_createItemGroupsInCharge(self):
        """
          Test when passing groupsInCharge while creating the item.
        """
        cfg = self.meetingConfig
        cfg.setUsedItemAttributes(['category', 'description', 'detailedDescription'])
        # by default no item exists
        self.changeUser('pmCreator1')
        req = self._prepareCreationData()

        # while passing no correct data
        req._creationData._groupsInCharge = [self.vendors_uid, 'unknown_uid']
        responseHolder = createItemResponse()
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        # optional field not enabled
        self.assertEqual(
            cm.exception.string,
            "The optional field \"groupsInCharge\" is not activated in this configuration!")
        # enable optional field, will fail because unknown_uid
        cfg.setUsedItemAttributes(cfg.getUsedItemAttributes() + ('groupsInCharge', ))

        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(
            cm.exception.string,
            'The \"groupsInCharge\" data contains wrong values: "unknown_uid"!')

        # now with correct data
        req._creationData._groupsInCharge = [self.vendors_uid, self.developers_uid]
        newItem, response = self._createItem(req)
        self.assertEqual(newItem.getGroupsInCharge(), [self.vendors_uid, self.developers_uid])

    def test_ws_createItemAssociatedGroups(self):
        """
          Test when passing associatedGroups while creating the item.
        """
        cfg = self.meetingConfig
        cfg.setUsedItemAttributes(['category', 'description', 'detailedDescription'])
        # by default no item exists
        self.changeUser('pmCreator1')
        req = self._prepareCreationData()

        # while passing no correct data
        req._creationData._associatedGroups = [self.vendors_uid, 'unknown_uid']
        responseHolder = createItemResponse()
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        # optional field not enabled
        self.assertEqual(
            cm.exception.string,
            "The optional field \"associatedGroups\" is not activated in this configuration!")
        # enable optional field, will fail because unknown_uid
        cfg.setUsedItemAttributes(cfg.getUsedItemAttributes() + ('associatedGroups', ))
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(
            cm.exception.string,
            'The \"associatedGroups\" data contains wrong values: "unknown_uid"!')

        # now with correct data
        req._creationData._associatedGroups = [self.vendors_uid, self.developers_uid]
        newItem, response = self._createItem(req)
        self.assertEqual(newItem.getAssociatedGroups(), (self.vendors_uid, self.developers_uid))

    def test_ws_createItemOptionalAdvisers(self):
        """
          Test when passing associatedGroups while creating the item.
        """
        cfg = self.meetingConfig
        cfg.setUsedItemAttributes(['category', 'description', 'detailedDescription'])

        # by default no item exists
        self.changeUser('pmCreator1')
        req = self._prepareCreationData()

        # while passing no correct data
        req._creationData._optionalAdvisers = [self.vendors_uid, 'unknown_uid']
        responseHolder = createItemResponse()
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        # advices not enabled
        self.assertEqual(
            cm.exception.string,
            "The advices functionnality is not enabled for this configuration!")
        # enable advices, will fail because unknown_uid
        cfg.setUseAdvices(True)
        cfg.setSelectableAdvisers([self.developers_uid, self.vendors_uid])
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEqual(
            cm.exception.string,
            'The \"optionalAdvisers\" data contains wrong values: "unknown_uid"!')

        # now with correct data
        req._creationData._optionalAdvisers = [self.developers_uid, self.vendors_uid]
        newItem, response = self._createItem(req)
        self.assertEqual(newItem.getOptionalAdvisers(), (self.developers_uid, self.vendors_uid))
        self.assertTrue(self.developers_uid in newItem.adviceIndex)
        self.assertTrue(self.vendors_uid in newItem.adviceIndex)

    def test_ws_createItemWfTransitions(self):
        """
          Test when passing wfTransitions while creating the item.
        """
        self.changeUser('pmCreator1')
        req = self._prepareCreationData()

        # correct wfTransitions
        req._wfTransitions = ['propose', 'validate']
        newItem, response = self._createItem(req)
        self.assertEqual(newItem.query_state(), 'validated')
        self.assertEqual(response._warnings, [])

        # correct and incorrect wfTransitions
        req._wfTransitions = ['propose', 'unknown_transition', 'validate']
        newItem, response = self._createItem(req)
        self.assertEqual(newItem.query_state(), 'validated')
        self.assertEqual(
            response._warnings,
            ["While treating wfTransitions, could not trigger the 'unknown_transition' transition!"])

        # 'present' with no available meeting
        req._wfTransitions = ['propose', 'validate', 'present']
        newItem, response = self._createItem(req)
        self.assertEqual(newItem.query_state(), 'validated')
        self.assertEqual(
            response._warnings,
            ["While treating wfTransitions, could not trigger the 'present' transition! "
             "Make sure a meeting accepting items exists in configuration 'plonegov-assembly'!"])

        # 'present' with available meeting
        self.changeUser('pmManager')
        meeting = self.create('Meeting')
        newItem, response = self._createItem(req)
        self.assertEqual(newItem.query_state(), 'presented')
        self.assertTrue(newItem in meeting.get_items())
        self.assertEqual(response._warnings, [])

    def test_ws_createItemWithAutoAskedAdvices(self):
        """
          Test item creation with auto asked advices.
          Test also the fact that advices are asked on item created from WS or not.
        """
        self.changeUser('siteadmin')
        cfg = self.meetingConfig
        # will ask advice auto when item created from WS
        cfg.setCustomAdvisers(
            [{'row_id': 'unique_id_123',
              'org': self.vendors_uid,
              'gives_auto_advice_on':
                "python: imio_history_utils.getLastWFAction(item, "
                "transition='create_item_using_imio_pm_ws_soap')",
              'for_item_created_from': '2016/08/08',
              'delay': '5',
              'delay_label': ''}, ])
        self.changeUser('pmCreator1')
        req = self._prepareCreationData()
        # check here that when response status is set to 302, it does not break
        # request and it is set back to 200 after creation
        self.request.RESPONSE.status = 302
        wsItem, response = self._createItem(req)
        self.assertTrue(wsItem.getAdviceDataFor(wsItem, self.vendors_uid))
        self.assertEqual(self.request.RESPONSE.status, 200)
        # now create an item manually, the auto advice is not asked
        item = self.create('MeetingItem')
        self.assertFalse(item.getAdviceDataFor(item, self.vendors_uid))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # add a prefix because we heritate from testMeeting and we
    # do not want every tests of testMeeting to be run here...
    suite.addTest(makeSuite(testSOAPCreateItem, prefix='test_ws_'))
    return suite
