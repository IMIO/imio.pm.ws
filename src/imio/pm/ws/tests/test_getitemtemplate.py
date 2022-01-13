# -*- coding: utf-8 -*-
#
# File: test_getitemtemplate.py
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

from imio.helpers.cache import cleanRamCacheFor
from imio.pm.ws.soap.soapview import SOAPView
from imio.pm.ws.tests.WS4PMTestCase import WS4PMTestCase
from imio.pm.ws.WS4PM_client import getItemTemplateRequest
from imio.pm.ws.WS4PM_client import getItemTemplateResponse

import os
import zipfile
import ZSI


class testSOAPGetItemTemplate(WS4PMTestCase):
    """
        Tests the soap.getItemTemplateRequest method by accessing the real SOAP service
    """

    def setUp(self):
        """ """
        WS4PMTestCase.setUp(self)
        # in the PM test profile, some templates are only defined for the plonemeeting-assembly
        self.usedMeetingConfigId = "plonemeeting-assembly"

    def test_ws_getItemTemplateRequest(self):
        """
          Test that getting an item with a given UID and specifying that we want
          showTemplates returns informations about generatable POD templates
        """
        self.changeUser('pmCreator1')
        self.failUnless(len(self.portal.portal_catalog(portal_type='MeetingItemPma')) == 0)
        # prepare data for a default item
        req = self._prepareCreationData()
        # remove unuseable catagory
        req._creationData._category = ''
        # create the item
        newItem, reponse = self._createItem(req)
        # if the user can not access the item, a ZSI Fault is raised
        req = getItemTemplateRequest()
        newItemUID = newItem.UID()
        req._itemUID = newItemUID
        responseHolder = getItemTemplateResponse()
        self.changeUser('pmCreator2')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).getItemTemplateRequest(req, responseHolder)
        self.assertEquals(cm.exception.string, 'You can not access this item!')
        # if we try to use another template, than one available for this item, a ZSI Fault is raised
        self.changeUser('pmCreator1')
        cfg = self.tool.get(self.usedMeetingConfigId)
        wrongTemplate = cfg.podtemplates.agendaTemplate
        req._templateId = '%s__format__%s' % (wrongTemplate.getId(), 'odt')
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).getItemTemplateRequest(req, responseHolder)
        self.assertEquals(cm.exception.string, 'You can not access this template!')
        # if everything is correct, we receive the rendered template
        req._templateId = '{0}__format__{1}'.format(cfg.podtemplates.itemTemplate.getId(), 'odt')
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        renderedTemplate = SOAPView(self.portal, req).getItemTemplateRequest(req, responseHolder)
        # check that the rendered file correspond to the newItem's data
        self._isCorrectlyRenderedTemplate(renderedTemplate, newItem)
        # test if PloneMeeting raise a PloneMeetingError
        # for example, trying to generate a PDF when Ooo is not in server mode
        cfg.podtemplates.itemTemplate.pod_formats = ['pdf']
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).getItemTemplateRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "Exception : Asked output format 'odt' is not available for template 'itemTemplate'!")

    def test_ws_getItemTemplateInTheNameOf(self):
        """
          Test that getting an item template inTheNameOf antother user works
          Create an item by 'pmCreator1', member of the 'developers' group
          Template will be generatable :
          - by 'pmManager'
          - while generating the template inTheNameOf 'pmCreator1'
          Template will NOT be generatable :
          - while generating the template inTheNameOf 'pmCreator2'
            that is not in the 'developers' group
        """
        # create an item by 'pmCreator1'
        self.changeUser('pmCreator1')
        # prepare data for a default item
        req = self._prepareCreationData()
        # remove unuseable catagory
        req._creationData._category = ''
        # create the item
        newItem, reponse = self._createItem(req)
        # prepare data to query the template
        req = getItemTemplateRequest()
        newItemUID = newItem.UID()
        req._itemUID = newItemUID
        cfg = self.meetingConfig
        req._templateId = '%s__format__%s' % (cfg.podtemplates.itemTemplate.getId(), 'odt')
        req._inTheNameOf = 'pmCreator1'
        # the current user can get item template inTheNameOf himself
        responseHolder = getItemTemplateResponse()
        # need to be a 'Manager' or 'MeetingManager'
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).getItemTemplateRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "You need to be 'Manager' or 'MeetingManager' to get "
                          "a template for an item 'inTheNameOf'!")
        # now as MeetingManager, it works
        self.changeUser('pmManager')
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        renderedTemplate = SOAPView(self.portal, req).getItemTemplateRequest(req, responseHolder)
        # check that the rendered file correspond to the newItem's data
        self._isCorrectlyRenderedTemplate(renderedTemplate, newItem)
        # as we switch user while using inTheNameOf, make sure we have
        # falled back to original user
        self.assertTrue(self.portal.portal_membership.getAuthenticatedMember().getId() == 'pmManager')
        # now inTheNameOf a user that can not access newItem
        req._inTheNameOf = 'pmCreator2'
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).getItemTemplateRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "You can not access this item!")
        req._inTheNameOf = 'unexistingUserId'
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).getItemTemplateRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "Trying to create an item 'inTheNameOf' an unexisting user 'unexistingUserId'!")
        self._check_after_inTheNameOf()

    def _isCorrectlyRenderedTemplate(self, renderedTemplate, item):
        """ """
        itemUID = item.UID()
        tmp_file = file('/tmp/%s.zip' % itemUID, 'w')
        tmp_file.write(renderedTemplate._file)
        tmp_file.close()
        zipped_file = zipfile.ZipFile('/tmp/%s.zip' % itemUID)
        self.assertTrue(item.Title() in zipped_file.read('content.xml'))
        os.remove('/tmp/%s.zip' % itemUID)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # add a prefix because we heritate from testMeeting and we do not want every tests of testMeeting to be run here...
    suite.addTest(makeSuite(testSOAPGetItemTemplate, prefix='test_ws_'))
    return suite
