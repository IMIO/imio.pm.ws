# -*- coding: utf-8 -*-
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
from imio.pm.ws.testing import WS4PM_PM_TEST_PROFILE_FUNCTIONAL
from imio.pm.ws.WS4PM_client import createItemRequest
from imio.pm.ws.WS4PM_client import createItemResponse
from imio.pm.ws.WS4PM_client import getItemInfosRequest
from imio.pm.ws.WS4PM_client import getItemInfosResponse
from imio.pm.ws.WS4PM_client import searchItemsResponse
from lxml import etree
from Products.PloneMeeting.tests.PloneMeetingTestCase import PloneMeetingTestCase
from ZSI import SoapWriter
from ZSI import TC
from ZSI.schema import GTD

import os


class WS4PMTestCase(PloneMeetingTestCase):
    '''Base class for defining WS4PM test cases.'''

    layer = WS4PM_PM_TEST_PROFILE_FUNCTIONAL

    def setUp(self):
        """ """
        PloneMeetingTestCase.setUp(self)
        # remove items of the config
        self.changeUser('admin')
        self._removeConfigObjectsFor(self.meetingConfig)
        self._removeConfigObjectsFor(self.meetingConfig2)
        # make sure 'detailedDescription' optional field is selected for both configs
        itemAttrs = self.meetingConfig.getUsedItemAttributes()
        self.meetingConfig.setUsedItemAttributes(itemAttrs + ('detailedDescription', ))
        itemAttrs = self.meetingConfig2.getUsedItemAttributes()
        self.meetingConfig2.setUsedItemAttributes(itemAttrs + ('detailedDescription', ))
        # use the 'plonegov-assembly' MeetingConfig that use real categories,
        # not useGroupsAsCategories, even if it could be changed during a test
        self.meetingConfig = self.meetingConfig2
        self.usedMeetingConfigId = 'plonegov-assembly'

    def _prepareCreationData(self):
        """
          Helper method for creating an item using the SOAP method createItem
        """
        # make sure we enabled the 'detailedDescription' optional field
        itemAttrs = self.meetingConfig.getUsedItemAttributes()
        self.meetingConfig.setUsedItemAttributes(itemAttrs + ('detailedDescription', ))
        req = createItemRequest()
        req._meetingConfigId = self.usedMeetingConfigId
        req._proposingGroupId = 'developers'
        CreationData = GTD('http://ws4pm.imio.be', 'CreationData')('').pyclass()
        CreationData._title = 'My new item title'
        CreationData._category = 'development'
        CreationData._description = '<p>Description</p>'
        CreationData._detailedDescription = '<p>Detailed description</p>'
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

    def _getItemInfos(self,
                      itemUID,
                      showAnnexes=False,
                      showExtraInfos=False,
                      showTemplates=False,
                      toBeDeserialized=True):
        """
          Call getItemInfos SOAP method with given itemUID parameter
        """
        req = getItemInfosRequest()
        req._UID = itemUID
        if showAnnexes:
            req._showAnnexes = True
        if showExtraInfos:
            req._showExtraInfos = True
        if showTemplates:
            req._showTemplates = True
        responseHolder = getItemInfosResponse()
        response = SOAPView(self.portal, req).getItemInfosRequest(req, responseHolder)
        if toBeDeserialized:
            return deserialize(response)
        else:
            return response

    def _searchItems(self, req):
        """
          Search items with data of req parameter
        """
        responseHolder = searchItemsResponse()
        response = SOAPView(self.portal, req).searchItemsRequest(req, responseHolder)
        return deserialize(response)




def serializeRequest(request):
    tc = getattr(request, 'typecode', None)
    sw = SoapWriter(nsdict={}, header=True, outputclass=None,
                    encodingStyle=None)
    return str(sw.serialize(request, tc))


def deserialize(objectToDeserialize):
    sw = SoapWriter(nsdict={}, header=True, outputclass=None,
                    encodingStyle=None)
    tc = TC.Any(pname=None, aslist=False)
    deserializedObject = sw.serialize(objectToDeserialize, tc).body
    root = etree.XML(str(deserializedObject))
    body = root[0]
    return etree.tostring(body, encoding='utf-8', pretty_print=True)
