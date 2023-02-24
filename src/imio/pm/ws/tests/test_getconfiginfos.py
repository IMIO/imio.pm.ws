# -*- coding: utf-8 -*-
#
# File: test_getconfiginfos.py
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


from collective.contact.plonegroup.utils import get_organizations
from imio.helpers.cache import cleanRamCacheFor
from imio.pm.ws.soap.soapview import SOAPView
from imio.pm.ws.tests.WS4PMTestCase import deserialize
from imio.pm.ws.tests.WS4PMTestCase import serializeRequest
from imio.pm.ws.tests.WS4PMTestCase import WS4PMTestCase
from imio.pm.ws.WS4PM_client import getConfigInfosRequest
from imio.pm.ws.WS4PM_client import getConfigInfosResponse

import ZSI


class testSOAPGetConfigInfos(WS4PMTestCase):
    """
        Tests the soap.getConfigInfosRequest method by accessing the real SOAP service
    """

    def test_ws_getConfigInfosRequest(self):
        """
          Test that getting informations about the configuration returns valuable informations
        """
        # any PM user can have these configuration informations
        self.changeUser('pmCreator1')
        req = getConfigInfosRequest()
        # Serialize the request so it can be easily tested
        request = serializeRequest(req)
        # This is what the sent enveloppe should looks like
        expected = """<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
                   """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
                   """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
                   """xmlns:xsd="http://www.w3.org/2001/XMLSchema" """ \
                   """xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">""" \
                   """<SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body xmlns:ns1="http://ws4pm.imio.be">""" \
                   """<ns1:getConfigInfosRequest><showCategories>false</showCategories></ns1:getConfigInfosRequest>""" \
                   """</SOAP-ENV:Body></SOAP-ENV:Envelope>"""
        result = """%s""" % request
        self.assertEquals(expected, result)
        # now really use the SOAP method to get informations about the configuration
        responseHolder = getConfigInfosResponse()
        response = SOAPView(self.portal, req).getConfigInfosRequest(req, responseHolder)
        resp = deserialize(response)
        # construct the expected result : header + content + footer
        # header
        expected = """<ns1:getConfigInfosResponse xmlns:ns1="http://ws4pm.imio.be" """ \
                   """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
                   """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
                   """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
                   """xmlns:xsd="http://www.w3.org/2001/XMLSchema" """ \
                   """xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">"""
        # _configInfo
        for cfg in self.tool.getActiveConfigs():
            expected += """
  <configInfo xsi:type="ns1:ConfigInfo">
    <UID>%s</UID>
    <id>%s</id>
    <title>%s</title>
    <description>%s</description>%s
  </configInfo>""" % (cfg.UID(),
                      cfg.getId(),
                      cfg.Title(),
                      cfg.Description(),
                      self._getItemPositiveDecidedStatesFromConfig(cfg))
        # _groupInfo
        for grp in get_organizations():
            expected += """
  <groupInfo xsi:type="ns1:GroupInfo">
    <UID>%s</UID>
    <id>%s</id>
    <title>%s</title>
    <description>%s</description>
  </groupInfo>""" % (grp.UID(),
                     grp.getId(),
                     grp.Title(),
                     grp.Description())
        # footer.  Empty description is represented like <description/>
        expected = expected.replace('<description></description>', '<description/>') \
            + "\n</ns1:getConfigInfosResponse>\n"
        self.assertEquals(expected, resp)

        # elements are correctly stored
        cfg = self.tool.getActiveConfigs()[0]
        self.assertEqual(response._configInfo[0]._id, cfg.id)
        self.assertEqual(response._configInfo[0]._title, cfg.Title())

    def test_ws_getConfigInfosItemPositiveDecidedStates(self):
        """This will return the MeetingConfig.itemPositiveDecidedStates."""
        self.changeUser('pmCreator1')
        req = getConfigInfosRequest()
        responseHolder = getConfigInfosResponse()
        response = SOAPView(self.portal, req).getConfigInfosRequest(req, responseHolder)
        cfg = self.tool.getActiveConfigs()[0]
        # we have defined itemPositiveDecidedStates
        self.assertTrue(cfg.getItemPositiveDecidedStates())
        self.assertEqual(response._configInfo[0]._itemPositiveDecidedStates,
                         cfg.getItemPositiveDecidedStates())
        self.assertTrue(deserialize(response))
        # works if no itemPositiveDecidedStates defined
        cfg.getItemPositiveDecidedStates = lambda: ()
        response = SOAPView(self.portal, req).getConfigInfosRequest(req, responseHolder)
        self.assertEqual(response._configInfo[0]._itemPositiveDecidedStates, ())
        self.assertTrue(deserialize(response))

    def test_ws_showCategories(self):
        """
          Test while getting configInfos with categories.
        """
        self.changeUser('pmCreator1')
        req = getConfigInfosRequest()
        req._showCategories = True
        # Serialize the request so it can be easily tested
        responseHolder = getConfigInfosResponse()
        response = SOAPView(self.portal, req).getConfigInfosRequest(req, responseHolder)
        resp = deserialize(response)
        expected = """<ns1:getConfigInfosResponse xmlns:ns1="http://ws4pm.imio.be" """ \
                   """xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
                   """xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" """ \
                   """xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
                   """xmlns:xsd="http://www.w3.org/2001/XMLSchema" """ \
                   """xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">"""
        # _configInfo
        for cfg in self.tool.getActiveConfigs():
            expected += """
  <configInfo xsi:type="ns1:ConfigInfo">
    <UID>%s</UID>
    <id>%s</id>
    <title>%s</title>
    <description>%s</description>%s%s
  </configInfo>""" % (cfg.UID(),
                      cfg.getId(),
                      cfg.Title(),
                      cfg.Description(),
                      self._getItemPositiveDecidedStatesFromConfig(cfg),
                      self._getResultCategoriesForConfig(cfg))
        # _groupInfo
        for grp in get_organizations():
            expected += """
  <groupInfo xsi:type="ns1:GroupInfo">
    <UID>%s</UID>
    <id>%s</id>
    <title>%s</title>
    <description>%s</description>
  </groupInfo>""" % (grp.UID(),
                     grp.getId(),
                     grp.Title(),
                     grp.Description())
        # footer.  Empty description is represented like <description/>
        expected = expected.replace('<description></description>', '<description/>') \
            + "\n</ns1:getConfigInfosResponse>\n"
        self.assertEquals(expected, resp)
        # the category 'subproducts' is only available to vendors
        self.assertFalse('<id>subproducts</id>' in resp)

    def test_ws_showCategoriesForUser(self):
        """
          Test while getting configInfos with categories and using userToShowCategoriesFor.
        """
        # first of all, we need to be a Manager/MeetingManager to use userToShowCategoriesFor
        self.changeUser('pmCreator1')
        req = getConfigInfosRequest()
        req._showCategories = True
        req._userToShowCategoriesFor = 'pmCreator1'
        responseHolder = getConfigInfosResponse()
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).getConfigInfosRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "You need to be 'Manager' or 'MeetingManager' to get available categories for a user!")
        # now try with a 'pmManager'
        self.changeUser('pmManager')
        req._userToShowCategoriesFor = 'unexistingUserId'
        # the userToShowCategoriesFor must exists!
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        with self.assertRaises(ZSI.Fault) as cm:
            SOAPView(self.portal, req).getConfigInfosRequest(req, responseHolder)
        self.assertEquals(cm.exception.string,
                          "Trying to get avaialble categories for an unexisting user 'unexistingUserId'!")
        # now get it.  The 'subproducts' category is only available to vendors (pmCreator2)
        req._userToShowCategoriesFor = 'pmCreator1'
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        response = SOAPView(self.portal, req).getConfigInfosRequest(req, responseHolder)
        resp = deserialize(response)
        # for 'pmCreator1', subproducts is not available
        self.assertFalse('<id>subproducts</id>' in resp)
        req._userToShowCategoriesFor = 'pmCreator2'
        cleanRamCacheFor('Products.PloneMeeting.ToolPloneMeeting.userIsAmong')
        response = SOAPView(self.portal, req).getConfigInfosRequest(req, responseHolder)
        resp = deserialize(response)
        # but for 'pmCreator2', subproducts is available
        self.assertTrue('<id>subproducts</id>' in resp)

    def _getResultCategoriesForConfig(self, config):
        """
          Helper method for generating result displayed about categories of a MeetingConfig
        """
        # if not using categories, return empty categories list
        if not config.meta_type == 'MeetingConfig' or 'category' not in config.getUsedItemAttributes():
            return ''

        result = ""
        for cat in config.getCategories():
            result += """
    <categories xsi:type="ns1:BasicInfo">
      <UID>%s</UID>
      <id>%s</id>
      <title>%s</title>
      <description>%s</description>
    </categories>""" % (cat.UID(), cat.getId(), cat.Title(), cat.Description())
        # Empty description is represented like <description/>
        result = result.replace('<description></description>', '<description/>')
        return result

    def _getItemPositiveDecidedStatesFromConfig(self, config):
        """
          Helper method for generating result displayed
          about MeetingConfig.itemPositiveDecidedStates
        """
        result = ""
        for state in config.getItemPositiveDecidedStates():
            result += """
    <itemPositiveDecidedStates>%s</itemPositiveDecidedStates>""" \
        % (state)
        return result


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # add a prefix because we heritate from testMeeting and we do not want every tests of testMeeting to be run here...
    suite.addTest(makeSuite(testSOAPGetConfigInfos, prefix='test_ws_'))
    return suite
