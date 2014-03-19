# -*- coding: utf-8 -*-
#
# File: test_createitem.py
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
import ZSI
import magic
from magic import MagicException
from zope.i18n import translate
from Products.PloneMeeting.interfaces import IAnnexable
from imio.pm.ws.tests.WS4PMTestCase import WS4PMTestCase
from imio.pm.ws.WS4PM_client import createItemResponse
from imio.pm.ws.tests.WS4PMTestCase import serializeRequest, deserialize
from imio.pm.ws.soap.soapview import SOAPView
from imio.pm.ws.soap.soapview import WRONG_HTML_WARNING
from imio.pm.ws.soap.soapview import MULTIPLE_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING
from imio.pm.ws.soap.soapview import MIMETYPE_NOT_FOUND_OF_ANNEX_WARNING


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
"""<description>&lt;p&gt;Description&lt;/p&gt;</description><decision>""" \
"""D\xc3\xa9cision&lt;strong&gt;wrongTagd&lt;/p&gt;</decision></creationData></ns1:createItemRequest>""" \
"""</SOAP-ENV:Body></SOAP-ENV:Envelope>""" % ('pmCreator1', 'meeting')
        result = """POST /plone/createItemRequest HTTP/1.0
Authorization: Basic %s:%s
Content-Length: 102
Content-Type: text/xml
SOAPAction: /
%s""" % ('pmCreator1', 'meeting', request)
        self.assertEquals(expected, result)
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
        self.assertEquals(expected, resp)
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
        self.failIf(obj.getDecision() != "<p></p>")

    def test_ws_createItemRaisedZSIFaults(self):
        """
          Test SOAP service behaviour when creating an item with some wrong arguments
        """
        # by default no item exists
        self.changeUser('pmCreator1')
        req = self._prepareCreationData()
        responseHolder = createItemResponse()
        # the title is mandatory
        req._creationData._title = None
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEquals(cm.exception.string, "A 'title' is mandatory!")
        req._creationData._title = 'A valid title'
        # the meetingConfigId must exists
        req._meetingConfigId = 'wrongMeetingConfigId'
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEquals(cm.exception.string, "Unknown meetingConfigId : 'wrongMeetingConfigId'!")
        req._meetingConfigId = self.usedMeetingConfigId
        # the connected user must be able to create an item for the given proposingGroupId
        req._proposingGroupId = 'vendors'
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEquals(cm.exception.string, "'pmCreator1' can not create items for the 'vendors' group!")
        # the connected user must be able to create an item with the given category
        # set back correct proposingGroup
        req._proposingGroupId = 'developers'
        # if category is mandatory and empty, it raises ZSI.Fault
        self.meetingConfig.setUseGroupsAsCategories(False)
        req._creationData._category = None
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEquals(cm.exception.string, "In this config, category is mandatory!")
        # wrong category and useGroupsAsCategories, ZSI.Fault
        self.meetingConfig.setUseGroupsAsCategories(True)
        req._creationData._category = 'wrong-category-id'
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "This config does not use categories, the given 'wrong-category-id' "
                          "category can not be used!")
        # wrong category and actually accepting categories, aka useGroupsAsCategories to False
        self.meetingConfig.setUseGroupsAsCategories(False)
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "'wrong-category-id' is not available for "
                          "the 'developers' group!")
        # if the user trying to create an item has no member area, a ZSI.Fault is raised
        # remove the 'pmCreator2' personal area
        self.changeUser('admin')
        self.portal.Members.manage_delObjects(ids=['pmCreator2'])
        req._proposingGroupId = 'vendors'
        self.changeUser('pmCreator2')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEquals(cm.exception.string, "No member area for 'pmCreator2'.  Never connected to PloneMeeting?")

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
        self.assertEquals(cm.exception.string,
                          "The optional field 'motivation' is not activated in this configuration!")
        # if we activate it, then the resulting item is correct
        self.meetingConfig.setUsedItemAttributes(self.meetingConfig.getUsedItemAttributes() + ('motivation', ))
        newItem, response = self._createItem(req)
        self.assertTrue(newItem.getMotivation() == '<p>Motivation sample text</p>')

    def test_ws_createItemWithOneAnnexRequest(self):
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
"""<description>&lt;p&gt;Description&lt;/p&gt;</description><decision>&lt;p&gt;Décision&lt;/p&gt;</decision>""" \
"""<annexes xsi:type="ns1:AnnexInfo"><title>%s</title><annexTypeId>%s</annexTypeId><filename>%s</filename><file>
%s</file></annexes></creationData></ns1:createItemRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>""" % \
('pmCreator1', 'meeting', annex._title, annex._annexTypeId, annex._filename, base64.encodestring(annex._file))
        result = """POST /plone/createItemRequest HTTP/1.0
Authorization: Basic %s:%s
Content-Length: 102
Content-Type: text/xml
SOAPAction: /
%s""" % ('pmCreator1', 'meeting', request)
        self.assertEquals(expected, result)
        newItem, response = self._createItem(req)
        #now check the created item have the annex
        annexes = IAnnexable(newItem).getAnnexesInOrder()
        #the annex is actually created
        self.failUnless(len(annexes) == 1)
        #the annex mimetype is correct
        annex = annexes[0]
        self.failUnless(annex.getContentType() == 'application/pdf')
        #the annex metadata are ok
        self.failUnless(annex.Title() == 'My annex 1' and annex.getMeetingFileType().getId() == 'financial-analysis')

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
        annexes = IAnnexable(newItem).getAnnexesInOrder()
        self.failUnless(len(annexes) == 1)
        # the annex mimetype is correct
        annex = annexes[0]
        self.failUnless(annex.getContentType() == 'application/msword')
        # the annex metadata are ok
        self.failUnless(annex.Title() == 'My crashing created annex' and
                        annex.getMeetingFileType().getId() == 'financial-analysis')
        # if libmagic crash and no valid filename provided, the annex is not created
        data = {'title': 'My crashing NOT created annex',
                'filename': 'file_crash_libmagic_without_extension',
                'file': 'file_crash_libmagic.doc'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data)]
        newItem2, response = self._createItem(req)
        self.failUnless(len(IAnnexable(newItem2).getAnnexesInOrder()) == 0)
        # a warning specifying that annex was not added because mimetype could
        # not reliabily be found is added in the response
        self.assertEquals(response._warnings, [translate(MIMETYPE_NOT_FOUND_OF_ANNEX_WARNING,
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
        data1 = {'title': 'My annex 1', 'filename': 'smallTestFile.pdf', 'file': 'smallTestFile.pdf'}
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
        # a file that will have several extensions found in mimetyps_registry
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
        #This is what the sent enveloppe should looks like
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
"""<description>&lt;p&gt;Description&lt;/p&gt;</description><decision>&lt;p&gt;Décision&lt;/p&gt;</decision>""" \
"""%s</creationData></ns1:createItemRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>""" \
% ('pmCreator1', 'meeting', annexesEnveloppePart)
        result = """POST /plone/createItemRequest HTTP/1.0
Authorization: Basic %s:%s
Content-Length: 102
Content-Type: text/xml
SOAPAction: /
%s""" % ('pmCreator1', 'meeting', request)
        self.assertEquals(expected, result)
        newItem, response = self._createItem(req)
        annexes = newItem.objectValues('MeetingFile')
        # 4 annexes are actually created
        self.failUnless(len(annexes) == 4)
        #the annexes mimetype are corrects
        self.failUnless(annexes[0].getContentType() == 'application/pdf')
        self.failUnless(annexes[1].getContentType() == 'application/vnd.oasis.opendocument.text')
        self.failUnless(annexes[2].getContentType() == 'application/msword')
        self.failUnless(annexes[3].getContentType() == 'application/octet-stream')
        # the annexes metadata are ok
        self.failUnless(annexes[0].Title() == 'My annex 1' and
                        annexes[0].getMeetingFileType().getId() == 'financial-analysis')
        self.failUnless(annexes[1].Title() == 'My annex 2' and
                        annexes[1].getMeetingFileType().getId() == 'budget-analysis')
        # meetingFileType is back to default one when a wrong file type is given in the annexInfo
        self.failUnless(annexes[2].Title() == 'My annex 3' and
                        annexes[2].getMeetingFileType().getId() == 'financial-analysis')
        self.failUnless(annexes[3].Title() == 'My annex 6' and
                        annexes[3].getMeetingFileType().getId() == 'budget-analysis')
        # annexes filename are the ones defined in the 'filename', either it is generated
        self.failUnless(annexes[0].getFile().filename == 'smallTestFile.pdf')
        self.failUnless(annexes[1].getFile().filename == 'arbitraryFilename.odt')
        self.failUnless(annexes[2].getFile().filename == 'largeTestFile.doc')
        self.failUnless(annexes[3].getFile().filename == 'validExtension.bin')
        # now try to create an item with an annex that has no file
        # when file attribute is not provided, the annex is not created
        data = {'title': 'My annex 7',
                'filename': 'validExtension.bin',
                'annexTypeId': 'budget-analysis'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data), ]
        self.assertEquals(req._creationData._annexes[0]._file, None)
        newItem, response = self._createItem(req)
        annexes = newItem.objectValues('MeetingFile')
        # no annexes have been added
        self.assertEquals(len(annexes), 0)

    def test_ws_createItemWithWarnings(self):
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
        self.assertEquals(expected, resp)
        #now test warnings around file mimetype
        data = {'title': 'My annex',
                'filename': 'notValidFileNameNoExtension',
                'file': 'octetStreamTestFile.bin',
                'annexTypeId': 'budget-analysis'}
        req._creationData._annexes = [self._prepareAnnexInfo(**data)]
        #several extensions found and no valid filename extension, the annex is not created and a warning is added
        newItem, response = self._createItem(req)
        resp = deserialize(response)
        #2 warnings are returned
        expected = """<ns1:createItemResponse xmlns:ns1="http://ws4pm.imio.be" """ \
            """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
            """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
            """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
            """xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <UID>%s</UID>
  <warnings>%s</warnings>
  <warnings>%s</warnings>
</ns1:createItemResponse>
""" % (newItem.UID(),
       translate(WRONG_HTML_WARNING,
                 domain='imio.pm.ws',
                 mapping={'item_path': newItem.absolute_url_path(),
                          'creator': 'pmCreator1'},
                 context=self.request),
       translate(MULTIPLE_EXTENSION_FOR_MIMETYPE_OF_ANNEX_WARNING,
                 domain='imio.pm.ws',
                 mapping={'mime': 'application/octet-stream',
                          'annex_path': 'notValidFileNameNoExtension',
                          'item_path': newItem.absolute_url_path()},
                 context=self.request)
       )
        self.assertEquals(expected, resp)

    def test_ws_createItemInTheNameOf(self):
        """
          It is possible for Managers and MeetingManagers to create an item inTheNameOf another user
          Every other checks are made except that for using the inTheNameOf functionnality :
          - the calling user must be 'Manager' or 'MeetingManager'
          - the created item is finally like if created by the inTheNameOf user
        """
        # check first a working example the degrades it...
        # and every related informations (creator, ownership, ...) are corretly linked to inTheNameOf user
        self.changeUser('pmManager')
        req = self._prepareCreationData()
        req._inTheNameOf = 'pmCreator2'
        req._proposingGroupId = 'vendors'
        responseHolder = createItemResponse()
        response = SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        # as we switch user while using inTheNameOf, make sure we have
        # falled back to original user
        self.assertTrue(self.portal.portal_membership.getAuthenticatedMember().getId() == 'pmManager')
        newItem = self.portal.uid_catalog(UID=response._UID)[0].getObject()
        # as the item is really created by the inTheNameOf user, everything is correct
        self.assertEquals(newItem.Creator(), 'pmCreator2')
        self.assertEquals(newItem.owner_info()['id'], 'pmCreator2')
        # with those data but with a non 'Manager'/'MeetingManager', it fails
        self.changeUser('pmCreator1')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "You need to be 'Manager' or 'MeetingManager' to create an item 'inTheNameOf'!")
        # now use the MeetingManager but specify a proposingGroup the inTheNameOf user can not create for
        self.changeUser('pmManager')
        req._proposingGroupId = 'developers'
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEquals(cm.exception.string, "'pmCreator2' can not create items for the 'developers' group!")
        # now for an unexisting inTheNameOf userid
        req._inTheNameOf = 'unexistingUserId'
        # set back correct proposingGroupId
        req._proposingGroupId = 'vendors'
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
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
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).createItemRequest(req, responseHolder)
        self.assertEquals(cm.exception.string, "No member area for 'pmCreator2'.  Never connected to PloneMeeting?")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # add a prefix because we heritate from testMeeting and we do not want every tests of testMeeting to be run here...
    suite.addTest(makeSuite(testSOAPCreateItem, prefix='test_ws_'))
    return suite
