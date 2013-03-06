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

import os
import zipfile
import ZSI
from appy.pod.renderer import NO_PY_PATH
from Products.PloneMeeting.PodTemplate import POD_ERROR
from imio.pm.ws.tests.WS4PMTestCase import WS4PMTestCase
from imio.pm.ws.WS4PM_client import getItemTemplateRequest, getItemTemplateResponse
from imio.pm.ws.soap.soapview import SOAPView


class testSOAPGetItemTemplate(WS4PMTestCase):
    """
        Tests the soap.getItemTemplateRequest method by accessing the real SOAP service
    """

    def test_getItemTemplateRequest(self):
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
        mc = self.portal.portal_plonemeeting.getMeetingConfig(newItem)
        wrongTemplate = mc.podtemplates.agendaTemplate
        req._templateId = wrongTemplate.getId()
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).getItemTemplateRequest(req, responseHolder)
        self.assertEquals(cm.exception.string, 'You can not access this template!')
        # if everything is correct, we receive the rendered template
        req._templateId = mc.podtemplates.itemTemplate.getId()
        renderedTemplate = SOAPView(self.portal, req).getItemTemplateRequest(req, responseHolder)
        # check that the rendered file correspond to the newItem's data
        tmp_file = file('/tmp/%s.zip' % newItemUID, 'w')
        tmp_file.write(renderedTemplate._file)
        tmp_file.close()
        zipped_file = zipfile.ZipFile('/tmp/%s.zip' % newItemUID)
        self.assertTrue(newItem.Title() in zipped_file.read('content.xml'))
        os.remove('/tmp/%s.zip' % newItemUID)
        # test if PloneMeeting raise a PloneMeetingError
        # for example, trying to generate a PDF when Ooo is not in server mode
        mc.podtemplates.itemTemplate.setPodFormat('pdf')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).getItemTemplateRequest(req, responseHolder)
        self.assertEquals(cm.exception.string, 'PloneMeetingError : %s' % POD_ERROR % NO_PY_PATH % 'pdf')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # add a prefix because we heritate from testMeeting and we do not want every tests of testMeeting to be run here...
    suite.addTest(makeSuite(testSOAPGetItemTemplate, prefix='test_'))
    return suite
