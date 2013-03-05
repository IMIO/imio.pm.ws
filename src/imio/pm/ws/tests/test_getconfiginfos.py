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


from imio.pm.ws.tests.WS4PMTestCase import WS4PMTestCase
from imio.pm.ws.WS4PM_client import getConfigInfosRequest, getConfigInfosResponse
from imio.pm.ws.tests.WS4PMTestCase import serializeRequest, deserialize
from imio.pm.ws.soap.soapview import SOAPView


class testSOAPGetConfigInfos(WS4PMTestCase):
    """
        Tests the soap.getConfigInfosRequest method by accessing the real SOAP service
    """

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
        expected = """<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
"""xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
"""xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">""" \
"""<SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body xmlns:ns1="http://ws4pm.imio.be"><ns1:getConfigInfosRequest>""" \
"""<dummy>dummy</dummy></ns1:getConfigInfosRequest></SOAP-ENV:Body></SOAP-ENV:Envelope>"""
        result = """%s""" % request
        self.assertEquals(expected, result)
        #now really use the SOAP method to get informations about the configuration
        responseHolder = getConfigInfosResponse()
        response = SOAPView(self.portal, req).getConfigInfosRequest(req, responseHolder)
        resp = deserialize(response)
        #construct the expected result : header + content + footer
        #header
        expected = """<ns1:getConfigInfosResponse xmlns:ns1="http://ws4pm.imio.be" """ \
"""xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" """ \
"""xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" """ \
"""xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">"""
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
  </configInfo>""" % (element.UID(),
                      element.getId(),
                      element.Title(),
                      element.Description(),
                      element.portal_type)
        #footer.  Empty description is represented like <description/>
        expected = expected.replace('<description></description>', '<description/>') \
                                    + "\n</ns1:getConfigInfosResponse>\n"
        self.assertEquals(expected, resp)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    # add a prefix because we heritate from testMeeting and we do not want every tests of testMeeting to be run here...
    suite.addTest(makeSuite(testSOAPGetConfigInfos, prefix='test_'))
    return suite
